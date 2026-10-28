import re
from typing import List, Dict, Any, Optional
from fastapi import UploadFile
from app.services.document_parser import extract_text_from_upload

RULE_CANDIDATE_PATTERNS = [
    {
        "type": "prohibited_term",
        "category": "terminology",
        "regex": re.compile(r"(?:never use|do not use|prohibited|avoid using|deprecated)\s*[:\-]?\s*[\"']?([A-Za-z0-9\s\-]+)[\"']?", re.IGNORECASE),
        "title_prefix": "Prohibited Term"
    },
    {
        "type": "required_term",
        "category": "terminology",
        "regex": re.compile(r"(?:must be referred to as|always use|approved term|canonical name)\s*[:\-]?\s*[\"']?([A-Za-z0-9\s\-]+)[\"']?", re.IGNORECASE),
        "title_prefix": "Required Brand Term"
    },
    {
        "type": "disclaimer",
        "category": "disclaimer",
        "regex": re.compile(r"(?:mandatory disclaimer|required disclosure|legal notice|must include)\s*[:\-]?\s*[\"']?([^\"'\n\.]+)[\"']?", re.IGNORECASE),
        "title_prefix": "Mandatory Disclaimer"
    },
    {
        "type": "tone",
        "category": "voice",
        "regex": re.compile(r"(?:tone of voice|brand tone|style requirement)\s*[:\-]?\s*[\"']?([^\"'\n\.]+)[\"']?", re.IGNORECASE),
        "title_prefix": "Tone & Style Guideline"
    },
    {
        "type": "approved_claim",
        "category": "promotional_claim",
        "regex": re.compile(r"(?:approved claim|verified fact|substantiated claim)\s*[:\-]?\s*[\"']?([^\"'\n\.]+)[\"']?", re.IGNORECASE),
        "title_prefix": "Approved Promotional Claim"
    },
    {
        "type": "accessibility",
        "category": "accessibility",
        "regex": re.compile(r"(?:accessibility|alt-text|contrast ratio|wcag)\s*[:\-]?\s*[\"']?([^\"'\n\.]+)[\"']?", re.IGNORECASE),
        "title_prefix": "Accessibility Standard"
    }
]

async def parse_guideline_document(file: UploadFile) -> Dict[str, Any]:
    """
    Extracts text and identifies candidate rules from uploaded guideline document.
    Does NOT automatically publish rules: returns candidates for human review.
    """
    extracted_text, metadata = await extract_text_from_upload(file)
    paragraphs = [p.strip() for p in extracted_text.split("\n\n") if len(p.strip()) > 15]

    candidates: List[Dict[str, Any]] = []
    seen_rules = set()

    for idx, para in enumerate(paragraphs):
        section_ref = f"Section {idx + 1}"
        
        for rule_pat in RULE_CANDIDATE_PATTERNS:
            match = rule_pat["regex"].search(para)
            if match:
                extracted_phrase = match.group(1).strip()
                if len(extracted_phrase) < 3 or extracted_phrase.lower() in seen_rules:
                    continue
                
                seen_rules.add(extracted_phrase.lower())
                rule_id_candidate = f"RULE-{rule_pat['type'].upper()[:5]}-{len(candidates) + 1:02d}"
                
                candidates.append({
                    "suggested_id": rule_id_candidate,
                    "rule_type": rule_pat["type"],
                    "category": rule_pat["category"],
                    "title": f"{rule_pat['title_prefix']}: {extracted_phrase[:40]}",
                    "rule_text": para,
                    "severity": "critical" if rule_pat["type"] in ("disclaimer", "prohibited_term") else "warning",
                    "source_reference": f"{metadata['filename']} ({section_ref})",
                    "page_reference": section_ref,
                    "prohibited_patterns": [extracted_phrase] if rule_pat["type"] == "prohibited_term" else [],
                    "required_phrases": [extracted_phrase] if rule_pat["type"] in ("required_term", "disclaimer") else [],
                    "confidence": "high" if len(extracted_phrase) > 5 else "moderate"
                })

    return {
        "filename": metadata["filename"],
        "size_bytes": metadata["size_bytes"],
        "page_count": metadata.get("page_count", 1),
        "extraction_method": metadata.get("extraction_method", "raw"),
        "raw_text_preview": extracted_text[:1500],
        "total_paragraphs": len(paragraphs),
        "candidates_found": len(candidates),
        "rule_candidates": candidates,
        "security_warnings": metadata.get("security_warnings", []),
        "prompt_injection_risk": metadata.get("prompt_injection_risk", False)
    }
