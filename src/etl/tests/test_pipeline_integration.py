"""Integration test — runs the full pipeline in local mode against the live API.

This test starts the FastAPI server in a background thread, runs the ETL
pipeline, and verifies that all local output artefacts are created.

NOTE: This test requires the HRIS API dependencies to be installed.
      It is marked slow and can be skipped with ``pytest -m "not slow"``.
"""

import os
import threading
import time
from pathlib import Path

import pytest
import uvicorn


def _run_api_server() -> None:
    """Start the FastAPI server on port 8099 in a daemon thread."""
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8099,
        log_level="error",
    )


@pytest.fixture(scope="module")
def api_server() -> None:
    """Launch the API in background and wait until ready."""
    t = threading.Thread(target=_run_api_server, daemon=True)
    t.start()

    # Wait for server to become ready
    import requests

    for _ in range(30):
        try:
            r = requests.get("http://127.0.0.1:8099/health", timeout=2)
            if r.status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    pytest.fail("API server did not start within 15 seconds")


@pytest.mark.slow
def test_full_pipeline(api_server: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the complete ETL pipeline end-to-end in local mode."""
    monkeypatch.setenv("LOCAL_MODE", "true")
    monkeypatch.setenv("HRIS_API_URL", "http://127.0.0.1:8099")
    monkeypatch.setenv("HRIS_API_KEY", "dev-api-key-change-me")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GCS_STAGING_BUCKET", "test-staging")
    monkeypatch.setenv("GCS_DASHBOARD_BUCKET", "test-dashboard")

    # Clear settings cache so env vars take effect
    from src.etl.config import settings as settings_mod
    settings_mod._settings_cache = None

    from src.etl.pipeline import run_pipeline

    result = run_pipeline()

    assert result["status"] == "Success"
    assert result["records_extracted"] > 0
    assert result["records_loaded"] > 0

    # Verify local output files exist
    bq_dir = Path("data") / "local_output" / "bigquery"
    assert (bq_dir / "dim_employee.parquet").exists()
    assert (bq_dir / "dim_location.parquet").exists()
    assert (bq_dir / "dim_job.parquet").exists()
    assert (bq_dir / "fact_daily_staffing.parquet").exists()
    assert (bq_dir / "fact_shift_gap.parquet").exists()
