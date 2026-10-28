from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class EvidenceBase(BaseModel):
    claim_title: str
    approved_wording: str
    structured_value: Optional[str] = None
    unit: Optional[str] = None
    prohibited_old_values: List[str] = []
    category: str = "pricing"  # pricing, clinical, security, market_share, legal
    description: Optional[str] = None
    applicable_context: Optional[str] = None
    source_type: str = "uploaded_document"
    source_location: Optional[str] = None
    source_url: Optional[str] = None
    source_document_id: Optional[str] = None
    page_or_section: Optional[str] = None
    evidence_owner: str = "Brand Compliance Lead"
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    review_date: Optional[str] = None
    applicable_product: Optional[str] = None
    applicable_market: Optional[str] = None
    applicable_channel: Optional[str] = None
    public_use_permission: bool = True

class EvidenceCreate(EvidenceBase):
    workspace_id: Optional[str] = "default-workspace"
    brand_id: Optional[str] = None
    status: Optional[str] = "approved"

class EvidenceUpdate(BaseModel):
    claim_title: Optional[str] = None
    approved_wording: Optional[str] = None
    structured_value: Optional[str] = None
    unit: Optional[str] = None
    prohibited_old_values: Optional[List[str]] = None
    category: Optional[str] = None
    description: Optional[str] = None
    applicable_context: Optional[str] = None
    source_type: Optional[str] = None
    source_location: Optional[str] = None
    source_url: Optional[str] = None
    page_or_section: Optional[str] = None
    evidence_owner: Optional[str] = None
    status: Optional[str] = None
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    review_date: Optional[str] = None
    applicable_product: Optional[str] = None
    applicable_market: Optional[str] = None
    applicable_channel: Optional[str] = None
    public_use_permission: Optional[bool] = None
    is_active: Optional[bool] = None
    changelog_reason: Optional[str] = None

class EvidenceVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evidence_id: str
    version_number: int
    approved_wording: str
    structured_value: Optional[str] = None
    status: str
    changelog: Optional[str] = None
    created_at: datetime

class EvidenceResponse(EvidenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    organization_id: Optional[str] = None
    brand_id: Optional[str] = None
    status: str
    approval_date: Optional[datetime] = None
    approved_by: Optional[str] = None
    version: int
    is_active: bool
    is_expired: Optional[bool] = False
    has_conflicts: Optional[bool] = False
    created_at: datetime
    updated_at: datetime

class ClaimVerificationRequest(BaseModel):
    claim_text: str
    brand_id: Optional[str] = None
    channel: Optional[str] = None
    market: Optional[str] = None

class ClaimVerificationResponse(BaseModel):
    status: str  # supported, unsupported, contradicted, expired, conflicting, human_review_required
    confidence: str
    claim_statement: str
    matched_evidence_id: Optional[str] = None
    matched_evidence_wording: Optional[str] = None
    source_reference: Optional[str] = None
    explanation: str
    suggested_correction: Optional[str] = None
