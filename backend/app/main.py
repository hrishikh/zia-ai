"""
Zia AI — FastAPI Application Entrypoint
Production-grade middleware stack, lifespan management, and route mounting.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.database import engine, Base
from app.api.v1.router import api_router
from app.middleware.rate_limit import SlidingWindowRateLimiter
from app.middleware.versioning import APIVersionMiddleware
from app.middleware.metrics import PrometheusMiddleware, metrics_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("🚀 Zia AI started successfully")
    print("Loaded GOOGLE_CLIENT_ID:", bool(settings.GOOGLE_CLIENT_ID))

    yield

    # Dispose DB engine on shutdown
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

# ── CORS — must be the first middleware after app init ──
# allow_origin_regex matches ALL *.vercel.app preview/production domains
# so we never need to update this when the Vercel URL changes.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(PrometheusMiddleware)
app.add_middleware(APIVersionMiddleware)
# app.add_middleware(SlidingWindowRateLimiter)

# ── Routes ──
app.include_router(api_router, prefix="/api/v1")
app.add_route("/metrics", metrics_endpoint)


@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "service": "zia-ai"}


@app.get("/", tags=["system"])
async def root():
    return {"message": "Zia AI Backend Running"}


@app.get("/debug/env", tags=["system"])
async def debug_env():
    return {"google_client_id_loaded": bool(settings.GOOGLE_CLIENT_ID)}