import pytest
from app.models.content import ContentDocument
from app.models.review import Finding, ReviewJob

def test_dashboard_metrics_endpoint(client):
    res = client.get("/api/v1/dashboard/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "pending_reviews" in data
    assert "findings_by_severity" in data
    assert "top_recurring_violations" in data
    assert data["data_mode"] == "seeded_demonstration_and_live"

def test_audit_logs_endpoint(client):
    res = client.get("/api/v1/dashboard/audit-logs")
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)
    assert len(logs) >= 1

def test_apply_suggested_correction_to_draft(client, db_session):
    doc = db_session.query(ContentDocument).filter(ContentDocument.id == "doc-demo-001").first()
    assert doc is not None

    job = db_session.query(ReviewJob).filter(ReviewJob.document_id == doc.id).first()
    assert job is not None

    # Find the pricing finding ($29/mo -> $49/mo)
    pricing_finding = db_session.query(Finding).filter(
        Finding.review_job_id == job.id,
        Finding.affected_text == "$29/mo"
    ).first()

    creator_login = client.post("/api/v1/auth/login", json={"email": "creator@novusbio.com", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {creator_login['access_token']}"}

    res = client.put(f"/api/v1/reviews/findings/{pricing_finding.id}/resolve", json={
        "status": "accepted",
        "resolution_notes": "Accepted approved canonical pricing."
    }, headers=headers)

    assert res.status_code == 200
    assert res.json()["status"] == "accepted"

    # Verify that the document text was updated with $49/mo and new version was created
    db_session.refresh(doc)
    assert "$49/mo" in doc.current_text
    assert doc.current_version >= 2
