from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.brand import BrandGuideline, ApprovedFact
from app.models.content import ContentDocument
from app.models.review import Finding, ReviewJob
from app.models.debugger import GuidelineInsight, ProposedGuidelineClarification
from app.services.audit_logger import log_audit_event

def run_guideline_debugger_clustering(db: Session) -> List[GuidelineInsight]:
    """
    Analyzes historical review findings across all drafts.
    Clusters recurring errors, detects potential rule ambiguities or stale facts,
    and creates or refreshes GuidelineInsight and ProposedGuidelineClarification drafts.
    """
    # 1. Fetch all findings with their document associations
    findings = db.query(Finding).all()
    if not findings:
        return []

    # Map review_job_id to document_id
    jobs = {j.id: j.document_id for j in db.query(ReviewJob.id, ReviewJob.document_id).all()}

    # Group findings by rule_id
    clusters_by_rule = defaultdict(list)
    for f in findings:
        if f.rule_id:
            doc_id = jobs.get(f.review_job_id, "unknown-doc")
            clusters_by_rule[f.rule_id].append((f, doc_id))

    insights = []

    for rule_id, items in clusters_by_rule.items():
        count = len(items)
        if count < 2:
            continue  # We need recurring evidence to form a debugger insight

        rule = db.query(BrandGuideline).filter(BrandGuideline.id == rule_id).first()
        fact = None
        if not rule:
            fact = db.query(ApprovedFact).filter(ApprovedFact.id == rule_id).first()

        finding_ids = [item[0].id for item in items]
        document_ids = list(set([item[1] for item in items]))
        quotes = [f'"{item[0].affected_text}"' for item in items[:4]]
        quotes_summary = ", ".join(quotes)

        # Detect pattern type and root cause
        if rule and "claim" in rule.category.lower():
            title = f"Recurring Guarantee Violations Linked to '{rule.title}'"
            root_cause = (
                f"The promotional claim guideline '{rule_id}' encourages confident and persuasive messaging, "
                f"but lacks an explicit boundary regarding absolute guarantees or unverified outcome claims. "
                f"Writers repeatedly interpret 'be bold' as permission to state guaranteed results."
            )
            pattern_type = "vague_guideline"
            suggested_action = (
                f"Clarify '{rule_id}' boundary: explicitly prohibit terms like 'guaranteed results', '100% effective', "
                f"and 'miracle' unless accompanied by a verified clinical/audit source certificate."
            )
            proposed_clarification = (
                f"{rule.rule_text} "
                f"BOUNDARY CLARIFICATION (v{rule.version + 1}): Do not promise guaranteed outcomes, 100% success rates, "
                f"or risk-free results unless an approved evidence record explicitly permits the claim."
            )

        elif fact and "price" in fact.category.lower():
            title = f"Repeated Outdated Pricing Citations for '{fact.id}'"
            root_cause = (
                f"Multiple drafts repeatedly cite legacy pricing ({quotes_summary}). "
                f"Sales collateral and draft templates have not been synchronized with the updated Q4 price schedule."
            )
            pattern_type = "outdated_fact"
            suggested_action = (
                f"Update content templates to enforce canonical price '{fact.canonical_value}' "
                f"and flag legacy figures as deprecated."
            )
            proposed_clarification = (
                f"Enforce canonical pricing '{fact.canonical_value}' across all marketing and sales assets. "
                f"Deprecate references to legacy pricing tiers."
            )

        else:
            title = f"Clustered Compliance Deviations for Rule '{rule_id}'"
            root_cause = (
                f"Observed {count} recurring findings under '{rule_id}'. "
                f"Reviewers frequently flag phrases ({quotes_summary}), suggesting creators find the guidance ambiguous or difficult to apply."
            )
            pattern_type = "recurring_violation"
            suggested_action = (
                f"Review guideline '{rule_id}' with the editorial team and add concrete positive/negative examples."
            )
            current_text = rule.rule_text if rule else (fact.claim_statement if fact else "")
            proposed_clarification = f"{current_text} (Clarified: Ensure clear examples and boundaries are provided)."

        # Check if insight already exists for this rule
        existing_insight = db.query(GuidelineInsight).filter(GuidelineInsight.rule_id == rule_id).first()
        if existing_insight:
            existing_insight.occurrence_count = count
            existing_insight.supporting_finding_ids = finding_ids
            existing_insight.supporting_document_ids = document_ids
            existing_insight.evidence_summary = (
                f"Observed in {count} drafts across {len(document_ids)} documents. "
                f"Sample flagged text: {quotes_summary}."
            )
            existing_insight.updated_at = datetime.utcnow()
            insight_obj = existing_insight
        else:
            insight_obj = GuidelineInsight(
                title=title,
                rule_id=rule_id,
                suspected_root_cause=root_cause,
                pattern_type=pattern_type,
                occurrence_count=count,
                supporting_finding_ids=finding_ids,
                supporting_document_ids=document_ids,
                evidence_summary=(
                    f"Observed in {count} drafts across {len(document_ids)} documents. "
                    f"Sample flagged text: {quotes_summary}."
                ),
                suggested_action=suggested_action,
                hypothesis_status="hypothesis"
            )
            db.add(insight_obj)
            db.flush()

        # Check if a proposed clarification exists
        prop = db.query(ProposedGuidelineClarification).filter(
            ProposedGuidelineClarification.insight_id == insight_obj.id,
            ProposedGuidelineClarification.approval_status == "pending"
        ).first()

        if not prop and rule:
            prop = ProposedGuidelineClarification(
                insight_id=insight_obj.id,
                target_rule_id=rule.id,
                current_rule_version=rule.version,
                proposed_version=rule.version + 1,
                original_rule_text=rule.rule_text,
                proposed_rule_text=proposed_clarification,
                clarification_summary=(
                    f"Addresses ambiguity highlighted by {count} recurring findings. "
                    f"Adds explicit boundaries to prevent unverified promotional claims."
                ),
                approval_status="pending"
            )
            db.add(prop)

        insights.append(insight_obj)

    db.commit()
    return insights

