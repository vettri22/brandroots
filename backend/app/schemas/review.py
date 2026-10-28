from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class FindingBase(BaseModel):
    category: str
    severity: str
    confidence: str
    detection_method: Optional[str] = "deterministic_verified"
    location_start: int
    location_end: int
    affected_text: str
    explanation: str
    rule_id: Optional[str] = None
    rule_version: int = 1
    evidence_ids: List[str] = []
    source_reference: Optional[str] = None
    suggested_correction: Optional[str] = None

class FindingResponse(FindingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    review_job_id: str
    status: str
    creator_decision: Optional[str] = None
    creator_decision_reason: Optional[str] = None
    reviewer_decision: Optional[str] = None
    reviewer_decision_reason: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

class FindingResolutionRequest(BaseModel):
    status: str  # accepted, edited, dismissed, escalated, rejected
    resolution_notes: Optional[str] = None
    custom_replacement_text: Optional[str] = None
    reason: Optional[str] = None

class SuggestionDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    finding_id: str
    document_id: str
    document_version: int
    action: str
    original_text: str
    applied_text: Optional[str] = None
    reason: Optional[str] = None
    actor_id: str
    actor_name: str
    actor_role: str
    created_at: datetime

class ApprovalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    document_version: int
    review_job_id: str
    status: str
    approver_id: str
    approver_name: str
    approver_role: str
    decision_reason: Optional[str] = None
    created_at: datetime

class ReviewJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    document_version: int
    status: str
    compliance_score: float
    findings_count: int
    critical_count: int
    warning_count: int
    suggestion_count: int
    guideline_snapshot: Dict[str, Any] = {}
    evidence_snapshot: Dict[str, Any] = {}
    provider_used: str
    model_name: Optional[str] = "local-hybrid-rules-v2.0"
    execution_duration_ms: Optional[int] = 45
    risk_level: Optional[str] = "low"
    requires_human_review: Optional[bool] = False
    created_at: datetime
    completed_at: Optional[datetime] = None
    findings: List[FindingResponse] = []

class ReviewCommentCreate(BaseModel):
    comment_text: str
    action_type: str = "comment"  # comment, request_changes, resubmit, approve, reject

class ReviewCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    document_version: int
    user_id: str
    user_name: str
    user_role: str
    comment_text: str
    action_type: str
    created_at: datetime
