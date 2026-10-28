from sqlalchemy.orm import Session
from app.models.auth import User, Workspace, UserRole, OrganizationMembership
from app.models.brand import Brand, BrandGuideline, GuidelineVersion, ApprovedFact, ApprovedTerminology, BrandAsset
from app.models.evidence import BrandEvidence, BrandEvidenceVersion, EvidenceStatus, SourceType
from app.models.content import ContentDocument, DocumentVersion, DocumentStatus
from app.models.review import ReviewJob, Finding, ReviewComment, ApprovalRecord
from app.models.debugger import GuidelineInsight, ProposedGuidelineClarification
from app.models.audit import AuditEvent
from app.core.security import get_password_hash
from app.services.compliance_engine import run_compliance_check
from app.services.guideline_debugger import run_guideline_debugger_clustering
from datetime import datetime, timedelta

def seed_demo_data(db: Session) -> dict:
    """
    Seeds a realistic, production-oriented governance environment for Proofline.
    Includes Organization, Brand, Evidence Ledger records, Brand Guidelines with versioning,
    Brand Assets with cryptographic hashes, multi-role users, sample review jobs, and Clarity Radar signals.
    """
    # 1. Organization / Workspace
    workspace = db.query(Workspace).filter(Workspace.slug == "novusbio-health").first()
    if not workspace:
        workspace = Workspace(
            id="ws-novusbio-001",
            name="NovusBio Health Organization",
            slug="novusbio-health"
        )
        db.add(workspace)
        db.flush()

    # 2. Brand
    brand = db.query(Brand).filter(Brand.slug == "novusbio-health").first()
    if not brand:
        brand = Brand(
            id="brand-novusbio-01",
            workspace_id=workspace.id,
            name="NovusBio Health",
            slug="novusbio-health",
            description="Clinical-grade patient intelligence and automated triage platform",
            website="https://novusbio.health",
            supported_channels=["website", "social", "email", "press_release", "ads"],
            supported_markets=["Global", "US", "EU", "APAC"],
            content_types=["article", "landing_page", "social_post", "whitepaper", "ad_copy"],
            tone_guidelines={"formality": "authoritative", "voice": "precise, empathetic, evidence-based"},
            claim_restrictions=["no_unsubstantiated_guarantees", "require_clinical_reference", "pricing_currency_disclosure"],
            is_active=True
        )
        db.add(brand)
        db.flush()

    # 3. Users with explicit RBAC roles
    users_data = [
        ("user-creator-01", "creator@novusbio.com", "Alex Chen", UserRole.CREATOR.value),
        ("user-reviewer-01", "reviewer@novusbio.com", "Dr. Maya Patel", UserRole.REVIEWER.value),
        ("user-owner-01", "owner@novusbio.com", "Elena Rostova", UserRole.BRAND_OWNER.value),
    ]
    for uid, email, name, role in users_data:
        existing_u = db.query(User).filter(User.email == email).first()
        if not existing_u:
            user = User(
                id=uid,
                workspace_id=workspace.id,
                organization_id=workspace.id,
                email=email,
                full_name=name,
                role=role,
                hashed_password=get_password_hash("demo1234"),
                is_active=True
            )
            db.add(user)
            db.flush()

            # Membership
            m = OrganizationMembership(
                organization_id=workspace.id,
                user_id=user.id,
                role=role
            )
            db.add(m)
    db.flush()

    # 4. Brand Evidence Ledger (Signature Feature)
    evidence_data = [
        {
            "id": "EVID-PRICE-STARTER",
            "claim_title": "NovusBio Pro Tier Canonical Pricing",
            "approved_wording": "NovusBio Pro plan is $49 per user per month billed annually.",
            "structured_value": "$49/mo",
            "unit": "USD/user/month",
            "prohibited_old_values": ["$29/mo", "$39/mo", "$19/mo"],
            "category": "pricing",
            "description": "Standard commercial pricing schedule for institutional healthcare providers.",
            "applicable_context": "Sales collateral, public website pricing tables, RFP submissions.",
            "source_type": SourceType.DOCUMENT.value,
            "source_location": "NovusBio Master Commercial Schedule Q4-2026.pdf",
            "page_or_section": "Section 4.1 Pricing Table",
            "evidence_owner": "Elena Rostova (Commercial Director)",
            "status": EvidenceStatus.APPROVED.value,
            "approval_date": datetime.utcnow() - timedelta(days=60),
            "effective_date": "2026-09-01",
            "expiry_date": "2027-12-31",
            "applicable_product": "Clinical Copilot",
            "applicable_market": "Global",
            "applicable_channel": "website",
            "public_use_permission": True,
            "version": 1
        },
        {
            "id": "EVID-CLINICAL-TRIAGE",
            "claim_title": "Emergency Department Triage Delay Reduction",
            "approved_wording": "Demonstrated an 87% reduction in emergency triage intake delay across 12,000 multi-center patient encounters.",
            "structured_value": "87% triage reduction",
            "unit": "Percentage",
            "prohibited_old_values": ["100% cure rate", "instant triage cure"],
            "category": "clinical",
            "description": "Double-blind peer-reviewed cohort study on triage efficiency in metropolitan emergency departments.",
            "applicable_context": "Clinical whitepapers, press releases, medical conference abstracts.",
            "source_type": SourceType.DOCUMENT.value,
            "source_location": "New England Health Informatics Review 2026.pdf",
            "page_or_section": "Page 42, Table 3.2",
            "evidence_owner": "Dr. Maya Patel (Clinical Research Lead)",
            "status": EvidenceStatus.APPROVED.value,
            "approval_date": datetime.utcnow() - timedelta(days=90),
            "effective_date": "2026-01-15",
            "expiry_date": "2028-01-15",
            "applicable_product": "Clinical Copilot",
            "applicable_market": "US",
            "applicable_channel": "press_release",
            "public_use_permission": True,
            "version": 1
        },
        {
            "id": "EVID-SECURITY-SOC2",
            "claim_title": "SOC2 Type II & HIPAA Compliance Verification",
            "approved_wording": "NovusBio platform holds verified SOC2 Type II certification and conforms to HIPAA security standards.",
            "structured_value": "SOC2 Type II & HIPAA",
            "unit": "Security Standard",
            "prohibited_old_values": ["unhackable platform", "military-grade zero risk"],
            "category": "security",
            "description": "Third-party audit report by Coalfire Systems covering security, availability, and confidentiality.",
            "applicable_context": "Enterprise security reviews, landing pages, trust center.",
            "source_type": SourceType.DOCUMENT.value,
            "source_location": "Trust & Security Assurance Report 2026.pdf",
            "page_or_section": "Executive Summary, p.4",
            "evidence_owner": "David Vance (CISO)",
            "status": EvidenceStatus.APPROVED.value,
            "approval_date": datetime.utcnow() - timedelta(days=120),
            "effective_date": "2026-01-15",
            "expiry_date": "2027-01-15",
            "applicable_product": "All NovusBio Services",
            "applicable_market": "Global",
            "applicable_channel": "website",
            "public_use_permission": True,
            "version": 1
        },
        {
            "id": "EVID-PILOT-2025",
            "claim_title": "2025 Beta Cohort Satisfaction Score (Expired)",
            "approved_wording": "Initial beta cohort reported 94% physician satisfaction during the 2025 pilot phase.",
            "structured_value": "94% satisfaction",
            "unit": "Percentage",
            "prohibited_old_values": [],
            "category": "clinical",
            "description": "Early exploratory pilot study from 2025. Superseded by 2026 multi-center clinical trials.",
            "applicable_context": "Historical reference only.",
            "source_type": SourceType.INTERNAL_REFERENCE.value,
            "source_location": "Pilot Evaluation Q3-2025.pdf",
            "page_or_section": "Section 2",
            "evidence_owner": "Elena Rostova",
            "status": EvidenceStatus.EXPIRED.value,
            "approval_date": datetime.utcnow() - timedelta(days=400),
            "effective_date": "2025-01-01",
            "expiry_date": "2025-09-30",
            "applicable_product": "Clinical Copilot Beta",
            "applicable_market": "US",
            "applicable_channel": "internal",
            "public_use_permission": False,
            "version": 1
        }
    ]
    for ed in evidence_data:
        if not db.query(BrandEvidence).filter(BrandEvidence.id == ed["id"]).first():
            ev_rec = BrandEvidence(**ed, workspace_id=workspace.id, brand_id=brand.id)
            db.add(ev_rec)
            db.flush()
            # Initial version
            v_rec = BrandEvidenceVersion(
                evidence_id=ev_rec.id,
                version_number=1,
                approved_wording=ev_rec.approved_wording,
                structured_value=ev_rec.structured_value,
                status=ev_rec.status,
                changelog="Initial evidence seeding",
                author_id="user-owner-01"
            )
            db.add(v_rec)

    # 5. Approved Facts (Backward compatibility bridge)
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
            db.add(ApprovedFact(**fd, workspace_id=workspace.id, brand_id=brand.id))

    # 6. Approved Terminology
    terms_data = [
        {
            "id": "TERM-PRODUCT-01",
            "preferred_term": "NovusBio Clinical Copilot",
            "prohibited_variants": ["Novus App", "BioBot", "AI auto-doctor", "BrandRoot"],
            "rationale": "Maintains premium clinical SaaS stature; avoids dehumanizing or toy-like bot naming.",
            "context_guidance": "Always capitalize full product name on first reference in body copy."
        },
        {
            "id": "TERM-AUDIENCE-01",
            "preferred_term": "Attending Physicians & Nurse Practitioners",
            "prohibited_variants": ["healthcare workers", "medics", "users"],
            "rationale": "Respects the professional credentials of our clinical audience in enterprise messaging.",
            "context_guidance": "Use formal professional titles when describing primary users."
        }
    ]
    for td in terms_data:
        if not db.query(ApprovedTerminology).filter(ApprovedTerminology.id == td["id"]).first():
            db.add(ApprovedTerminology(**td, workspace_id=workspace.id, brand_id=brand.id, version=1, is_active=True))

    # 7. Brand Guidelines
    rules_data = [
        {
            "id": "RULE-CLAIM-01",
            "category": "promotional_claim",
            "title": "Substantiated Clinical Outcome Claims",
            "rule_text": "Do not state absolute guarantees of diagnosis or treatment outcomes. Phrases like 'guaranteed results', '100% cure', or 'zero risk' are strictly prohibited.",
            "rule_type": "prohibited_term",
            "severity": "critical",
            "owner_role": "brand_owner",
            "source_reference": "FDA Digital Health Policy & Brand Manual 2026 p.8",
            "page_reference": "Section 2.1",
            "effective_date": "2026-01-01",
            "version": 1,
            "is_active": True,
            "prohibited_patterns": ["guaranteed results", "guaranteed clinical success", "100% cure", "zero risk", "miracle cure"],
            "required_phrases": [],
            "clarification_notes": "Identified as ambiguous in Guideline Clarity Radar: writers repeatedly confused confident tone with absolute guarantee."
        },
        {
            "id": "RULE-DISCLAIMER-01",
            "category": "disclaimer",
            "title": "Mandatory Clinical Decision Support Disclosure",
            "rule_text": "All promotional materials, pricing sheets, and trial announcements must include the statutory clinical decision support disclosure.",
            "rule_type": "disclaimer",
            "severity": "high",
            "owner_role": "brand_owner",
            "source_reference": "Medical Governance Standard 2026, Section 9",
            "page_reference": "Section 9.4",
            "effective_date": "2026-01-01",
            "version": 1,
            "is_active": True,
            "prohibited_patterns": [],
            "required_phrases": ["NovusBio Clinical Copilot is an assistive decision-support tool and does not substitute for independent clinical judgment."],
            "clarification_notes": "Required in footer of all marketing materials."
        },
        {
            "id": "RULE-VOICE-01",
            "category": "voice",
            "title": "Authoritative & Evidence-Based Tone",
            "rule_text": "Maintain an authoritative, objective, and scientifically grounded tone. Avoid sensationalist clickbait, hype, or fear-based urgency marketing.",
            "rule_type": "tone",
            "severity": "warning",
            "owner_role": "brand_owner",
            "source_reference": "Brand Voice Handbook 2026 p.14",
            "page_reference": "Page 14",
            "effective_date": "2026-01-01",
            "version": 1,
            "is_active": True,
            "prohibited_patterns": ["revolutionary miracle", "doctors are shocked", "unbelievable secret"],
            "required_phrases": [],
            "clarification_notes": "Enforces scientific decorum."
        }
    ]
    for rd in rules_data:
        if not db.query(BrandGuideline).filter(BrandGuideline.id == rd["id"]).first():
            g_rec = BrandGuideline(**rd, workspace_id=workspace.id, brand_id=brand.id)
            db.add(g_rec)
            db.flush()
            # Initial version
            gv = GuidelineVersion(
                guideline_id=g_rec.id,
                version_number=1,
                title=g_rec.title,
                rule_text=g_rec.rule_text,
                severity=g_rec.severity,
                prohibited_patterns=g_rec.prohibited_patterns,
                required_phrases=g_rec.required_phrases,
                changelog="Initial guideline publication",
                author_id="user-owner-01"
            )
            db.add(gv)

    # 8. Brand Assets with Cryptographic Signatures
    assets_data = [
        {
            "id": "ASSET-LOGO-PRIMARY",
            "asset_type": "logo",
            "name": "NovusBio Primary Horizontal Logo",
            "value": "novusbio-primary.svg",
            "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "mime_type": "image/svg+xml",
            "width": 800,
            "height": 200,
            "min_width": 200,
            "min_height": 50,
            "alt_text_required": True,
            "usage_guideline": "Always display on dark navy (#0A0F1D) background with 24px padding."
        },
        {
            "id": "ASSET-COLOR-NAVY",
            "asset_type": "color",
            "name": "Proofline Deep Navy Foundation",
            "value": "#0A0F1D",
            "color_hex": "#0A0F1D",
            "alt_text_required": False,
            "usage_guideline": "Primary background color for all dark-mode digital interfaces."
        },
        {
            "id": "ASSET-COLOR-ELECTRIC",
            "asset_type": "color",
            "name": "Electric Cyan Brand Accent",
            "value": "#38BDF8",
            "color_hex": "#38BDF8",
            "alt_text_required": False,
            "usage_guideline": "Interactive highlights, primary CTAs, active indicators."
        }
    ]
    for ad in assets_data:
        if not db.query(BrandAsset).filter(BrandAsset.id == ad["id"]).first():
            db.add(BrandAsset(**ad, workspace_id=workspace.id, brand_id=brand.id, is_active=True))

    db.commit()

    # 9. Seed Demonstrative Content Documents & Historical Review Jobs
    demo_drafts = [
        {
            "id": "doc-demo-001",
            "title": "NovusBio Q4 Clinical Product Launch Announcement",
            "content_type": "press_release",
            "channel": "press_release",
            "market": "US",
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen",
            "raw_text": (
                "NovusBio is proud to announce the next generation of our BioBot platform, "
                "available today starting at just $29/mo per practitioner. "
                "Our breakthrough clinical system offers guaranteed results for emergency triage "
                "intake, eliminating diagnosis delay with revolutionary miracle accuracy."
            ),
            "status": DocumentStatus.SUBMITTED.value
        },
        {
            "id": "doc-demo-002",
            "title": "Hospital Network Case Study & ROI Brief",
            "content_type": "article",
            "channel": "website",
            "market": "Global",
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen",
            "raw_text": (
                "Memorial Health deployed the BioBot solution across 4 hospital branches. "
                "Our team achieved guaranteed success in outpatient scheduling while cutting institutional software fees to $29/mo. "
                "All patient records benefit from doctors are shocked level speed."
            ),
            "status": DocumentStatus.CHANGES_REQUESTED.value
        },
        {
            "id": "doc-demo-003",
            "title": "Clinical Efficiency Whitepaper Draft",
            "content_type": "whitepaper",
            "channel": "website",
            "market": "US",
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen",
            "raw_text": (
                "NovusBio Clinical Copilot delivers guaranteed outcome metrics in patient triage. "
                "Our protocol ensures zero risk transition for acute care units."
            ),
            "status": DocumentStatus.SUBMITTED.value
        },
        {
            "id": "doc-demo-004",
            "title": "Enterprise Security and Trust Whitepaper",
            "content_type": "whitepaper",
            "channel": "website",
            "market": "Global",
            "creator_id": "user-creator-01",
            "creator_name": "Alex Chen",
            "raw_text": (
                "The NovusBio Clinical Copilot is built for enterprise healthcare security. "
                "Demonstrated an 87% reduction in emergency triage intake delay across 12,000 multi-center patient encounters. "
                "NovusBio platform holds verified SOC2 Type II certification and conforms to HIPAA security standards. "
                "NovusBio Clinical Copilot is an assistive decision-support tool and does not substitute for independent clinical judgment."
            ),
            "status": DocumentStatus.APPROVED.value,
            "approved_version": 1
        }
    ]

    for d_data in demo_drafts:
        existing_doc = db.query(ContentDocument).filter(ContentDocument.id == d_data["id"]).first()
        if not existing_doc:
            doc = ContentDocument(
                id=d_data["id"],
                workspace_id=workspace.id,
                organization_id=workspace.id,
                brand_id=brand.id,
                title=d_data["title"],
                content_type=d_data["content_type"],
                channel=d_data["channel"],
                market=d_data["market"],
                raw_text=d_data["raw_text"],
                current_text=d_data["raw_text"],
                status=d_data["status"],
                creator_id=d_data["creator_id"],
                creator_name=d_data["creator_name"],
                assigned_reviewer_id="user-reviewer-01",
                assigned_reviewer_name="Dr. Maya Patel",
                current_version=1,
                approved_version=d_data.get("approved_version"),
                approved_at=datetime.utcnow() - timedelta(days=2) if d_data.get("approved_version") else None,
                approved_by_name="Dr. Maya Patel" if d_data.get("approved_version") else None
            )
            db.add(doc)
            db.flush()

            ver = DocumentVersion(
                document_id=doc.id,
                version_number=1,
                text_snapshot=doc.raw_text,
                changelog="Initial submitted draft",
                author_id=doc.creator_id,
                author_name=doc.creator_name
            )
            db.add(ver)
            db.commit()

            # Execute real compliance review to populate findings
            job = run_compliance_check(
                db=db,
                document=doc,
                user_id="user-creator-01",
                user_name="Alex Chen",
                user_role="creator"
            )

            if d_data["status"] == DocumentStatus.APPROVED.value:
                # Record approval record
                approval = ApprovalRecord(
                    document_id=doc.id,
                    document_version=1,
                    review_job_id=job.id,
                    status="approved",
                    approver_id="user-reviewer-01",
                    approver_name="Dr. Maya Patel",
                    approver_role="reviewer",
                    decision_reason="All factual claims verified against Brand Evidence Ledger. Approved for publication."
                )
                db.add(approval)
                db.commit()

    # 10. Run Guideline Clarity Radar clustering to populate insights
    run_guideline_debugger_clustering(db, brand_id=brand.id)

    return {"status": "success", "workspace_id": workspace.id, "brand_id": brand.id}
