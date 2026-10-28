from app.routers.auth import router as auth_router
from app.routers.brand import router as brand_router
from app.routers.evidence import router as evidence_router
from app.routers.assets import router as assets_router
from app.routers.documents import router as documents_router
from app.routers.reviews import router as reviews_router
from app.routers.debugger import router as debugger_router
from app.routers.dashboard import router as dashboard_router
from app.routers.notifications import router as notifications_router
from app.routers.seed import router as seed_router

__all__ = [
    "auth_router",
    "brand_router",
    "evidence_router",
    "assets_router",
    "documents_router",
    "reviews_router",
    "debugger_router",
    "dashboard_router",
    "notifications_router",
    "seed_router"
]
