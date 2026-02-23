"""Cloud Function HTTP entry point for the WellNow ETL pipeline.

When deployed as a 2nd-gen Cloud Function this module's ``main`` function
is the HTTP trigger handler. Cloud Scheduler sends a POST request daily
at 06:00 UTC.

Usage (local test)::

    python -m src.etl.main
"""

import json
from typing import Any

from src.etl.pipeline import run_pipeline
from src.etl.utils.logger import get_logger

logger = get_logger(__name__)


def main(request: Any = None) -> tuple[str, int, dict[str, str]]:
    """Cloud Function entry point.

    Args:
        request: Flask-like request object injected by Cloud Functions.

    Returns:
        (body, status_code, headers) tuple.
    """
    logger.info("ETL pipeline triggered")

    try:
        summary = run_pipeline()
        status = summary.get("status", "Unknown")
        code = 200 if status == "Success" else 500

        return (
            json.dumps(summary, default=str),
            code,
            {"Content-Type": "application/json"},
        )
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        error_body = json.dumps({
            "status": "Failed",
            "error": str(exc),
        })
        return (
            error_body,
            500,
            {"Content-Type": "application/json"},
        )


if __name__ == "__main__":
    body, code, _headers = main()
    print(f"\nHTTP {code}")
    print(body)
