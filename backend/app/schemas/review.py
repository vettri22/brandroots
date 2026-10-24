from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class FindingBase(BaseModel):
    category: str
    severity: str
    confidence: str
    location_start: int
    location_end: int
    affected_text: str
    explanation: str
    rule_id: Optional[str] = None
    rule_version: int = 1
    source_reference: Optional[str] = None
    suggested_correction: Optional[str] = None

class FindingResponse(FindingBase):
    id: str
    review_job_id: str
    status: str
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FindingResolutionRequest(BaseModel):
    status: str  # accepted, edited, dismissed, escalated
    resolution_notes: Optional[str] = None
    custom_replacement_text: Optional[str] = None

class ReviewJobResponse(BaseModel):
    id: str
    document_id: str
    document_version: int
    status: str
    compliance_score: float
    findings_count: int
    critical_count: int
    warning_count: int
    suggestion_count: int
    guideline_snapshot: Dict[str, Any]
    provider_used: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    findings: List[FindingResponse] = []

    class Config:
        from_attributes = True

class ReviewCommentCreate(BaseModel):
    comment_text: str
    action_type: str = "comment"  # comment, request_changes, resubmit, approve, reject

class ReviewCommentResponse(BaseModel):
    id: str
    document_id: str
    user_id: str
    user_name: str
    user_role: str
    comment_text: str
    action_type: str
    created_at: datetime

    class Config:
        from_attributes = True
