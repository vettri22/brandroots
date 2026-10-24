from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BrandGuidelineBase(BaseModel):
    id: str
    category: str
    title: str
    rule_text: str
    severity: str = "warning"
    owner_role: str = "brand_owner"
    source_reference: Optional[str] = None
    effective_date: Optional[str] = None
    is_active: bool = True
    prohibited_patterns: List[str] = []
    required_phrases: List[str] = []
    clarification_notes: Optional[str] = None

class BrandGuidelineCreate(BrandGuidelineBase):
    pass

class BrandGuidelineUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    rule_text: Optional[str] = None
    severity: Optional[str] = None
    source_reference: Optional[str] = None
    effective_date: Optional[str] = None
    is_active: Optional[bool] = None
    prohibited_patterns: Optional[List[str]] = None
    required_phrases: Optional[List[str]] = None
    clarification_notes: Optional[str] = None

class BrandGuidelineResponse(BrandGuidelineBase):
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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
    pass

class ApprovedFactResponse(ApprovedFactBase):
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApprovedTerminologyBase(BaseModel):
    id: str
    preferred_term: str
    prohibited_variants: List[str] = []
    rationale: str
    context_guidance: Optional[str] = None
    is_active: bool = True

class ApprovedTerminologyCreate(ApprovedTerminologyBase):
    pass

class ApprovedTerminologyResponse(ApprovedTerminologyBase):
    version: int
    created_at: datetime

    class Config:
        from_attributes = True
