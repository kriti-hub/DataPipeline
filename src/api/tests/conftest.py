"""Shared test fixtures for the HRIS API test suite."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.config import settings
from src.api.main import app

API_KEY = settings.hris_api_key


@pytest.fixture
def client():
    """Yield an async httpx client wired to the FastAPI app."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Return headers with a valid API key."""
    return {"X-API-Key": API_KEY}
