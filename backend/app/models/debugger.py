import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, ForeignKey
from app.database import Base

class GuidelineInsight(Base):
    """
    Guideline Clarity Radar signal backed by real review history and finding aggregations.
    """
    __tablename__ = "guideline_insights"

    id = Column(String(50), primary_key=True, default=lambda: f"DBG-{uuid.uuid4().hex[:8].upper()}")
    workspace_id = Column(String(36), default="default-workspace")
    organization_id = Column(String(36), nullable=True)
    brand_id = Column(String(36), nullable=True)
    title = Column(String(200), nullable=False)
    rule_id = Column(String(50), nullable=True)  # Associated guideline or fact ID
    suspected_root_cause = Column(Text, nullable=False)  # e.g. "Ambiguous boundary between promotional confidence and guarantee"
    pattern_type = Column(String(50), nullable=False)  # recurring_violation, vague_guideline, outdated_fact, frequent_override, conflicting_rules
    occurrence_count = Column(Integer, default=1, nullable=False)
    supporting_finding_ids = Column(JSON, default=list)  # list of Finding IDs
    supporting_document_ids = Column(JSON, default=list)  # list of Document IDs
    evidence_summary = Column(Text, nullable=False)  # Evidence quotes & context from drafts
    suggested_action = Column(Text, nullable=False)  # Proposed remedy
    hypothesis_status = Column(String(30), default="hypothesis", nullable=False)  # hypothesis, confirmed, dismissed
    status_marking = Column(String(50), default="under_investigation", nullable=False)  # under_investigation, needs_clarification, updated, resolved, not_an_issue
    decision_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Modern alias for the Guideline Clarity Radar
GuidelineClaritySignal = GuidelineInsight

class ProposedGuidelineClarification(Base):
    __tablename__ = "proposed_guideline_clarifications"

    id = Column(String(50), primary_key=True, default=lambda: f"PROP-{uuid.uuid4().hex[:8].upper()}")
    insight_id = Column(String(50), ForeignKey("guideline_insights.id"), nullable=True)
    target_rule_id = Column(String(50), nullable=False)
    current_rule_version = Column(Integer, default=1, nullable=False)
    proposed_version = Column(Integer, default=2, nullable=False)
    original_rule_text = Column(Text, nullable=False)
    proposed_rule_text = Column(Text, nullable=False)
    clarification_summary = Column(Text, nullable=False)  # Why this clarifies the ambiguity
    proposing_actor = Column(String(100), default="Guideline Clarity Engine")
    approval_status = Column(String(30), default="pending", nullable=False)  # pending, approved, rejected
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
