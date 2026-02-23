"""Tests for the /api/v1/workers endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.config import settings
from src.api.main import app

API_KEY = settings.hris_api_key


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY}


@pytest.mark.asyncio
async def test_list_workers_default(client: AsyncClient, headers: dict) -> None:
    """Default request returns paginated workers."""
    resp = await client.get("/api/v1/workers", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "pagination" in body
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["page_size"] == 100
    assert len(body["data"]) <= 100


@pytest.mark.asyncio
async def test_list_workers_pagination(client: AsyncClient, headers: dict) -> None:
    """Custom page size works."""
    resp = await client.get(
        "/api/v1/workers?page=1&page_size=10", headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 10
    assert body["pagination"]["page_size"] == 10


@pytest.mark.asyncio
async def test_filter_by_role_type(client: AsyncClient, headers: dict) -> None:
    """Filter by role_type returns only matching records."""
    resp = await client.get(
        "/api/v1/workers?role_type=Provider", headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    for emp in body["data"]:
        assert emp["role_type"] == "Provider"


@pytest.mark.asyncio
async def test_filter_by_location_id(client: AsyncClient, headers: dict) -> None:
    """Filter by location_id returns only matching records."""
    resp = await client.get(
        "/api/v1/workers?location_id=LOC-001", headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    for emp in body["data"]:
        assert emp["location_id"] == "LOC-001"


@pytest.mark.asyncio
async def test_filter_by_status(client: AsyncClient, headers: dict) -> None:
    """Filter by status returns only matching records."""
    resp = await client.get(
        "/api/v1/workers?status=Active", headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    for emp in body["data"]:
        assert emp["status"] == "Active"


@pytest.mark.asyncio
async def test_get_single_worker(client: AsyncClient, headers: dict) -> None:
    """Get a specific employee by ID."""
    resp = await client.get("/api/v1/workers/EMP-00001", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["employee_id"] == "EMP-00001"


@pytest.mark.asyncio
async def test_get_worker_not_found(client: AsyncClient, headers: dict) -> None:
    """Non-existent employee returns 404."""
    resp = await client.get("/api/v1/workers/EMP-99999", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_worker_response_schema(client: AsyncClient, headers: dict) -> None:
    """Verify all expected fields are present in a worker record."""
    resp = await client.get(
        "/api/v1/workers?page_size=1", headers=headers
    )
    assert resp.status_code == 200
    emp = resp.json()["data"][0]
    required_fields = {
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "hire_date",
        "status",
        "role_type",
        "job_title",
        "schedule_type",
        "location_id",
        "is_people_manager",
    }
    assert required_fields.issubset(emp.keys())
