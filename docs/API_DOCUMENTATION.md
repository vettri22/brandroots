# BrandRoots — REST API Documentation

**Base URL:** `/api/v1`

---

## 1. Authentication (`/auth`)

### `POST /auth/login`
Authenticates a user and returns a Bearer JWT.
- **Request Body:**
  ```json
  { "email": "creator@novusbio.com", "password": "demo1234" }
  ```
- **Response:**
  ```json
  { "access_token": "eyJhbG...", "token_type": "bearer", "user": { ... } }
  ```

### `POST /auth/switch-demo-role`
Switches active demo persona instantly for hackathon evaluation (`creator`, `reviewer`, `brand_owner`).

---

## 2. Content Review Workbench (`/documents` & `/reviews`)

### `POST /documents`
Creates a new draft from pasted canvas text.

### `POST /documents/upload`
Uploads a `.pdf`, `.docx`, or `.txt` file. Safely extracts text and checks for prompt injection.

### `POST /reviews/check/{document_id}`
Executes hybrid compliance review. Returns calculated compliance score (0-100) and structured findings.

### `PUT /reviews/findings/{finding_id}/resolve`
Resolves finding (`accepted`, `edited`, `dismissed`, `escalated`). When `accepted`, automatically applies suggested correction to the active draft and bumps document version.

### `POST /reviews/documents/{document_id}/transition`
Transitions content lifecycle (`draft` → `submitted` → `in_review` → `changes_requested` → `resubmitted` → `approved`).
*Enforces role policies: creators cannot self-approve.*

---

## 3. Guideline Debugger (`/debugger`) — Signature Feature

### `POST /debugger/cluster`
Scans stored findings across all documents. Identifies recurring patterns and generates draft guideline clarifications.

### `GET /debugger/insights`
Lists clustered ambiguity insights with suspected root cause, observed quotes, finding IDs, and hypothesis status.

### `POST /debugger/insights/{insight_id}/evaluate`
Confirms or dismisses a root cause hypothesis with reviewer notes.

### `GET /debugger/clarifications`
Retrieves draft guideline clarifications (`v1 -> v2`).

### `POST /debugger/clarifications/{proposal_id}/decide`
**Brand Owner only.** Approves (with optional custom edits) or rejects the proposed clarification. Upon approval, increments active guideline version and retains historical review snapshots.

---

## 4. Brand Knowledge (`/brand`)

- `GET /brand/guidelines`: Lists active guidelines.
- `PUT /brand/guidelines/{id}`: Substantive edit (increments version).
- `DELETE /brand/guidelines/{id}`: Soft deactivation (preserves historical review trace).
- `GET /brand/facts`: Lists verified facts and current commercial prices.
- `GET /brand/terminology`: Lists preferred terminology and prohibited variants.

---

## 5. Dashboard & Provenance (`/dashboard`)

- `GET /dashboard/metrics`: Aggregated counts of pending reviews, findings by severity, top recurring violations, and ambiguity candidates.
- `GET /dashboard/audit-logs`: Append-only governance log of every decision and state transition.
