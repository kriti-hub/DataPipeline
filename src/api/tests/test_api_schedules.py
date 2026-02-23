"""Tests for the /api/v1/schedules endpoint."""

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
async def test_list_schedules_default(client: AsyncClient, headers: dict) -> None:
    """Default request returns paginated schedules."""
    resp = await client.get("/api/v1/schedules", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "pagination" in body
    assert len(body["data"]) <= 100


@pytest.mark.asyncio
async def test_filter_by_date_range(client: AsyncClient, headers: dict) -> None:
    """Filter by date range."""
    resp = await client.get(
        "/api/v1/schedules?start_date=2025-12-01&end_date=2025-12-31",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    for rec in body["data"]:
        assert "2025-12-01" <= rec["shift_date"] <= "2025-12-31"


@pytest.mark.asyncio
async def test_filter_by_location(client: AsyncClient, headers: dict) -> None:
    """Filter by location ID."""
    resp = await client.get(
        "/api/v1/schedules?location_id=LOC-001&page_size=10",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    for rec in body["data"]:
        assert rec["location_id"] == "LOC-001"


@pytest.mark.asyncio
async def test_schedule_record_schema(client: AsyncClient, headers: dict) -> None:
    """Verify schedule record has all required fields."""
    resp = await client.get(
        "/api/v1/schedules?page_size=1", headers=headers
    )
    assert resp.status_code == 200
    rec = resp.json()["data"][0]
    required = {
        "location_id",
        "shift_date",
        "shift_window",
        "scheduled_provider_hours",
        "actual_provider_hours",
        "overtime_hours",
        "callout_count",
        "required_providers",
        "scheduled_providers",
        "actual_providers",
    }
    assert required.issubset(rec.keys())
