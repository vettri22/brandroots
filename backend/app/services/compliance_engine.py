import time
from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.brand import BrandGuideline, ApprovedFact, ApprovedTerminology
from app.models.evidence import BrandEvidence, EvidenceStatus
from app.models.content import ContentDocument
from app.models.review import ReviewJob, Finding, FindingStatus
from app.services.llm_provider import get_llm_service
from app.services.audit_logger import log_audit_event
from app.services.evidence_service import is_evidence_expired

def calculate_compliance_score(findings: List[Dict[str, Any]]) -> float:
    """
    Transparent weighted score deduction from 100.0:
    Critical: -25.0 pts
    High/Warning: -10.0 pts
    Medium: -5.0 pts
    Low/Suggestion: -2.0 pts
    """
    penalty = 0.0
    for f in findings:
        sev = f.get("severity", "medium").lower()
        if sev == "critical":
            penalty += 25.0
        elif sev in ("high", "warning"):
            penalty += 10.0
        elif sev == "medium":
            penalty += 5.0
        else:
            penalty += 2.0
    return max(0.0, min(100.0, round(100.0 - penalty, 1)))

def deduplicate_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates overlapping or redundant findings targeting the same span and rule.
    """
    unique = []
    seen = set()
    for f in findings:
        key = (f.get("location_start"), f.get("location_end"), f.get("rule_id"), f.get("category"))
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique

def run_compliance_check(
    db: Session,
    document: ContentDocument,
    user_id: str,
    user_name: str,
    user_role: str
) -> ReviewJob:
    """
    Executes the Proofline Preflight Review Engine pipeline:
    1. Extracts and normalizes content text
    2. Queries active guidelines, approved terminology, and authorized evidence records
    3. Runs deterministic and contextual compliance verification
    4. Verifies cited rule and evidence IDs against the database
    5. Deduplicates findings and computes risk level and score
    6. Persists immutable ReviewJob and Finding records with provenance snapshots
    """
    start_time = time.time()
    brand_id = document.brand_id

    # 1. Fetch active guidelines, facts, terminology, evidence
    guidelines_query = db.query(BrandGuideline).filter(BrandGuideline.is_active == True)
    if brand_id:
        guidelines_query = guidelines_query.filter(or_(BrandGuideline.brand_id == brand_id, BrandGuideline.brand_id == None))
    guidelines = guidelines_query.all()

    facts = db.query(ApprovedFact).filter(ApprovedFact.is_active == True).all()
    terms = db.query(ApprovedTerminology).filter(ApprovedTerminology.is_active == True).all()

    evidence_query = db.query(BrandEvidence).filter(
        BrandEvidence.is_active == True,
        BrandEvidence.status == EvidenceStatus.APPROVED.value
    )
    if brand_id:
        evidence_query = evidence_query.filter(or_(BrandEvidence.brand_id == brand_id, BrandEvidence.brand_id == None))
    evidence_records = evidence_query.all()

    # Create serializable snapshots for audit & historical traceability
    guideline_dicts = [
        {
            "id": g.id,
            "category": g.category,
            "title": g.title,
            "rule_text": g.rule_text,
            "severity": g.severity,
            "version": g.version,
            "source_reference": g.source_reference,
            "is_active": g.is_active,
            "prohibited_patterns": g.prohibited_patterns,
            "required_phrases": g.required_phrases
        }
        for g in guidelines
    ]
    fact_dicts = [
        {
            "id": f.id,
            "category": f.category,
            "claim_statement": f.claim_statement,
            "canonical_value": f.canonical_value,
            "prohibited_old_values": f.prohibited_old_values,
            "source_document": f.source_document,
            "version": f.version,
            "is_active": f.is_active
        }
        for f in facts
    ]
    evidence_dicts = [
        {
            "id": e.id,
            "category": e.category,
            "claim_title": e.claim_title,
            "approved_wording": e.approved_wording,
            "structured_value": e.structured_value,
            "prohibited_old_values": e.prohibited_old_values,
            "source_location": e.source_location,
            "page_or_section": e.page_or_section,
            "version": e.version,
            "expiry_date": e.expiry_date,
            "is_expired": is_evidence_expired(e),
            "public_use_permission": e.public_use_permission,
            "is_active": e.is_active
        }
        for e in evidence_records
    ]
    term_dicts = [
        {
            "id": t.id,
            "preferred_term": t.preferred_term,
            "prohibited_variants": t.prohibited_variants,
            "rationale": t.rationale,
            "version": t.version,
            "is_active": t.is_active
        }
        for t in terms
    ]

    guideline_snapshot = {g.id: g.version for g in guidelines}
    evidence_snapshot = {e.id: e.version for e in evidence_records}

    # 2. Run analysis
    llm_service = get_llm_service()
    text_to_review = document.current_text or document.raw_text
    analysis_res = llm_service.analyze_content(
        text=text_to_review,
        rules=guideline_dicts,
        facts=fact_dicts,
        evidence=evidence_dicts,
        terminology=term_dicts
    )

    # 3. Deduplicate findings
    deduped_raw_findings = deduplicate_findings(analysis_res.findings)

    # 4. Verify cited rule & evidence IDs exist in database
    valid_rule_ids = set([g.id for g in guidelines] + [t.id for t in terms] + [f.id for f in facts] + [e.id for e in evidence_records])
    verified_findings = []
    for f in deduped_raw_findings:
        rid = f.get("rule_id")
        if rid and rid not in valid_rule_ids:
            # If cited rule doesn't exist, flag or clear ID to maintain referential integrity
            f["rule_id"] = None
        verified_findings.append(f)

    # 5. Compute metrics & risk level
    compliance_score = calculate_compliance_score(verified_findings)
    crit_count = sum(1 for f in verified_findings if f.get("severity") == "critical")
    warn_count = sum(1 for f in verified_findings if f.get("severity") in ("warning", "high"))
    sugg_count = sum(1 for f in verified_findings if f.get("severity") in ("medium", "suggestion", "low"))

    risk_level = "low"
    requires_human_review = False
    if crit_count > 0:
        risk_level = "critical"
        requires_human_review = True
    elif warn_count > 1:
        risk_level = "high"
        requires_human_review = True
    elif warn_count > 0:
        risk_level = "medium"

    duration_ms = int((time.time() - start_time) * 1000)

    # 6. Create immutable ReviewJob
    job = ReviewJob(
        workspace_id=document.workspace_id,
        organization_id=document.organization_id,
        brand_id=document.brand_id,
        document_id=document.id,
        document_version=document.current_version,
        status="completed",
        compliance_score=compliance_score,
        findings_count=len(verified_findings),
        critical_count=crit_count,
        warning_count=warn_count,
        suggestion_count=sugg_count,
        guideline_snapshot=guideline_snapshot,
        evidence_snapshot=evidence_snapshot,
        provider_used=analysis_res.provider_type,
        model_name=analysis_res.model_name,
        execution_duration_ms=max(1, duration_ms),
        risk_level=risk_level,
        requires_human_review=requires_human_review,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    db.add(job)
    db.flush()

    # 7. Persist findings
    for f_data in verified_findings:
        finding = Finding(
            review_job_id=job.id,
            category=f_data.get("category", "general"),
            severity=f_data.get("severity", "medium"),
            confidence=f_data.get("confidence", "moderate"),
            detection_method=f_data.get("detection_method", "deterministic_verified"),
            location_start=f_data.get("location_start", 0),
            location_end=f_data.get("location_end", 0),
            affected_text=f_data.get("affected_text", ""),
            explanation=f_data.get("explanation", ""),
            rule_id=f_data.get("rule_id"),
            rule_version=f_data.get("rule_version", 1),
            evidence_ids=f_data.get("evidence_ids", []),
            source_reference=f_data.get("source_reference"),
            suggested_correction=f_data.get("suggested_correction"),
            status=FindingStatus.OPEN.value
        )
        db.add(finding)

    db.commit()
    db.refresh(job)

    log_audit_event(
        db=db,
        event_type="REVIEW_COMPLETED",
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        target_type="document",
        target_id=document.id,
        summary=f"Completed preflight review for '{document.title}' v{document.current_version} (Score: {compliance_score}%, Findings: {len(verified_findings)}, Risk: {risk_level})",
        details={
            "review_job_id": job.id,
            "compliance_score": compliance_score,
            "critical_count": crit_count,
            "risk_level": risk_level,
            "duration_ms": duration_ms
        }
    )

    return job
