"""TDental Golden -- FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.middleware import validate_token
from app.core.config import settings
from app.core.database import close_pool, init_pool

from app.api.auth import bootstrap_auth_tables, router as auth_router
from app.api.appointments import router as appointments_router
from app.api.categories import router as categories_router
from app.api.commission import router as commission_router
from app.api.companies import router as companies_router
from app.api.customers import router as customers_router
from app.api.dashboard import router as dashboard_router
from app.api.employees import router as employees_router
from app.api.exam_sessions import router as exam_sessions_router
from app.api.exports import router as exports_router
from app.api.finance import router as finance_router
from app.api.hr import router as hr_router
from app.api.inventory import router as inventory_router
from app.api.notifications import router as notifications_router
from app.api.public_site import (
    bootstrap_public_site_tables,
    router as public_site_router,
)
from app.api.reports import router as reports_router
from app.api.settings import router as settings_router
from app.api.tasks import router as tasks_router
from app.api.treatments import router as treatments_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _cookie_samesite() -> str:
    value = settings.COOKIE_SAMESITE.lower()
    if value not in {"lax", "strict", "none"}:
        return "strict" if settings.IS_PRODUCTION else "lax"
    return value

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    logger.info("[BOOT] Starting TDental Golden on port %s", settings.APP_PORT)
    init_pool(settings.DATABASE_URL)
    try:
        bootstrap_auth_tables()
    except RuntimeError:
        logger.warning("[BOOT] Skipping auth bootstrap because DB pool is unavailable")
    except Exception:
        logger.exception("[BOOT] Failed to bootstrap auth tables")
    try:
        bootstrap_public_site_tables()
    except RuntimeError:
        logger.warning("[BOOT] Skipping public-site bootstrap because DB pool is unavailable")
    except Exception:
        logger.exception("[BOOT] Failed to bootstrap public-site tables")
    yield
    close_pool()
    logger.info("[SHUTDOWN] TDental Golden stopped")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TDental Golden",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if settings.IS_PRODUCTION else "/docs",
    redoc_url=None if settings.IS_PRODUCTION else "/redoc",
    openapi_url=None if settings.IS_PRODUCTION else "/openapi.json",
)

# -- CORS -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Attach baseline browser hardening headers."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response

# -- Static files -----------------------------------------------------------

_static_dir = Path(__file__).resolve().parent.parent / "static"
_login_page = _static_dir / "login.html"
_app_page = _static_dir / "tdental.html"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
else:
    logger.warning("[BOOT] Static directory not found at %s", _static_dir)

# -- Routers ----------------------------------------------------------------

app.include_router(auth_router)
app.include_router(appointments_router)
app.include_router(customers_router)
app.include_router(companies_router)
app.include_router(employees_router)
app.include_router(categories_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(finance_router)
app.include_router(tasks_router)
app.include_router(commission_router)
app.include_router(treatments_router)
app.include_router(exam_sessions_router)
app.include_router(inventory_router)
app.include_router(hr_router)
app.include_router(settings_router)
app.include_router(notifications_router)
app.include_router(public_site_router)
app.include_router(exports_router)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}


@app.get("/")
def root(request: Request):
    """Serve SPA for valid session; otherwise redirect to login."""
    token = request.cookies.get("tdental_session")
    if not token:
        return RedirectResponse(url="/login")

    try:
        validate_token(token, require_session=True)
    except HTTPException:
        response = RedirectResponse(url="/login")
        response.delete_cookie(
            key="tdental_session",
            path="/",
            secure=settings.COOKIE_SECURE,
            httponly=True,
            samesite=_cookie_samesite(),
        )
        return response

    return FileResponse(_app_page)


@app.get("/login")
def login_page(request: Request):
    """Serve the login page for frontend redirects."""
    token = request.cookies.get("tdental_session")
    if token:
        try:
            validate_token(token, require_session=True)
            return RedirectResponse(url="/")
        except HTTPException:
            response = FileResponse(_login_page)
            response.delete_cookie(
                key="tdental_session",
                path="/",
                secure=settings.COOKIE_SECURE,
                httponly=True,
                samesite=_cookie_samesite(),
            )
            return response

    return FileResponse(_login_page)


@app.get("/app")
def app_page(request: Request):
    """Convenience route for direct SPA access."""
    token = request.cookies.get("tdental_session")
    if not token:
        return RedirectResponse(url="/login")

    try:
        validate_token(token, require_session=True)
    except HTTPException:
        response = RedirectResponse(url="/login")
        response.delete_cookie(
            key="tdental_session",
            path="/",
            secure=settings.COOKIE_SECURE,
            httponly=True,
            samesite=_cookie_samesite(),
        )
        return response

    return FileResponse(_app_page)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=not settings.IS_PRODUCTION,
    )
