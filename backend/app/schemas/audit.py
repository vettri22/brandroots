from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    organization_id: Optional[str] = None
    brand_id: Optional[str] = None
    event_type: str
    actor_id: str
    actor_name: str
    actor_role: str
    target_type: str
    target_id: str
    summary: str
    details: Dict[str, Any] = {}
    timestamp: datetime
