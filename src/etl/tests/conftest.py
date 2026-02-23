"""Shared test fixtures for the ETL test suite."""

import os
from datetime import date

import pytest


@pytest.fixture(autouse=True)
def _local_mode_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure every test runs in LOCAL_MODE (no GCP credentials needed)."""
    monkeypatch.setenv("LOCAL_MODE", "true")
    monkeypatch.setenv("HRIS_API_URL", "http://localhost:8000")
    monkeypatch.setenv("HRIS_API_KEY", "dev-api-key-change-me")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GCS_STAGING_BUCKET", "test-staging")
    monkeypatch.setenv("GCS_DASHBOARD_BUCKET", "test-dashboard")


@pytest.fixture
def sample_employees() -> list[dict]:
    """Minimal employee records for unit tests."""
    return [
        {
            "employee_id": "EMP-00001",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@wellnow.com",
            "hire_date": date(2024, 3, 15),
            "termination_date": None,
            "status": "Active",
            "role_type": "Provider",
            "job_title": "Physician (MD)",
            "job_level": "Senior",
            "schedule_type": "Full-time",
            "location_id": "LOC-001",
            "manager_employee_id": None,
            "is_people_manager": False,
        },
        {
            "employee_id": "EMP-00002",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@wellnow.com",
            "hire_date": date(2023, 1, 10),
            "termination_date": date(2025, 6, 30),
            "status": "Terminated",
            "role_type": "FrontDesk",
            "job_title": "Front Desk Coordinator",
            "job_level": "Staff",
            "schedule_type": "Full-time",
            "location_id": "LOC-001",
            "manager_employee_id": "EMP-00003",
            "is_people_manager": False,
        },
        {
            "employee_id": "EMP-00003",
            "first_name": "Alice",
            "last_name": "Brown",
            "email": "alice.brown@wellnow.com",
            "hire_date": date(2020, 7, 1),
            "termination_date": None,
            "status": "Active",
            "role_type": "OfficeMgr",
            "job_title": "Office Manager",
            "job_level": "Office Manager",
            "schedule_type": "Full-time",
            "location_id": "LOC-001",
            "manager_employee_id": None,
            "is_people_manager": True,
        },
    ]


@pytest.fixture
def sample_locations() -> list[dict]:
    """Minimal location records for unit tests."""
    return [
        {
            "location_id": "LOC-001",
            "location_name": "WellNow Buffalo 1",
            "region": "Northeast",
            "state": "NY",
            "metro_area": "Buffalo",
            "location_type": "Suburban",
            "operating_hours_start": "08:00",
            "operating_hours_end": "20:00",
            "days_open_per_week": 7,
            "budgeted_provider_fte": 3.0,
            "budgeted_support_fte": 6.0,
            "opened_date": date(2019, 4, 1),
            "is_active": True,
        },
    ]


@pytest.fixture
def sample_schedules() -> list[dict]:
    """Minimal schedule records for unit tests."""
    return [
        {
            "location_id": "LOC-001",
            "shift_date": date(2025, 12, 1),
            "shift_window": "AM",
            "scheduled_provider_hours": 8.0,
            "actual_provider_hours": 8.0,
            "scheduled_support_hours": 12.0,
            "actual_support_hours": 12.0,
            "overtime_hours": 0.0,
            "callout_count": 0,
            "required_providers": 2,
            "scheduled_providers": 2,
            "actual_providers": 2,
        },
        {
            "location_id": "LOC-001",
            "shift_date": date(2025, 12, 1),
            "shift_window": "PM",
            "scheduled_provider_hours": 8.0,
            "actual_provider_hours": 4.0,
            "scheduled_support_hours": 12.0,
            "actual_support_hours": 8.0,
            "overtime_hours": 2.0,
            "callout_count": 1,
            "required_providers": 2,
            "scheduled_providers": 2,
            "actual_providers": 1,
        },
    ]


@pytest.fixture
def sample_volumes() -> list[dict]:
    """Minimal patient volume records for unit tests."""
    return [
        {
            "location_id": "LOC-001",
            "visit_date": date(2025, 12, 1),
            "patient_visits": 60,
            "avg_wait_time_minutes": 22.5,
        },
    ]
