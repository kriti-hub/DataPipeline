"""Pydantic models for location API responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class LocationResponse(BaseModel):
    """Single WellNow clinic location record."""

    model_config = ConfigDict(strict=True)

    location_id: str
    location_name: str
    region: str
    state: str
    metro_area: str
    location_type: str
    operating_hours_start: str
    operating_hours_end: str
    days_open_per_week: int
    budgeted_provider_fte: float
    budgeted_support_fte: float
    opened_date: date
    is_active: bool


class LocationListResponse(BaseModel):
    """List of all location records."""

    model_config = ConfigDict(strict=True)

    data: list[LocationResponse]
    total_locations: int
