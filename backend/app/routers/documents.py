import difflib
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
    brand_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ContentDocument).order_by(ContentDocument.updated_at.desc())
    if brand_id:
        query = query.filter(or_(ContentDocument.brand_id == brand_id, ContentDocument.brand_id == None))
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
        workspace_id=current_user.workspace_id or "default-workspace",
        organization_id=current_user.organization_id or current_user.workspace_id,
        brand_id=doc_in.brand_id,
        title=doc_in.title,
        content_type=doc_in.content_type,
        channel=doc_in.channel or "website",
        market=doc_in.market or "Global",
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
        author_id=current_user.id,
        author_name=current_user.full_name
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
    brand_id: Optional[str] = Form(None),
    channel: Optional[str] = Form("website"),
    market: Optional[str] = Form("Global"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and safely extract text from PDF or DOCX file with prompt-injection defense.
    """
    extracted_text, metadata = await extract_text_from_upload(file)

    doc = ContentDocument(
        workspace_id=current_user.workspace_id or "default-workspace",
        organization_id=current_user.organization_id or current_user.workspace_id,
        brand_id=brand_id,
        title=title,
        content_type=metadata.get("extension", ".txt").replace(".", ""),
        channel=channel,
        market=market,
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
        author_id=current_user.id,
        author_name=current_user.full_name
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
    if update_in.channel:
        doc.channel = update_in.channel
    if update_in.market:
        doc.market = update_in.market

    if update_in.current_text and update_in.current_text != doc.current_text:
        old_version = doc.current_version
        was_approved = (doc.status == DocumentStatus.APPROVED.value or doc.approved_version is not None)
        
        doc.current_text = update_in.current_text
        doc.current_version += 1

        # Version-bound approval invalidation: editing approved content invalidates approval!
        if was_approved:
            doc.status = DocumentStatus.DRAFT.value
            doc.approved_version = None
            doc.approved_at = None
            doc.approved_by_id = None
            doc.approved_by_name = None

            log_audit_event(
                db=db,
                event_type="APPROVAL_INVALIDATED",
                actor_id=current_user.id,
                actor_name=current_user.full_name,
                actor_role=current_user.role,
                target_type="document",
                target_id=doc.id,
                summary=f"Approval invalidated: '{doc.title}' modified from approved v{old_version} to v{doc.current_version}. New preflight review required before publication.",
                details={"old_version": old_version, "new_version": doc.current_version}
            )

        # Create new immutable version snapshot
        ver = DocumentVersion(
            document_id=doc.id,
            version_number=doc.current_version,
            text_snapshot=doc.current_text,
            changelog=update_in.changelog or f"Updated draft to v{doc.current_version}",
            author_id=current_user.id,
            author_name=current_user.full_name
        )
        db.add(ver)

    doc.updated_at = datetime.utcnow()
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

@router.get("/{document_id}/diff")
def get_version_diff(
    document_id: str,
    v1: int = Query(..., description="Base version number"),
    v2: int = Query(..., description="Target version number"),
    db: Session = Depends(get_db)
):
    """
    Computes unified text diff between two versions of a document.
    """
    ver1 = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
        DocumentVersion.version_number == v1
    ).first()
    ver2 = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
        DocumentVersion.version_number == v2
    ).first()

    if not ver1 or not ver2:
        raise HTTPException(status_code=404, detail=f"Versions {v1} and/or {v2} not found for document {document_id}")

    lines1 = ver1.text_snapshot.splitlines(keepends=True)
    lines2 = ver2.text_snapshot.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        lines1, lines2,
        fromfile=f"v{v1}",
        tofile=f"v{v2}",
        lineterm=""
    ))

    return {
        "document_id": document_id,
        "v1": v1,
        "v2": v2,
        "diff_lines": diff,
        "diff_text": "".join(diff),
        "v1_text": ver1.text_snapshot,
        "v2_text": ver2.text_snapshot
    }
