"""
Zia AI — FastAPI Application Entrypoint
Production-grade middleware stack, lifespan management, route mounting,
and Zia Brain (Groq LLM) integration.
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

# ── Zia Brain imports (core/ and tools/ live inside backend/) ──
from core.memory import ShortTermMemory
from core.brain import ZiaBrain
from tools.base_tool import ToolRegistry
from tools.email_tool import EmailTool
from tools.os_tool import OpenFileTool, LaunchAppTool
from tools.browser_tool import YouTubeTool, YouTubeControlTool

# ── Zia Brain singleton (shared across all requests) ──
_registry = ToolRegistry()
_registry.register(EmailTool())
_registry.register(OpenFileTool())
_registry.register(LaunchAppTool())
_registry.register(YouTubeTool())
_registry.register(YouTubeControlTool())

_memory = ShortTermMemory(max_turns=20)

brain = ZiaBrain(
    registry=_registry,
    memory=_memory,
)

print(f"🧠 Brain singleton created — model: {settings.GROQ_MODEL}")
print(f"🔧 Tools loaded: {_registry.tool_names}")


# ── Lifespan ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("🚀 Zia AI started successfully")

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

# ── CORS — must be first middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
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


# ── System Endpoints ──

@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "zia-ai",
        "brain_model": settings.GROQ_MODEL,
        "tools": _registry.tool_names,
    }


@app.get("/", tags=["system"])
async def root():
    return {"message": "Zia AI Backend Running"}


@app.get("/debug/env", tags=["system"])
async def debug_env():
    return {"google_client_id_loaded": bool(settings.GOOGLE_CLIENT_ID)}


@app.get("/cors-test", tags=["system"])
def cors_test():
    return {"status": "ok"}