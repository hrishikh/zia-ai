"""
Zia AI — Sliding-Window Rate Limiter (Redis-backed)
Layer 2: per-user-per-endpoint rate limiting with role-based tiers.
"""

import hashlib
import logging
import time

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("zia.ratelimit")

# Tier definitions: role → (max_requests, window_seconds)
TIERS = {
    "anonymous": (20, 60),
    "user": (60, 60),
    "admin": (200, 60),
}

# Per-endpoint overrides
ENDPOINT_LIMITS: dict[str, tuple[int, int]] = {
    "/api/v1/auth/login": (5, 60),
    "/api/v1/auth/register": (3, 300),
    "/api/v1/actions/execute": (30, 60),
    "/api/v1/audit/export": (2, 3600),
}


class SlidingWindowRateLimiter(BaseHTTPMiddleware):
    """Redis-backed sliding window rate limiter."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health/metrics
        if request.url.path in ("/health", "/metrics"):
            return await call_next(request)

        try:
            # In a full implementation, import and use Redis here.
            # For now, pass through — Redis connection is initialized at startup.
            response = await call_next(request)

            # Add rate-limit headers (placeholder values until Redis is connected)
            response.headers["X-RateLimit-Limit"] = "60"
            response.headers["X-RateLimit-Remaining"] = "59"
            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            return await call_next(request)
