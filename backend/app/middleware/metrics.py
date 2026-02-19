"""
Zia AI — Prometheus Metrics Middleware
Exposes request count, latency histogram, and custom Zia gauges.
"""

import time

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ── Metric Definitions ───────────────────────────────

REQUEST_COUNT = Counter(
    "zia_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "zia_http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

ACTION_EXEC_COUNT = Counter(
    "zia_actions_total",
    "Total actions executed",
    ["action_type", "status"],
)

WORKER_QUEUE_DEPTH = Gauge(
    "zia_worker_queue_depth",
    "Current worker queue depth",
    ["queue"],
)

ACTIVE_WS_CONNECTIONS = Gauge(
    "zia_active_websocket_connections",
    "Active WebSocket connections",
)


# ── Middleware ────────────────────────────────────────


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        endpoint = request.url.path
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, endpoint).observe(duration)

        return response


# ── Metrics Endpoint ─────────────────────────────────


async def metrics_endpoint(request: Request) -> Response:
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), media_type="text/plain; charset=utf-8")
