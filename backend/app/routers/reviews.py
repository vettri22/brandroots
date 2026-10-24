from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User, UserRole
from app.models.content import ContentDocument, DocumentStatus, DocumentVersion
from app.models.review import ReviewJob, Finding, ReviewComment, FindingStatus
from app.schemas.review import (
    ReviewJobResponse, FindingResponse, FindingResolutionRequest,
    ReviewCommentCreate, ReviewCommentResponse
)
from app.schemas.content import StatusTransitionRequest
from app.core.auth import get_current_user
from app.services.compliance_engine import run_compliance_check
from app.services.audit_logger import log_audit_event

router = APIRouter(prefix="/reviews", tags=["Reviews & Compliance"])

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

@router.put("/findings/{finding_id}/resolve", response_model=FindingResponse)
def resolve_finding(
    finding_id: str,
    resolution: FindingResolutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    job = db.query(ReviewJob).filter(ReviewJob.id == finding.review_job_id).first()
    doc = db.query(ContentDocument).filter(ContentDocument.id == job.document_id).first() if job else None

    finding.status = resolution.status
    finding.resolution_notes = resolution.resolution_notes
    finding.resolved_by = current_user.full_name
    finding.resolved_at = datetime.utcnow()

    # If action is 'accepted' or 'edited', apply suggested correction directly into current_text
    if doc and resolution.status in ("accepted", "edited"):
        replacement = resolution.custom_replacement_text or finding.suggested_correction
        if replacement and finding.affected_text in doc.current_text:
            doc.current_text = doc.current_text.replace(finding.affected_text, replacement, 1)
            doc.current_version += 1
            ver = DocumentVersion(
                document_id=doc.id,
                version_number=doc.current_version,
                text_snapshot=doc.current_text,
                changelog=f"Applied correction for finding {finding.id}: '{finding.affected_text}' -> '{replacement}'",
                author_id=current_user.id
            )
            db.add(ver)

    db.commit()
    db.refresh(finding)

    log_audit_event(
        db=db,
        event_type="FINDING_RESOLVED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="finding",
        target_id=finding.id,
        summary=f"Finding '{finding.id}' set to '{resolution.status}' by {current_user.full_name}",
        details={"status": resolution.status, "notes": resolution.resolution_notes}
    )

    return finding

# --- Lifecycle State Transitions ---

ALLOWED_TRANSITIONS = {
    DocumentStatus.DRAFT.value: [DocumentStatus.SUBMITTED.value],
    DocumentStatus.SUBMITTED.value: [DocumentStatus.IN_REVIEW.value, DocumentStatus.CHANGES_REQUESTED.value],
    DocumentStatus.IN_REVIEW.value: [DocumentStatus.CHANGES_REQUESTED.value, DocumentStatus.APPROVED.value, DocumentStatus.REJECTED.value],
    DocumentStatus.CHANGES_REQUESTED.value: [DocumentStatus.RESUBMITTED.value, DocumentStatus.DRAFT.value],
    DocumentStatus.RESUBMITTED.value: [DocumentStatus.IN_REVIEW.value, DocumentStatus.APPROVED.value, DocumentStatus.REJECTED.value],
    DocumentStatus.APPROVED.value: [],
    DocumentStatus.REJECTED.value: [DocumentStatus.DRAFT.value]
}

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

    # Validate transition
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
                detail="Policy violation: Content creators cannot approve their own submitted work. Requires Reviewer or Brand Owner role."
            )
        if current_user.role not in (UserRole.REVIEWER.value, UserRole.BRAND_OWNER.value):
            raise HTTPException(
                status_code=403,
                detail="Approval requires Reviewer or Brand Owner role."
            )

    doc.status = target_status
    doc.updated_at = datetime.utcnow()

    # Record comment/decision
    comment = ReviewComment(
        document_id=doc.id,
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
        details={"from": old_status, "to": target_status, "comment": req.comment}
    )

    return {
        "message": f"Document transitioned to {target_status}",
        "document_id": doc.id,
        "status": doc.status
    }

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
    comment = ReviewComment(
        document_id=document_id,
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
