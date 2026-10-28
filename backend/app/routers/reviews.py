from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.auth import User, UserRole
from app.models.content import ContentDocument, DocumentStatus, DocumentVersion
from app.models.review import (
    ReviewJob, Finding, ReviewComment, FindingStatus, SuggestionDecision, ApprovalRecord
)
from app.models.notification import Notification
from app.schemas.review import (
    ReviewJobResponse, FindingResponse, FindingResolutionRequest,
    ReviewCommentCreate, ReviewCommentResponse,
    SuggestionDecisionResponse, ApprovalRecordResponse
)
from app.schemas.content import StatusTransitionRequest
from app.core.auth import get_current_user, require_role, require_permission
from app.services.compliance_engine import run_compliance_check
from app.services.audit_logger import log_audit_event

router = APIRouter(prefix="/reviews", tags=["Preflight Review Engine & Correction Studio"])

@router.post("/check/{document_id}", response_model=ReviewJobResponse)
def trigger_review(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(ContentDocument).filter(ContentDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    job = run_compliance_check(
        db=db,
        document=doc,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role
    )
    return job

@router.get("/jobs/{document_id}", response_model=List[ReviewJobResponse])
def get_document_review_jobs(document_id: str, db: Session = Depends(get_db)):
    return db.query(ReviewJob).filter(ReviewJob.document_id == document_id).order_by(ReviewJob.created_at.desc()).all()

@router.get("/findings/{review_job_id}", response_model=List[FindingResponse])
def get_job_findings(review_job_id: str, db: Session = Depends(get_db)):
    return db.query(Finding).filter(Finding.review_job_id == review_job_id).all()

# --- Correction Studio: Accept / Reject / Edit Suggestion ---

@router.put("/findings/{finding_id}/resolve", response_model=FindingResponse)
def resolve_finding(
    finding_id: str,
    resolution: FindingResolutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Correction Studio:
    - accept suggestion: patches draft, creates immutable DocumentVersion, logs SuggestionDecision
    - reject suggestion: records rejection reason and audit event without modifying draft
    - edit suggestion: applies custom wording, creates DocumentVersion, logs SuggestionDecision
    """
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    job = db.query(ReviewJob).filter(ReviewJob.id == finding.review_job_id).first()
    doc = db.query(ContentDocument).filter(ContentDocument.id == job.document_id).first() if job else None
    if not doc:
        raise HTTPException(status_code=404, detail="Associated content document not found")

    action = resolution.status.lower()
    finding.status = action
    finding.creator_decision = action
    finding.creator_decision_reason = resolution.reason or resolution.resolution_notes
    finding.resolution_notes = resolution.resolution_notes
    finding.resolved_by = current_user.full_name
    finding.resolved_at = datetime.utcnow()

    applied_text = None
    if action in ("accepted", "edited"):
        replacement = resolution.custom_replacement_text if action == "edited" else finding.suggested_correction
        applied_text = replacement
        if replacement and finding.affected_text in doc.current_text:
            # Patch draft in-place
            doc.current_text = doc.current_text.replace(finding.affected_text, replacement, 1)
            doc.current_version += 1

            # Invalidate approval if document was previously approved
            if doc.status == DocumentStatus.APPROVED.value or doc.approved_version is not None:
                doc.status = DocumentStatus.DRAFT.value
                doc.approved_version = None
                doc.approved_at = None
                doc.approved_by_id = None
                doc.approved_by_name = None

            doc.updated_at = datetime.utcnow()

            # Save immutable version snapshot
            ver = DocumentVersion(
                document_id=doc.id,
                version_number=doc.current_version,
                text_snapshot=doc.current_text,
                changelog=f"Correction Studio ({action}): '{finding.affected_text}' -> '{replacement}'",
                author_id=current_user.id,
                author_name=current_user.full_name
            )
            db.add(ver)

    # Persist decision record
    decision = SuggestionDecision(
        finding_id=finding.id,
        document_id=doc.id,
        document_version=doc.current_version,
        action=action,
        original_text=finding.affected_text,
        applied_text=applied_text,
        reason=resolution.reason or resolution.resolution_notes,
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role
    )
    db.add(decision)
    db.commit()
    db.refresh(finding)

    log_audit_event(
        db=db,
        event_type=f"SUGGESTION_{action.upper()}",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="finding",
        target_id=finding.id,
        summary=f"Suggestion {action} by {current_user.full_name}: '{finding.affected_text}' (Reason: {resolution.reason or 'None'})",
        details={"action": action, "applied_text": applied_text, "reason": resolution.reason}
    )

    return finding

# --- Review Queue & Workflow Transitions ---

ALLOWED_TRANSITIONS = {
    DocumentStatus.DRAFT.value: [DocumentStatus.SUBMITTED.value, DocumentStatus.ARCHIVED.value],
    DocumentStatus.SUBMITTED.value: [DocumentStatus.IN_REVIEW.value, DocumentStatus.CHANGES_REQUESTED.value, DocumentStatus.ARCHIVED.value],
    DocumentStatus.IN_REVIEW.value: [DocumentStatus.CHANGES_REQUESTED.value, DocumentStatus.APPROVED.value, DocumentStatus.REJECTED.value],
    DocumentStatus.CHANGES_REQUESTED.value: [DocumentStatus.RESUBMITTED.value, DocumentStatus.DRAFT.value, DocumentStatus.ARCHIVED.value],
    DocumentStatus.RESUBMITTED.value: [DocumentStatus.IN_REVIEW.value, DocumentStatus.APPROVED.value, DocumentStatus.REJECTED.value],
    DocumentStatus.APPROVED.value: [DocumentStatus.DRAFT.value, DocumentStatus.ARCHIVED.value],
    DocumentStatus.REJECTED.value: [DocumentStatus.DRAFT.value, DocumentStatus.RESUBMITTED.value, DocumentStatus.ARCHIVED.value],
    DocumentStatus.ARCHIVED.value: [DocumentStatus.DRAFT.value]
}

@router.get("/queue")
def get_review_queue(
    brand_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns pending review queue items awaiting reviewer action.
    """
    active_statuses = [
        DocumentStatus.SUBMITTED.value,
        DocumentStatus.IN_REVIEW.value,
        DocumentStatus.RESUBMITTED.value
    ]
    query = db.query(ContentDocument).filter(ContentDocument.status.in_(active_statuses))
    if brand_id:
        query = query.filter(or_(ContentDocument.brand_id == brand_id, ContentDocument.brand_id == None))
    if assignee_id:
        query = query.filter(ContentDocument.assigned_reviewer_id == assignee_id)
        
    items = query.order_by(ContentDocument.updated_at.desc()).all()
    queue_data = []
    for doc in items:
        latest_job = db.query(ReviewJob).filter(ReviewJob.document_id == doc.id).order_by(ReviewJob.created_at.desc()).first()
        queue_data.append({
            "document": doc,
            "latest_review_job": latest_job
        })
    return queue_data

@router.post("/documents/{document_id}/assign")
def assign_reviewer(
    document_id: str,
    reviewer_id: str,
    current_user: User = Depends(require_permission("content:review")),
    db: Session = Depends(get_db)
):
    doc = db.query(ContentDocument).filter(ContentDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    reviewer = db.query(User).filter(User.id == reviewer_id).first()
    if not reviewer:
        raise HTTPException(status_code=404, detail="Reviewer not found")
        
    doc.assigned_reviewer_id = reviewer.id
    doc.assigned_reviewer_name = reviewer.full_name
    doc.updated_at = datetime.utcnow()
    
    # Send notification to reviewer
    notif = Notification(
        workspace_id=doc.workspace_id,
        user_id=reviewer.id,
        title="New Review Assignment",
        message=f"You have been assigned to review '{doc.title}' (v{doc.current_version}) by {current_user.full_name}.",
        notification_type="review_action",
        reference_type="document",
        reference_id=doc.id
    )
    db.add(notif)
    db.commit()
    db.refresh(doc)
    return {"message": f"Assigned '{doc.title}' to {reviewer.full_name}"}

@router.post("/documents/{document_id}/transition")
def transition_document_status(
    document_id: str,
    req: StatusTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(ContentDocument).filter(ContentDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    old_status = doc.status
    target_status = req.new_status.lower()

    # Validate state machine
    allowed = ALLOWED_TRANSITIONS.get(old_status, [])
    if target_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Illegal transition from '{old_status}' to '{target_status}'. Allowed transitions: {allowed}"
        )

    # Policy Enforcement: Creators cannot approve their own work!
    if target_status == DocumentStatus.APPROVED.value:
        if current_user.role == UserRole.CREATOR.value and doc.creator_id == current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Policy violation: Content creators cannot approve their own submitted work. Requires Reviewer or Brand Administrator role."
            )
        if current_user.role not in (UserRole.REVIEWER.value, UserRole.BRAND_OWNER.value, "brand_admin", "org_owner"):
            raise HTTPException(
                status_code=403,
                detail="Approval requires Reviewer, Brand Administrator, or Org Owner role."
            )

        # Get latest review job to bind approval
        latest_job = db.query(ReviewJob).filter(
            ReviewJob.document_id == doc.id,
            ReviewJob.document_version == doc.current_version
        ).order_by(ReviewJob.created_at.desc()).first()

        # Version-bound approval!
        doc.approved_version = doc.current_version
        doc.approved_at = datetime.utcnow()
        doc.approved_by_id = current_user.id
        doc.approved_by_name = current_user.full_name

        approval = ApprovalRecord(
            document_id=doc.id,
            document_version=doc.current_version,
            review_job_id=latest_job.id if latest_job else "unreviewed",
            status="approved",
            approver_id=current_user.id,
            approver_name=current_user.full_name,
            approver_role=current_user.role,
            decision_reason=req.comment or "Meets brand guidelines and evidence standards"
        )
        db.add(approval)

        # Create notification for creator
        notif = Notification(
            workspace_id=doc.workspace_id,
            user_id=doc.creator_id,
            title="Document Approved",
            message=f"'{doc.title}' v{doc.current_version} has been approved by {current_user.full_name}.",
            notification_type="approval",
            reference_type="document",
            reference_id=doc.id
        )
        db.add(notif)

    elif target_status in (DocumentStatus.CHANGES_REQUESTED.value, DocumentStatus.REJECTED.value):
        # Notify creator of change request or rejection
        notif = Notification(
            workspace_id=doc.workspace_id,
            user_id=doc.creator_id,
            title=f"Document {target_status.replace('_', ' ').title()}",
            message=f"Reviewer {current_user.full_name} set '{doc.title}' to {target_status}. Notes: {req.comment or 'None'}",
            notification_type="review_action",
            reference_type="document",
            reference_id=doc.id
        )
        db.add(notif)

    doc.status = target_status
    doc.updated_at = datetime.utcnow()

    # Record comment/decision
    comment = ReviewComment(
        document_id=doc.id,
        document_version=doc.current_version,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        comment_text=req.comment or f"Status changed from {old_status} to {target_status}",
        action_type=target_status
    )
    db.add(comment)
    db.commit()
    db.refresh(doc)

    log_audit_event(
        db=db,
        event_type="DOCUMENT_STATUS_TRANSITION",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="document",
        target_id=doc.id,
        summary=f"Document '{doc.title}' transitioned from '{old_status}' to '{target_status}' by {current_user.full_name} ({current_user.role})",
        details={"from": old_status, "to": target_status, "comment": req.comment, "version": doc.current_version}
    )

    return {
        "message": f"Document transitioned to {target_status}",
        "document_id": doc.id,
        "status": doc.status,
        "current_version": doc.current_version,
        "approved_version": doc.approved_version
    }

@router.get("/documents/{document_id}/approvals", response_model=List[ApprovalRecordResponse])
def get_document_approvals(document_id: str, db: Session = Depends(get_db)):
    return db.query(ApprovalRecord).filter(
        ApprovalRecord.document_id == document_id
    ).order_by(ApprovalRecord.created_at.desc()).all()

@router.get("/documents/{document_id}/comments", response_model=List[ReviewCommentResponse])
def get_document_comments(document_id: str, db: Session = Depends(get_db)):
    return db.query(ReviewComment).filter(ReviewComment.document_id == document_id).order_by(ReviewComment.created_at.asc()).all()

@router.post("/documents/{document_id}/comments", response_model=ReviewCommentResponse)
def add_document_comment(
    document_id: str,
    comment_in: ReviewCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(ContentDocument).filter(ContentDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    comment = ReviewComment(
        document_id=document_id,
        document_version=doc.current_version,
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_role=current_user.role,
        comment_text=comment_in.comment_text,
        action_type=comment_in.action_type
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
