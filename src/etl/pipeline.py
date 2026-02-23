"""Pipeline orchestrator — sequences Extract → Validate → Transform → Load → Export.

Each stage is tracked with timing and record counts. On completion (or failure)
a summary row is written to ``_pipeline_runs``.

Usage (local)::

    python -m src.etl.pipeline          # full pipeline
    python -m src.etl.pipeline --local  # explicit local mode (default)
"""

import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.etl.config.settings import get_destination_config, get_settings
from src.etl.export_dashboard_data import export_all
from src.etl.extract import extract_all
from src.etl.load import load_all
from src.etl.transform import transform_all
from src.etl.utils.gcp import load_to_bigquery
from src.etl.utils.logger import get_logger
from src.etl.utils.metrics import PipelineMetrics
from src.etl.validate import validate_all

logger = get_logger(__name__)


def run_pipeline() -> dict[str, Any]:
    """Execute the full ETL pipeline.

    Returns:
        Pipeline run summary dict (same shape as ``_pipeline_runs`` row).
    """
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    metrics = PipelineMetrics(run_id=run_id)
    logger.info("Pipeline started: %s", run_id, extra={"run_id": run_id})

    try:
        # ──────────────────────────────────────────────────────────────
        # Stage 1: Extract
        # ──────────────────────────────────────────────────────────────
        sm = metrics.start_stage("extract")
        raw_data = extract_all()
        metrics.end_stage(
            sm,
            records_out=sum(len(v) for v in raw_data.values()),
        )
        metrics.records_extracted = sum(len(v) for v in raw_data.values())

        # ──────────────────────────────────────────────────────────────
        # Stage 2: Validate
        # ──────────────────────────────────────────────────────────────
        sm = metrics.start_stage("validate")
        validation = validate_all(raw_data, run_id=run_id)
        clean_data = validation["clean"]
        quarantine = validation["quarantine"]
        dq_log = validation["dq_log"]
        metrics.record_validation(
            passed=sum(len(v) for v in clean_data.values()),
            quarantined=len(quarantine),
        )
        metrics.end_stage(sm)

        # ──────────────────────────────────────────────────────────────
        # Stage 3: Transform
        # ──────────────────────────────────────────────────────────────
        sm = metrics.start_stage("transform")
        tables = transform_all(clean_data, run_id=run_id)
        metrics.end_stage(
            sm,
            records_out=sum(len(df) for df in tables.values()),
        )

        # ──────────────────────────────────────────────────────────────
        # Stage 4: Load
        # ──────────────────────────────────────────────────────────────
        sm = metrics.start_stage("load")
        load_all(tables, dq_log, quarantine, metrics)
        metrics.end_stage(sm)

        # ──────────────────────────────────────────────────────────────
        # Stage 5: Export dashboard JSON
        # ──────────────────────────────────────────────────────────────
        sm = metrics.start_stage("export")
        metrics.finalize(status="Success")
        export_all(tables, dq_log, metrics.summary())
        metrics.end_stage(sm)

        # Write pipeline run metadata
        _persist_run_metadata(metrics)

        logger.info(
            "Pipeline %s completed successfully",
            run_id,
            extra={"run_id": run_id, "stage": "complete"},
        )

    except Exception as exc:
        metrics.finalize(status="Failed", error=str(exc))
        _persist_run_metadata(metrics)
        logger.exception(
            "Pipeline %s failed: %s",
            run_id,
            exc,
            extra={"run_id": run_id, "stage": "error"},
        )
        raise

    return metrics.summary()


def _persist_run_metadata(metrics: PipelineMetrics) -> None:
    """Write the ``_pipeline_runs`` row."""
    dest = get_destination_config()
    project = dest.get("project_id", "")
    dataset = dest["dataset_id"]
    tid = f"{project}.{dataset}._pipeline_runs" if project else f"{dataset}._pipeline_runs"

    summary = metrics.summary()
    df = pd.DataFrame([summary])
    # Cast ISO string timestamps to proper datetime for BigQuery compatibility
    for col in ("started_at", "completed_at"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True)
    load_to_bigquery(df, tid, "WRITE_APPEND")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    result = run_pipeline()

    print("\n" + "=" * 60)
    print("PIPELINE RUN SUMMARY")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k:30s}: {v}")
    print("=" * 60)

    sys.exit(0 if result["status"] == "Success" else 1)
