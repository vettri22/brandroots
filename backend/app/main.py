from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import (
    auth_router,
    brand_router,
    documents_router,
    reviews_router,
    debugger_router,
    dashboard_router,
    seed_router
)
from app.seed_data.demo_company import seed_demo_data

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Brand-Governance Platform with Guideline Debugger — Inkloom Hackathon Round 2 (Team vettriselvam190)"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev & Vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(brand_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(reviews_router, prefix=settings.API_PREFIX)
app.include_router(debugger_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(seed_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def startup_event():
    # Automatically seed demonstration company on startup if DB is unseeded
    db = SessionLocal()
    try:
        from app.models.brand import BrandGuideline
        rule_count = db.query(BrandGuideline).count()
        if rule_count == 0:
            print("[BrandRoots] Fresh database detected. Initializing demonstration brand 'NovusBio Health'...")
            seed_demo_data(db)
            print("[BrandRoots] Demonstration brand successfully initialized.")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "team": "vettriselvam190",
        "status": "operational",
        "demo_mode": settings.DEMO_MODE,
        "docs_url": "/docs",
        "signature_feature": "Guideline Debugger",
        "compliance_engine": "hybrid_deterministic"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.ENVIRONMENT
    }
