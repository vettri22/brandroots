from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class ImageComplianceCheckRequest(BaseModel):
    asset_id: Optional[str] = None
    brand_id: Optional[str] = None
    alt_text: Optional[str] = None
    intended_channel: Optional[str] = "website"

class ImageComplianceCheckResponse(BaseModel):
    is_compliant: bool
    file_type: str
    width: int
    height: int
    file_size_bytes: int
    sha256_hash: str
    matching_asset_id: Optional[str] = None
    is_exact_sha256_match: bool = False
    exact_match_asset: Optional[Dict[str, Any]] = None
    similarity_match: Optional[Dict[str, Any]] = None
    contrast_ratio: Optional[float] = None
    contrast_status: str  # pass, fail, not_measurable
    alt_text_status: str  # pass, missing, low_quality, not_required
    alt_text_valid: bool = False
    dominant_colors: List[str] = []
    palette_compliance: Optional[Dict[str, Any]] = None
    findings: List[Dict[str, Any]] = []
    violations: List[str] = []
    details: str
