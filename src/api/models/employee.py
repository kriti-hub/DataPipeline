"""Pydantic models for employee/worker API responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from src.api.models.common import PaginationMeta


class EmployeeResponse(BaseModel):
    """Single employee record returned by the workers endpoint."""

    model_config = ConfigDict(strict=True)

    employee_id: str
    first_name: str
    last_name: str
    email: str
    hire_date: date
    termination_date: date | None = None
    status: str
    role_type: str
    job_title: str
    job_level: str | None = None
    schedule_type: str
    location_id: str
    manager_employee_id: str | None = None
    is_people_manager: bool


class EmployeeListResponse(BaseModel):
    """Paginated list of employee records."""

    model_config = ConfigDict(strict=True)

    data: list[EmployeeResponse]
    pagination: PaginationMeta
