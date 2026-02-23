"""GCP client helpers — BigQuery and Cloud Storage abstractions.

In local / CI mode (``LOCAL_MODE=true``), these helpers write to local files
instead of calling the real GCP APIs, so the full pipeline can run without
credentials.

Usage::

    from src.etl.utils.gcp import get_bq_client, load_to_bigquery, upload_to_gcs
"""

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from src.etl.utils.logger import get_logger

logger = get_logger(__name__)

LOCAL_MODE = os.environ.get("LOCAL_MODE", "true").lower() == "true"

# When running locally, persist artefacts under this directory
_LOCAL_OUTPUT_DIR = Path("data") / "local_output"


# ---------------------------------------------------------------------------
# BigQuery helpers
# ---------------------------------------------------------------------------

def get_bq_client() -> Any:
    """Return a BigQuery client (or a no-op stub in local mode).

    Returns:
        A ``google.cloud.bigquery.Client`` in production, or ``None``
        when ``LOCAL_MODE`` is enabled.
    """
    if LOCAL_MODE:
        logger.info("LOCAL_MODE: BigQuery client stub (writes to local files)")
        return None
    from google.cloud import bigquery  # type: ignore[import-untyped]
    return bigquery.Client()


def load_to_bigquery(
    df: pd.DataFrame,
    table_id: str,
    write_disposition: str = "WRITE_TRUNCATE",
    *,
    client: Any = None,
) -> int:
    """Load a DataFrame into a BigQuery table (or local Parquet in local mode).

    Args:
        df: DataFrame to load.
        table_id: Fully-qualified BigQuery table id
                  (``project.dataset.table``).
        write_disposition: ``WRITE_TRUNCATE`` or ``WRITE_APPEND``.
        client: Optional pre-existing BigQuery client.

    Returns:
        Number of rows written.
    """
    rows = len(df)
    if LOCAL_MODE:
        out_dir = _LOCAL_OUTPUT_DIR / "bigquery"
        out_dir.mkdir(parents=True, exist_ok=True)
        table_short = table_id.rsplit(".", 1)[-1]
        out_path = out_dir / f"{table_short}.parquet"

        if write_disposition == "WRITE_APPEND" and out_path.exists():
            existing = pd.read_parquet(out_path)
            df = pd.concat([existing, df], ignore_index=True)

        df.to_parquet(out_path, index=False)
        logger.info(
            "LOCAL_MODE: Wrote %d rows to %s",
            rows,
            out_path,
            extra={"table": table_short, "rows": rows},
        )
        return rows

    # Production path
    if client is None:
        client = get_bq_client()
    from google.cloud import bigquery  # type: ignore[import-untyped]

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # block until complete
    logger.info(
        "Loaded %d rows into %s (%s)",
        rows,
        table_id,
        write_disposition,
        extra={"table": table_id, "rows": rows},
    )
    return rows


# ---------------------------------------------------------------------------
# Cloud Storage helpers
# ---------------------------------------------------------------------------

def upload_to_gcs(
    data: dict | list,
    bucket_name: str,
    blob_path: str,
) -> str:
    """Upload a JSON-serializable object to Cloud Storage (or local file).

    Args:
        data: The Python object to serialize as JSON.
        bucket_name: Target GCS bucket.
        blob_path: Object path within the bucket.

    Returns:
        The GCS URI (``gs://…``) or local file path.
    """
    if LOCAL_MODE:
        out_dir = _LOCAL_OUTPUT_DIR / "gcs" / bucket_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / blob_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)
        logger.info("LOCAL_MODE: Wrote JSON to %s", out_path)
        return str(out_path)

    from google.cloud import storage  # type: ignore[import-untyped]

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(
        json.dumps(data, default=str),
        content_type="application/json",
    )
    uri = f"gs://{bucket_name}/{blob_path}"
    logger.info("Uploaded JSON to %s", uri)
    return uri


def upload_raw_json(
    data: list[dict],
    bucket_name: str,
    endpoint: str,
    run_date: str,
    timestamp: str,
) -> str:
    """Stage raw extracted JSON to GCS (or local file).

    Args:
        data: List of records extracted from the API.
        bucket_name: Staging bucket.
        endpoint: API endpoint name.
        run_date: ISO date string (YYYY-MM-DD).
        timestamp: ISO timestamp for uniqueness.

    Returns:
        Storage URI or local path.
    """
    # Sanitise timestamp for Windows compatibility (colons are illegal in filenames)
    safe_ts = timestamp.replace(":", "-")
    blob_path = f"raw/{endpoint}/{run_date}/{safe_ts}.json"
    return upload_to_gcs(data, bucket_name, blob_path)
