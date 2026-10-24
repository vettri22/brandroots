import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, ForeignKey
from app.database import Base

class GuidelineInsight(Base):
    __tablename__ = "guideline_insights"

    id = Column(String(50), primary_key=True, default=lambda: f"DBG-{uuid.uuid4().hex[:8].upper()}")
    workspace_id = Column(String(36), default="default-workspace")
    title = Column(String(200), nullable=False)
    rule_id = Column(String(50), nullable=True)  # Associated guideline or fact ID
    suspected_root_cause = Column(Text, nullable=False)  # "Ambiguous boundary between promotional confidence and guarantee"
    pattern_type = Column(String(50), nullable=False)  # recurring_violation, vague_guideline, outdated_fact, frequent_dismissal
    occurrence_count = Column(Integer, default=1, nullable=False)
    supporting_finding_ids = Column(JSON, default=list)  # list of Finding IDs
    supporting_document_ids = Column(JSON, default=list)  # list of Document IDs
    evidence_summary = Column(Text, nullable=False)  # Evidence quotes & context from drafts
    suggested_action = Column(Text, nullable=False)  # "Clarify rule boundary to explicitly prohibit 'guaranteed' unless certified"
    hypothesis_status = Column(String(30), default="hypothesis", nullable=False)  # hypothesis, confirmed, dismissed
    decision_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    proposing_actor = Column(String(100), default="Guideline Debugger Engine")
    approval_status = Column(String(30), default="pending", nullable=False)  # pending, approved, rejected
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
