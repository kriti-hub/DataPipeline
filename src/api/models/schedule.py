"""Pydantic models for schedule/shift API responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from src.api.models.common import PaginationMeta


class ShiftRecord(BaseModel):
    """Single shift record for a location on a given date."""

    model_config = ConfigDict(strict=True)

    location_id: str
    shift_date: date
    shift_window: str
    scheduled_provider_hours: float
    actual_provider_hours: float
    scheduled_support_hours: float
    actual_support_hours: float
    overtime_hours: float
    callout_count: int
    required_providers: int
    scheduled_providers: int
    actual_providers: int


class ScheduleResponse(BaseModel):
    """Paginated list of shift schedule records."""

    model_config = ConfigDict(strict=True)

    data: list[ShiftRecord]
    pagination: PaginationMeta
