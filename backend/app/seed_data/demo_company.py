from sqlalchemy.orm import Session
from app.models.auth import User, Workspace, UserRole
from app.models.brand import BrandGuideline, ApprovedFact, ApprovedTerminology, BrandAsset
from app.models.content import ContentDocument, DocumentVersion, DocumentStatus
from app.models.review import ReviewJob, Finding, ReviewComment
from app.models.debugger import GuidelineInsight, ProposedGuidelineClarification
from app.models.audit import AuditEvent
from app.core.security import get_password_hash
from app.services.compliance_engine import run_compliance_check
from app.services.guideline_debugger import run_guideline_debugger_clustering
from datetime import datetime

def seed_demo_data(db: Session) -> dict:
    """
    Seeds a comprehensive, realistic brand governance environment for 'NovusBio Health'.
    Includes approved facts, active rules, multiple historical drafts with recurring issues,
    pre-computed review findings, and Guideline Debugger insights.
    """
    # 1. Workspace
    workspace = db.query(Workspace).filter(Workspace.slug == "novusbio-health").first()
    if not workspace:
        workspace = Workspace(
            id="ws-novusbio-001",
            name="NovusBio Health (Hackathon Demo)",
            slug="novusbio-health"
        )
        db.add(workspace)
        db.flush()

    # 2. Users with explicit roles
    users_data = [
        ("user-creator-01", "creator@novusbio.com", "Alex Chen (Content Creator)", UserRole.CREATOR.value),
        ("user-reviewer-01", "reviewer@novusbio.com", "Dr. Maya Patel (Compliance Reviewer)", UserRole.REVIEWER.value),
        ("user-owner-01", "owner@novusbio.com", "Elena Rostova (Brand Governance Owner)", UserRole.BRAND_OWNER.value),
    ]
    for uid, email, name, role in users_data:
        if not db.query(User).filter(User.email == email).first():
            user = User(
                id=uid,
                workspace_id=workspace.id,
                email=email,
                full_name=name,
                role=role,
                hashed_password=get_password_hash("demo1234")
            )
            db.add(user)
    db.flush()

    # 3. Approved Facts
    facts_data = [
        {
            "id": "FACT-PRICE-PRO",
            "category": "pricing",
            "claim_statement": "NovusBio Pro plan is $49 per user per month billed annually.",
            "canonical_value": "$49/mo",
            "unit": "USD/user/month",
            "prohibited_old_values": ["$29/mo", "$39/mo", "$19/mo"],
            "source_document": "NovusBio Master Commercial Schedule Q4-2026",
            "effective_date": "2026-09-01",
            "expiry_date": "2027-12-31",
            "version": 1,
            "is_active": True
        },
        {
            "id": "FACT-HIPAA-CERT",
            "category": "compliance_cert",
            "claim_statement": "NovusBio platform holds SOC2 Type II and HIPAA conformity certificates.",
            "canonical_value": "SOC2 Type II & HIPAA Certified",
            "unit": "Certificate",
            "prohibited_old_values": ["HIPAA certified doctor replacement"],
            "source_document": "Trust & Security Assurance Report 2026",
            "effective_date": "2026-01-15",
            "version": 1,
            "is_active": True
        },
        {
            "id": "FACT-LATENCY-SLA",
            "category": "performance_sla",
            "claim_statement": "Average clinical triage response latency is under 250 milliseconds with 99.95% uptime SLA.",
            "canonical_value": "<250ms latency / 99.95% SLA",
            "unit": "Milliseconds",
            "prohibited_old_values": ["instantaneous diagnosis"],
            "source_document": "Engineering SLA Spec v3.1",
            "effective_date": "2026-03-01",
            "version": 1,
            "is_active": True
        }
    ]
    for fd in facts_data:
        if not db.query(ApprovedFact).filter(ApprovedFact.id == fd["id"]).first():
            db.add(ApprovedFact(**fd, workspace_id=workspace.id))

    # 4. Approved Terminology
    terms_data = [
        {
            "id": "TERM-PRODUCT-01",
            "preferred_term": "NovusBio Clinical Copilot",
            "prohibited_variants": ["Novus App", "BioBot", "AI auto-doctor", "BrandRoot"],
            "rationale": "Maintains premium clinical SaaS stature; avoids dehumanizing or toy-like bot naming.",
            "context_guidance": "Always capitalize full product name on first reference in body copy.",
            "version": 1,
            "is_active": True
        },
        {
            "id": "TERM-CARE-01",
            "preferred_term": "clinician-supervised AI assistance",
            "prohibited_variants": ["autonomous diagnosis", "automated physician replacement", "doctor replacement"],
            "rationale": "Legal and regulatory compliance requirement. NovusBio is clinical decision support, not an unassisted replacement.",
            "context_guidance": "Use when explaining diagnostic acceleration workflows.",
            "version": 1,
            "is_active": True
        }
    ]
    for td in terms_data:
        if not db.query(ApprovedTerminology).filter(ApprovedTerminology.id == td["id"]).first():
            db.add(ApprovedTerminology(**td, workspace_id=workspace.id))

    # 5. Brand Guidelines
    guidelines_data = [
        {
            "id": "RULE-CLAIM-01",
            "category": "promotional_claim",
            "title": "Promotional Claim Boundaries & Outcome Guarantees",
            "rule_text": "Be confident and persuasive in marketing materials. Emphasize validated efficiency and clinical adoption without making unsupported absolute outcome claims or risk-free assertions.",
            "severity": "critical",
            "owner_role": "brand_owner",
            "source_reference": "NovusBio Brand Playbook 2026, Section 4.2",
            "effective_date": "2026-01-01",
            "version": 1,
            "is_active": True,
            "prohibited_patterns": ["guaranteed results", "100% cure", "foolproof outcome", "zero risk", "miracle cure", "guaranteed success"],
            "required_phrases": [],
            "clarification_notes": "Initial launch version. Targeted for clarification by Guideline Debugger."
        },
        {
            "id": "RULE-VOICE-01",
            "category": "voice",
            "title": "Empathetic, Rigorous & Clinically Responsible Voice",
            "rule_text": "Communications must reflect clinical rigor, professional empathy, and calm authority. Avoid sensationalism, hyperbole, or fear-based urgency.",
            "severity": "warning",
            "owner_role": "brand_owner",
            "source_reference": "Voice & Tone Stylebook 2026, p.8",
            "effective_date": "2026-01-01",
            "version": 1,
            "is_active": True,
            "prohibited_patterns": ["game changer", "revolutionary miracle", "act before it's too late", "magic solution"],
            "required_phrases": [],
            "clarification_notes": None
        },
        {
            "id": "RULE-DISCLAIMER-01",
            "category": "disclaimer",
            "title": "Mandatory Clinical Triage Regulatory Disclaimer",
            "rule_text": "All promotional overviews discussing clinical outcomes must include the approved investigational disclaimer in the footer.",
            "severity": "high",
            "owner_role": "brand_owner",
            "source_reference": "Regulatory Notice R-2026-B",
            "effective_date": "2026-02-15",
            "version": 1,
            "is_active": True,
            "prohibited_patterns": [],
            "required_phrases": ["For investigational use with clinician oversight. Not intended as an autonomous diagnostic substitute."],
            "clarification_notes": None
        }
    ]
    for gd in guidelines_data:
        if not db.query(BrandGuideline).filter(BrandGuideline.id == gd["id"]).first():
            db.add(BrandGuideline(**gd, workspace_id=workspace.id))

    # 6. Brand Assets
    assets_data = [
        {"id": "ASSET-COLOR-NAVY", "asset_type": "color", "name": "Deep Medical Navy", "value": "#0A192F", "usage_guideline": "Primary background and brand banner color"},
        {"id": "ASSET-COLOR-TEAL", "asset_type": "color", "name": "Clinical Cyan", "value": "#0D9488", "usage_guideline": "Accent buttons, highlights, and verified badges"},
        {"id": "ASSET-TYPO-PRIMARY", "asset_type": "typography", "name": "Inter & JetBrains Mono", "value": "Inter, sans-serif", "usage_guideline": "Body and heading typography"}
    ]
    for ad in assets_data:
        if not db.query(BrandAsset).filter(BrandAsset.id == ad["id"]).first():
            db.add(BrandAsset(**ad, workspace_id=workspace.id))

    db.commit()

    # 7. Sample Drafts (Demonstrating recurring errors for Guideline Debugger)
    sample_drafts = [
        {
            "id": "doc-demo-001",
            "title": "Q4 Commercial Sales Deck - Hero Pitch",
            "content_type": "text",
            "raw_text": (
                "Transform your hospital emergency department with NovusBio Clinical Copilot. "
                "Our revolutionary platform offers guaranteed results for diagnostic intake acceleration. "
                "The starter plan is available now for just $29/mo per practitioner. "
                "Say goodbye to waitlists with our BioBot assistant today!"
            ),
            "status": DocumentStatus.DRAFT.value,
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen (Content Creator)"
        },
        {
            "id": "doc-demo-002",
            "title": "Outreach Email - Clinical Decision Support",
            "content_type": "text",
            "raw_text": (
                "Dear Chief Medical Officer, discover how NovusBio Clinical Copilot delivers guaranteed results "
                "in patient triage. Pricing starts at only $29/mo with zero risk on our 30-day pilot."
            ),
            "status": DocumentStatus.SUBMITTED.value,
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen (Content Creator)"
        },
        {
            "id": "doc-demo-003",
            "title": "Press Release Draft - Hospital Partnership",
            "content_type": "text",
            "raw_text": (
                "Metropolitan Health Partners today deployed NovusBio Clinical Copilot across 12 facilities, "
                "offering clinicians guaranteed results and foolproof outcome acceleration for emergency intake."
            ),
            "status": DocumentStatus.IN_REVIEW.value,
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen (Content Creator)"
        },
        {
            "id": "doc-demo-004",
            "title": "LinkedIn Sponsored Carousel Post",
            "content_type": "text",
            "raw_text": (
                "Are emergency room bottlenecks slowing down patient care? Experience guaranteed results "
                "and clinician-supervised AI assistance. Plans start at $29/mo."
            ),
            "status": DocumentStatus.SUBMITTED.value,
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen (Content Creator)"
        },
        {
            "id": "doc-demo-005",
            "title": "Annual Healthcare Leadership Conference Abstract",
            "content_type": "text",
            "raw_text": (
                "Session Abstract: Implementing AI in Regional Trauma Centers. "
                "Learn how NovusBio guarantees results across 50,000 emergency admissions."
            ),
            "status": DocumentStatus.CHANGES_REQUESTED.value,
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen (Content Creator)"
        }
    ]

    for sd in sample_drafts:
        existing_doc = db.query(ContentDocument).filter(ContentDocument.id == sd["id"]).first()
        if not existing_doc:
            doc = ContentDocument(
                id=sd["id"],
                workspace_id=workspace.id,
                title=sd["title"],
                content_type=sd["content_type"],
                raw_text=sd["raw_text"],
                current_text=sd["raw_text"],
                status=sd["status"],
                creator_id=sd["creator_id"],
                creator_name=sd["creator_name"],
                current_version=1
            )
            db.add(doc)
            db.flush()

            ver = DocumentVersion(
                document_id=doc.id,
                version_number=1,
                text_snapshot=doc.raw_text,
                changelog="Initial seeded demonstration draft",
                author_id=sd["creator_id"]
            )
            db.add(ver)

            # Run compliance check on each seeded draft to generate real findings
            run_compliance_check(
                db=db,
                document=doc,
                user_id=sd["creator_id"],
                user_name=sd["creator_name"],
                user_role="creator"
            )

    db.commit()

    # Run Guideline Debugger Clustering across all seeded drafts!
    run_guideline_debugger_clustering(db)

    # Initial Audit Trail Entry
    db.add(AuditEvent(
        workspace_id=workspace.id,
        event_type="DEMO_DATA_INITIALIZED",
        actor_id="system",
        actor_name="Demo Seed Orchestrator",
        actor_role="system",
        target_type="workspace",
        target_id=workspace.id,
        summary="Initialized NovusBio Health demonstration workspace with approved facts, guidelines, and 5 sample drafts.",
        details={"version": "2.0.0", "team": "vettriselvam190"}
    ))
    db.commit()

    return {"status": "success", "message": "Demo company data seeded successfully"}
