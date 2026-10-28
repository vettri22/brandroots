import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import (
    auth_router,
    brand_router,
    evidence_router,
    assets_router,
    documents_router,
    reviews_router,
    debugger_router,
    dashboard_router,
    notifications_router,
    seed_router
)
from app.seed_data.demo_company import seed_demo_data

# Create database tables
Base.metadata.create_all(bind=engine)

async def render_keep_alive_loop(external_url: str):
    """
    Prevents Render free tier from sleeping by pinging the public health check every 10 minutes.
    (Render free services spin down after 15 minutes of inactivity).
    """
    health_endpoint = external_url.rstrip("/") + "/health"
    print(f"[Proofline Keep-Alive] Automatic anti-sleep ping enabled for: {health_endpoint}")
    # Wait 60s for full server initialization
    await asyncio.sleep(60)
    while True:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(health_endpoint)
                print(f"[Proofline Keep-Alive] Anti-sleep ping to {health_endpoint} -> status {res.status_code}")
        except Exception as err:
            print(f"[Proofline Keep-Alive] Ping notice: {err}")
        # Ping every 10 minutes (600 seconds)
        await asyncio.sleep(600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Modern lifespan handler: initialize and seed demo brand if unseeded
    db = SessionLocal()
    try:
        from app.models.brand import BrandGuideline
        rule_count = db.query(BrandGuideline).count()
        if rule_count == 0:
            print("[Proofline] Fresh database detected. Initializing demonstration brand environment...")
            seed_demo_data(db)
            print("[Proofline] Demonstration brand environment initialized.")
    except Exception as e:
        print(f"[Proofline] Startup notice: {e}")
    finally:
        db.close()

    # Start automatic anti-sleep pinger if running on Render or custom URL is configured
    ping_task = None
    render_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("APP_URL") or os.environ.get("KEEP_ALIVE_URL")
    if render_url:
        ping_task = asyncio.create_task(render_keep_alive_loop(render_url))

    yield

    if ping_task:
        ping_task.cancel()

app = FastAPI(
    title="Proofline — Brand Governance Platform",
    version=settings.APP_VERSION,
    description="Production-oriented Brand Governance Platform with Brand Evidence Ledger, Preflight Review Engine, Correction Studio, and Guideline Clarity Radar.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers under /api/v1
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(brand_router, prefix=settings.API_PREFIX)
app.include_router(evidence_router, prefix=settings.API_PREFIX)
app.include_router(assets_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(reviews_router, prefix=settings.API_PREFIX)
app.include_router(debugger_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(notifications_router, prefix=settings.API_PREFIX)
app.include_router(seed_router, prefix=settings.API_PREFIX)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.ENVIRONMENT
    }

# Check for compiled frontend distribution
FRONTEND_DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.isdir(FRONTEND_DIST_DIR):
    assets_dir = os.path.join(FRONTEND_DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="spa-assets")

    @app.get("/")
    def serve_spa_root():
        index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"app": "Proofline", "status": "operational", "api_docs": "/docs"}

    @app.get("/{full_path:path}")
    def serve_spa_fallback(full_path: str):
        # Don't intercept API or docs routes
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json", "health"):
            return None
        candidate = os.path.join(FRONTEND_DIST_DIR, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        index_file = os.path.join(FRONTEND_DIST_DIR, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        return {"app": "Proofline", "status": "operational", "api_docs": "/docs"}
else:
    @app.get("/")
    def root():
        return {
            "app": "Proofline — Brand Governance Platform",
            "version": settings.APP_VERSION,
            "status": "operational",
            "api_docs": "/docs",
            "features": {
                "evidence_ledger": "active",
                "preflight_review_engine": "active",
                "correction_studio": "active",
                "guideline_clarity_radar": "active",
                "version_bound_approvals": "enforced"
            }
        }
