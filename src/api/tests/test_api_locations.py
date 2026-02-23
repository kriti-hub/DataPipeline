"""Tests for the /api/v1/locations endpoint."""

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
async def test_list_locations(client: AsyncClient, headers: dict) -> None:
    """Returns all 80 locations."""
    resp = await client.get("/api/v1/locations", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_locations"] == 80
    assert len(body["data"]) == 80


@pytest.mark.asyncio
async def test_location_record_schema(client: AsyncClient, headers: dict) -> None:
    """Verify location record has all required fields."""
    resp = await client.get("/api/v1/locations", headers=headers)
    assert resp.status_code == 200
    loc = resp.json()["data"][0]
    required = {
        "location_id",
        "location_name",
        "region",
        "state",
        "metro_area",
        "location_type",
        "operating_hours_start",
        "operating_hours_end",
        "days_open_per_week",
        "budgeted_provider_fte",
        "budgeted_support_fte",
        "opened_date",
        "is_active",
    }
    assert required.issubset(loc.keys())


@pytest.mark.asyncio
async def test_location_types_valid(client: AsyncClient, headers: dict) -> None:
    """All location types should be Urban, Suburban, or Rural."""
    resp = await client.get("/api/v1/locations", headers=headers)
    assert resp.status_code == 200
    valid_types = {"Urban", "Suburban", "Rural"}
    for loc in resp.json()["data"]:
        assert loc["location_type"] in valid_types
