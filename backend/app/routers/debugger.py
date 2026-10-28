from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User, UserRole
from app.models.debugger import GuidelineInsight, ProposedGuidelineClarification
from app.schemas.debugger import (
    GuidelineInsightResponse, HypothesisActionRequest,
    ProposedClarificationResponse, ClarificationApprovalRequest
)
from app.core.auth import get_current_user, require_role
from app.services.guideline_debugger import (
    run_guideline_debugger_clustering,
    confirm_or_dismiss_hypothesis,
    approve_guideline_clarification
)
from app.services.audit_logger import log_audit_event

router = APIRouter(prefix="/debugger", tags=["Guideline Debugger"])

@router.post("/cluster", response_model=List[GuidelineInsightResponse])
def trigger_clustering(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Runs clustering across all review findings in the database.
    Identifies recurring violations and generates draft guideline clarifications.
    """
    insights = run_guideline_debugger_clustering(db)
    return insights

@router.get("/insights", response_model=List[GuidelineInsightResponse])
def list_insights(db: Session = Depends(get_db)):
    # Run clustering automatically if no insights exist yet
    existing = db.query(GuidelineInsight).order_by(GuidelineInsight.occurrence_count.desc()).all()
    if not existing:
        existing = run_guideline_debugger_clustering(db)
    return existing

@router.post("/insights/{insight_id}/evaluate", response_model=GuidelineInsightResponse)
def evaluate_hypothesis(
    insight_id: str,
    req: HypothesisActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        updated = confirm_or_dismiss_hypothesis(
            db=db,
            insight_id=insight_id,
            action=req.action,
            notes=req.decision_notes,
            status_marking=req.status_marking,
            user_name=current_user.full_name,
            user_role=current_user.role
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/clarifications", response_model=List[ProposedClarificationResponse])
def list_clarifications(
    status_filter: str = "pending",
    db: Session = Depends(get_db)
):
    query = db.query(ProposedGuidelineClarification)
    if status_filter != "all":
        query = query.filter(ProposedGuidelineClarification.approval_status == status_filter)
    return query.order_by(ProposedGuidelineClarification.created_at.desc()).all()

@router.post("/clarifications/{proposal_id}/decide")
def decide_clarification(
    proposal_id: str,
    req: ClarificationApprovalRequest,
    current_user: User = Depends(require_role([UserRole.BRAND_OWNER.value])),
    db: Session = Depends(get_db)
):
    """
    Explicit approval or rejection of a proposed guideline clarification.
    Only the Brand Owner role is permitted to modify active brand guidelines.
    """
    proposal = db.query(ProposedGuidelineClarification).filter(
        ProposedGuidelineClarification.id == proposal_id
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if req.decision.lower() == "approve":
        rule, prop = approve_guideline_clarification(
            db=db,
            proposal_id=proposal_id,
            brand_owner_name=current_user.full_name,
            edited_rule_text=req.edited_rule_text,
            notes=req.notes
        )
        return {
            "message": f"Clarification approved! Guideline '{rule.id}' updated to version v{rule.version}.",
            "rule_id": rule.id,
            "new_version": rule.version,
            "rule_text": rule.rule_text,
            "proposal_status": prop.approval_status
        }
    else:
        proposal.approval_status = "rejected"
        proposal.reviewer_notes = req.notes
        proposal.reviewed_by = current_user.full_name
        proposal.reviewed_at = db.query(ProposedGuidelineClarification).first().created_at

        log_audit_event(
            db=db,
            event_type="CLARIFICATION_REJECTED",
            actor_id=current_user.id,
            actor_name=current_user.full_name,
            actor_role=current_user.role,
            target_type="clarification",
            target_id=proposal.id,
            summary=f"Brand Owner rejected guideline clarification proposal '{proposal.id}'"
        )
        db.commit()
        return {
            "message": f"Proposal '{proposal_id}' was rejected.",
            "proposal_status": "rejected"
        }
