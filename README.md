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

## Production Free Cloud Deployment Guide

BrandRoots is architected to run **100% free** without requiring any paid infrastructure or external database provisioning:
- **Backend on Render (Free Tier)**: Runs FastAPI with an embedded SQLite database (`sqlite:///./brandroots.db`) pre-seeded with NovusBio Health enterprise data. Includes an active anti-sleep ping loop so the free tier **never goes to sleep**.
- **Frontend on Vercel (Free Tier)**: Runs the Vite React 18 production build with client-side SPA routing (`vercel.json`) and connects seamlessly to Render via CORS.

---

### Method A: Deploy Full Platform on Render (Fastest & 1-Click Free)

Render can build and host both the FastAPI backend and React frontend together as a single unified service:

1. Push your repository to GitHub.
2. Sign in to [Render.com](https://render.com) (free account).
3. Click **New +** -> **Web Service** -> Select your `brandroots` repository.
4. Render will automatically detect `render.yaml`. If setting manually:
   - **Environment**: `Python 3`
   - **Build Command**: `cd frontend && npm install && npm run build && cd ../backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. In **Environment Variables**, add:
   - `ENVIRONMENT` = `production`
   - `DEMO_MODE` = `true`
   - `SECRET_KEY` = `generate-any-32-char-random-string`
   - `LLM_PROVIDER` = `hybrid_deterministic`
   - `DATABASE_URL` = `sqlite:///./brandroots.db`
   - `RENDER_EXTERNAL_URL` = `https://<your-render-service-name>.onrender.com` *(enables built-in anti-sleep pinger)*
6. Click **Create Web Service**. Within 3 minutes, your live URL is active!

---

### Method B: Deploy Backend on Render + Frontend on Vercel (Separated Free Tier)

If you prefer hosting the React frontend separately on Vercel:

#### 1. Backend on Render:
- Follow Step A above, with **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set `RENDER_EXTERNAL_URL` = `https://<your-backend-name>.onrender.com`
- Note your live Render backend URL (e.g. `https://brandroots-api.onrender.com`).

#### 2. Frontend on Vercel:
1. Sign in to [Vercel.com](https://vercel.com) (free account).
2. Click **Add New...** -> **Project** -> Select your `brandroots` GitHub repository.
3. In the project settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Expand **Environment Variables** and add:
   - `VITE_API_URL` = `https://<your-backend-name>.onrender.com/api/v1`
5. Click **Deploy**. Vercel will build and assign an instant live URL (`https://<your-app>.vercel.app`).

---

### Anti-Sleep Configuration (Render Free Tier Never Spins Down)

Render's free tier idles after 15 minutes of inactivity. BrandRoots includes two redundant zero-cost mechanisms to keep it awake 24/7:
1. **Built-in Automatic Self-Ping**: Setting `RENDER_EXTERNAL_URL` triggers an internal async background loop in `backend/app/main.py` that pings `/health` every 10 minutes.
2. **GitHub Actions Workflow**: A ready-to-use cron workflow is included in `.github/workflows/keepalive.yml`. Simply add your live URL to repository secrets as `RENDER_APP_URL` to send an external ping every 10 minutes.

---

## 5-Minute Judge Evaluation Walkthrough

Follow this self-guided script to evaluate all features and verify the three committed Round 3 improvements:

1. **Dashboard & Demo Environment (`/`)**:
   - Notice the system status indicator: Preflight Review Engine, Brand Evidence Ledger, Correction Studio, and Clarity Radar are all **Active**.
   - Switch active user roles dynamically in the navigation header (**Brand Owner**, **Reviewer**, **Content Creator**) to verify strict role-based access control (RBAC).

2. **Brand Evidence Ledger (`/evidence`) [Delivered Commitment #2]**:
   - Explore the active ledger for **NovusBio Health** with audit IDs, sources, owners, and expiration dates.
   - Click **Claim Verification Sandbox** to test claim classification:
     - Input supported claim: `NovusBio Pro plan is $49/mo` -> Validates as **Supported** with citation.
     - Input contradictory claim: `NovusBio Pro plan costs $29/mo` -> Validates as **Contradicted** with evidence diff.
     - Input expired claim: `Clinical diagnostic accuracy is 99.4%` -> Flags as **Expired**.
     - Input unbacked claim: `Guaranteed cure for all viral strains` -> Flags as **Unsupported**.
   - Review the **Conflict Detection Matrix** and **Expiring Soon Radar**.

3. **Preflight Review Workbench (`/reviews`)**:
   - Open draft `doc-demo-001` (*"NovusBio Q4 Promotional Launch Copy"*).
   - Click **Run Preflight Review Engine**:
     - Deterministic and rule-based pipelines inspect terminology, claims, and disclaimers.
     - Real-time compliance score calculated with weighted deduction breakdown.

4. **Correction Studio & Version-Bound Approvals (`/reviews`)**:
   - Inspect individual findings with rule explanations and suggested fixes.
   - Click **Accept Fix** or **Reject Fix** with reviewer rationale.
   - Observe **Version-Bound Approvals**: Editing the text immediately increments the document version and invalidates existing approvals, requiring a fresh preflight review.

5. **Visual Asset Inspector (`/assets`) [Delivered Commitment #1]**:
   - View registered brand assets with cryptographic SHA-256 fingerprints.
   - Test image compliance verification: perceptual dHash matching, luminance contrast ratio (WCAG 2.1 AA 4.5:1 threshold), and mandatory alt-text auditing.

6. **Guideline Clarity Radar (`/radar`) [Delivered Commitment #3]**:
   - Inspect recurring friction clusters and reviewer override patterns.
   - View the **Empirical Benchmark Evaluation**: 52 labeled test drafts demonstrating **91.7% Precision/Recall/F1** and a **78.0% drop in guideline violations** after adopting v2 clarifications.
   - Review proposed guideline clarifications with before/after diffs and one-click owner approval.

---

## Seed Data & Demonstrations

Proofline comes pre-seeded with enterprise demo data for **NovusBio Health** (`org-demo-001`):
- Approved guidelines for medical claims (`RULE-CLAIM-01`), commercial pricing (`FACT-PRICE-PRO`), and clinical terminology.
- 4 realistic content drafts (`doc-demo-001` through `doc-demo-004`) showcasing draft submissions, approval states, and recurring friction patterns for the Guideline Clarity Radar.
