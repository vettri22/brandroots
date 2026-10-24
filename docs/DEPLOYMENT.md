# BrandRoots — Deployment Guide

**Inkloom AI Hackathon Round 2 | Team:** `vettriselvam190`

This guide explains how to deploy BrandRoots to production using **Render** (Backend), **Vercel** (Frontend), and **Supabase** (PostgreSQL Database).

---

## 1. Prerequisites

- Python 3.11+
- Node.js 20+ & npm
- A Supabase account (free tier PostgreSQL)
- A Render account (FastAPI Web Service)
- A Vercel account (React SPA)

---

## 2. Database Setup (Supabase)

1. Create a new project in the Supabase Dashboard.
2. In **Project Settings** → **Database**, copy your **URI connection string**:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres
   ```
3. BrandRoots uses SQLAlchemy `Base.metadata.create_all()` which automatically provisions all 11 tables and indexes on first startup.
4. If you prefer to run manual SQL migrations, use the standard DDL script provided in `scripts/schema_postgresql.sql`.

---

## 3. Backend Deployment (Render)

1. Connect your GitHub repository to Render.
2. Create a new **Web Service**:
   - **Name**: `brandroots-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. In **Environment Variables**, set:
   - `ENVIRONMENT`: `production`
   - `DEMO_MODE`: `false` (or `true` if demonstrating with seeded data)
   - `DATABASE_URL`: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`
   - `SECRET_KEY`: `[GENERATE_A_RANDOM_64_CHAR_HEX]`
   - `LLM_PROVIDER`: `hybrid_deterministic` (or `openai` if API key configured)
4. Deploy service. Once live, test `https://brandroots-backend.onrender.com/health`.

---

## 4. Frontend Deployment (Vercel)

1. In Vercel, click **Add New Project** and select your BrandRoots repository.
2. Configure settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add Environment Variable:
   - `VITE_API_URL`: `https://brandroots-backend.onrender.com/api/v1`
4. Click **Deploy**. Vercel will build and serve the static bundle with globally edge-cached CDN routes.

---

## 5. Local Development Quickstart

To run the complete platform locally without cloud credentials:

### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
UI will be live at: `http://localhost:5173`
