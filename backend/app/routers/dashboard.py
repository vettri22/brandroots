from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.content import ContentDocument, DocumentStatus
from app.models.review import Finding, ReviewJob
from app.models.brand import BrandGuideline, ApprovedFact
from app.models.debugger import GuidelineInsight
from app.models.audit import AuditEvent
from app.schemas.audit import AuditEventResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    # 1. Pending reviews
    pending_docs = db.query(ContentDocument).filter(
        ContentDocument.status.in_([DocumentStatus.SUBMITTED.value, DocumentStatus.IN_REVIEW.value, DocumentStatus.RESUBMITTED.value])
    ).count()

    total_docs = db.query(ContentDocument).count()
    approved_docs = db.query(ContentDocument).filter(ContentDocument.status == DocumentStatus.APPROVED.value).count()

    # 2. Findings by Severity
    severity_counts = {
        "critical": db.query(Finding).filter(Finding.severity == "critical").count(),
        "warning": db.query(Finding).filter(Finding.severity.in_(["high", "warning"])).count(),
        "suggestion": db.query(Finding).filter(Finding.severity.in_(["medium", "low", "suggestion"])).count(),
    }

    # 3. Findings by Category
    category_rows = db.query(Finding.category, func.count(Finding.id)).group_by(Finding.category).all()
    category_counts = {cat: count for cat, count in category_rows}

    # 4. Top Recurring Violations
    rule_counts = db.query(Finding.rule_id, func.count(Finding.id))\
        .filter(Finding.rule_id != None)\
        .group_by(Finding.rule_id)\
        .order_by(func.count(Finding.id).desc())\
        .limit(5).all()
    top_violations = [{"rule_id": r[0], "count": r[1]} for r in rule_counts]

    # 5. Guideline Ambiguity Candidates
    ambiguity_insights = db.query(GuidelineInsight).filter(
        GuidelineInsight.hypothesis_status.in_(["hypothesis", "confirmed"])
    ).count()

    # 6. Expired / Inactive Facts
    active_facts = db.query(ApprovedFact).filter(ApprovedFact.is_active == True).count()
    active_guidelines = db.query(BrandGuideline).filter(BrandGuideline.is_active == True).count()

    return {
        "data_mode": "seeded_demonstration_and_live",
        "pending_reviews": pending_docs,
        "total_documents": total_docs,
        "approved_documents": approved_docs,
        "findings_by_severity": severity_counts,
        "findings_by_category": category_counts,
        "top_recurring_violations": top_violations,
        "guideline_ambiguity_candidates": ambiguity_insights,
        "active_guidelines_count": active_guidelines,
        "active_facts_count": active_facts
    }

@router.get("/audit-logs", response_model=List[AuditEventResponse])
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
