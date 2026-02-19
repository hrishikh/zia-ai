"""
Zia AI — API Version Negotiation Middleware
Injects X-API-Version + Sunset/Deprecation headers (RFC 8594).
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request

# Deprecated versions: version → {sunset date, successor}
DEPRECATED_VERSIONS: dict[str, dict] = {
    # "v1": {"sunset": "2027-06-01", "successor": "v2"},
}


class APIVersionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Extract version from URL path
        path = request.url.path
        version = None
        for segment in path.split("/"):
            if segment.startswith("v") and segment[1:].isdigit():
                version = segment
                break

        if version:
            response.headers["X-API-Version"] = version

            if version in DEPRECATED_VERSIONS:
                info = DEPRECATED_VERSIONS[version]
                response.headers["Deprecation"] = "true"
                response.headers["Sunset"] = info["sunset"]
                response.headers["Link"] = (
                    f'</api/{info["successor"]}>; rel="successor-version"'
                )

        return response
