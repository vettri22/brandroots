from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class BrandBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    website: Optional[str] = None
    supported_channels: List[str] = ["website", "social", "email", "press_release", "ads"]
    supported_markets: List[str] = ["Global", "US", "EU", "APAC"]
    content_types: List[str] = ["article", "landing_page", "social_post", "whitepaper", "ad_copy"]
    tone_guidelines: Dict[str, Any] = {"formality": "professional", "voice": "authoritative, trustworthy"}
    claim_restrictions: List[str] = ["no_unsubstantiated_guarantees", "require_clinical_reference"]

class BrandCreate(BrandBase):
    workspace_id: Optional[str] = "default-workspace"

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    supported_channels: Optional[List[str]] = None
    supported_markets: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    tone_guidelines: Optional[Dict[str, Any]] = None
    claim_restrictions: Optional[List[str]] = None
    is_active: Optional[bool] = None

class BrandResponse(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class BrandGuidelineBase(BaseModel):
    id: str
    category: str
    title: str
    rule_text: str
    rule_type: str = "prohibited_term"
    severity: str = "warning"
    owner_role: str = "brand_owner"
    source_reference: Optional[str] = None
    page_reference: Optional[str] = None
    effective_date: Optional[str] = None
    is_active: bool = True
    prohibited_patterns: List[str] = []
    required_phrases: List[str] = []
    clarification_notes: Optional[str] = None

class BrandGuidelineCreate(BrandGuidelineBase):
    brand_id: Optional[str] = None

class BrandGuidelineUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    rule_text: Optional[str] = None
    rule_type: Optional[str] = None
    severity: Optional[str] = None
    source_reference: Optional[str] = None
    page_reference: Optional[str] = None
    effective_date: Optional[str] = None
    is_active: Optional[bool] = None
    prohibited_patterns: Optional[List[str]] = None
    required_phrases: Optional[List[str]] = None
    clarification_notes: Optional[str] = None
    changelog_reason: Optional[str] = None

class GuidelineVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    guideline_id: str
    version_number: int
    title: str
    rule_text: str
    severity: str
    prohibited_patterns: List[str]
    required_phrases: List[str]
    changelog: Optional[str] = None
    author_id: Optional[str] = None
    created_at: datetime

class BrandGuidelineResponse(BrandGuidelineBase):
    model_config = ConfigDict(from_attributes=True)

    brand_id: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime

class ApprovedFactBase(BaseModel):
    id: str
    category: str
    claim_statement: str
    canonical_value: Optional[str] = None
    unit: Optional[str] = None
    prohibited_old_values: List[str] = []
    source_document: str
    effective_date: str
    expiry_date: Optional[str] = None
    is_active: bool = True

class ApprovedFactCreate(ApprovedFactBase):
    brand_id: Optional[str] = None

class ApprovedFactResponse(ApprovedFactBase):
    model_config = ConfigDict(from_attributes=True)

    version: int
    created_at: datetime
    updated_at: datetime

class ApprovedTerminologyBase(BaseModel):
    id: str
    preferred_term: str
    prohibited_variants: List[str] = []
    rationale: str
    context_guidance: Optional[str] = None
    is_active: bool = True

class ApprovedTerminologyCreate(ApprovedTerminologyBase):
    brand_id: Optional[str] = None

class ApprovedTerminologyResponse(ApprovedTerminologyBase):
    model_config = ConfigDict(from_attributes=True)

    version: int
    created_at: datetime

class BrandAssetBase(BaseModel):
    id: str
    asset_type: str
    name: str
    value: str
    file_path: Optional[str] = None
    sha256_hash: Optional[str] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    color_hex: Optional[str] = None
    alt_text_required: bool = True
    usage_guideline: Optional[str] = None
    is_active: bool = True

class BrandAssetCreate(BrandAssetBase):
    brand_id: Optional[str] = None

class BrandAssetResponse(BrandAssetBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime

class TestRuleRequest(BaseModel):
    rule_type: str
    pattern_or_phrase: str
    sample_text: str

class TestRuleResponse(BaseModel):
    matched: bool
    matches_found: List[str] = []
    details: str
