from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ContentDocumentCreate(BaseModel):
    title: str
    raw_text: str
    content_type: str = "text"
    channel: str = "website"
    market: str = "Global"
    original_filename: Optional[str] = None
    brand_id: Optional[str] = None

class ContentDocumentUpdate(BaseModel):
    title: Optional[str] = None
    current_text: Optional[str] = None
    changelog: Optional[str] = None
    channel: Optional[str] = None
    market: Optional[str] = None

class StatusTransitionRequest(BaseModel):
    new_status: str  # submitted, in_review, changes_requested, resubmitted, approved, rejected, archived
    comment: Optional[str] = None
    assigned_reviewer_id: Optional[str] = None

class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    text_snapshot: str
    changelog: Optional[str] = None
    author_id: str
    author_name: Optional[str] = "Creator"
    created_at: datetime

class ContentDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    organization_id: Optional[str] = None
    brand_id: Optional[str] = None
    title: str
    content_type: str
    channel: Optional[str] = "website"
    market: Optional[str] = "Global"
    original_filename: Optional[str] = None
    raw_text: str
    current_text: str
    status: str
    creator_id: str
    creator_name: str
    assigned_reviewer_id: Optional[str] = None
    assigned_reviewer_name: Optional[str] = None
    current_version: int
    approved_version: Optional[int] = None
    approved_at: Optional[datetime] = None
    approved_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
