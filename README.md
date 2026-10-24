# BrandRoots — Intelligent Brand Governance & Guideline Debugger

**Inkloom AI Hackathon Round 2 Build Report & Complete Source Code**  
**Team Name:** `vettriselvam190`  
**Target Organization:** Growing organizations publishing content through employees, agencies, freelancers, and AI tools.

---

## 🚀 Overview

BrandRoots is a pre-publication brand-governance workbench. While traditional checkers only identify localized errors in isolated drafts, BrandRoots introduces the **Guideline Debugger**: an intelligent engine that investigates whether repeated content mistakes are symptoms of vague, contradictory, missing, or outdated brand guidelines.

### The Defining Loop:
1. **Detect**: Identifies outdated facts (`$29/mo` instead of canonical `$49/mo`), prohibited terminology (`BioBot`), and unsupported outcome guarantees (`guaranteed results`) with explicit source document citations.
2. **Correct**: Content creators accept suggested corrections with 1-click in-place draft patching and version tracking.
3. **Debug**: When multiple drafts repeatedly make the same mistake, the **Guideline Debugger** clusters the findings, surfaces the evidence, isolates the ambiguous rule, and generates a draft clarification (e.g., `v1 -> v2`).
4. **Govern**: An authorized **Brand Owner** explicitly reviews and approves the clarification. Future drafts are checked against `v2` while past review records retain `v1` for historical traceability.

---

## 🛠️ Technology Stack

- **Frontend**: React 19, TypeScript, Tailwind CSS, Vite, Lucide React.
- **Backend**: Python 3.11, FastAPI, Pydantic v2, Uvicorn.
- **Database & Auth**: PostgreSQL / SQLite with SQLAlchemy 2.0 ORM, JWT Bearer authentication, and role-based access control.
- **Document Processing**: PyMuPDF (`fitz`) for PDF text parsing and `python-docx` for Word DOCX extraction, backed by prompt injection defense.
- **Compliance Engine**: Hybrid deterministic rule verifier + contextual claim heuristic evaluator (`local_hybrid_deterministic`).
- **Testing**: `pytest` (19 automated tests) and `vitest` (frontend component test suite).

---

## 🏃 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

### 3. Run Automated Tests
```bash
# Backend pytest suite (19 tests)
cd backend
pytest -v

# Frontend vitest suite
cd frontend
npm test
```

### 4. Run End-to-End Demo Verification Script
```bash
python scripts/verify_e2e_demo.py
```

---

## 👥 Personas & Pre-Seeded Demonstration

The application comes pre-seeded with a fictional brand (**NovusBio Health**) and three distinct roles that can be switched instantly via the top navigation bar:

1. **Creator** (`Alex Chen`): Submits drafts, inspects explainable findings, and applies brand corrections.
2. **Reviewer** (`Dr. Maya Patel`): Inspects content, comments, requests revisions, and approves/rejects content. *(Self-approval policy prevents creators from approving their own work).*
3. **Brand Owner** (`Elena Rostova`): Manages brand guidelines, canonical pricing, verified facts, and approves Guideline Debugger clarifications.

---

## 📂 Repository Structure

```
brandroots/
├── backend/
│   ├── app/
│   │   ├── config.py             # Settings and environment configuration
│   │   ├── database.py           # SQLAlchemy database session and Base
│   │   ├── main.py               # FastAPI entrypoint and startup seeder
│   │   ├── core/                 # Auth, JWT, and role-based permissions
│   │   ├── models/               # SQLAlchemy relational data models (11 tables)
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   ├── services/             # Document parser, compliance engine, debugger, audit
│   │   ├── routers/              # REST API endpoints
│   │   └── seed_data/            # NovusBio Health demonstration seed data
│   ├── tests/                    # 19 automated pytest unit and integration tests
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── components/           # UI components (RoleSwitcher, FindingCard, Badge, Layout)
│   │   ├── pages/                # Governance Hub, Workbench, Debugger, Brand Knowledge, Audit
│   │   ├── context/              # AuthContext for role switching
│   │   ├── services/api.ts       # Typed REST API client
│   │   └── types/                # TypeScript interface definitions
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docs/                         # Architecture, Deployment, and API documentation
├── scripts/                      # E2E demo verification script and PDF generator
├── BrandRoots_Round2_Build_Report.pdf
├── .env.example
└── README.md
```

---

## 🔮 Commitments for Round 3

1. **Multimodal brand review**: Visual asset checks for uploaded campaign images, logo placement, color contrast, and automated image alt-text guidance.
2. **Stronger evidence and claim verification**: Version-aware semantic retrieval pipeline that distinguishes verified, contradicted, expired, and unsupported claims with source-level traceability.
3. **Measurable governance intelligence**: Guideline Debugger clustering evaluation against a labeled ground-truth dataset with precision/recall benchmarks on ambiguity detection.
