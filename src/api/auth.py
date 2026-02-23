"""API key authentication middleware.

Validates the X-API-Key header on every request except /health.
Returns 401 with a structured error response if the key is missing or invalid.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.api.config import settings


EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware that validates X-API-Key header on protected endpoints."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Check API key for non-exempt paths."""
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": 401,
                        "message": "Unauthorized",
                        "details": (
                            "Missing API key. "
                            "Provide a valid X-API-Key header."
                        ),
                    }
                },
            )

        if api_key != settings.hris_api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": 401,
                        "message": "Unauthorized",
                        "details": (
                            "Invalid API key. "
                            "Provide a valid X-API-Key header."
                        ),
                    }
                },
            )

        return await call_next(request)
