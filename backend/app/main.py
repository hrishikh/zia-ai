"""
Zia AI — FastAPI Application Entrypoint
Production-grade middleware stack, lifespan management, and route mounting.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import engine, Base
from app.api.v1.router import api_router
from app.middleware.rate_limit import SlidingWindowRateLimiter
from app.middleware.versioning import APIVersionMiddleware
from app.middleware.metrics import PrometheusMiddleware, metrics_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables. Shutdown: dispose engine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Zia AI",
    version="1.0.0",
    description="Production AI Assistant API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── Middleware Stack (order matters: last added = first executed) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-API-Version"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(APIVersionMiddleware)
app.add_middleware(SlidingWindowRateLimiter)

# ── Routes ──
app.include_router(api_router, prefix="/api/v1")
app.add_route("/metrics", metrics_endpoint)


@app.get("/health", tags=["system"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": "1.0.0", "service": "zia-ai"}
