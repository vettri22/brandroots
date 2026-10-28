# Proofline — System Architecture & Technical Design

## 1. Executive Architecture Summary

Proofline is designed as a modular, multi-tenant enterprise brand governance platform. It orchestrates high-throughput content ingestion, deterministic rule validation, semantic evidence verification, and version-bound human approval workflows.

```
                              [ Content Authors & Reviewers ]
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     Proofline Web UI      │
                               │  (React 18 + TypeScript)  │
                               └─────────────┬─────────────┘
                                             │ REST API (Bearer JWT)
                                             ▼
                             ┌───────────────────────────────┐
                             │      FastAPI Gateway / API    │
                             │  (Lifespan, CORS, Rate Limit) │
                             └───────┬───────────────┬───────┘
                                     │               │
            ┌────────────────────────┘               └────────────────────────┐
            ▼                                                                 ▼
┌─────────────────────────┐                                       ┌─────────────────────────┐
│ Preflight Engine & LLM  │                                       │   Brand Evidence Ledger │
│  - Phrase / Regex Rules │                                       │   - Canonical Claims    │
│  - Prompt Sanitizer     │                                       │   - Conflict Detector   │
│  - PyMuPDF / docx Parse │                                       │   - Expiry Monitor      │
│  - Asset Contrast / SHA │                                       │   - Version History     │
└───────────┬─────────────┘                                       └───────────┬─────────────┘
            │                                                                 │
            └────────────────────────┬────────────────────────────────────────┘
                                     ▼
                       ┌───────────────────────────┐
                       │    SQLAlchemy 2.0 ORM     │
                       │    (Alembic Migrations)   │
                       └─────────────┬─────────────┘
                                     ▼
                       ┌───────────────────────────┐
                       │ SQLite (Dev) / PostgreSQL │
                       │    (Multi-Tenant Data)    │
                       └───────────────────────────┘
```

---

## 2. Core Subsystems

### A. Preflight Review Pipeline (`app/services/compliance_engine.py`)
1. **Extraction & Sanitization**: Document payloads (raw text, PDF, DOCX) pass through `guideline_ingestion.py` which strips zero-width non-printing characters, scans for adversarial prompt injection signatures (`System prompt override`, `Ignore all instructions`), and normalizes whitespace.
2. **Deterministic Evaluation**: Content is matched against active brand rules:
   - Prohibited terms and obsolete pricing schedules (`FACT-PRICE-PRO`).
   - Mandatory phrases and required regulatory disclaimers.
   - Tone and stylistic heuristics.
3. **Evidence Ledger Verification**: High-risk statements are compared against `BrandEvidence` records. Claims lacking approved ledger support or citing superseded/expired figures trigger critical findings.
4. **Contextual AI Augmentation**: If configured, `BaseLLMService` executes contextual analysis with strict JSON schema validation, timeout guards, and retry limits. If no API key is provided, the platform safely falls back to deterministic checks without fabricating AI results.
5. **Deduplication & Risk-Based Scoring**: Findings are consolidated, risk weights are aggregated, and compliance scores are calculated:
   $$\text{Score} = \max(0, 100 - \sum \text{Finding Penalties})$$

### B. Brand Evidence Ledger (`app/services/evidence_service.py`)
- **Immutability & Audit Trail**: Every change to an approved claim increments its version counter and writes a snapshot to `brand_evidence_versions`.
- **Temporal Validity**: Claims have explicit `effective_date` and `expiry_date` timestamps. The engine continuously detects claims that are expiring soon or currently expired.
- **Conflict Matrix**: When new evidence is created, the system checks existing active claims for contradictory numerical values or conflicting scopes across channels and markets.

### C. Guideline Clarity Radar (`app/services/guideline_debugger.py`)
- **Signal Aggregation**: Pulls from `SuggestionDecision` event tables where content creators reject suggested corrections with explanatory notes.
- **Hypothesis Clustering**: Groups violations by rule ID, calculates override rates, and identifies ambiguous rules.
- **Clarification Publication**: Generates `ProposedGuidelineClarification` drafts with explicit boundary improvements. Once approved by a Brand Administrator, active rule versions increment while historical documents retain their original review snapshot.

### D. Visual Asset & Accessibility Engine (`app/services/asset_checker.py`)
- **Cryptographic Hashing**: Computes SHA-256 digests of image assets and compares against registered brand assets.
- **Perceptual dHash Similarity**: Generates 64-bit difference hashes to detect altered or scaled versions of approved logos.
- **Luminance Contrast Calculation**: Converts RGB pixels to relative luminance according to WCAG 2.1 specifications:
  $$L = 0.2126 \cdot R + 0.7152 \cdot G + 0.0722 \cdot B$$
  Calculates contrast ratio $(L_1 + 0.05) / (L_2 + 0.05)$ and flags violations failing the 4.5:1 AA threshold.

---

## 3. Database Schema & Multi-Tenancy

Data isolation is guaranteed through workspace and organization identifiers:

| Model | Table Name | Purpose |
| :--- | :--- | :--- |
| `Organization` | `organizations` | Top-level tenant account |
| `User` | `users` | User credentials and global permissions |
| `OrganizationMembership` | `organization_memberships` | Role mapping per organization |
| `Brand` | `brands` | Brand workspace container |
| `BrandEvidence` | `brand_evidence` | Canonical claims and sources |
| `BrandEvidenceVersion` | `brand_evidence_versions` | Version history of evidence records |
| `BrandGuideline` | `brand_guidelines` | Active and historical brand rules |
| `BrandAsset` | `brand_assets` | Approved logos, palettes, and imagery |
| `ContentDocument` | `content_documents` | Draft documents with version tracking |
| `DocumentVersion` | `document_versions` | Immutable revision snapshots |
| `ReviewJob` | `review_jobs` | Review runs and compliance scores |
| `Finding` | `findings` | Identified violations and suggested corrections |
| `SuggestionDecision` | `suggestion_decisions` | Accepted/rejected finding decisions |
| `ApprovalRecord` | `approval_records` | Version-bound formal approvals |
| `GuidelineInsight` | `guideline_insights` | Clarity radar ambiguity signals |
| `ProposedGuidelineClarification` | `proposed_guideline_clarifications` | Draft guideline revisions |
| `AuditEvent` | `audit_events` | Immutable security and compliance log |

---

## 4. Version-Bound Approval Lifecycle

```
[Draft v1] ──(Submit)──> [Submitted v1] ──(Review)──> [In Review v1]
                                                             │
                  ┌──────────────────────────────────────────┴─────────────────┐
                  ▼                                                            ▼
          [Changes Requested]                                          [Approved at v1]
                  │                                                            │
         (Creator edits text)                                         (Any subsequent edit)
                  ▼                                                            ▼
            [Draft v2]  <───────────────────────────────────────────── [Approval Revoked]
```

1. Approvals are strictly bound to `document.current_version`.
2. Content creators cannot approve their own work (`creator_id != current_user.id`).
3. Any editorial edit to an approved document immediately revokes approval (`approved_version = None`), sets status to `draft`, and increments the version counter.
