import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class EvidenceStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"

class SourceType(str, enum.Enum):
    DOCUMENT = "uploaded_document"
    URL = "url"
    INTERNAL_REFERENCE = "internal_reference"
    MANUAL = "manual"

class BrandEvidence(Base):
    __tablename__ = "brand_evidence"

    id = Column(String(50), primary_key=True, default=lambda: f"EVID-{uuid.uuid4().hex[:8].upper()}")
    workspace_id = Column(String(36), default="default-workspace")
    organization_id = Column(String(36), nullable=True)
    brand_id = Column(String(36), nullable=True)
    
    # Claim & Value
    claim_title = Column(String(255), nullable=False)
    approved_wording = Column(Text, nullable=False)
    structured_value = Column(String(100), nullable=True)  # e.g. "$49/mo" or "99.9% uptime"
    unit = Column(String(50), nullable=True)
    prohibited_old_values = Column(JSON, default=list)  # legacy superseded claims
    category = Column(String(50), default="pricing", nullable=False)  # pricing, clinical, security, market_share, legal
    description = Column(Text, nullable=True)
    applicable_context = Column(Text, nullable=True)
    
    # Source Reference & Provenance
    source_type = Column(String(50), default=SourceType.DOCUMENT.value, nullable=False)
    source_location = Column(String(255), nullable=True)  # filename or location
    source_url = Column(String(500), nullable=True)
    source_document_id = Column(String(100), nullable=True)
    page_or_section = Column(String(100), nullable=True)
    
    # Governance & Ownership
    evidence_owner = Column(String(100), nullable=False, default="Brand Compliance Lead")
    status = Column(String(30), default=EvidenceStatus.APPROVED.value, nullable=False)
    approval_date = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Dates & Expiry
    effective_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)  # ISO string or YYYY-MM-DD
    review_date = Column(String(50), nullable=True)
    
    # Scope & Permissions
    applicable_product = Column(String(100), nullable=True)
    applicable_market = Column(String(50), nullable=True)
    applicable_channel = Column(String(50), nullable=True)
    public_use_permission = Column(Boolean, default=True, nullable=False)
    
    # Versioning & Audit
    version = Column(Integer, default=1, nullable=False)
    created_by_id = Column(String(36), nullable=True)
    updated_by_id = Column(String(36), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("BrandEvidenceVersion", back_populates="evidence", cascade="all, delete-orphan", order_by="BrandEvidenceVersion.version_number")

class BrandEvidenceVersion(Base):
    __tablename__ = "brand_evidence_versions"

    id = Column(String(50), primary_key=True, default=lambda: f"EVV-{uuid.uuid4().hex[:8].upper()}")
    evidence_id = Column(String(50), ForeignKey("brand_evidence.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    approved_wording = Column(Text, nullable=False)
    structured_value = Column(String(100), nullable=True)
    status = Column(String(30), nullable=False)
    changelog = Column(Text, nullable=True)
    author_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    evidence = relationship("BrandEvidence", back_populates="versions")
