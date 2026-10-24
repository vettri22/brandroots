from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContentDocumentCreate(BaseModel):
    title: str
    raw_text: str
    content_type: str = "text"
    original_filename: Optional[str] = None

class ContentDocumentUpdate(BaseModel):
    title: Optional[str] = None
    current_text: Optional[str] = None
    changelog: Optional[str] = None

class StatusTransitionRequest(BaseModel):
    new_status: str  # submitted, in_review, changes_requested, resubmitted, approved, rejected
    comment: Optional[str] = None

class DocumentVersionResponse(BaseModel):
    id: str
    document_id: str
    version_number: int
    text_snapshot: str
    changelog: Optional[str] = None
    author_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ContentDocumentResponse(BaseModel):
    id: str
    workspace_id: str
    title: str
    content_type: str
    original_filename: Optional[str] = None
    raw_text: str
    current_text: str
    status: str
    creator_id: str
    creator_name: str
    assigned_reviewer_id: Optional[str] = None
    current_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
