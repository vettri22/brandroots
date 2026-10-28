import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, default=lambda: f"NOTIF-{uuid.uuid4().hex[:8].upper()}")
    workspace_id = Column(String(36), default="default-workspace")
    organization_id = Column(String(36), nullable=True)
    user_id = Column(String(36), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="review_action")  # review_action, approval, comment, clarity_radar, evidence_expired
    reference_type = Column(String(50), nullable=True)  # document, review, evidence, insight
    reference_id = Column(String(100), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
