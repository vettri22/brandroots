import re
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.auth import User, UserRole
from app.models.brand import (
    Brand, BrandGuideline, GuidelineVersion, ApprovedFact, ApprovedTerminology, BrandAsset
)
from app.schemas.brand import (
    BrandBase, BrandCreate, BrandUpdate, BrandResponse,
    BrandGuidelineCreate, BrandGuidelineUpdate, BrandGuidelineResponse,
    GuidelineVersionResponse,
    ApprovedFactCreate, ApprovedFactResponse,
    ApprovedTerminologyCreate, ApprovedTerminologyResponse,
    BrandAssetCreate, BrandAssetResponse,
    TestRuleRequest, TestRuleResponse
)
from app.core.auth import get_current_user, require_role, require_permission
from app.services.audit_logger import log_audit_event
from app.services.guideline_ingestion import parse_guideline_document

router = APIRouter(prefix="/brand", tags=["Brand Knowledge & Rules"])

# --- Brand Workspaces ---

@router.get("/brands", response_model=List[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    return db.query(Brand).filter(Brand.is_active == True).all()

@router.post("/brands", response_model=BrandResponse)
def create_brand(
    data: BrandCreate,
    current_user: User = Depends(require_permission("brand:create")),
    db: Session = Depends(get_db)
):
    existing = db.query(Brand).filter(Brand.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Brand with slug '{data.slug}' already exists")
        
    brand = Brand(
        workspace_id=data.workspace_id or current_user.workspace_id or "default-workspace",
        name=data.name,
        slug=data.slug,
        description=data.description,
        website=data.website,
        supported_channels=data.supported_channels,
        supported_markets=data.supported_markets,
        content_types=data.content_types,
        tone_guidelines=data.tone_guidelines,
        claim_restrictions=data.claim_restrictions,
        is_active=True
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)
    
    log_audit_event(
        db=db,
        event_type="BRAND_CREATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="brand",
        target_id=brand.id,
        summary=f"Created brand '{brand.name}' ({brand.slug})"
    )
    return brand

@router.get("/brands/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: str, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.put("/brands/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: str,
    data: BrandUpdate,
    current_user: User = Depends(require_permission("brand:edit")),
    db: Session = Depends(get_db)
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
        
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(brand, k, v)
    brand.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(brand)
    
    log_audit_event(
        db=db,
        event_type="BRAND_UPDATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="brand",
        target_id=brand.id,
        summary=f"Updated brand settings for '{brand.name}'"
    )
    return brand

# --- Guidelines & Ingestion ---

@router.get("/guidelines", response_model=List[BrandGuidelineResponse])
def list_guidelines(
    brand_id: Optional[str] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(BrandGuideline)
    if not include_inactive:
        query = query.filter(BrandGuideline.is_active == True)
    if brand_id:
        query = query.filter(or_(BrandGuideline.brand_id == brand_id, BrandGuideline.brand_id == None))
    return query.all()

@router.post("/guidelines", response_model=BrandGuidelineResponse)
def create_guideline(
    data: BrandGuidelineCreate,
    current_user: User = Depends(require_permission("guidelines:manage")),
    db: Session = Depends(get_db)
):
    existing = db.query(BrandGuideline).filter(BrandGuideline.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Guideline with ID '{data.id}' already exists")

    rule = BrandGuideline(
        id=data.id,
        brand_id=data.brand_id,
        category=data.category,
        title=data.title,
        rule_text=data.rule_text,
        rule_type=data.rule_type,
        severity=data.severity,
        owner_role=data.owner_role,
        source_reference=data.source_reference,
        page_reference=data.page_reference,
        effective_date=data.effective_date or datetime.utcnow().strftime("%Y-%m-%d"),
        version=1,
        is_active=data.is_active,
        prohibited_patterns=data.prohibited_patterns,
        required_phrases=data.required_phrases,
        clarification_notes=data.clarification_notes
    )
    db.add(rule)
    db.flush()

    # Initial version record
    v_record = GuidelineVersion(
        guideline_id=rule.id,
        version_number=1,
        title=rule.title,
        rule_text=rule.rule_text,
        severity=rule.severity,
        prohibited_patterns=rule.prohibited_patterns,
        required_phrases=rule.required_phrases,
        changelog="Initial guideline creation",
        author_id=current_user.id
    )
    db.add(v_record)
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
    current_user: User = Depends(require_permission("guidelines:manage")),
    db: Session = Depends(get_db)
):
    rule = db.query(BrandGuideline).filter(BrandGuideline.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Guideline not found")

    old_text = rule.rule_text
    data_dict = data.model_dump(exclude_unset=True)
    changelog_reason = data_dict.pop("changelog_reason", "Guideline update")

    is_substantive = False
    if "rule_text" in data_dict and data_dict["rule_text"] != old_text:
        is_substantive = True
    if "prohibited_patterns" in data_dict or "required_phrases" in data_dict:
        is_substantive = True

    if is_substantive:
        rule.version += 1

    for field, val in data_dict.items():
        setattr(rule, field, val)

    rule.updated_at = datetime.utcnow()

    if is_substantive:
        v_record = GuidelineVersion(
            guideline_id=rule.id,
            version_number=rule.version,
            title=rule.title,
            rule_text=rule.rule_text,
            severity=rule.severity,
            prohibited_patterns=rule.prohibited_patterns,
            required_phrases=rule.required_phrases,
            changelog=changelog_reason,
            author_id=current_user.id
        )
        db.add(v_record)

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
        summary=f"Updated rule '{rule.id}' to v{rule.version}"
    )
    return rule

@router.delete("/guidelines/{rule_id}")
def deactivate_guideline(
    rule_id: str,
    current_user: User = Depends(require_permission("guidelines:manage")),
    db: Session = Depends(get_db)
):
    rule = db.query(BrandGuideline).filter(BrandGuideline.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Guideline not found")

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
        summary=f"Deactivated rule '{rule.id}' (historical review trace preserved)"
    )
    return {"message": f"Guideline '{rule_id}' deactivated successfully"}

@router.get("/guidelines/{rule_id}/versions", response_model=List[GuidelineVersionResponse])
def get_guideline_versions(rule_id: str, db: Session = Depends(get_db)):
    return db.query(GuidelineVersion).filter(
        GuidelineVersion.guideline_id == rule_id
    ).order_by(GuidelineVersion.version_number.desc()).all()

@router.post("/guidelines/test", response_model=TestRuleResponse)
def test_rule_condition(req: TestRuleRequest):
    """
    Test a rule pattern or phrase against sample content without saving.
    """
    pattern_str = req.pattern_or_phrase.strip()
    sample = req.sample_text
    
    if req.rule_type == "prohibited_term":
        regex = re.compile(rf"\b{re.escape(pattern_str)}\b", re.IGNORECASE)
        matches = [m.group(0) for m in regex.finditer(sample)]
        return {
            "matched": len(matches) > 0,
            "matches_found": matches,
            "details": f"Found {len(matches)} occurrence(s) of prohibited term '{pattern_str}'." if matches else f"No matches found for '{pattern_str}'."
        }
    elif req.rule_type == "required_term" or req.rule_type == "disclaimer":
        found = pattern_str.lower() in sample.lower()
        return {
            "matched": found,
            "matches_found": [pattern_str] if found else [],
            "details": f"Required phrase '{pattern_str}' is present in sample." if found else f"Required phrase '{pattern_str}' is MISSING from sample."
        }
    else:
        # Regex or substring
        try:
            regex = re.compile(pattern_str, re.IGNORECASE)
            matches = [m.group(0) for m in regex.finditer(sample)]
            return {
                "matched": len(matches) > 0,
                "matches_found": matches,
                "details": f"Matched pattern: {len(matches)} instances found."
            }
        except Exception as e:
            return {
                "matched": False,
                "matches_found": [],
                "details": f"Invalid regex pattern: {str(e)}"
            }

@router.post("/guidelines/ingest-document")
async def ingest_guideline_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("guidelines:manage")),
    db: Session = Depends(get_db)
):
    """
    Ingests PDF or DOCX brand playbook and extracts candidate rules for human review.
    Does NOT automatically create authoritative policy.
    """
    result = await parse_guideline_document(file)
    log_audit_event(
        db=db,
        event_type="GUIDELINE_DOCUMENT_INGESTED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="document",
        target_id=file.filename or "unknown",
        summary=f"Ingested guideline document '{file.filename}', identified {result['candidates_found']} candidate rules for review"
    )
    return result

# --- Approved Facts (Legacy bridge) ---

@router.get("/facts", response_model=List[ApprovedFactResponse])
def list_facts(db: Session = Depends(get_db)):
    return db.query(ApprovedFact).filter(ApprovedFact.is_active == True).all()

@router.post("/facts", response_model=ApprovedFactResponse)
def create_fact(
    data: ApprovedFactCreate,
    current_user: User = Depends(require_permission("evidence:create")),
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
        summary=f"Created approved fact '{fact.id}'"
    )
    return fact

# --- Terminology ---

@router.get("/terminology", response_model=List[ApprovedTerminologyResponse])
def list_terminology(db: Session = Depends(get_db)):
    return db.query(ApprovedTerminology).filter(ApprovedTerminology.is_active == True).all()

@router.post("/terminology", response_model=ApprovedTerminologyResponse)
def create_terminology(
    data: ApprovedTerminologyCreate,
    current_user: User = Depends(require_permission("guidelines:manage")),
    db: Session = Depends(get_db)
):
    existing = db.query(ApprovedTerminology).filter(ApprovedTerminology.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Term with ID '{data.id}' already exists")

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

    log_audit_event(
        db=db,
        event_type="TERMINOLOGY_CREATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="term",
        target_id=term.id,
        summary=f"Added brand terminology '{term.preferred_term}'"
    )
    return term

# --- Assets ---

@router.get("/assets", response_model=List[BrandAssetResponse])
def list_assets(brand_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(BrandAsset).filter(BrandAsset.is_active == True)
    if brand_id:
        query = query.filter(or_(BrandAsset.brand_id == brand_id, BrandAsset.brand_id == None))
    return query.all()

@router.post("/assets", response_model=BrandAssetResponse)
def create_asset(
    data: BrandAssetCreate,
    current_user: User = Depends(require_permission("guidelines:manage")),
    db: Session = Depends(get_db)
):
    existing = db.query(BrandAsset).filter(BrandAsset.id == data.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Asset with ID '{data.id}' already exists")

    asset = BrandAsset(
        id=data.id,
        brand_id=data.brand_id,
        asset_type=data.asset_type,
        name=data.name,
        value=data.value,
        file_path=data.file_path,
        sha256_hash=data.sha256_hash,
        mime_type=data.mime_type,
        width=data.width,
        height=data.height,
        min_width=data.min_width,
        min_height=data.min_height,
        color_hex=data.color_hex,
        alt_text_required=data.alt_text_required,
        usage_guideline=data.usage_guideline,
        is_active=data.is_active
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
