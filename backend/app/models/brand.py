import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Brand(Base):
    __tablename__ = "brands"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, default="default-workspace")
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    supported_channels = Column(JSON, default=lambda: ["website", "social", "email", "press_release", "ads"])
    supported_markets = Column(JSON, default=lambda: ["Global", "US", "EU", "APAC"])
    content_types = Column(JSON, default=lambda: ["article", "landing_page", "social_post", "whitepaper", "ad_copy"])
    tone_guidelines = Column(JSON, default=lambda: {"formality": "professional", "voice": "authoritative, trustworthy", "pace": "concise"})
    claim_restrictions = Column(JSON, default=lambda: ["no_unsubstantiated_guarantees", "require_clinical_reference", "pricing_currency_disclosure"])
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="brands")
    guidelines = relationship("BrandGuideline", back_populates="brand", cascade="all, delete-orphan")
    assets = relationship("BrandAsset", back_populates="brand", cascade="all, delete-orphan")

class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(String(50), primary_key=True)  # e.g. "RULE-VOICE-01", "RULE-CLAIM-01"
    workspace_id = Column(String(36), default="default-workspace")
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=True)
    category = Column(String(50), nullable=False)  # voice, terminology, promotional_claim, disclaimer, asset, accessibility
    title = Column(String(200), nullable=False)
    rule_text = Column(Text, nullable=False)
    rule_type = Column(String(50), default="prohibited_term")  # required_term, prohibited_term, disclaimer, tone, visual, accessibility, human_review
    severity = Column(String(20), default="warning")  # critical, warning, suggestion
    owner_role = Column(String(50), default="brand_owner")
    source_reference = Column(String(255), nullable=True)  # e.g. "Brand Playbook 2026 v2, p.14"
    page_reference = Column(String(50), nullable=True)
    effective_date = Column(String(50), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    prohibited_patterns = Column(JSON, default=list)  # list of strings / regex patterns to catch deterministically
    required_phrases = Column(JSON, default=list)  # required terms or disclaimers
    clarification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = relationship("Brand", back_populates="guidelines")
    versions = relationship("GuidelineVersion", back_populates="guideline", cascade="all, delete-orphan", order_by="GuidelineVersion.version_number")

class GuidelineVersion(Base):
    __tablename__ = "guideline_versions"

    id = Column(String(50), primary_key=True, default=lambda: f"GV-{uuid.uuid4().hex[:10].upper()}")
    guideline_id = Column(String(50), ForeignKey("brand_guidelines.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    rule_text = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    prohibited_patterns = Column(JSON, default=list)
    required_phrases = Column(JSON, default=list)
    changelog = Column(Text, nullable=True)
    author_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    guideline = relationship("BrandGuideline", back_populates="versions")

class ApprovedFact(Base):
    """
    Maintained for direct backward compatibility with existing tests and fact matching.
    """
    __tablename__ = "approved_facts"

    id = Column(String(50), primary_key=True)  # e.g. "FACT-PRICE-STARTER"
    workspace_id = Column(String(36), default="default-workspace")
    brand_id = Column(String(36), nullable=True)
    category = Column(String(50), nullable=False)  # pricing, feature, certification, SLA
    claim_statement = Column(Text, nullable=False)  # "Starter plan is $49 per month billed annually"
    canonical_value = Column(String(100), nullable=True)  # "$49/mo"
    unit = Column(String(50), nullable=True)  # "USD/month"
    prohibited_old_values = Column(JSON, default=list)  # ["$29/mo", "$39/mo"]
    source_document = Column(String(255), nullable=False)  # "Pricing Sheet Q4-2026"
    version = Column(Integer, default=1, nullable=False)
    effective_date = Column(String(50), nullable=False)
    expiry_date = Column(String(50), nullable=True)  # Optional expiry date
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ApprovedTerminology(Base):
    __tablename__ = "approved_terminology"

    id = Column(String(50), primary_key=True)  # e.g. "TERM-PRODUCT-01"
    workspace_id = Column(String(36), default="default-workspace")
    brand_id = Column(String(36), nullable=True)
    preferred_term = Column(String(100), nullable=False)  # "BrandRoots Intelligence Platform"
    prohibited_variants = Column(JSON, default=list)  # ["BrandRoot", "Brand Roots Tool", "AI auto-publisher"]
    rationale = Column(Text, nullable=False)
    context_guidance = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(String(50), primary_key=True)  # e.g. "ASSET-LOGO-PRIMARY"
    workspace_id = Column(String(36), default="default-workspace")
    brand_id = Column(String(36), ForeignKey("brands.id"), nullable=True)
    asset_type = Column(String(50), nullable=False)  # logo, color, typography, image, icon
    name = Column(String(100), nullable=False)
    value = Column(String(255), nullable=False)  # "#0F172A", "Inter", "assets/logo-primary.svg"
    file_path = Column(String(500), nullable=True)
    sha256_hash = Column(String(64), nullable=True)  # Cryptographic hash for exact match verification
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    min_width = Column(Integer, nullable=True)
    min_height = Column(Integer, nullable=True)
    color_hex = Column(String(20), nullable=True)
    alt_text_required = Column(Boolean, default=True, nullable=False)
    usage_guideline = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("Brand", back_populates="assets")
