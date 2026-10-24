import pytest
from app.models.brand import BrandGuideline, ApprovedFact, ApprovedTerminology

def test_list_guidelines(client):
    res = client.get("/api/v1/brand/guidelines")
    assert res.status_code == 200
    guidelines = res.json()
    assert len(guidelines) >= 3
    rule_ids = [g["id"] for g in guidelines]
    assert "RULE-CLAIM-01" in rule_ids
    assert "RULE-VOICE-01" in rule_ids
    assert "RULE-DISCLAIMER-01" in rule_ids

def test_list_approved_facts(client):
    res = client.get("/api/v1/brand/facts")
    assert res.status_code == 200
    facts = res.json()
    assert len(facts) >= 2
    fact_ids = [f["id"] for f in facts]
    assert "FACT-PRICE-PRO" in fact_ids

def test_guideline_version_increment_on_update(client, db_session):
    rule = db_session.query(BrandGuideline).filter(BrandGuideline.id == "RULE-VOICE-01").first()
    old_version = rule.version

    # Login as brand owner
    login = client.post("/api/v1/auth/login", json={"email": "owner@novusbio.com", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    res = client.put(f"/api/v1/brand/guidelines/RULE-VOICE-01", json={
        "rule_text": "Updated voice rule requiring utmost clinical precision and empathetic warmth."
    }, headers=headers)

    assert res.status_code == 200
    updated = res.json()
    assert updated["version"] == old_version + 1

def test_soft_deactivation_preserves_historical_trace(client, db_session):
    login = client.post("/api/v1/auth/login", json={"email": "owner@novusbio.com", "password": "demo1234"}).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    res = client.delete("/api/v1/brand/guidelines/RULE-VOICE-01", headers=headers)
    assert res.status_code == 200

    # Rule still exists in DB as inactive
    rule = db_session.query(BrandGuideline).filter(BrandGuideline.id == "RULE-VOICE-01").first()
    assert rule is not None
    assert rule.is_active is False
