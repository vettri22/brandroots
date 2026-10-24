import pytest
from app.services.guideline_debugger import (
    run_guideline_debugger_clustering,
    confirm_or_dismiss_hypothesis,
    approve_guideline_clarification
)
from app.models.brand import BrandGuideline
from app.models.debugger import GuidelineInsight, ProposedGuidelineClarification
from app.models.review import ReviewJob

def test_guideline_debugger_clustering_finds_recurring_guarantees(db_session):
    insights = run_guideline_debugger_clustering(db_session)
    assert len(insights) >= 1

    # Find the insight for RULE-CLAIM-01
    claim_insight = next((ins for ins in insights if ins.rule_id == "RULE-CLAIM-01"), None)
    assert claim_insight is not None
    assert claim_insight.occurrence_count >= 3
    assert claim_insight.pattern_type in ("vague_guideline", "recurring_violation")
    assert "guarantee" in claim_insight.title.lower() or "claim" in claim_insight.title.lower()
    assert claim_insight.hypothesis_status in ("hypothesis", "confirmed")

def test_hypothesis_evaluation(db_session):
    insights = run_guideline_debugger_clustering(db_session)
    insight = insights[0]

    evaluated = confirm_or_dismiss_hypothesis(
        db=db_session,
        insight_id=insight.id,
        action="confirm",
        notes="Reviewer team confirms writers find the bold vs guarantee boundary ambiguous.",
        user_name="Dr. Maya Patel",
        user_role="reviewer"
    )
    assert evaluated.hypothesis_status == "confirmed"
    assert "Dr. Maya Patel" in evaluated.reviewed_by

def test_brand_owner_explicit_clarification_approval(db_session):
    insights = run_guideline_debugger_clustering(db_session)
    insight = next(ins for ins in insights if ins.rule_id == "RULE-CLAIM-01")

    proposal = db_session.query(ProposedGuidelineClarification).filter(
        ProposedGuidelineClarification.insight_id == insight.id
    ).first()
    assert proposal is not None
    assert proposal.approval_status == "pending"

    target_rule = db_session.query(BrandGuideline).filter(BrandGuideline.id == "RULE-CLAIM-01").first()
    initial_version = target_rule.version

    # Brand Owner explicitly approves
    updated_rule, approved_prop = approve_guideline_clarification(
        db=db_session,
        proposal_id=proposal.id,
        brand_owner_name="Elena Rostova",
        edited_rule_text="Be confident and persuasive. BOUNDARY (v2): Never promise guaranteed outcomes.",
        notes="Approved during weekly brand council review."
    )

    assert approved_prop.approval_status == "approved"
    assert updated_rule.version == initial_version + 1
    assert "BOUNDARY (v2)" in updated_rule.rule_text

    # Historical review snapshots should still reflect previous versions
    old_jobs = db_session.query(ReviewJob).all()
    for job in old_jobs:
        if "RULE-CLAIM-01" in job.guideline_snapshot:
            # Snapshot preserves the historical version recorded at review time
            assert job.guideline_snapshot["RULE-CLAIM-01"] == initial_version
