import pytest
from app.services.compliance_engine import calculate_compliance_score, run_compliance_check
from app.models.content import ContentDocument

def test_compliance_score_deductions():
    # 1 critical (-25) + 1 warning (-10) = 65.0
    findings = [
        {"severity": "critical"},
        {"severity": "warning"}
    ]
    score = calculate_compliance_score(findings)
    assert score == 65.0

    # Clean draft = 100.0
    assert calculate_compliance_score([]) == 100.0

def test_compliance_check_detects_demo_violations(db_session):
    doc = ContentDocument(
        id="test-doc-check-01",
        title="Test Problematic Draft",
        content_type="text",
        raw_text=(
            "Our hospital AI tool gives clinicians guaranteed results for emergency care. "
            "Get started for just $29/mo with our BioBot today."
        ),
        current_text=(
            "Our hospital AI tool gives clinicians guaranteed results for emergency care. "
            "Get started for just $29/mo with our BioBot today."
        ),
        status="draft",
        creator_id="user-creator-01",
        creator_name="Alex Chen",
        current_version=1
    )
    db_session.add(doc)
    db_session.commit()

    job = run_compliance_check(
        db=db_session,
        document=doc,
        user_id="user-creator-01",
        user_name="Alex Chen",
        user_role="creator"
    )

    assert job.status == "completed"
    assert job.findings_count >= 3
    assert job.compliance_score < 70.0

    # Verify structured findings
    findings = job.findings
    categories = [f.category for f in findings]
    affected_texts = [f.affected_text for f in findings]

    assert any("guaranteed results" in txt.lower() for txt in affected_texts)
    assert any("$29/mo" in txt for txt in affected_texts)
    assert any("BioBot" in txt for txt in affected_texts)

    # Verify structured fields
    for f in findings:
        assert f.id.startswith("FND-")
        assert f.severity in ("critical", "high", "warning", "medium", "low", "suggestion")
        assert f.explanation is not None and len(f.explanation) > 5
        assert f.suggested_correction is not None
        assert f.source_reference is not None
