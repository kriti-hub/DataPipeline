"""Pydantic models for HRIS API request and response schemas."""

from src.api.models.common import ErrorDetail, ErrorResponse, PaginationMeta
from src.api.models.employee import EmployeeListResponse, EmployeeResponse
from src.api.models.location import LocationListResponse, LocationResponse
from src.api.models.patient_volume import DailyVolumeRecord, VolumeResponse
from src.api.models.schedule import ScheduleResponse, ShiftRecord

__all__ = [
    "DailyVolumeRecord",
    "EmployeeListResponse",
    "EmployeeResponse",
    "ErrorDetail",
    "ErrorResponse",
    "LocationListResponse",
    "LocationResponse",
    "PaginationMeta",
    "ScheduleResponse",
    "ShiftRecord",
    "VolumeResponse",
]
