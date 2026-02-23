"""Terminations endpoint.

GET /api/v1/terminations — Paginated termination records with date-range filter.
"""

import math
from datetime import date

from fastapi import APIRouter, Query

from src.api.generators.termination_generator import get_terminations_filtered
from src.api.models.common import PaginationMeta

router = APIRouter(prefix="/api/v1/terminations", tags=["Terminations"])


@router.get("")
async def list_terminations(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(100, ge=1, le=500, description="Records per page"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
) -> dict:
    """Return paginated termination records.

    Args:
        page: Page number.
        page_size: Records per page.
        start_date: Inclusive start date filter.
        end_date: Inclusive end date filter.

    Returns:
        Paginated termination records with metadata.
    """
    data = get_terminations_filtered(
        start_date=start_date,
        end_date=end_date,
    )

    total = len(data)
    total_pages = max(1, math.ceil(total / page_size))
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_data = data[start_idx:end_idx]

    return {
        "data": page_data,
        "pagination": PaginationMeta(
            page=page,
            page_size=page_size,
            total_records=total,
            total_pages=total_pages,
        ).model_dump(),
    }
