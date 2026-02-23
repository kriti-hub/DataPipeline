"""Tests for the /api/v1/patient-volume endpoint."""

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
async def test_list_patient_volume(client: AsyncClient, headers: dict) -> None:
    """Default request returns paginated volumes."""
    resp = await client.get("/api/v1/patient-volume", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "pagination" in body


@pytest.mark.asyncio
async def test_filter_by_date_range(client: AsyncClient, headers: dict) -> None:
    """Filter by date range."""
    resp = await client.get(
        "/api/v1/patient-volume?start_date=2025-12-01&end_date=2025-12-31",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    for rec in body["data"]:
        assert "2025-12-01" <= rec["visit_date"] <= "2025-12-31"


@pytest.mark.asyncio
async def test_volume_record_schema(client: AsyncClient, headers: dict) -> None:
    """Verify volume record has all required fields."""
    resp = await client.get(
        "/api/v1/patient-volume?page_size=1", headers=headers
    )
    assert resp.status_code == 200
    rec = resp.json()["data"][0]
    required = {"location_id", "visit_date", "patient_visits", "avg_wait_time_minutes"}
    assert required.issubset(rec.keys())


@pytest.mark.asyncio
async def test_visits_positive(client: AsyncClient, headers: dict) -> None:
    """Patient visits should be positive."""
    resp = await client.get(
        "/api/v1/patient-volume?page_size=50", headers=headers
    )
    assert resp.status_code == 200
    for rec in resp.json()["data"]:
        assert rec["patient_visits"] >= 1
