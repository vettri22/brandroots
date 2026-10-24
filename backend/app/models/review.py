import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class FindingStatus(str, enum.Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    EDITED = "edited"
    DISMISSED = "dismissed"
    ESCALATED = "escalated"

class ReviewJob(Base):
    __tablename__ = "review_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("content_documents.id"), nullable=False)
    document_version = Column(Integer, default=1, nullable=False)
    status = Column(String(30), default="completed", nullable=False)  # pending, running, completed, failed
    compliance_score = Column(Float, default=100.0)  # 0.0 to 100.0
    findings_count = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    suggestion_count = Column(Integer, default=0)
    guideline_snapshot = Column(JSON, default=dict)  # Records guideline versions used during this review
    provider_used = Column(String(50), default="hybrid_engine")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("ContentDocument", back_populates="review_jobs")
    findings = relationship("Finding", back_populates="review_job", cascade="all, delete-orphan")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(50), primary_key=True, default=lambda: f"FND-{uuid.uuid4().hex[:8].upper()}")
    review_job_id = Column(String(36), ForeignKey("review_jobs.id"), nullable=False)
    category = Column(String(50), nullable=False)  # promotional_claim, pricing, terminology, tone, disclaimer
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    confidence = Column(String(30), default="deterministic")  # deterministic, high, moderate, unverified
    location_start = Column(Integer, default=0)
    location_end = Column(Integer, default=0)
    affected_text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    rule_id = Column(String(50), nullable=True)  # link to BrandGuideline or ApprovedFact
    rule_version = Column(Integer, default=1)
    source_reference = Column(String(255), nullable=True)  # playbook reference or "No verified source found"
    suggested_correction = Column(Text, nullable=True)
    status = Column(String(30), default=FindingStatus.OPEN.value, nullable=False)
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    review_job = relationship("ReviewJob", back_populates="findings")

class ReviewComment(Base):
    __tablename__ = "review_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("content_documents.id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    user_name = Column(String(100), nullable=False)
    user_role = Column(String(50), nullable=False)
    comment_text = Column(Text, nullable=False)
    action_type = Column(String(50), default="comment")  # comment, request_changes, resubmit, approve, reject
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("ContentDocument", back_populates="comments")
