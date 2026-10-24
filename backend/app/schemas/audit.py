from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class AuditEventResponse(BaseModel):
    id: str
    workspace_id: str
    event_type: str
    actor_id: str
    actor_name: str
    actor_role: str
    target_type: str
    target_id: str
    summary: str
    details: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True
