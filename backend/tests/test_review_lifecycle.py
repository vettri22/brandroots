import pytest
from app.models.content import ContentDocument, DocumentStatus
from app.models.auth import UserRole

def test_lifecycle_allowed_and_forbidden_transitions(client, db_session):
    doc = ContentDocument(
        id="test-doc-lifecycle-01",
        title="Lifecycle Test Document",
        content_type="text",
        raw_text="Sample text for review lifecycle testing.",
        current_text="Sample text for review lifecycle testing.",
        status=DocumentStatus.DRAFT.value,
        creator_id="user-creator-01",
        creator_name="Alex Chen",
        current_version=1
    )
    db_session.add(doc)
    db_session.commit()

    # 1. Creator logs in and submits draft
    creator_login = client.post("/api/v1/auth/login", json={"email": "creator@novusbio.com", "password": "demo1234"}).json()
    creator_headers = {"Authorization": f"Bearer {creator_login['access_token']}"}

    # Direct draft -> approved should fail
    illegal_res = client.post(f"/api/v1/reviews/documents/{doc.id}/transition", json={
        "new_status": "approved"
    }, headers=creator_headers)
    assert illegal_res.status_code == 400

    # Legal: draft -> submitted
    submit_res = client.post(f"/api/v1/reviews/documents/{doc.id}/transition", json={
        "new_status": "submitted",
        "comment": "Submitting first draft for compliance review."
    }, headers=creator_headers)
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == DocumentStatus.SUBMITTED.value

    # 2. Reviewer moves to in_review
    reviewer_login = client.post("/api/v1/auth/login", json={"email": "reviewer@novusbio.com", "password": "demo1234"}).json()
    reviewer_headers = {"Authorization": f"Bearer {reviewer_login['access_token']}"}

    review_res = client.post(f"/api/v1/reviews/documents/{doc.id}/transition", json={
        "new_status": "in_review",
        "comment": "Beginning compliance inspection."
    }, headers=reviewer_headers)
    assert review_res.status_code == 200

    # 3. Reviewer requests changes
    changes_res = client.post(f"/api/v1/reviews/documents/{doc.id}/transition", json={
        "new_status": "changes_requested",
        "comment": "Please remove unsupported guarantee phrases."
    }, headers=reviewer_headers)
    assert changes_res.status_code == 200
    assert changes_res.json()["status"] == DocumentStatus.CHANGES_REQUESTED.value

    # 4. Creator resubmits
    resubmit_res = client.post(f"/api/v1/reviews/documents/{doc.id}/transition", json={
        "new_status": "resubmitted",
        "comment": "Revised draft with corrections applied."
    }, headers=creator_headers)
    assert resubmit_res.status_code == 200
    assert resubmit_res.json()["status"] == DocumentStatus.RESUBMITTED.value

    # Policy check: Creator cannot approve their own work!
    creator_approval_res = client.post(f"/api/v1/reviews/documents/{doc.id}/transition", json={
        "new_status": "approved",
        "comment": "Creator attempting to self-approve."
    }, headers=creator_headers)
    assert creator_approval_res.status_code == 403
    assert "creators cannot approve their own" in creator_approval_res.json()["detail"].lower()

    # Authorized Reviewer approves
    reviewer_approval_res = client.post(f"/api/v1/reviews/documents/{doc.id}/transition", json={
        "new_status": "approved",
        "comment": "All corrections verified. Approved for publication."
    }, headers=reviewer_headers)
    assert reviewer_approval_res.status_code == 200
    assert reviewer_approval_res.json()["status"] == DocumentStatus.APPROVED.value
