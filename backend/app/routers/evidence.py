import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.auth import User, UserRole
from app.models.evidence import BrandEvidence, BrandEvidenceVersion, EvidenceStatus
from app.schemas.evidence import (
    EvidenceCreate, EvidenceUpdate, EvidenceResponse, EvidenceVersionResponse,
    ClaimVerificationRequest, ClaimVerificationResponse
)
from app.core.auth import get_current_user, require_role, require_permission
from app.services.audit_logger import log_audit_event
from app.services.evidence_service import (
    is_evidence_expired, detect_evidence_conflicts, verify_claim_against_ledger, parse_date
)

router = APIRouter(prefix="/evidence", tags=["Brand Evidence Ledger"])

@router.get("", response_model=List[EvidenceResponse])
def list_evidence(
    brand_id: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    include_archived: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(BrandEvidence)
    if not include_archived:
        query = query.filter(BrandEvidence.status != EvidenceStatus.ARCHIVED.value)
    if brand_id:
        query = query.filter(or_(BrandEvidence.brand_id == brand_id, BrandEvidence.brand_id == None))
    if category:
        query = query.filter(BrandEvidence.category == category)
    if status_filter:
        query = query.filter(BrandEvidence.status == status_filter)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                BrandEvidence.claim_title.ilike(search_fmt),
                BrandEvidence.approved_wording.ilike(search_fmt),
                BrandEvidence.structured_value.ilike(search_fmt),
                BrandEvidence.source_location.ilike(search_fmt)
            )
        )
    
    records = query.order_by(BrandEvidence.created_at.desc()).all()
    for rec in records:
        rec.is_expired = is_evidence_expired(rec)
    return records

@router.post("", response_model=EvidenceResponse)
def create_evidence(
    data: EvidenceCreate,
    current_user: User = Depends(require_permission("evidence:create")),
    db: Session = Depends(get_db)
):
    ev_id = f"EVID-{uuid.uuid4().hex[:8].upper()}"
    evidence = BrandEvidence(
        id=ev_id,
        workspace_id=data.workspace_id or "default-workspace",
        brand_id=data.brand_id,
        claim_title=data.claim_title,
        approved_wording=data.approved_wording,
        structured_value=data.structured_value,
        unit=data.unit,
        prohibited_old_values=data.prohibited_old_values or [],
        category=data.category,
        description=data.description,
        applicable_context=data.applicable_context,
        source_type=data.source_type,
        source_location=data.source_location,
        source_url=data.source_url,
        source_document_id=data.source_document_id,
        page_or_section=data.page_or_section,
        evidence_owner=data.evidence_owner or current_user.full_name,
        status=data.status or EvidenceStatus.APPROVED.value,
        approval_date=datetime.utcnow() if data.status == "approved" else None,
        approved_by=current_user.full_name if data.status == "approved" else None,
        effective_date=data.effective_date or datetime.utcnow().strftime("%Y-%m-%d"),
        expiry_date=data.expiry_date,
        review_date=data.review_date,
        applicable_product=data.applicable_product,
        applicable_market=data.applicable_market,
        applicable_channel=data.applicable_channel,
        public_use_permission=data.public_use_permission,
        version=1,
        created_by_id=current_user.id,
        updated_by_id=current_user.id,
        is_active=True
    )
    db.add(evidence)
    db.flush()

    # Initial version snapshot
    version_record = BrandEvidenceVersion(
        evidence_id=evidence.id,
        version_number=1,
        approved_wording=evidence.approved_wording,
        structured_value=evidence.structured_value,
        status=evidence.status,
        changelog="Initial evidence creation",
        author_id=current_user.id
    )
    db.add(version_record)
    db.commit()
    db.refresh(evidence)

    log_audit_event(
        db=db,
        event_type="EVIDENCE_CREATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="evidence",
        target_id=evidence.id,
        summary=f"Added evidence record '{evidence.id}': '{evidence.claim_title}'"
    )

    evidence.is_expired = is_evidence_expired(evidence)
    return evidence

