# BrandRoots — System Architecture

**Inkloom AI Hackathon Round 2 | Team:** `vettriselvam190`

BrandRoots is an intelligent pre-publication brand-governance platform. Its signature contribution is the **Guideline Debugger**, which analyzes recurring mistakes across reviewed content drafts to discover whether the underlying brand guidelines are vague, contradictory, outdated, or lacking boundaries.

---

## 1. High-Level Architectural Diagram

```
                    ┌──────────────────────────────────────────────┐
                    │       BrandRoots React SPA (Frontend)       │
                    │   Vite + TypeScript + Tailwind CSS (Navy)   │
                    └──────────────────────┬───────────────────────┘
                                           │ REST API (Bearer JWT / Demo Roles)
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │            FastAPI Backend Engine            │
                    │       Python 3.11 + Pydantic v2 + Uvicorn    │
                    └──────┬───────────────┬────────────────┬──────┘
                           │               │                │
            ┌──────────────┴──────┐ ┌──────┴─────────┐ ┌────┴────────────────┐
            │ Document Ingestion  │ │ Hybrid Engine  │ │ Guideline Debugger  │
            │ PyMuPDF (PDF)       │ │ Deterministic  │ │ Recurring Clustering│
            │ python-docx (DOCX)  │ │ Fact Verifier  │ │ Root-Cause Discovery│
            │ Injection Guard     │ │ Context Heuristic│ │ Proposal Generator  │
            └─────────────────────┘ └────────────────┘ └─────────────────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────────────┐
                    │      Relational Storage & Provenance Layer   │
                    │   PostgreSQL / SQLite + SQLAlchemy 2.0 ORM   │
                    │   Immutable Audits, Jobs, Versions, Rules    │
                    └──────────────────────────────────────────────┘
```

---

## 2. Core Architectural Subsystems

### A. Role-Based Access Control (RBAC) & Workspace Isolation
- **Creator**: Submits drafts, uploads files, accepts or edits suggested corrections, resubmits revised work.
- **Reviewer**: Inspects drafts, leaves audit comments, requests revisions, approves/rejects content. *(Self-approval policy prevents creators from approving their own work).*
- **Brand Owner**: Manages canonical guidelines, verified facts, commercial pricing, and explicitly approves or rejects guideline clarifications produced by the Guideline Debugger.

### B. Hybrid Compliance Engine
- **Deterministic Pipeline**:
  - Matches exact prohibited terms and preferred terminology variants.
  - Detects stale/deprecated pricing (e.g., `$29/mo` vs canonical `$49/mo`).
  - Enforces mandatory regulatory disclaimers and effective dates.
- **Contextual & Semantic Layer**:
  - Catches absolute outcome guarantees (`"guaranteed results"`, `"100% cure"`, `"zero risk"`).
  - Flags unapproved clinical claims or hyperbole.
  - Transparently labels confidence as `deterministic_verified`, `rule_pattern_match`, or `contextual_heuristic`.
- **Structured Explainability**:
  - Each finding provides: Finding ID, Severity, Category, Plain Language Explanation ("Why it matters"), Stored Source Reference, Rule Version, and Suggested Correction.

### C. Guideline Debugger Subsystem (Signature Engine)
1. **Finding Aggregation**: Groups findings by `rule_id` and pattern type across all historical review jobs.
2. **Cluster Analysis**: When recurring findings exceed threshold (≥ 2 drafts), analyzes text quotes and reviewer feedback.
3. **Hypothesis Generation**: Distinguishes creator carelessness from guideline ambiguity (e.g. bold tone vs guaranteed outcome boundary).
4. **Draft Clarification Proposal**: Formulates proposed text (e.g. `v1 -> v2`) with an explicit boundary clause.
5. **Human Governance Approval**: Requires explicit Brand Owner approval. Once approved:
   - Guideline version is incremented.
   - Future reviews immediately test against `v2`.
   - Historical reviews permanently retain their version `v1` snapshot.

### D. Document Security & Prompt Injection Mitigation
- Max file upload size capped at 10 MB.
- PyMuPDF and python-docx operate in isolated byte streams.
- Text sanitization inspects incoming text for instruction-override patterns (`Ignore previous instructions`, `system: you are now...`) before passing into the evaluation pipeline.

---

## 3. Database Schema

- `workspaces`: Multi-tenant boundary.
- `users`: Identity, credentials, and role.
- `brand_guidelines`: ID, category, rule text, severity, version, active status, source reference.
- `approved_facts`: Canonical commercial claims, prices, unit, prohibited legacy values, validity dates.
- `approved_terminology`: Preferred term, prohibited variants, rationale.
- `content_documents`: Draft canvas, current version, lifecycle state, author.
- `document_versions`: Immutable snapshots of every saved revision.
- `review_jobs`: Compliance score, guideline version snapshot, findings summary.
- `findings`: Explainable issues, citations, and resolution status.
- `guideline_insights`: Recurring error clusters, root cause hypothesis.
- `proposed_guideline_clarifications`: Draft guideline revisions awaiting Brand Owner review.
- `audit_events`: Append-only governance log of every decision and state transition.
