import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class FindingStatus(str, enum.Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    EDITED = "edited"
    DISMISSED = "dismissed"
    REJECTED = "rejected"
    ESCALATED = "escalated"

class ReviewJob(Base):
    __tablename__ = "review_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), default="default-workspace")
    organization_id = Column(String(36), nullable=True)
    brand_id = Column(String(36), nullable=True)
    document_id = Column(String(36), ForeignKey("content_documents.id"), nullable=False)
    document_version = Column(Integer, default=1, nullable=False)
    status = Column(String(30), default="completed", nullable=False)  # pending, running, completed, failed
    compliance_score = Column(Float, default=100.0)  # 0.0 to 100.0
    findings_count = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    suggestion_count = Column(Integer, default=0)
    
    # Evidence & Rule Provenance
    guideline_snapshot = Column(JSON, default=dict)  # Records guideline versions used
    evidence_snapshot = Column(JSON, default=dict)   # Records evidence IDs and versions verified
    provider_used = Column(String(50), default="hybrid_engine")
    model_name = Column(String(100), default="local-hybrid-rules-v2.0")
    execution_duration_ms = Column(Integer, default=45)
    
    # Risk and Routing
    risk_level = Column(String(20), default="low")  # critical, high, medium, low
    requires_human_review = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("ContentDocument", back_populates="review_jobs")
    findings = relationship("Finding", back_populates="review_job", cascade="all, delete-orphan")
    approvals = relationship("ApprovalRecord", back_populates="review_job", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(50), primary_key=True, default=lambda: f"FND-{uuid.uuid4().hex[:8].upper()}")
    review_job_id = Column(String(36), ForeignKey("review_jobs.id"), nullable=False)
    document_version_id = Column(String(36), nullable=True)
    category = Column(String(50), nullable=False)  # promotional_claim, pricing, terminology, tone, disclaimer, visual, accessibility
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    confidence = Column(String(30), default="deterministic")  # deterministic, high, moderate, unverified
    detection_method = Column(String(50), default="deterministic_verified")  # deterministic_verified, rule_condition_match, ai_assisted, contextual_heuristic
    
    location_start = Column(Integer, default=0)
    location_end = Column(Integer, default=0)
    affected_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    
    # Explicit Citations
    rule_id = Column(String(50), nullable=True)
    rule_version = Column(Integer, default=1)
    evidence_ids = Column(JSON, default=list)  # List of verified evidence IDs (e.g. ["EVID-PRICE-01"])
    source_reference = Column(String(255), nullable=True)
    suggested_correction = Column(Text, nullable=True)
    
    # Workflow Decisions
    status = Column(String(30), default=FindingStatus.OPEN.value, nullable=False)
    creator_decision = Column(String(30), nullable=True)  # accepted, rejected, edited
    creator_decision_reason = Column(Text, nullable=True)
    reviewer_decision = Column(String(30), nullable=True) # confirmed, dismissed, escalated
    reviewer_decision_reason = Column(Text, nullable=True)
    
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    review_job = relationship("ReviewJob", back_populates="findings")
    decisions = relationship("SuggestionDecision", back_populates="finding", cascade="all, delete-orphan")

class SuggestionDecision(Base):
    """
    Persistent record of every creator action on a suggestion (accept, reject with reason, edit).
    """
    __tablename__ = "suggestion_decisions"

    id = Column(String(50), primary_key=True, default=lambda: f"DEC-{uuid.uuid4().hex[:8].upper()}")
    finding_id = Column(String(50), ForeignKey("findings.id"), nullable=False)
    document_id = Column(String(36), nullable=False)
    document_version = Column(Integer, nullable=False)
    action = Column(String(30), nullable=False)  # accepted, rejected, edited
    original_text = Column(Text, nullable=False)
    applied_text = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    actor_id = Column(String(36), nullable=False)
    actor_name = Column(String(100), nullable=False)
    actor_role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    finding = relationship("Finding", back_populates="decisions")

class ReviewComment(Base):
    __tablename__ = "review_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("content_documents.id"), nullable=False)
    document_version = Column(Integer, default=1, nullable=False)
    user_id = Column(String(36), nullable=False)
    user_name = Column(String(100), nullable=False)
    user_role = Column(String(50), nullable=False)
    comment_text = Column(Text, nullable=False)
    action_type = Column(String(50), default="comment")  # comment, request_changes, resubmit, approve, reject
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("ContentDocument", back_populates="comments")

class ApprovalRecord(Base):
    """
    Version-bound approval record. Every approval strictly belongs to an exact document version.
    """
    __tablename__ = "approval_records"

    id = Column(String(50), primary_key=True, default=lambda: f"APP-{uuid.uuid4().hex[:8].upper()}")
    document_id = Column(String(36), ForeignKey("content_documents.id"), nullable=False)
    document_version = Column(Integer, nullable=False)
    review_job_id = Column(String(36), ForeignKey("review_jobs.id"), nullable=False)
    status = Column(String(30), nullable=False)  # approved, rejected, changes_requested
    approver_id = Column(String(36), nullable=False)
    approver_name = Column(String(100), nullable=False)
    approver_role = Column(String(50), nullable=False)
    decision_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("ContentDocument", back_populates="approvals")
    review_job = relationship("ReviewJob", back_populates="approvals")
