"""Structured JSON logging for the ETL pipeline.

Provides a pre-configured logger that outputs JSON-formatted log records
suitable for Cloud Logging ingestion.

Usage::

    from src.etl.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Extraction complete", extra={"records": 1200})
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra fields from ``logger.info(..., extra={...})``
        for key in ("records", "duration_ms", "stage", "run_id", "table",
                     "rule_id", "error", "bytes_written", "rows"):
            val = getattr(record, key, None)
            if val is not None:
                payload[key] = val
        if record.exc_info and record.exc_info[1]:
            payload["exception"] = str(record.exc_info[1])
        return json.dumps(payload, default=str)


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a JSON-emitting logger.

    Args:
        name: Logger name (usually ``__name__``).
        level: Log level string.

    Returns:
        Configured :class:`logging.Logger`.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
