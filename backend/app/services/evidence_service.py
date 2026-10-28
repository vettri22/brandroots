import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.evidence import BrandEvidence, BrandEvidenceVersion, EvidenceStatus
from app.models.brand import ApprovedFact

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

def is_evidence_expired(evidence: BrandEvidence) -> bool:
    if evidence.status == EvidenceStatus.EXPIRED.value:
        return True
    if evidence.expiry_date:
        exp = parse_date(evidence.expiry_date)
        if exp and exp < datetime.utcnow():
            return True
    return False

def detect_evidence_conflicts(db: Session, brand_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Identifies active evidence records that present potentially contradictory or conflicting statements.
    """
    query = db.query(BrandEvidence).filter(
        BrandEvidence.is_active == True,
        BrandEvidence.status == EvidenceStatus.APPROVED.value
    )
    if brand_id:
        query = query.filter(or_(BrandEvidence.brand_id == brand_id, BrandEvidence.brand_id == None))
    
    records = query.all()
    conflicts = []
    
    # Check for legacy values that match another active approved record
    for i in range(len(records)):
        rec_a = records[i]
        old_vals_a = [v.lower() for v in (rec_a.prohibited_old_values or [])]
        for j in range(i + 1, len(records)):
            rec_b = records[j]
            old_vals_b = [v.lower() for v in (rec_b.prohibited_old_values or [])]
            
            # Check 1: rec_a canonical value is in rec_b prohibited old values or vice-versa
            val_a = (rec_a.structured_value or "").lower()
            val_b = (rec_b.structured_value or "").lower()
            
            conflict_detected = False
            reason = ""
            
            if val_a and val_a in old_vals_b:
                conflict_detected = True
                reason = f"Record '{rec_a.id}' approves structured value '{rec_a.structured_value}', which is marked as prohibited/superseded by '{rec_b.id}'."
            elif val_b and val_b in old_vals_a:
                conflict_detected = True
                reason = f"Record '{rec_b.id}' approves structured value '{rec_b.structured_value}', which is marked as prohibited/superseded by '{rec_a.id}'."
            elif rec_a.category == rec_b.category and rec_a.applicable_product == rec_b.applicable_product and rec_a.applicable_product is not None:
                if rec_a.structured_value and rec_b.structured_value and rec_a.structured_value != rec_b.structured_value:
                    conflict_detected = True
                    reason = f"Records '{rec_a.id}' and '{rec_b.id}' both define conflicting structured values for product '{rec_a.applicable_product}': '{rec_a.structured_value}' vs '{rec_b.structured_value}'."
            
            if conflict_detected:
                conflicts.append({
                    "evidence_a_id": rec_a.id,
                    "evidence_a_title": rec_a.claim_title,
                    "evidence_b_id": rec_b.id,
                    "evidence_b_title": rec_b.claim_title,
                    "category": rec_a.category,
                    "reason": reason
                })
                
    return conflicts

def verify_claim_against_ledger(
    db: Session,
    claim_text: str,
    brand_id: Optional[str] = None,
    channel: Optional[str] = None,
    market: Optional[str] = None
) -> Dict[str, Any]:
    """
    Substantiates content against the Brand Evidence Ledger.
    Distinguishes carefully between:
    - supported
    - contradicted
    - expired
    - unsupported
    - human_review_required
    Missing evidence does NOT prove a statement is false.
    """
    query = db.query(BrandEvidence).filter(BrandEvidence.is_active == True)
    if brand_id:
        query = query.filter(or_(BrandEvidence.brand_id == brand_id, BrandEvidence.brand_id == None))
    
    evidence_records = query.all()
    text_lower = claim_text.lower()
    
    # 1. Check for Contradicted Claims (e.g. text contains prohibited legacy value)
    for ev in evidence_records:
        old_vals = ev.prohibited_old_values or []
        for old_val in old_vals:
            if old_val.lower() in text_lower:
                return {
                    "status": "contradicted",
                    "confidence": "deterministic_verified",
                    "claim_statement": claim_text,
                    "matched_evidence_id": ev.id,
                    "matched_evidence_wording": ev.approved_wording,
                    "source_reference": f"{ev.source_location or ev.source_url or 'Evidence Ledger'} ({ev.page_or_section or 'General'})",
                    "explanation": f"Claim uses deprecated figure/statement '{old_val}'. Current approved fact '{ev.id}' canonical value is '{ev.structured_value or ev.approved_wording}'.",
                    "suggested_correction": ev.structured_value or ev.approved_wording
                }
                
    # 2. Check for Supported or Expired Claims
    for ev in evidence_records:
        # Match by canonical structured value or key phrase in approved wording
        matched = False
        if ev.structured_value and ev.structured_value.lower() in text_lower:
            matched = True
        elif len(ev.approved_wording) > 10 and ev.approved_wording.lower() in text_lower:
            matched = True
        elif ev.claim_title and ev.claim_title.lower() in text_lower:
            matched = True
            
        if matched:
            # Check expiry
            if is_evidence_expired(ev):
                return {
                    "status": "expired",
                    "confidence": "deterministic_verified",
                    "claim_statement": claim_text,
                    "matched_evidence_id": ev.id,
                    "matched_evidence_wording": ev.approved_wording,
                    "source_reference": f"{ev.source_location or 'Evidence Ledger'} (Expired: {ev.expiry_date})",
                    "explanation": f"Claim matches evidence record '{ev.id}', but this evidence record expired on {ev.expiry_date}. Evidence must be reviewed and re-authorized before publication.",
                    "suggested_correction": f"Verify updated evidence for '{ev.claim_title}' before citing in public materials"
                }
            
            # Check public use permission
            if not ev.public_use_permission and channel in ("website", "social", "ads", "press_release"):
                return {
                    "status": "human_review_required",
                    "confidence": "high",
                    "claim_statement": claim_text,
                    "matched_evidence_id": ev.id,
                    "matched_evidence_wording": ev.approved_wording,
                    "source_reference": ev.source_location,
                    "explanation": f"Evidence '{ev.id}' is approved for internal use only. Public use on channel '{channel}' is not permitted without explicit legal approval.",
                    "suggested_correction": "Obtain public release clearance or replace with public-approved claim"
                }
                
            return {
                "status": "supported",
                "confidence": "deterministic_verified",
                "claim_statement": claim_text,
                "matched_evidence_id": ev.id,
                "matched_evidence_wording": ev.approved_wording,
                "source_reference": f"{ev.source_location or ev.source_url or 'Evidence Ledger'} ({ev.page_or_section or 'General'})",
                "explanation": f"Claim is verified and substantiated by approved evidence record '{ev.id}' ({ev.claim_title}).",
                "suggested_correction": None
            }
            
    # 3. Check for Absolute Outcome Guarantees
    guarantee_pattern = re.compile(r"\b(guaranteed\s+(results|roi|outcome|cure|success)|100%\s+(effective|money-back|cure)|zero\s+risk)\b", re.IGNORECASE)
    if guarantee_pattern.search(claim_text):
        return {
            "status": "unsupported",
            "confidence": "contextual_heuristic",
            "claim_statement": claim_text,
            "matched_evidence_id": None,
            "matched_evidence_wording": None,
            "source_reference": "Brand Governance Standards",
            "explanation": "Claim asserts an absolute outcome guarantee without registered clinical or audit evidence. Note: Missing evidence does not prove a claim is false, but brand policy requires documented substantiation before publication.",
            "suggested_correction": "Qualify wording with measured findings or cite verified trial outcomes"
        }
        
    # 4. Standard Unsupported Notice
    return {
        "status": "unsupported",
        "confidence": "moderate",
        "claim_statement": claim_text,
        "matched_evidence_id": None,
        "matched_evidence_wording": None,
        "source_reference": "Brand Evidence Ledger",
        "explanation": "No matching approved evidence was found in the Brand Evidence Ledger. (Note: The absence of evidence does not mean the statement is false, but it cannot be verified as approved brand fact).",
        "suggested_correction": "Submit a new evidence record or reference existing verified documentation"
    }
