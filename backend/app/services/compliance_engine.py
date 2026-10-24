from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.brand import BrandGuideline, ApprovedFact, ApprovedTerminology
from app.models.content import ContentDocument
from app.models.review import ReviewJob, Finding, FindingStatus
from app.services.llm_provider import get_llm_service
from app.services.audit_logger import log_audit_event

def calculate_compliance_score(findings: List[Dict[str, Any]]) -> float:
    """
    Transparent weighted score deduction from 100.0
    Critical: -25 pts
    High/Warning: -10 pts
    Medium: -5 pts
    Low/Suggestion: -2 pts
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

def run_compliance_check(
    db: Session,
    document: ContentDocument,
    user_id: str,
    user_name: str,
    user_role: str
) -> ReviewJob:
    """
    Executes hybrid deterministic and contextual brand compliance review.
    Captures snapshot of guidelines used so future revisions remain historically traceable.
    """
    # 1. Fetch active guidelines, facts, terminology
    guidelines = db.query(BrandGuideline).filter(BrandGuideline.is_active == True).all()
    facts = db.query(ApprovedFact).filter(ApprovedFact.is_active == True).all()
    terms = db.query(ApprovedTerminology).filter(ApprovedTerminology.is_active == True).all()

    # Create serializable snapshots
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

    version_snapshot = {
        g.id: g.version for g in guidelines
    }

    # 2. Execute analysis
    llm_service = get_llm_service()
    text_to_review = document.current_text or document.raw_text
    analysis_res = llm_service.analyze_content(
        text=text_to_review,
        rules=guideline_dicts,
        facts=fact_dicts,
        terminology=term_dicts
    )

    raw_findings = analysis_res.findings
    score = calculate_compliance_score(raw_findings)

    crit_cnt = sum(1 for f in raw_findings if f.get("severity") == "critical")
    warn_cnt = sum(1 for f in raw_findings if f.get("severity") in ("high", "warning"))
    sugg_cnt = sum(1 for f in raw_findings if f.get("severity") in ("medium", "low", "suggestion"))

    # 3. Create ReviewJob record
    job = ReviewJob(
        document_id=document.id,
        document_version=document.current_version,
        status="completed",
        compliance_score=score,
        findings_count=len(raw_findings),
        critical_count=crit_cnt,
        warning_count=warn_cnt,
        suggestion_count=sugg_cnt,
        guideline_snapshot=version_snapshot,
        provider_used=analysis_res.provider_type,
        completed_at=datetime.utcnow()
    )
    db.add(job)
    db.flush()

    # 4. Insert Finding records
    for rf in raw_findings:
        finding = Finding(
            review_job_id=job.id,
            category=rf.get("category", "voice"),
            severity=rf.get("severity", "warning"),
            confidence=rf.get("confidence", "rule_based"),
            location_start=rf.get("location_start", 0),
            location_end=rf.get("location_end", 0),
            affected_text=rf.get("affected_text", ""),
            explanation=rf.get("explanation", ""),
            rule_id=rf.get("rule_id"),
            rule_version=rf.get("rule_version", 1),
            source_reference=rf.get("source_reference"),
            suggested_correction=rf.get("suggested_correction"),
            status=FindingStatus.OPEN.value
        )
        db.add(finding)

    db.commit()
    db.refresh(job)

    # 5. Audit Log
    log_audit_event(
        db=db,
        event_type="REVIEW_COMPLETED",
        actor_id=user_id,
        actor_name=user_name,
        actor_role=user_role,
        target_type="document",
        target_id=document.id,
        summary=f"Automated compliance review completed for '{document.title}' (Score: {score}/100, Findings: {len(raw_findings)})",
        details={
            "job_id": job.id,
            "document_version": document.current_version,
            "score": score,
            "findings_count": len(raw_findings),
            "provider_used": analysis_res.provider_type
        }
    )

    return job
