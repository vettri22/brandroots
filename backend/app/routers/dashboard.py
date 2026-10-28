from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db
from app.models.content import ContentDocument, DocumentStatus
from app.models.review import Finding, ReviewJob, SuggestionDecision, ApprovalRecord
from app.models.brand import BrandGuideline, ApprovedFact, Brand
from app.models.evidence import BrandEvidence, EvidenceStatus
from app.models.debugger import GuidelineInsight
from app.models.audit import AuditEvent
from app.schemas.audit import AuditEventResponse
from app.services.evidence_service import is_evidence_expired

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/metrics")
def get_dashboard_metrics(
    brand_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Computes real operational governance metrics from actual database events and records.
    Every metric is backed by persistent database records.
    """
    # Filter documents
    doc_query = db.query(ContentDocument)
    if brand_id:
        doc_query = doc_query.filter(or_(ContentDocument.brand_id == brand_id, ContentDocument.brand_id == None))
    
    total_docs = doc_query.count()
    pending_docs = doc_query.filter(
        ContentDocument.status.in_([
            DocumentStatus.SUBMITTED.value,
            DocumentStatus.IN_REVIEW.value,
            DocumentStatus.RESUBMITTED.value
        ])
    ).count()
    approved_docs = doc_query.filter(ContentDocument.status == DocumentStatus.APPROVED.value).count()
    changes_requested_docs = doc_query.filter(ContentDocument.status == DocumentStatus.CHANGES_REQUESTED.value).count()
    rejected_docs = doc_query.filter(ContentDocument.status == DocumentStatus.REJECTED.value).count()

    # Review Jobs & Score
    job_query = db.query(ReviewJob)
    if brand_id:
        job_query = job_query.filter(or_(ReviewJob.brand_id == brand_id, ReviewJob.brand_id == None))
    completed_reviews = job_query.filter(ReviewJob.status == "completed").count()
    avg_score_row = job_query.filter(ReviewJob.status == "completed").with_entities(func.avg(ReviewJob.compliance_score)).scalar()
    avg_compliance_score = round(float(avg_score_row), 1) if avg_score_row is not None else 100.0

    # Unresolved High Severity Findings
    finding_query = db.query(Finding)
    severity_counts = {
        "critical": db.query(Finding).filter(Finding.severity == "critical", Finding.status == "open").count(),
        "warning": db.query(Finding).filter(Finding.severity.in_(["high", "warning"]), Finding.status == "open").count(),
        "suggestion": db.query(Finding).filter(Finding.severity.in_(["medium", "low", "suggestion"]), Finding.status == "open").count(),
    }
    unresolved_high_severity = severity_counts["critical"] + severity_counts["warning"]

    # Findings by Category
    category_rows = db.query(Finding.category, func.count(Finding.id))\
        .filter(Finding.status == "open")\
        .group_by(Finding.category).all()
    category_counts = {cat: count for cat, count in category_rows}

    # Top Recurring Violations
    rule_counts = db.query(Finding.rule_id, func.count(Finding.id))\
        .filter(Finding.rule_id != None)\
        .group_by(Finding.rule_id)\
        .order_by(func.count(Finding.id).desc())\
        .limit(5).all()
    
    top_violations = []
    for r in rule_counts:
        rule_meta = db.query(BrandGuideline).filter(BrandGuideline.id == r[0]).first()
        title = rule_meta.title if rule_meta else r[0]
        top_violations.append({
            "rule_id": r[0],
            "title": title,
            "count": r[1]
        })

    # Evidence Expiry metrics
    all_evidence = db.query(BrandEvidence).filter(BrandEvidence.is_active == True).all()
    expired_evidence_count = sum(1 for e in all_evidence if is_evidence_expired(e))

    # Overrides from SuggestionDecisions
    override_count = db.query(SuggestionDecision).filter(SuggestionDecision.action == "rejected").count()

    # Guideline Clarity Radar Signals
    clarity_signals_count = db.query(GuidelineInsight).filter(
        GuidelineInsight.status_marking.in_(["under_investigation", "needs_clarification"])
    ).count()

    # Approvals recorded
    approvals_count = db.query(ApprovalRecord).filter(ApprovalRecord.status == "approved").count()

    return {
        "data_mode": "seeded_demonstration_and_live",
        "is_empty": (total_docs == 0 and completed_reviews == 0),
        "total_documents": total_docs,
        "pending_reviews": pending_docs,
        "completed_reviews": completed_reviews,
        "approved_documents": approved_docs,
        "changes_requested_documents": changes_requested_docs,
        "rejected_documents": rejected_docs,
        "approvals_recorded": approvals_count,
        "average_compliance_score": avg_compliance_score,
        "unresolved_high_severity": unresolved_high_severity,
        "findings_by_severity": severity_counts,
        "findings_by_category": category_counts,
        "top_recurring_violations": top_violations,
        "expired_evidence_count": expired_evidence_count,
        "repeated_overrides_count": override_count,
        "guideline_clarity_signals_count": clarity_signals_count,
        "active_guidelines_count": db.query(BrandGuideline).filter(BrandGuideline.is_active == True).count(),
        "active_evidence_count": len(all_evidence)
    }

@router.get("/audit-logs", response_model=List[AuditEventResponse])
def get_audit_logs(
    limit: int = 50,
    target_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if target_type:
        query = query.filter(AuditEvent.target_type == target_type)
    return query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()
