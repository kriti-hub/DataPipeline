"""Tests for API key authentication middleware."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.config import settings
from src.api.main import app

API_KEY = settings.hris_api_key


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_no_auth_required(client: AsyncClient) -> None:
    """Health endpoint should not require API key."""
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_valid_key(client: AsyncClient) -> None:
    """Valid API key should allow access to protected endpoints."""
    resp = await client.get(
        "/api/v1/locations",
        headers={"X-API-Key": API_KEY},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_missing_key(client: AsyncClient) -> None:
    """Missing API key should return 401."""
    resp = await client.get("/api/v1/locations")
    assert resp.status_code == 401
    body = resp.json()
    assert body["error"]["code"] == 401
    assert "Missing" in body["error"]["details"]


@pytest.mark.asyncio
async def test_invalid_key(client: AsyncClient) -> None:
    """Invalid API key should return 401."""
    resp = await client.get(
        "/api/v1/locations",
        headers={"X-API-Key": "wrong-key"},
    )
    assert resp.status_code == 401
    body = resp.json()
    assert "Invalid" in body["error"]["details"]


@pytest.mark.asyncio
async def test_docs_no_auth_required(client: AsyncClient) -> None:
    """OpenAPI docs should not require authentication."""
    resp = await client.get("/docs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json_no_auth(client: AsyncClient) -> None:
    """OpenAPI JSON schema should not require authentication."""
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
