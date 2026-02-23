"""Pydantic validation schemas for each data entity flowing through the ETL.

These schemas are used in the *validate* stage to enforce structure and types
on the raw records extracted from the HRIS API before transformation.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


# ---------------------------------------------------------------------------
# Source-system schemas (match the API response shapes)
# ---------------------------------------------------------------------------

class EmployeeRecord(BaseModel):
    """Validates a single employee record from ``/api/v1/workers``."""

    model_config = ConfigDict(strict=False)  # allow str→date coercion

    employee_id: str
    first_name: str
    last_name: str
    email: str
    hire_date: date
    termination_date: Optional[date] = None
    status: str
    role_type: str
    job_title: str
    job_level: Optional[str] = None
    schedule_type: str
    location_id: str
    manager_employee_id: Optional[str] = None
    is_people_manager: bool


class ScheduleRecord(BaseModel):
    """Validates a single shift record from ``/api/v1/schedules``."""

    model_config = ConfigDict(strict=False)

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


class PatientVolumeRecord(BaseModel):
    """Validates a single daily volume record from ``/api/v1/patient-volume``."""

    model_config = ConfigDict(strict=False)

    location_id: str
    visit_date: date
    patient_visits: int
    avg_wait_time_minutes: float


class LocationRecord(BaseModel):
    """Validates a single location record from ``/api/v1/locations``."""

    model_config = ConfigDict(strict=False)

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


class TerminationRecord(BaseModel):
    """Validates a termination event from ``/api/v1/terminations``."""

    model_config = ConfigDict(strict=False)

    employee_id: str
    first_name: str
    last_name: str
    role_type: str
    location_id: str
    hire_date: date
    termination_date: date
    termination_category: str
    termination_reason: str


# ---------------------------------------------------------------------------
# Schema registry — maps endpoint names to their Pydantic model
# ---------------------------------------------------------------------------

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "workers": EmployeeRecord,
    "schedules": ScheduleRecord,
    "patient-volume": PatientVolumeRecord,
    "locations": LocationRecord,
    "terminations": TerminationRecord,
}
