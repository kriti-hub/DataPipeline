"""Health check / readiness probe endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Return API health status and server timestamp.

    Returns:
        Dictionary with status and current UTC timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "wellnow-hris-api",
    }
