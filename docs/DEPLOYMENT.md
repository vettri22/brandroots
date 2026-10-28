# Proofline — Enterprise Deployment Guide

This guide details multiple deployment strategies for Proofline, ranging from single-command Docker deployment on cloud VPS instances to modern serverless/managed infrastructure (PostgreSQL, Render/Railway, and Vercel/Netlify).

---

## Architecture Overview

Proofline consists of three core components:
1. **Frontend**: React 18 SPA built with Vite, Tailwind CSS, and TanStack Query.
2. **Backend**: FastAPI REST API running Python 3.11+ with Uvicorn.
3. **Database**: PostgreSQL 15+ (managed RDS/Supabase/Neon or containerized).
4. **Storage**: Local filesystem or private object storage (S3/GCS/Supabase) for document uploads and brand assets.

---

## Strategy 1: Docker Compose (Recommended for VPS / AWS EC2 / DigitalOcean)

The simplest, production-ready full-stack deployment method using container orchestration.

### 1. Prerequisites
- Linux host (Ubuntu 22.04 LTS or Debian 12 recommended)
- Docker Engine $\ge 24.0$ & Docker Compose v2

### 2. Deployment Steps
```bash
# 1. Clone the repository on your server
git clone https://github.com/your-org/proofline.git /opt/proofline
cd /opt/proofline

# 2. Configure production environment
cp .env.example .env
nano .env
# Set a strong SECRET_KEY, POSTGRES_PASSWORD, and your domain
```

### 3. Launch Services
```bash
docker compose up -d --build
```

### 4. Verify Services
```bash
# Check running containers
docker compose ps

# Check backend health
curl http://localhost:8000/health
# Response: {"status":"healthy","database":"connected","environment":"production"}
```

### 5. Configure SSL / Reverse Proxy (Nginx + Certbot)
Point your domain's DNS (`app.proofline.com` and `api.proofline.com`) to your server's public IP:
```nginx
# /etc/nginx/sites-available/proofline.conf
server {
    server_name app.proofline.com;

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 30M;
    }
}
```
Enable HTTPS via Certbot:
```bash
sudo certbot --nginx -d app.proofline.com
```

---

## Strategy 2: Cloud Managed Platforms (Vercel + Render / Railway + Supabase / Neon)

Ideal for teams seeking serverless scaling without managing OS infrastructure.

### Step 1: Database (Supabase or Neon PostgreSQL)
1. Create a PostgreSQL project on [Supabase](https://supabase.com) or [Neon](https://neon.tech).
2. Copy the pooled or direct connection string:
   ```
   postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres?sslmode=require
   ```
3. Run Alembic migrations:
   ```bash
   cd backend
   export DATABASE_URL="postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres?sslmode=require"
   alembic upgrade head
   ```

### Step 2: Backend API (Render / Railway / Fly.io)
#### On Render:
1. Connect your repository to [Render](https://render.com).
2. Create a new **Web Service**:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add Environment Variables:
   - `DATABASE_URL`: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres?sslmode=require`
   - `SECRET_KEY`: `<GENERATE_RANDOM_64_CHAR_HEX>`
   - `ENVIRONMENT`: `production`
   - `LLM_PROVIDER`: `hybrid_deterministic` (or `openai`, `anthropic`, `gemini`)
   - `LLM_API_KEY`: `<YOUR_API_KEY>` (optional, deterministic checks run offline)
   - `ALLOWED_ORIGINS`: `https://app.proofline.com,https://your-frontend.vercel.app`
4. Deploy and verify: `https://your-backend.onrender.com/health`.

### Step 3: Frontend (Vercel / Cloudflare Pages)
#### On Vercel:
1. Connect the repository to [Vercel](https://vercel.com).
2. Configure project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add Environment Variables:
   - `VITE_API_URL`: `https://your-backend.onrender.com/api/v1`
4. Click **Deploy**. Vercel will build and distribute the production bundle globally.

---

## Strategy 3: AWS / Google Cloud (ECS / Cloud Run / Kubernetes)

### Container Registries:
1. Build and tag the backend image:
   ```bash
   docker build -t proofline-backend:latest ./backend
   docker tag proofline-backend:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/proofline-backend:latest
   docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/proofline-backend:latest
   ```
2. Build and tag the frontend image:
   ```bash
   docker build -t proofline-frontend:latest ./frontend
   docker tag proofline-frontend:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/proofline-frontend:latest
   docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/proofline-frontend:latest
   ```

### Runtime Settings:
- Mount an EFS or S3 bucket volume for `/app/uploads` to store ingested guideline documents and image assets persistently.
- Use AWS Secrets Manager or GCP Secret Manager to inject `DATABASE_URL` and `SECRET_KEY`.
- Set container health check path to `/health` with a 15-second interval.

---

## Production Security & Maintenance Checklist

- [ ] **Secret Rotation**: Rotate `SECRET_KEY` and database credentials periodically.
- [ ] **Database Backups**: Enable automated daily snapshots and Point-in-Time Recovery (PITR).
- [ ] **CORS Lock-down**: Ensure `ALLOWED_ORIGINS` strictly specifies your production domain(s) rather than wildcard `*`.
- [ ] **Rate Limiting**: Enable rate limiting on `/api/v1/auth/login` and `/api/v1/auth/register`.
- [ ] **File Size Caps**: Configure Nginx `client_max_body_size 30M;` to match the application limits.
- [ ] **SSL/TLS**: Enforce TLS 1.3 with HSTS headers.