def confirm_or_dismiss_hypothesis(
    db: Session,
    insight_id: str,
    action: str,  # confirm or dismiss
    notes: Optional[str],
    user_name: str,
    user_role: str
) -> GuidelineInsight:
    insight = db.query(GuidelineInsight).filter(GuidelineInsight.id == insight_id).first()
    if not insight:
        raise ValueError(f"Insight '{insight_id}' not found")

    new_status = "confirmed" if action.lower() == "confirm" else "dismissed"
    insight.hypothesis_status = new_status
    insight.decision_notes = notes
    insight.reviewed_by = user_name
    insight.reviewed_at = datetime.utcnow()

    log_audit_event(
        db=db,
        event_type="HYPOTHESIS_EVALUATED",
        actor_id=user_name,
        actor_name=user_name,
        actor_role=user_role,
        target_type="insight",
        target_id=insight.id,
        summary=f"Guideline Debugger hypothesis '{insight.id}' was {new_status} by {user_name} ({user_role})",
        details={"status": new_status, "notes": notes}
    )

    db.commit()
    db.refresh(insight)
    return insight

def approve_guideline_clarification(
    db: Session,
    proposal_id: str,
    brand_owner_name: str,
    edited_rule_text: Optional[str] = None,
    notes: Optional[str] = None
) -> Tuple[BrandGuideline, ProposedGuidelineClarification]:
    """
    Brand Owner explicitly approves a proposed guideline clarification.
    Increments the guideline version and records the change in audit history.
    Subsequent reviews will use the new version while historical reviews retain their version.
    """
    proposal = db.query(ProposedGuidelineClarification).filter(
        ProposedGuidelineClarification.id == proposal_id
    ).first()
    if not proposal:
        raise ValueError(f"Proposal '{proposal_id}' not found")

    rule = db.query(BrandGuideline).filter(BrandGuideline.id == proposal.target_rule_id).first()
    if not rule:
        raise ValueError(f"Target guideline '{proposal.target_rule_id}' not found")

    # Final text is either edited by Brand Owner or accepted as proposed
    final_text = edited_rule_text.strip() if (edited_rule_text and edited_rule_text.strip()) else proposal.proposed_rule_text

    old_version = rule.version
    new_version = old_version + 1

    # Update the active guideline
    rule.rule_text = final_text
    rule.version = new_version
    rule.clarification_notes = (
        f"Updated to v{new_version} via Guideline Debugger (Proposal {proposal.id}). "
        f"Approved by {brand_owner_name} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}. "
        f"Notes: {notes or 'No additional notes'}"
    )
    rule.updated_at = datetime.utcnow()

    # Update proposal record
    proposal.approval_status = "approved"
    proposal.reviewed_by = brand_owner_name
    proposal.reviewed_at = datetime.utcnow()
    proposal.reviewer_notes = notes

    # If linked to an insight, mark insight as confirmed
    if proposal.insight_id:
        insight = db.query(GuidelineInsight).filter(GuidelineInsight.id == proposal.insight_id).first()
        if insight:
            insight.hypothesis_status = "confirmed"
            insight.decision_notes = f"Clarification approved and published as version {new_version}."

    log_audit_event(
        db=db,
        event_type="CLARIFICATION_APPROVED",
        actor_id=brand_owner_name,
        actor_name=brand_owner_name,
        actor_role="brand_owner",
        target_type="rule",
        target_id=rule.id,
        summary=f"Brand Owner '{brand_owner_name}' approved clarification for '{rule.id}'. Version incremented from v{old_version} to v{new_version}.",
        details={
            "proposal_id": proposal.id,
            "old_version": old_version,
            "new_version": new_version,
            "new_rule_text": final_text
        }
    )

    db.commit()
    db.refresh(rule)
    db.refresh(proposal)
    return rule, proposal
