"""Pydantic models for patient volume API responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from src.api.models.common import PaginationMeta


class DailyVolumeRecord(BaseModel):
    """Daily patient visit count for a single location."""

    model_config = ConfigDict(strict=True)

    location_id: str
    visit_date: date
    patient_visits: int
    avg_wait_time_minutes: float


class VolumeResponse(BaseModel):
    """Paginated list of daily patient volume records."""

    model_config = ConfigDict(strict=True)

    data: list[DailyVolumeRecord]
    pagination: PaginationMeta
