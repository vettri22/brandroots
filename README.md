# Proofline — Enterprise Brand Governance & Preflight Intelligence Platform

Proofline is an enterprise full-stack brand governance platform that ensures every piece of published content strictly complies with approved corporate brand guidelines, uses authorized and current facts, respects terminology and visual standards, and passes rigorous version-bound human approval workflows.

Built from the ground up for high-compliance industries (health, biotechnology, finance, and enterprise SaaS), Proofline replaces decorative cards, static prototypes, and simulated SaaS with real deterministic validation, traceable evidence verification, and AI-assisted contextual analysis.

---

## Key Differentiators & Core Modules

### 1. Brand Evidence Ledger (Signature Feature)
- **Database-Backed Truth Source**: Traceable, expiry-aware records for approved claims, clinical facts, commercial pricing, source documents, ownership, and public-use permissions.
- **Automated Expiry & Conflict Detection**: Flags expired claims, conflicting figures, and prohibited superseded values (e.g., outdated pricing or unverified medical guarantees).
- **Interactive Claim Verification Engine**: Deterministically verifies claims against the active ledger and distinguishes between supported, contradicted, expired, and unverified claims.

### 2. Preflight Review Engine
- **Hybrid Analysis Pipeline**: Combines deterministic phrase, regex, and tone rules with semantic LLM contextual checks (via a provider-agnostic interface with explicit timeouts, fallbacks, and schema validation).
- **Prompt Injection Defense & Document Extraction**: Extracts and sanitizes content from PDF (`PyMuPDF`) and DOCX (`python-docx`) files, blocking adversarial prompt injection attempts.
- **Risk-Based Routing & Scoring**: Calculates weighted compliance scores (0–100) with severe penalties for unsupported claims or regulatory violations.

### 3. Correction Studio
- **Dedicated Split Canvas**: Interactive side-by-side editing canvas with live character counts and version baseline preservation.
- **Actionable Findings**: Each finding surfaces affected passages, rule IDs, source citations, severity, confidence scores, and canonical brand suggestions.
- **Suggestion Decision Event Sinks**: Accepts, edits, or dismisses suggestions with mandatory justification reasons that are permanently logged to audit tables and feed the Guideline Clarity Radar.
- **Visual Version Comparison**: Generates unified diff hunks (insertions, deletions, and context) comparing any two content revisions.

### 4. Guideline Clarity Radar (Signature Feature)
- **Root-Cause Telemetry**: Clusters recurring editor overrides, repeated rejections, and ambiguous violations across review history.
- **Investigation Lifecycle**: Manages clarification signals through explicit states (`under_investigation`, `needs_clarification`, `updated`, `resolved`, `not_an_issue`).
- **Clarification Publication Workflow**: Brand Administrators review proposed guideline revisions with side-by-side before/after boundaries and publish clarified rules, preserving historical document snapshots.

### 5. Version-Bound Formal Approvals
- **Strict Version Binding**: Approvals belong strictly to an exact immutable content version (e.g., `v2`).
- **Self-Approval Prevention**: Content creators are strictly prohibited from approving their own submitted drafts.
- **Edit Invalidation**: Editing an approved document automatically revokes approval, transitions the document back to `draft`, and increments the version counter.

### 6. Visual Brand Asset & Accessibility Validator
- **Cryptographic Fingerprinting**: Calculates SHA-256 hashes and perceptual dHash signatures for uploaded logos and photography.
- **WCAG Accessibility & Contrast**: Automatically computes luminance contrast ratios (enforcing WCAG AA 4.5:1 standards) and verifies mandatory alt-text policies.

### 7. Multi-Tenant Role-Based Access Control (RBAC)
- **Zero Frontend Trust**: Backend authorization matrix enforces granular permissions on every endpoint across 5 standard roles:
  - `org_owner`: Complete workspace control, invitations, and billing
  - `brand_admin`: Guideline management, asset registration, and ledger approval
  - `reviewer`: Queue management, change requests, and version-bound sign-offs
  - `creator`: Drafting, uploading, and revising content
  - `read_only`: Audit inspection and read-only telemetry

---

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2, Alembic Migrations, Pydantic v2, PyMuPDF, python-docx, Pillow, OpenCV (headless).
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Vitest.
- **Database**: SQLite (default local development) / PostgreSQL 15+ (production container).
- **Infrastructure**: Docker, Docker Compose, GitHub Actions CI.

---

## Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### 1. Clone & Configure Environment
```bash
git clone https://github.com/your-org/proofline.git
cd proofline
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
python -m pytest tests -v
uvicorn app.main:app --reload --port 8000
```
Backend API will be running at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm test -- --run
npm run build
npm run dev
```
Frontend will be running at `http://localhost:5173`.

---

## Running with Docker Compose

To run the entire full-stack platform with PostgreSQL:
```bash
docker-compose up --build
```
- Web Application: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

---

## Automated Test Verification

Proofline includes full test coverage for both backend services and frontend components.

- **Backend Pytest Suite** (25 automated integration tests):
  ```bash
  cd backend
  pytest tests -v
  ```
  Covers Evidence Ledger CRUD, claim verification, version-bound approval gating, SuggestionDecision rejection tracking, visual asset hash matching, contrast calculation, prompt injection sanitization, and lifecycle state machines.

- **Frontend Vitest Suite** (Unit & Integration tests):
  ```bash
  cd frontend
  npm test -- --run
  ```
  Covers FindingCard interactions, dismiss modals, and navigation workflows.

---

## Seed Data & Demonstrations

Proofline comes pre-seeded with enterprise demo data for **NovusBio Health** (`org-demo-001`):
- Approved guidelines for medical claims (`RULE-CLAIM-01`), commercial pricing (`FACT-PRICE-PRO`), and clinical terminology.
- 4 realistic content drafts (`doc-demo-001` through `doc-demo-004`) showcasing draft submissions, approval states, and recurring friction patterns for the Guideline Clarity Radar.
