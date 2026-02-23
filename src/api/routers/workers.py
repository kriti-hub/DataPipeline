"""Workers (employee) endpoints.

GET /api/v1/workers       — Paginated employee list with optional filters
GET /api/v1/workers/{id}  — Single employee detail
"""

import math

from fastapi import APIRouter, HTTPException, Query

from src.api.generators.employee_generator import get_employees
from src.api.models.common import PaginationMeta
from src.api.models.employee import EmployeeListResponse, EmployeeResponse

router = APIRouter(prefix="/api/v1/workers", tags=["Workers"])


@router.get("", response_model=EmployeeListResponse)
async def list_workers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(100, ge=1, le=500, description="Records per page"),
    location_id: str | None = Query(None, description="Filter by location ID"),
    role_type: str | None = Query(None, description="Filter by role type"),
    status: str | None = Query(None, description="Filter by status (Active/Terminated)"),
) -> EmployeeListResponse:
    """Return a paginated list of employees with optional filters.

    Args:
        page: Page number (1-indexed).
        page_size: Number of records per page.
        location_id: Optional filter by location_id.
        role_type: Optional filter by role_type.
        status: Optional filter by employment status.

    Returns:
        Paginated employee list with metadata.
    """
    data = get_employees()

    if location_id:
        data = [e for e in data if e["location_id"] == location_id]
    if role_type:
        data = [e for e in data if e["role_type"] == role_type]
    if status:
        data = [e for e in data if e["status"] == status]

    total = len(data)
    total_pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    page_data = data[start:end]

    return EmployeeListResponse(
        data=[EmployeeResponse(**e) for e in page_data],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_records=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_worker(employee_id: str) -> EmployeeResponse:
    """Return a single employee by ID.

    Args:
        employee_id: The employee ID (e.g., EMP-00001).

    Returns:
        The matching employee record.

    Raises:
        HTTPException: 404 if employee not found.
    """
    for emp in get_employees():
        if emp["employee_id"] == employee_id:
            return EmployeeResponse(**emp)

    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": 404,
                "message": "Not Found",
                "details": f"Employee {employee_id} not found.",
            }
        },
    )
