import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    CHANGES_REQUESTED = "changes_requested"
    RESUBMITTED = "resubmitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class ContentDocument(Base):
    __tablename__ = "content_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), default="default-workspace")
    title = Column(String(200), nullable=False)
    content_type = Column(String(20), default="text")  # text, pdf, docx
    original_filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)  # original uploaded or submitted text
    current_text = Column(Text, nullable=False)  # active revision with accepted edits
    status = Column(String(30), default=DocumentStatus.DRAFT.value, nullable=False)
    creator_id = Column(String(36), nullable=False)
    creator_name = Column(String(100), nullable=False)
    assigned_reviewer_id = Column(String(36), nullable=True)
    current_version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan", order_by="DocumentVersion.version_number")
    review_jobs = relationship("ReviewJob", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("ReviewComment", back_populates="document", cascade="all, delete-orphan")

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("content_documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    text_snapshot = Column(Text, nullable=False)
    changelog = Column(Text, nullable=True)
    author_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("ContentDocument", back_populates="versions")
