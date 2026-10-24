from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User, UserRole
from app.models.brand import BrandGuideline, ApprovedFact, ApprovedTerminology, BrandAsset
from app.schemas.brand import (
    BrandGuidelineCreate, BrandGuidelineUpdate, BrandGuidelineResponse,
    ApprovedFactCreate, ApprovedFactResponse,
    ApprovedTerminologyCreate, ApprovedTerminologyResponse
)
from app.core.auth import get_current_user, require_role
from app.services.audit_logger import log_audit_event

router = APIRouter(prefix="/brand", tags=["Brand Knowledge"])

# --- Guidelines ---

@router.get("/guidelines", response_model=List[BrandGuidelineResponse])
def list_guidelines(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(BrandGuideline)
    if not include_inactive:
        query = query.filter(BrandGuideline.is_active == True)
    return query.all()

@router.post("/guidelines", response_model=BrandGuidelineResponse)
def create_guideline(
    data: BrandGuidelineCreate,
    current_user: User = Depends(require_role([UserRole.BRAND_OWNER.value])),
    db: Session = Depends(get_db)
):
    existing = db.query(BrandGuideline).filter(BrandGuideline.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Guideline with ID '{data.id}' already exists")

    rule = BrandGuideline(
        id=data.id,
        category=data.category,
        title=data.title,
        rule_text=data.rule_text,
        severity=data.severity,
        owner_role=data.owner_role,
        source_reference=data.source_reference,
        effective_date=data.effective_date or datetime.utcnow().strftime("%Y-%m-%d"),
        version=1,
        is_active=data.is_active,
        prohibited_patterns=data.prohibited_patterns,
        required_phrases=data.required_phrases,
        clarification_notes=data.clarification_notes
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    log_audit_event(
        db=db,
        event_type="RULE_CREATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="rule",
        target_id=rule.id,
        summary=f"Created brand guideline '{rule.id}' ({rule.title})"
    )

    return rule

@router.put("/guidelines/{rule_id}", response_model=BrandGuidelineResponse)
def update_guideline(
    rule_id: str,
    data: BrandGuidelineUpdate,
    current_user: User = Depends(require_role([UserRole.BRAND_OWNER.value])),
    db: Session = Depends(get_db)
):
    rule = db.query(BrandGuideline).filter(BrandGuideline.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Guideline not found")

    old_version = rule.version
    if data.rule_text and data.rule_text != rule.rule_text:
        rule.version += 1  # Increment version on substantive rule change

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, val)

    rule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rule)

    log_audit_event(
        db=db,
        event_type="RULE_UPDATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="rule",
        target_id=rule.id,
        summary=f"Updated guideline '{rule.id}' (v{old_version} -> v{rule.version})"
    )

    return rule

@router.delete("/guidelines/{rule_id}")
def deactivate_guideline(
    rule_id: str,
    current_user: User = Depends(require_role([UserRole.BRAND_OWNER.value])),
    db: Session = Depends(get_db)
):
    rule = db.query(BrandGuideline).filter(BrandGuideline.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Guideline not found")
    
    # Safe deactivation - never delete permanently to preserve historical audit & review trace
    rule.is_active = False
    rule.updated_at = datetime.utcnow()
    db.commit()

    log_audit_event(
        db=db,
        event_type="RULE_DEACTIVATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="rule",
        target_id=rule.id,
        summary=f"Deactivated guideline '{rule.id}' (historical reviews remain preserved)"
    )

    return {"message": f"Guideline '{rule_id}' deactivated successfully (historical reviews preserved)"}

# --- Approved Facts ---

@router.get("/facts", response_model=List[ApprovedFactResponse])
def list_facts(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(ApprovedFact)
    if not include_inactive:
        query = query.filter(ApprovedFact.is_active == True)
    return query.all()

@router.post("/facts", response_model=ApprovedFactResponse)
def create_fact(
    data: ApprovedFactCreate,
    current_user: User = Depends(require_role([UserRole.BRAND_OWNER.value])),
    db: Session = Depends(get_db)
):
    existing = db.query(ApprovedFact).filter(ApprovedFact.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Fact with ID '{data.id}' already exists")

    fact = ApprovedFact(
        id=data.id,
        category=data.category,
        claim_statement=data.claim_statement,
        canonical_value=data.canonical_value,
        unit=data.unit,
        prohibited_old_values=data.prohibited_old_values,
        source_document=data.source_document,
        effective_date=data.effective_date,
        expiry_date=data.expiry_date,
        version=1,
        is_active=data.is_active
    )
    db.add(fact)
    db.commit()
    db.refresh(fact)

    log_audit_event(
        db=db,
        event_type="FACT_CREATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="fact",
        target_id=fact.id,
        summary=f"Added approved fact '{fact.id}': {fact.claim_statement}"
    )

    return fact

# --- Terminology ---

@router.get("/terminology", response_model=List[ApprovedTerminologyResponse])
def list_terminology(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(ApprovedTerminology)
    if not include_inactive:
        query = query.filter(ApprovedTerminology.is_active == True)
    return query.all()

@router.post("/terminology", response_model=ApprovedTerminologyResponse)
def create_terminology(
    data: ApprovedTerminologyCreate,
    current_user: User = Depends(require_role([UserRole.BRAND_OWNER.value])),
    db: Session = Depends(get_db)
):
    term = ApprovedTerminology(
        id=data.id,
        preferred_term=data.preferred_term,
        prohibited_variants=data.prohibited_variants,
        rationale=data.rationale,
        context_guidance=data.context_guidance,
        version=1,
        is_active=data.is_active
    )
    db.add(term)
    db.commit()
    db.refresh(term)
    return term

# --- Assets ---

@router.get("/assets")
def list_assets(db: Session = Depends(get_db)):
    return db.query(BrandAsset).all()
