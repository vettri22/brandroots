import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from app.database import Base

class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(String(50), primary_key=True)  # e.g. "RULE-VOICE-01", "RULE-CLAIM-01"
    workspace_id = Column(String(36), default="default-workspace")
    category = Column(String(50), nullable=False)  # voice, terminology, promotional_claim, disclaimer, asset
    title = Column(String(200), nullable=False)
    rule_text = Column(Text, nullable=False)
    severity = Column(String(20), default="warning")  # critical, warning, suggestion
    owner_role = Column(String(50), default="brand_owner")
    source_reference = Column(String(255), nullable=True)  # e.g. "Brand Playbook 2026 v2, p.14"
    effective_date = Column(String(50), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    prohibited_patterns = Column(JSON, default=list)  # list of strings / regex patterns to catch deterministically
    required_phrases = Column(JSON, default=list)  # required terms or disclaimers
    clarification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ApprovedFact(Base):
    __tablename__ = "approved_facts"

    id = Column(String(50), primary_key=True)  # e.g. "FACT-PRICE-STARTER"
    workspace_id = Column(String(36), default="default-workspace")
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
    preferred_term = Column(String(100), nullable=False)  # "BrandRoots Intelligence Platform"
    prohibited_variants = Column(JSON, default=list)  # ["BrandRoot", "Brand Roots Tool", "AI auto-publisher"]
    rationale = Column(Text, nullable=False)
    context_guidance = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(String(50), primary_key=True)  # e.g. "ASSET-COLOR-NAVY"
    workspace_id = Column(String(36), default="default-workspace")
    asset_type = Column(String(50), nullable=False)  # color, logo, typography
    name = Column(String(100), nullable=False)
    value = Column(String(255), nullable=False)  # "#0F172A", "Inter", "assets/logo-primary.svg"
    usage_guideline = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
