import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.database import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(50), primary_key=True, default=lambda: f"AUD-{uuid.uuid4().hex[:10].upper()}")
    workspace_id = Column(String(36), default="default-workspace")
    organization_id = Column(String(36), nullable=True)
    brand_id = Column(String(36), nullable=True)
    event_type = Column(String(60), nullable=False)  
    # e.g.: RULE_CREATED, RULE_UPDATED, CLARIFICATION_PROPOSED, CLARIFICATION_APPROVED, 
    #       DOCUMENT_SUBMITTED, REVIEW_COMPLETED, CHANGE_REQUESTED, DOCUMENT_APPROVED, 
    #       DOCUMENT_EDITED, SUGGESTION_ACCEPTED, SUGGESTION_REJECTED, EVIDENCE_CREATED, EVIDENCE_EXPIRED
    actor_id = Column(String(100), nullable=False)
    actor_name = Column(String(100), nullable=False)
    actor_role = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)  # rule, document, finding, clarification, insight, evidence, brand
    target_id = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
