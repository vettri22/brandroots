import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.auth import User
from app.models.brand import BrandAsset
from app.schemas.brand import BrandAssetResponse, BrandAssetCreate
from app.schemas.asset import ImageComplianceCheckResponse
from app.core.auth import get_current_user, require_permission
from app.services.asset_checker import verify_image_compliance, compute_sha256
from PIL import Image
import io

router = APIRouter(prefix="/assets", tags=["Visual Assets & Accessibility"])

@router.get("", response_model=List[BrandAssetResponse])
def list_brand_assets(brand_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(BrandAsset).filter(BrandAsset.is_active == True)
    if brand_id:
        query = query.filter(or_(BrandAsset.brand_id == brand_id, BrandAsset.brand_id == None))
    return query.all()

@router.post("/verify-image", response_model=ImageComplianceCheckResponse)
async def verify_image_endpoint(
    file: UploadFile = File(...),
    brand_id: Optional[str] = Form(None),
    alt_text: Optional[str] = Form(None),
    intended_channel: Optional[str] = Form("website"),
    db: Session = Depends(get_db)
):
    """
    Measurable visual compliance & accessibility checks for uploaded image:
    - Dimensions and format check
    - Cryptographic SHA-256 hash match against approved brand assets
    - Visual similarity detection
    - Contrast ratio calculation
    - Alt-text presence and quality check
    """
    content = await file.read()
    registered_assets = db.query(BrandAsset).filter(BrandAsset.is_active == True).all()
    
    result = verify_image_compliance(
        content=content,
        filename=file.filename or "image.png",
        registered_assets=registered_assets,
        alt_text=alt_text,
        intended_channel=intended_channel or "website"
    )
    return result

@router.post("/register", response_model=BrandAssetResponse)
async def register_approved_asset(
    name: str = Form(...),
    asset_type: str = Form("logo"),  # logo, color, typography, icon, image
    brand_id: Optional[str] = Form(None),
    usage_guideline: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("guidelines:manage")),
    db: Session = Depends(get_db)
):
    """
    Registers a canonical brand asset into the approved library with cryptographic SHA-256 signature.
    """
    content = await file.read()
    sha256 = compute_sha256(content)
    
    width = None
    height = None
    mime_type = file.content_type or "image/png"
    
    try:
        img = Image.open(io.BytesIO(content))
        width, height = img.size
    except Exception:
        pass

    asset_id = f"ASSET-{uuid.uuid4().hex[:8].upper()}"
    asset = BrandAsset(
        id=asset_id,
        workspace_id=current_user.workspace_id or "default-workspace",
        brand_id=brand_id,
        asset_type=asset_type,
        name=name,
        value=file.filename,
        file_path=f"storage/assets/{asset_id}_{file.filename}",
        sha256_hash=sha256,
        mime_type=mime_type,
        width=width,
        height=height,
        alt_text_required=True,
        usage_guideline=usage_guideline,
        is_active=True
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
