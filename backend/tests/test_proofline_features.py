import io
import pytest
from app.models.auth import User, Workspace, UserRole
from app.models.content import ContentDocument, DocumentStatus, DocumentVersion
from app.models.review import ReviewJob, Finding, SuggestionDecision, ApprovalRecord
from app.models.evidence import BrandEvidence, EvidenceStatus
from app.models.brand import Brand, BrandAsset
from app.services.evidence_service import verify_claim_against_ledger, is_evidence_expired, detect_evidence_conflicts
from app.services.asset_checker import verify_image_compliance, compute_sha256
from PIL import Image

def test_evidence_ledger_crud_and_versioning(client, db_session):
    # 1. Login as Brand Owner
    login_res = client.post("/api/v1/auth/login", json={"email": "owner@novusbio.com", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {login_res['access_token']}"}

    # 2. Create new evidence record
    create_payload = {
        "claim_title": "Enterprise Cloud Uptime Guarantee",
        "approved_wording": "NovusBio guarantees 99.99% multi-region cloud uptime backed by an audited enterprise SLA.",
        "structured_value": "99.99% uptime",
        "unit": "Percentage",
        "category": "security",
        "source_type": "uploaded_document",
        "source_location": "Cloud Architecture & Availability Audit Q3-2026.pdf",
        "page_or_section": "Section 2.1 Availability SLA",
        "evidence_owner": "Elena Rostova",
        "effective_date": "2026-10-01",
        "expiry_date": "2027-10-01",
        "public_use_permission": True,
        "status": "approved"
    }
    res = client.post("/api/v1/evidence", json=create_payload, headers=headers)
    assert res.status_code == 200
    ev = res.json()
    assert ev["id"].startswith("EVID-")
    assert ev["version"] == 1
    assert ev["is_expired"] is False

    # 3. Update evidence wording (substantive update increments version)
    update_payload = {
        "approved_wording": "NovusBio guarantees 99.995% multi-region cloud uptime backed by an audited enterprise SLA.",
        "structured_value": "99.995% uptime",
        "changelog_reason": "Upgraded availability SLA tier from 99.99% to 99.995%."
    }
    update_res = client.put(f"/api/v1/evidence/{ev['id']}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["version"] == 2
    assert updated["structured_value"] == "99.995% uptime"

    # 4. Check version history
    versions_res = client.get(f"/api/v1/evidence/{ev['id']}/versions")
    assert versions_res.status_code == 200
    assert len(versions_res.json()) >= 2

def test_evidence_claim_verification(db_session):
    # 1. Supported claim: cites Pro plan $49/mo
    res_sup = verify_claim_against_ledger(
        db=db_session,
        claim_text="Our NovusBio Pro plan is $49/mo with full clinical copilot capabilities."
    )
    assert res_sup["status"] == "supported"
    assert "EVID-PRICE-STARTER" in res_sup["matched_evidence_id"]

    # 2. Contradicted claim: cites prohibited legacy value $29/mo
    res_contra = verify_claim_against_ledger(
        db=db_session,
        claim_text="Get the NovusBio Pro plan for only $29/mo today!"
    )
    assert res_contra["status"] == "contradicted"
    assert "EVID-PRICE-STARTER" in res_contra["matched_evidence_id"]
    assert "$49/mo" in res_contra["suggested_correction"]

    # 3. Expired evidence: cites expired beta trial
    res_exp = verify_claim_against_ledger(
        db=db_session,
        claim_text="Physicians reported 94% satisfaction in our pilot trial phase."
    )
    assert res_exp["status"] == "expired"
    assert "expired" in res_exp["explanation"].lower()

    # 4. Unsupported claim: fabricated claim with no evidence
    res_unsup = verify_claim_against_ledger(
        db=db_session,
        claim_text="NovusBio cures all chronic conditions with proprietary nanobots."
    )
    assert res_unsup["status"] == "unsupported"
    assert res_unsup["matched_evidence_id"] is None

def test_version_bound_approval_and_edit_invalidation(client, db_session):
    creator_login = client.post("/api/v1/auth/login", json={"email": "creator@novusbio.com", "password": "demo1234"}).json()
    creator_headers = {"Authorization": f"Bearer {creator_login['access_token']}"}

    reviewer_login = client.post("/api/v1/auth/login", json={"email": "reviewer@novusbio.com", "password": "demo1234"}).json()
    reviewer_headers = {"Authorization": f"Bearer {reviewer_login['access_token']}"}

    # 1. Creator creates a draft
    create_res = client.post("/api/v1/documents", json={
        "title": "Version Bound Approval Test Draft",
        "raw_text": "Compliant text with NovusBio Clinical Copilot and verified facts.",
        "content_type": "article"
    }, headers=creator_headers)
    assert create_res.status_code == 200
    doc_id = create_res.json()["id"]

    # 2. Submit for review
    sub_res = client.post(f"/api/v1/reviews/documents/{doc_id}/transition", json={
        "new_status": "submitted",
        "comment": "Submitting for compliance review"
    }, headers=creator_headers)
    assert sub_res.status_code == 200

    # 3. Reviewer moves to in_review
    in_rev = client.post(f"/api/v1/reviews/documents/{doc_id}/transition", json={
        "new_status": "in_review",
        "comment": "Starting inspection"
    }, headers=reviewer_headers)
    assert in_rev.status_code == 200

    # 4. Policy check: Creator cannot approve their own work!
    creator_app_res = client.post(f"/api/v1/reviews/documents/{doc_id}/transition", json={
        "new_status": "approved",
        "comment": "Self approving"
    }, headers=creator_headers)
    assert creator_app_res.status_code == 403

    # 5. Authorized Reviewer approves (bound to v1)
    app_res = client.post(f"/api/v1/reviews/documents/{doc_id}/transition", json={
        "new_status": "approved",
        "comment": "Approved version 1"
    }, headers=reviewer_headers)
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "approved"
    assert app_res.json()["approved_version"] == 1

    # Verify ApprovalRecord was persisted
    approvals_res = client.get(f"/api/v1/reviews/documents/{doc_id}/approvals")
    assert approvals_res.status_code == 200
    assert len(approvals_res.json()) >= 1
    assert approvals_res.json()[0]["document_version"] == 1

    # 6. Creator edits approved document text -> MUST INVALIDATE APPROVAL!
    edit_res = client.put(f"/api/v1/documents/{doc_id}", json={
        "current_text": "Edited text after approval adding unreviewed statements.",
        "changelog": "Added post-approval revisions"
    }, headers=creator_headers)
    assert edit_res.status_code == 200
    updated_doc = edit_res.json()
    assert updated_doc["current_version"] == 2
    assert updated_doc["status"] == "draft"  # Approval revoked!
    assert updated_doc["approved_version"] is None

def test_correction_studio_reject_with_reason(client, db_session):
    creator_login = client.post("/api/v1/auth/login", json={"email": "creator@novusbio.com", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {creator_login['access_token']}"}

    # Find a finding
    finding = db_session.query(Finding).filter(Finding.status == "open").first()
    assert finding is not None

    # Reject suggestion with explicit reason
    reject_res = client.put(f"/api/v1/reviews/findings/{finding.id}/resolve", json={
        "status": "rejected",
        "reason": "Technical quote from client interview; exception approved by legal."
    }, headers=headers)
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"
    assert reject_res.json()["creator_decision"] == "rejected"

    # Verify persistent SuggestionDecision was stored
    decision = db_session.query(SuggestionDecision).filter(SuggestionDecision.finding_id == finding.id).first()
    assert decision is not None
    assert decision.action == "rejected"
    assert "Technical quote" in decision.reason

def test_visual_asset_cryptographic_and_accessibility_checks(client, db_session):
    # Generate test image in memory (200x200 solid blue)
    img = Image.new("RGB", (200, 200), color=(10, 15, 29))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()
    computed_hash = compute_sha256(img_bytes)

    # Register an approved asset with this exact hash
    asset = BrandAsset(
        id="ASSET-TEST-BLUE",
        workspace_id="default-workspace",
        asset_type="logo",
        name="Official Brand Blue Shield",
        value="blue-shield.png",
        sha256_hash=computed_hash,
        width=200,
        height=200,
        is_active=True
    )
    db_session.add(asset)
    db_session.commit()

    # Test 1: Upload image with alt text and matching hash
    files = {"file": ("blue-shield.png", img_bytes, "image/png")}
    data = {"alt_text": "Official NovusBio Blue Shield Logo"}
    res = client.post("/api/v1/assets/verify-image", files=files, data=data)
    assert res.status_code == 200
    body = res.json()
    assert body["sha256_hash"] == computed_hash
    assert body["exact_match_asset"] is not None
    assert body["exact_match_asset"]["id"] == "ASSET-TEST-BLUE"
    assert body["alt_text_status"] == "pass"

    # Test 2: Upload image without alt text -> fails accessibility check
    files_no_alt = {"file": ("blue-shield.png", img_bytes, "image/png")}
    res_no_alt = client.post("/api/v1/assets/verify-image", files=files_no_alt, data={"alt_text": ""})
    assert res_no_alt.status_code == 200
    body_no_alt = res_no_alt.json()
    assert body_no_alt["alt_text_status"] == "missing"
    assert any(f["category"] == "accessibility" for f in body_no_alt["findings"])

def test_guideline_radar_status_marking(client, db_session):
    # Check that Guideline Clarity Radar insights can be marked with governance statuses
    insights = client.get("/api/v1/debugger/insights").json()
    assert len(insights) >= 1
    target = insights[0]

    # Evaluate with status_marking="under_investigation"
    owner_login = client.post("/api/v1/auth/login", json={"email": "owner@novusbio.com", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {owner_login['access_token']}"}

    eval_res = client.post(f"/api/v1/debugger/insights/{target['id']}/evaluate", json={
        "action": "confirm",
        "status_marking": "needs_clarification",
        "decision_notes": "Brand council scheduled for review."
    }, headers=headers)
    assert eval_res.status_code == 200
    assert eval_res.json()["status_marking"] == "needs_clarification"
