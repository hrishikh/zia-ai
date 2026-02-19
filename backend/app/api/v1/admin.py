"""
Zia AI — Admin API
Health, config, and service management.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_admin
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    """Detailed health check (public)."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "zia-ai-backend",
    }


@router.get("/config")
async def get_config(user: dict = Depends(require_admin)):
    """Get current config (admin only, secrets redacted)."""
    return {
        "app_name": settings.APP_NAME,
        "debug": settings.DEBUG,
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
        "max_confirmation_ttl_minutes": settings.MAX_CONFIRMATION_TTL_MINUTES,
        "worker_max_jobs": settings.WORKER_MAX_JOBS,
        "worker_job_timeout": settings.WORKER_JOB_TIMEOUT,
        "database": "***REDACTED***",
        "redis": "***REDACTED***",
        "encryption_key": "***REDACTED***",
    }
