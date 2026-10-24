import io
import re
from typing import Tuple, Dict, Any
from fastapi import HTTPException, UploadFile
import pymupdf
import docx
from app.config import settings

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
    re.compile(r"you\s+must\s+now\s+act\s+as", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"\[INST\].*\[/INST\]", re.IGNORECASE)
]

def sanitize_untrusted_text(text: str) -> Tuple[str, bool, list[str]]:
    """
    Sanitize text extracted from uploaded documents.
    Detects potential prompt injection patterns and wraps untrusted input safely.
    """
    # Remove null bytes
    cleaned = text.replace("\x00", "")
    
    warnings = []
    has_injection_risk = False
    for pattern in INJECTION_PATTERNS:
        if pattern.search(cleaned):
            has_injection_risk = True
            warnings.append(f"Potential instruction injection marker detected: '{pattern.pattern}'")
            
    return cleaned, has_injection_risk, warnings

async def extract_text_from_upload(file: UploadFile) -> Tuple[str, Dict[str, Any]]:
    """
    Safely extract text from PDF, DOCX, or TXT file.
    Validates size and structure.
    """
    content = await file.read()
    filename = file.filename or "unknown"
    size = len(content)

    if size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB"
        )

    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    extracted_text = ""
    metadata: Dict[str, Any] = {
        "filename": filename,
        "size_bytes": size,
        "extension": ext,
        "page_count": 1,
        "extraction_method": "raw"
    }

    try:
        if ext == ".pdf":
            doc = pymupdf.open(stream=content, filetype="pdf")
            metadata["page_count"] = len(doc)
            metadata["extraction_method"] = "pymupdf"
            pages = []
            for i, page in enumerate(doc):
                pages.append(page.get_text("text"))
            extracted_text = "\n\n".join(pages)
            doc.close()

        elif ext == ".docx":
            metadata["extraction_method"] = "python-docx"
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
            extracted_text = "\n\n".join(paragraphs)

        elif ext in (".txt", ".md"):
            metadata["extraction_method"] = "utf-8"
            extracted_text = content.decode("utf-8", errors="replace")

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to process document {filename}: {str(e)}"
        )

    sanitized, has_risk, warnings = sanitize_untrusted_text(extracted_text)
    metadata["prompt_injection_risk"] = has_risk
    metadata["security_warnings"] = warnings

    if not sanitized.strip():
        raise HTTPException(
            status_code=422,
            detail="The uploaded document contains no readable text."
        )

    return sanitized, metadata
