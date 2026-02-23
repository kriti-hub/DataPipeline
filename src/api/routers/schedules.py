"""Schedules endpoint.

GET /api/v1/schedules — Paginated shift schedule data with date-range
                        and location filters.
"""

import math
from datetime import date

from fastapi import APIRouter, Query

from src.api.generators.schedule_generator import get_schedules_filtered
from src.api.models.common import PaginationMeta
from src.api.models.schedule import ScheduleResponse, ShiftRecord

router = APIRouter(prefix="/api/v1/schedules", tags=["Schedules"])


@router.get("", response_model=ScheduleResponse)
async def list_schedules(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(100, ge=1, le=500, description="Records per page"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    location_id: str | None = Query(None, description="Filter by location ID"),
) -> ScheduleResponse:
    """Return paginated shift schedule data.

    Args:
        page: Page number.
        page_size: Records per page.
        start_date: Inclusive start date filter.
        end_date: Inclusive end date filter.
        location_id: Filter by location ID.

    Returns:
        Paginated schedule records with metadata.
    """
    data = get_schedules_filtered(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
    )

    total = len(data)
    total_pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end_idx = start + page_size
    page_data = data[start:end_idx]

    return ScheduleResponse(
        data=[ShiftRecord(**r) for r in page_data],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_records=total,
            total_pages=total_pages,
        ),
    )
