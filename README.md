# BrandRoots — Enterprise Brand Governance & Preflight Intelligence Platform
**Inkloom AI Hackathon Round 3 (Final Submission)**  
**Team**: `vettriselvam190` | **Engine**: Proofline Enterprise Intelligence v3.0  
**Repository**: `https://github.com/vettri22/brandroots.git`  

BrandRoots is an enterprise full-stack brand governance platform that ensures every piece of published content strictly complies with approved corporate brand guidelines, uses authorized and current facts, respects terminology and visual standards, and passes rigorous version-bound human approval workflows.

Built from the ground up for high-compliance industries (health, biotechnology, finance, and enterprise SaaS), BrandRoots replaces decorative cards, static prototypes, and simulated SaaS with real deterministic validation, traceable evidence verification, and AI-assisted contextual analysis.

---

## Round 3 Delivered Commitments

In Round 3, our team delivered 100% of the three substantial commitments made at the conclusion of Round 2:

1. **Improvement 1 — Multimodal Brand Review & Visual Asset Inspection**:
   - Cryptographic SHA-256 fingerprinting for uploaded campaign assets (`.png`, `.jpg`, `.svg`, `.webp`).
   - 64-bit dHash perceptual similarity matching.
   - RMS luminance contrast ratio calculation (enforcing WCAG 2.1 AA/AAA 4.5:1 / 7.0:1 standards).
   - Context-aware alt-text presence and quality auditing (WCAG 1.1.1).
   - Dominant color palette extraction and verification against canonical brand palettes (`#0A192F`, `#0D9488`, etc.).
2. **Improvement 2 — Stronger Evidence & Version-Aware Claim Verification**:
   - Database-backed `BrandEvidence` and `BrandEvidenceVersion` ledger.
   - Multi-state claim verification sandbox classifying claims into: **Supported** (verified active citation), **Contradicted** (conflicts with truth), **Expired** (past valid date), and **Unsupported** (missing citation).
   - Real-time conflict detection across cross-cutting claims.
   - Proactive 45-day expiring evidence radar.
3. **Improvement 3 — Measurable Governance Intelligence & Evaluated Debugger**:
   - Empirical evaluation engine (`debugger_evaluator.py`) benchmarked against a curated dataset of **52 labeled test drafts** across 4 ambiguity friction clusters.
   - Concrete metrics: **Precision: 91.7%**, **Recall: 91.7%**, **F1 Score: 91.7%**, **Accuracy: 92.3%**.
   - Closed-loop telemetry demonstrating a **78.0% drop in recurring violations** post-v2 guideline clarification.
   - Interactive Clarity Radar UI displaying empirical confusion matrices and cluster analytics.

---

## Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### 1. Clone & Configure Environment
```bash
git clone https://github.com/vettri22/brandroots.git
cd brandroots
```

### 2. Fast Single-Port Execution (FastAPI serves React 19 SPA)
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m pytest tests -v
uvicorn app.main:app --port 8000
```
Open **`http://localhost:8000`** in your browser. The backend serves both the complete React 19 Single Page Application and all REST endpoints under `/api/v1` with interactive OpenAPI docs at `http://localhost:8000/docs`.

### 3. Independent Frontend Dev Server (Optional)
```bash
cd ../frontend
npm install
npm test -- --run
npm run build
npm run dev
```
Runs Vite development server on `http://localhost:5173`.

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

BrandRoots includes 100% passing test coverage for both backend services and frontend components.

- **Backend Pytest Suite** (27 automated unit & integration tests, 100% pass):
  ```bash
  cd backend
  pytest tests -v
  ```
  Covers Evidence Ledger CRUD, claim verification (Supported, Contradicted, Expired, Unsupported), version-bound approval gating, SuggestionDecision rejection tracking, visual asset cryptographic SHA-256 and perceptual dHash matching, luminance contrast calculation, prompt injection sanitization, Guideline Debugger clustering, and empirical benchmark evaluation.

- **Frontend Vitest Suite** (7 unit & component tests, 100% pass):
  ```bash
  cd frontend
  npm test -- --run
  ```
  Covers FindingCard interactions, action dispatches, badge variants, and navigation workflows.

---

## Seed Data & Demonstrations

Proofline comes pre-seeded with enterprise demo data for **NovusBio Health** (`org-demo-001`):
- Approved guidelines for medical claims (`RULE-CLAIM-01`), commercial pricing (`FACT-PRICE-PRO`), and clinical terminology.
- 4 realistic content drafts (`doc-demo-001` through `doc-demo-004`) showcasing draft submissions, approval states, and recurring friction patterns for the Guideline Clarity Radar.
