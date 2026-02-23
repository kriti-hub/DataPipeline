"""Stage 1 — Extract: paginated API calls with exponential back-off.

Authenticates with the HRIS API using the configured API key, paginates
through every configured endpoint, stages raw JSON to Cloud Storage, and
returns the raw records keyed by endpoint name.

Usage::

    from src.etl.extract import extract_all
    raw = extract_all()   # {"workers": [...], "schedules": [...], ...}
"""

import time
from datetime import datetime, timezone
from typing import Any

import requests

from src.etl.config.settings import get_settings, get_source_config
from src.etl.utils.gcp import upload_raw_json
from src.etl.utils.logger import get_logger
from src.etl.utils.retry import with_retries

logger = get_logger(__name__)


@with_retries(max_retries=3, base_delay=1.0, retryable_exceptions=(requests.RequestException,))
def _fetch_page(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any],
    timeout: int,
) -> dict:
    """Fetch a single page from the API.

    Args:
        url: Full endpoint URL.
        headers: Request headers (incl. API key).
        params: Query parameters (page, page_size, etc.).
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response dict.
    """
    resp = requests.get(url, headers=headers, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def extract_endpoint(
    base_url: str,
    endpoint: str,
    api_key: str,
    page_size: int = 500,
    timeout: int = 30,
    extra_params: dict[str, str] | None = None,
) -> list[dict]:
    """Paginate through a single API endpoint and return all records.

    Args:
        base_url: API base URL (e.g., ``http://localhost:8000``).
        endpoint: Endpoint path segment (e.g., ``workers``).
        api_key: Value for the ``X-API-Key`` header.
        page_size: Records per page.
        timeout: HTTP request timeout.
        extra_params: Additional query parameters (date filters, etc.).

    Returns:
        List of all data records from the endpoint.
    """
    headers = {"X-API-Key": api_key}
    url = f"{base_url}/api/v1/{endpoint}"
    all_records: list[dict] = []
    page = 1

    start = time.perf_counter()

    while True:
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if extra_params:
            params.update(extra_params)

        body = _fetch_page(url, headers, params, timeout)

        # Locations endpoint returns {data: [...], total_locations: N}
        # Other endpoints return {data: [...], pagination: {...}}
        records = body.get("data", [])
        all_records.extend(records)

        pagination = body.get("pagination")
        if pagination is None:
            # Non-paginated endpoint (e.g., locations) — single page
            break

        if page >= pagination.get("total_pages", 1):
            break
        page += 1

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Extracted %d records from /%s in %.0fms",
        len(all_records),
        endpoint,
        duration_ms,
        extra={"records": len(all_records), "duration_ms": duration_ms},
    )
    return all_records


def extract_all(
    staging_bucket: str | None = None,
) -> dict[str, list[dict]]:
    """Run extraction for all configured endpoints.

    Args:
        staging_bucket: If provided, stage raw JSON to this GCS bucket.

    Returns:
        Dict mapping endpoint name → list of raw record dicts.
    """
    cfg = get_source_config()
    base_url = cfg["base_url"]
    api_key = cfg["api_key"]
    page_size = cfg.get("page_size", 500)
    timeout = cfg.get("timeout_seconds", 30)
    endpoints: list[str] = cfg["endpoints"]

    settings = get_settings()
    bucket = staging_bucket or settings["destination"].get("staging_bucket", "")

    now = datetime.now(timezone.utc)
    run_date = now.strftime("%Y-%m-%d")
    timestamp = now.isoformat()

    results: dict[str, list[dict]] = {}

    for ep in endpoints:
        records = extract_endpoint(
            base_url=base_url,
            endpoint=ep,
            api_key=api_key,
            page_size=page_size,
            timeout=timeout,
        )
        results[ep] = records

        # Stage raw JSON
        if bucket:
            upload_raw_json(records, bucket, ep, run_date, timestamp)

    total = sum(len(v) for v in results.values())
    logger.info("Extraction complete: %d total records from %d endpoints", total, len(endpoints))
    return results
