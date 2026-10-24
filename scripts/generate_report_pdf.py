import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def build_pdf(filename="BrandRoots_Round2_Build_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()

    # Color definitions
    navy_dark = colors.HexColor("#0A1424")
    navy_surface = colors.HexColor("#0E1B31")
    charcoal_border = colors.HexColor("#1E355F")
    teal_accent = colors.HexColor("#0D9488")
    teal_light = colors.HexColor("#2DD4BF")
    text_white = colors.HexColor("#FFFFFF")
    text_light = colors.HexColor("#E2E8F0")
    text_muted = colors.HexColor("#94A3B8")
    rose_accent = colors.HexColor("#F43F5E")
    amber_accent = colors.HexColor("#F59E0B")

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=teal_accent,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=text_muted,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=teal_accent,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4,
        alignment=TA_LEFT
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#0F172A")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#FFFFFF")
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("BRANDROOTS - ROUND 2 BUILD REPORT", title_style))
    story.append(Paragraph(
        "<b>Inkloom AI Hackathon Round 2</b> | Team: <b>vettriselvam190</b> | Status: <b>Shipped & Verified Application</b>",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=teal_accent, spaceBefore=0, spaceAfter=12))

    # Executive Summary Box
    summary_text = (
        "<b>Executive Summary:</b> BrandRoots is an intelligent pre-publication brand-governance platform. "
        "Unlike conventional linters that merely flag isolated mistakes in individual drafts, BrandRoots introduces "
        "the <b>Guideline Debugger</b>: an engine that investigates whether repeated content mistakes are symptoms of vague, "
        "contradictory, or outdated brand instructions. In Round 2, the team moved beyond the proposal to deliver a "
        "working full-stack implementation with React 19, FastAPI, hybrid compliance checks, safe PyMuPDF/python-docx extraction, "
        "persistent rule versioning, and an immutable governance audit trail."
    )
    summary_table = Table([[Paragraph(summary_text, callout_style)]], colWidths=[532])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDFA")),
        ('BORDER', (0,0), (-1,-1), 1, teal_accent),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # Section 1: Problem & Target Users
    story.append(Paragraph("1. The Problem and Target Users", h1_style))
    story.append(Paragraph(
        "Modern organizations publish high-velocity content through dispersed employees, external agencies, freelancers, "
        "and generative AI tools. This causes messaging drift: outdated pricing tiers, unauthorized medical claims, "
        "deprecated terminology, and missing regulatory disclosures. When teams repeatedly make the same mistake, reviewers "
        "continually spend hours correcting symptoms rather than the root cause: an ambiguous or boundary-lacking guideline.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Target Users:</b><br/>"
        "&bull; <b>Content Creators:</b> Need rapid, explainable feedback before submission, with 1-click suggested corrections.<br/>"
        "&bull; <b>Compliance & Legal Reviewers:</b> Need traceable citations to approved policies with strict approval gates.<br/>"
        "&bull; <b>Brand Governance Owners:</b> Need a system that learns from review history, surfaces recurring rule ambiguities, and manages versioned guidelines.",
        body_style
    ))

    # Section 2: Actual Product Architecture
    story.append(Paragraph("2. Actual Product Architecture", h1_style))
    story.append(Paragraph(
        "BrandRoots is architected as a modular, three-tier cloud-ready system:<br/>"
        "&bull; <b>Frontend Layer:</b> Single Page Application built on React 19, TypeScript, and Tailwind CSS. Features role switching (Creator, Reviewer, Brand Owner), live canvas editing, split review workbench, and the signature Guideline Debugger interface.<br/>"
        "&bull; <b>Backend Layer:</b> High-performance Python 3.11 service using FastAPI and Pydantic v2. Provides REST endpoints for document ingestion, review execution, status transitions, and clustering.<br/>"
        "&bull; <b>Ingestion & Security Engine:</b> PyMuPDF (fitz) for PDF extraction and python-docx for DOCX files, equipped with size limits (10MB) and a prompt-injection regex guard that detects instruction-override attempts.<br/>"
        "&bull; <b>Data & Provenance Layer:</b> Relational database (SQLite local development default, PostgreSQL / Supabase cloud-ready) tracking 11 core tables with immutable version snapshots and append-only audit events.",
        body_style
    ))

    # Section 3: Features Implemented and Verified
    story.append(Paragraph("3. Features Implemented and Verified", h1_style))
    features_data = [
        [Paragraph("Feature Module", table_header), Paragraph("Implementation Details", table_header), Paragraph("Verification Status", table_header)],
        [
            Paragraph("Role-Based Access Control", table_cell),
            Paragraph("Creator, Reviewer, and Brand Owner roles enforced on backend. Policy prevents creators from approving their own work.", table_cell),
            Paragraph("VERIFIED (pytest + UI)", table_cell)
        ],
        [
            Paragraph("Hybrid Compliance Engine", table_cell),
            Paragraph("Combines deterministic matching (exact terms, pricing conflicts, required disclaimers) with contextual heuristic checks (guaranteed outcomes).", table_cell),
            Paragraph("VERIFIED (100% test pass)", table_cell)
        ],
        [
            Paragraph("Structured Explainability", table_cell),
            Paragraph("Every finding includes severity, plain-language explanation, source document citation, rule version, and suggested correction.", table_cell),
            Paragraph("VERIFIED (Schema validated)", table_cell)
        ],
        [
            Paragraph("Interactive Correction", table_cell),
            Paragraph("Creators can accept suggestions with 1-click in-place draft patching, triggering a new document version snapshot.", table_cell),
            Paragraph("VERIFIED (E2E & UI)", table_cell)
        ],
        [
            Paragraph("Content Lifecycle", table_cell),
            Paragraph("Full state machine: Draft -> Submitted -> In Review -> Changes Requested -> Resubmitted -> Approved / Rejected.", table_cell),
            Paragraph("VERIFIED (API & transitions)", table_cell)
        ],
        [
            Paragraph("Guideline Debugger", table_cell),
            Paragraph("Clusters recurring violations across drafts, isolates ambiguous rules, proposes draft clarifications, and supports Brand Owner approval.", table_cell),
            Paragraph("VERIFIED (Signature flow)", table_cell)
        ],
        [
            Paragraph("Document Ingestion", table_cell),
            Paragraph("Safe extraction of PDF and DOCX files with prompt injection detection and file size validation.", table_cell),
            Paragraph("VERIFIED (PyMuPDF + docx)", table_cell)
        ],
        [
            Paragraph("Immutable Audit Trail", table_cell),
            Paragraph("Append-only log recording all rule changes, approvals, comments, and finding resolutions.", table_cell),
            Paragraph("VERIFIED (DB & UI feed)", table_cell)
        ]
    ]
    f_table = Table(features_data, colWidths=[120, 292, 120])
    f_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy_dark),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(f_table)
    story.append(Spacer(1, 8))

    # Section 4: Explanation of the Guideline Debugger
    story.append(Paragraph("4. The Signature Feature: Guideline Debugger", h1_style))
    story.append(Paragraph(
        "The **Guideline Debugger** embodies BrandRoots' core thesis: <i>recurring mistakes are data</i>. "
        "Instead of treating repeated violations as creator incompetence, the debugger monitors review history to locate "
        "systemic ambiguities in the company's guidelines.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Debugger Workflow:</b><br/>"
        "1. <b>Aggregation:</b> The engine clusters stored review findings by rule ID across all documents.<br/>"
        "2. <b>Evidence Extraction:</b> When recurring violations are spotted (e.g., 5 drafts promising 'guaranteed results'), the debugger extracts exact quotes and calculates frequency.<br/>"
        "3. <b>Root Cause Hypothesis:</b> It analyzes why the guideline failed (e.g., <code>RULE-CLAIM-01</code> encouraged bold persuasion but lacked an explicit boundary regarding outcome guarantees).<br/>"
        "4. <b>Draft Proposal:</b> It generates a proposed clarification (e.g., <code>RULE-CLAIM-01 v1 -> v2</code>) adding an explicit boundary clause.<br/>"
        "5. <b>Human-in-the-Loop Approval:</b> An authorized Brand Owner explicitly reviews, edits, and approves the proposal. The active guideline version is incremented to v2, ensuring future reviews enforce the clarified rule while historical review snapshots remain intact.",
        body_style
    ))

    # Section 5: Technology & Implementation Details
    story.append(Paragraph("5. Technology and Implementation Details", h1_style))
    story.append(Paragraph(
        "&bull; <b>Backend Engine:</b> Built with FastAPI 0.115, Python 3.11, Pydantic 2.13, and SQLAlchemy 2.0. Clean architecture separating schemas, ORM models, routers, and domain services.<br/>"
        "&bull; <b>Compliance Engine (LLM & Heuristic):</b> Provider interface supports external LLM providers (OpenAI/Anthropic/Gemini) with structured outputs, paired with an offline, transparent <code>local_hybrid_deterministic</code> engine that delivers 100% reproducible checks without external key dependencies.<br/>"
        "&bull; <b>Frontend Architecture:</b> React 19 SPA bundled with Vite 6. Features deep navy surfaces (<code>#0A1424</code>), restrained teal accents (<code>#0D9488</code>), accessible contrast, responsive layout, and role-based views.<br/>"
        "&bull; <b>Security & Ingestion:</b> Byte-level file inspection via PyMuPDF and python-docx. Prompt injection guard neutralizes instruction hijacking markers.",
        body_style
    ))

    # Section 6: What Changed from Round 1 and Why
    story.append(Paragraph("6. What Changed from Round 1 and Why", h1_style))
    story.append(Paragraph(
        "In the Round 1 proposal, BrandRoots was conceptualized as a multi-format governance platform. For Round 2, the team made deliberate, principled adjustments:<br/>"
        "1. <b>Focused Scope on High-Value Text and Documents:</b> Following the build plan, text editor and PDF/DOCX review workflows were prioritized over multimodal image analysis to ensure the core Guideline Debugger and approval lifecycle were fully operational and rigorously tested.<br/>"
        "2. <b>Decoupled Local Engine:</b> To guarantee complete testability without external API fragility, an intelligent local hybrid engine was implemented. External integrations remain configurable via environment variables without faking connectivity.<br/>"
        "3. <b>Relational Data Integrity:</b> Rather than flat JSON blobs, an 11-table relational schema was implemented with foreign key constraints, versioned snapshots, and an append-only audit trail.",
        body_style
    ))

    # Section 7: Test Results and Measurable Findings
    story.append(Paragraph("7. Test Results and Measurable Findings", h1_style))
    test_data = [
        [Paragraph("Test Suite", table_header), Paragraph("Scope & Criteria", table_header), Paragraph("Executed Tests", table_header), Paragraph("Pass Rate", table_header)],
        [
            Paragraph("Backend Unit & Integration", table_cell),
            Paragraph("Auth RBAC, Guideline CRUD, Pricing checks, Lifecycle transitions, Version bumps, PyMuPDF/docx extraction, Debugger clustering", table_cell),
            Paragraph("19 pytest tests", table_cell),
            Paragraph("<b>100% (19/19 PASSED)</b>", table_cell)
        ],
        [
            Paragraph("Frontend Component Tests", table_cell),
            Paragraph("Badge rendering, FindingCard action dispatch, severity mapping", table_cell),
            Paragraph("2 vitest tests", table_cell),
            Paragraph("<b>100% (2/2 PASSED)</b>", table_cell)
        ],
        [
            Paragraph("End-to-End Demo Workflow", table_cell),
            Paragraph("Complete 9-step simulation: creation -> detection -> correction -> review -> clustering -> ambiguity confirmation -> v2 approval -> audit", table_cell),
            Paragraph("1 automated script (verify_e2e_demo.py)", table_cell),
            Paragraph("<b>100% (9/9 Steps PASSED)</b>", table_cell)
        ],
        [
            Paragraph("Frontend Production Build", table_cell),
            Paragraph("Vite production bundling and TypeScript static verification", table_cell),
            Paragraph("npm run build", table_cell),
            Paragraph("<b>0 errors (Built in 14.8s)</b>", table_cell)
        ]
    ]
    t_table = Table(test_data, colWidths=[120, 222, 100, 90])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy_dark),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 8))

    # Section 8: What Does Not Work Yet (Honest Limitations)
    story.append(Paragraph("8. What Does Not Work Yet (Known Limitations)", h1_style))
    story.append(Paragraph(
        "In adherence to hackathon integrity guidelines, current limitations are transparently documented:<br/>"
        "&bull; <b>Multimodal Image Review:</b> BrandRoots currently inspects textual content, PDFs, and DOCX files. Image logo positioning, color contrast in uploaded graphics, and visual alt-text audits are not yet supported.<br/>"
        "&bull; <b>External Cloud Auth / Public Hosting:</b> The current build runs on a fully functional local JWT session engine with seeded demo personas. Live deployment to public Vercel/Render instances requires cloud credentials and is ready for deployment following <code>docs/DEPLOYMENT.md</code>.<br/>"
        "&bull; <b>Automated Embedding Clustering:</b> Finding clustering currently groups by rule ID, category, and lexical patterns; semantic vector clustering using pgvector is reserved for Round 3.",
        body_style
    ))

    # Section 9: Verified Repository and URLs
    story.append(Paragraph("9. Verified Repository and Application URLs", h1_style))
    story.append(Paragraph(
        "&bull; <b>Local Application:</b> Frontend live at <code>http://localhost:5173</code> | Backend live at <code>http://localhost:8000</code><br/>"
        "&bull; <b>Source Code Workspace:</b> Clean repository prepared in <code>scratch/brandroots</code> with complete source code, tests, and documentation.<br/>"
        "&bull; <b>Deployment Status:</b> Pre-configured for Render (backend) and Vercel (frontend) via Supabase PostgreSQL. Deployment instructions documented in <code>docs/DEPLOYMENT.md</code>.",
        body_style
    ))

    # Section 10: Commitments for Round 3
    story.append(Paragraph("10. Commitments for Round 3", h1_style))
    story.append(Paragraph(
        "The team commits to three substantial improvements for Round 3:<br/>"
        "&bull; <b>Improvement 1 — Multimodal brand review:</b> Add reliable visual asset checks for uploaded campaign images, including logo placement, brand color consistency, and accessibility checks such as automated alt-text guidance.<br/>"
        "&bull; <b>Improvement 2 — Stronger evidence and claim verification:</b> Build a version-aware evidence retrieval and claim-verification pipeline that distinguishes verified, contradicted, expired, and unsupported claims, with source-level traceability.<br/>"
        "&bull; <b>Improvement 3 — Measurable governance intelligence:</b> Improve the Guideline Debugger with semantic clustering, reviewer feedback loops, ambiguity confirmation metrics, and empirical evaluation against a labelled test dataset.",
        body_style
    ))

    # Build the document
    doc.build(story)
    print(f"[OK] Report PDF successfully generated: {filename}")

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "BrandRoots_Round2_Build_Report.pdf"
    build_pdf(out_path)