@router.get("/conflicts")
def get_evidence_conflicts(brand_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns conflicting or contradictory active evidence records.
    """
    conflicts = detect_evidence_conflicts(db, brand_id=brand_id)
    return {
        "conflict_count": len(conflicts),
        "conflicts": conflicts
    }

@router.get("/expiring-soon")
def get_expiring_evidence(
    days: int = Query(30, description="Window in days to check for upcoming expiration"),
    db: Session = Depends(get_db)
):
    threshold = datetime.utcnow() + timedelta(days=days)
    records = db.query(BrandEvidence).filter(
        BrandEvidence.is_active == True,
        BrandEvidence.expiry_date != None
    ).all()
    
    expiring = []
    expired = []
    for r in records:
        dt = parse_date(r.expiry_date)
        if dt:
            if dt < datetime.utcnow():
                expired.append({
                    "id": r.id,
                    "title": r.claim_title,
                    "expiry_date": r.expiry_date,
                    "owner": r.evidence_owner,
                    "status": "expired"
                })
            elif dt <= threshold:
                expiring.append({
                    "id": r.id,
                    "title": r.claim_title,
                    "expiry_date": r.expiry_date,
                    "owner": r.evidence_owner,
                    "days_remaining": (dt - datetime.utcnow()).days
                })
                
    return {
        "expired_count": len(expired),
        "expired_records": expired,
        "expiring_soon_count": len(expiring),
        "expiring_soon_records": expiring
    }

@router.post("/verify-claim", response_model=ClaimVerificationResponse)
def verify_claim_endpoint(req: ClaimVerificationRequest, db: Session = Depends(get_db)):
    """
    Verifies claim against Brand Evidence Ledger. Distinguishes supported, unsupported,
    contradicted, expired, conflicting, and review-required claims.
    """
    return verify_claim_against_ledger(
        db=db,
        claim_text=req.claim_text,
        brand_id=req.brand_id,
        channel=req.channel,
        market=req.market
    )

@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    ev = db.query(BrandEvidence).filter(BrandEvidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    ev.is_expired = is_evidence_expired(ev)
    return ev

@router.put("/{evidence_id}", response_model=EvidenceResponse)
def update_evidence(
    evidence_id: str,
    data: EvidenceUpdate,
    current_user: User = Depends(require_permission("evidence:create")),
    db: Session = Depends(get_db)
):
    ev = db.query(BrandEvidence).filter(BrandEvidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    old_wording = ev.approved_wording
    data_dict = data.model_dump(exclude_unset=True)
    changelog_reason = data_dict.pop("changelog_reason", "Updated evidence record")

    # Increment version if wording or value changed
    is_substantive = False
    if "approved_wording" in data_dict and data_dict["approved_wording"] != old_wording:
        is_substantive = True
    if "structured_value" in data_dict and data_dict["structured_value"] != ev.structured_value:
        is_substantive = True
        
    if is_substantive:
        ev.version += 1

    for k, v in data_dict.items():
        setattr(ev, k, v)
        
    ev.updated_by_id = current_user.id
    ev.updated_at = datetime.utcnow()

    # Save new version record
    if is_substantive:
        version_rec = BrandEvidenceVersion(
            evidence_id=ev.id,
            version_number=ev.version,
            approved_wording=ev.approved_wording,
            structured_value=ev.structured_value,
            status=ev.status,
            changelog=changelog_reason,
            author_id=current_user.id
        )
        db.add(version_rec)

    db.commit()
    db.refresh(ev)

    log_audit_event(
        db=db,
        event_type="EVIDENCE_UPDATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="evidence",
        target_id=ev.id,
        summary=f"Updated evidence record '{ev.id}' (v{ev.version})"
    )

    ev.is_expired = is_evidence_expired(ev)
    return ev

@router.post("/{evidence_id}/status", response_model=EvidenceResponse)
def update_evidence_status(
    evidence_id: str,
    new_status: str,
    reason: Optional[str] = None,
    current_user: User = Depends(require_permission("evidence:approve")),
    db: Session = Depends(get_db)
):
    ev = db.query(BrandEvidence).filter(BrandEvidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence record not found")
        
    valid_statuses = [s.value for s in EvidenceStatus]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
        
    ev.status = new_status
    if new_status == EvidenceStatus.APPROVED.value:
        ev.approval_date = datetime.utcnow()
        ev.approved_by = current_user.full_name
    elif new_status == EvidenceStatus.REJECTED.value:
        ev.rejection_reason = reason
        
    ev.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ev)
    
    log_audit_event(
        db=db,
        event_type="EVIDENCE_STATUS_CHANGED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="evidence",
        target_id=ev.id,
        summary=f"Changed evidence '{ev.id}' status to '{new_status}' (Reason: {reason or 'None'})"
    )

    ev.is_expired = is_evidence_expired(ev)
    return ev

@router.delete("/{evidence_id}")
def archive_evidence(
    evidence_id: str,
    current_user: User = Depends(require_permission("evidence:approve")),
    db: Session = Depends(get_db)
):
    ev = db.query(BrandEvidence).filter(BrandEvidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence record not found")
        
    ev.status = EvidenceStatus.ARCHIVED.value
    ev.is_active = False
    ev.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Evidence record '{evidence_id}' has been archived"}

@router.get("/{evidence_id}/versions", response_model=List[EvidenceVersionResponse])
def get_evidence_versions(evidence_id: str, db: Session = Depends(get_db)):
    return db.query(BrandEvidenceVersion).filter(
        BrandEvidenceVersion.evidence_id == evidence_id
    ).order_by(BrandEvidenceVersion.version_number.desc()).all()
