from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.auth import User
from app.models.content import ContentDocument, DocumentVersion, DocumentStatus
from app.schemas.content import (
    ContentDocumentCreate, ContentDocumentUpdate, ContentDocumentResponse,
    DocumentVersionResponse
)
from app.core.auth import get_current_user
from app.services.document_parser import extract_text_from_upload
from app.services.audit_logger import log_audit_event

router = APIRouter(prefix="/documents", tags=["Content Documents"])

@router.get("", response_model=List[ContentDocumentResponse])
def list_documents(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ContentDocument).order_by(ContentDocument.updated_at.desc())
    if status_filter:
        query = query.filter(ContentDocument.status == status_filter)
    return query.all()

@router.post("", response_model=ContentDocumentResponse)
def create_text_document(
    doc_in: ContentDocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = ContentDocument(
        title=doc_in.title,
        content_type=doc_in.content_type,
        original_filename=doc_in.original_filename,
        raw_text=doc_in.raw_text,
        current_text=doc_in.raw_text,
        status=DocumentStatus.DRAFT.value,
        creator_id=current_user.id,
        creator_name=current_user.full_name,
        current_version=1
    )
    db.add(doc)
    db.flush()

    # Save initial version snapshot
    version = DocumentVersion(
        document_id=doc.id,
        version_number=1,
        text_snapshot=doc.raw_text,
        changelog="Initial draft created",
        author_id=current_user.id
    )
    db.add(version)
    db.commit()
    db.refresh(doc)

    log_audit_event(
        db=db,
        event_type="DOCUMENT_CREATED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="document",
        target_id=doc.id,
        summary=f"Created new draft '{doc.title}'"
    )

    return doc

@router.post("/upload", response_model=ContentDocumentResponse)
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and safely extract text from PDF or DOCX file.
    """
    extracted_text, metadata = await extract_text_from_upload(file)

    doc = ContentDocument(
        title=title,
        content_type=metadata.get("extension", ".txt").replace(".", ""),
        original_filename=file.filename,
        raw_text=extracted_text,
        current_text=extracted_text,
        status=DocumentStatus.DRAFT.value,
        creator_id=current_user.id,
        creator_name=current_user.full_name,
        current_version=1
    )
    db.add(doc)
    db.flush()

    version = DocumentVersion(
        document_id=doc.id,
        version_number=1,
        text_snapshot=extracted_text,
        changelog=f"Uploaded {file.filename} (extracted via {metadata.get('extraction_method')})",
        author_id=current_user.id
    )
    db.add(version)
    db.commit()
    db.refresh(doc)

    log_audit_event(
        db=db,
        event_type="DOCUMENT_UPLOADED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="document",
        target_id=doc.id,
        summary=f"Uploaded '{doc.title}' from file {file.filename}",
        details=metadata
    )

    return doc

@router.get("/{document_id}", response_model=ContentDocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(ContentDocument).filter(ContentDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.put("/{document_id}", response_model=ContentDocumentResponse)
def update_document_text(
    document_id: str,
    update_in: ContentDocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(ContentDocument).filter(ContentDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if update_in.title:
        doc.title = update_in.title

    if update_in.current_text and update_in.current_text != doc.current_text:
        doc.current_text = update_in.current_text
        doc.current_version += 1

        # Create new version snapshot
        ver = DocumentVersion(
            document_id=doc.id,
            version_number=doc.current_version,
            text_snapshot=doc.current_text,
            changelog=update_in.changelog or f"Updated draft to v{doc.current_version}",
            author_id=current_user.id
        )
        db.add(ver)

    db.commit()
    db.refresh(doc)

    log_audit_event(
        db=db,
        event_type="DOCUMENT_REVISED",
        actor_id=current_user.id,
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        target_type="document",
        target_id=doc.id,
        summary=f"Revised document '{doc.title}' to version v{doc.current_version}",
        details={"changelog": update_in.changelog}
    )

    return doc

@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
def get_document_versions(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(ContentDocument).filter(ContentDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.desc()).all()
