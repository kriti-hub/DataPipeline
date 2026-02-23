"""Locations endpoint.

GET /api/v1/locations — Full list of WellNow clinic locations.
"""

from fastapi import APIRouter

from src.api.generators.organization import get_locations
from src.api.models.location import LocationListResponse, LocationResponse

router = APIRouter(prefix="/api/v1/locations", tags=["Locations"])


@router.get("", response_model=LocationListResponse)
async def list_locations() -> LocationListResponse:
    """Return all WellNow clinic locations.

    Returns:
        Complete list of locations with count.
    """
    data = get_locations()
    return LocationListResponse(
        data=[LocationResponse(**loc) for loc in data],
        total_locations=len(data),
    )
