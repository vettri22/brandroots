from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class GuidelineInsightResponse(BaseModel):
    id: str
    workspace_id: str
    title: str
    rule_id: Optional[str] = None
    suspected_root_cause: str
    pattern_type: str
    occurrence_count: int
    supporting_finding_ids: List[str]
    supporting_document_ids: List[str]
    evidence_summary: str
    suggested_action: str
    hypothesis_status: str
    decision_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HypothesisActionRequest(BaseModel):
    action: str  # confirm, dismiss
    decision_notes: Optional[str] = None

class ProposedClarificationResponse(BaseModel):
    id: str
    insight_id: Optional[str] = None
    target_rule_id: str
    current_rule_version: int
    proposed_version: int
    original_rule_text: str
    proposed_rule_text: str
    clarification_summary: str
    proposing_actor: str
    approval_status: str  # pending, approved, rejected
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ClarificationApprovalRequest(BaseModel):
    decision: str  # approve, reject
    edited_rule_text: Optional[str] = None  # Allow Brand Owner to customize before accepting
    notes: Optional[str] = None
