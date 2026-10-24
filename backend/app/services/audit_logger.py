from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.audit import AuditEvent

def log_audit_event(
    db: Session,
    event_type: str,
    actor_id: str,
    actor_name: str,
    actor_role: str,
    target_type: str,
    target_id: str,
    summary: str,
    details: Optional[Dict[str, Any]] = None,
    workspace_id: str = "default-workspace"
) -> AuditEvent:
    event = AuditEvent(
        workspace_id=workspace_id,
        event_type=event_type,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        target_type=target_type,
        target_id=target_id,
        summary=summary,
        details=details or {}
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
