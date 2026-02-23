"""Stage 4 — Load: write DataFrames to BigQuery (or local Parquet).

Dimensions use ``WRITE_TRUNCATE`` (full refresh).
Facts use ``WRITE_APPEND`` (incremental).
Utility tables (_pipeline_runs, _data_quality_log, _quarantine) use APPEND.

Usage::

    from src.etl.load import load_all
    load_all(tables, dq_log, quarantine, metrics)
"""

from typing import Any

import pandas as pd

from src.etl.config.settings import get_destination_config, get_settings
from src.etl.utils.gcp import get_bq_client, load_to_bigquery
from src.etl.utils.logger import get_logger
from src.etl.utils.metrics import PipelineMetrics

logger = get_logger(__name__)


def _full_table_id(dataset: str, table: str, project: str = "") -> str:
    """Build ``project.dataset.table`` or ``dataset.table``."""
    if project:
        return f"{project}.{dataset}.{table}"
    return f"{dataset}.{table}"


def load_all(
    tables: dict[str, pd.DataFrame],
    dq_log: list[dict],
    quarantine: list[dict],
    metrics: PipelineMetrics,
) -> None:
    """Load all transformed DataFrames and utility records into BigQuery.

    Args:
        tables: Table name → DataFrame (dim_employee, dim_location, etc.).
        dq_log: Data-quality check results for ``_data_quality_log``.
        quarantine: Quarantined records for ``_quarantine``.
        metrics: Pipeline run metrics (summary written to ``_pipeline_runs``).
    """
    dest = get_destination_config()
    settings = get_settings()
    project = dest.get("project_id", "")
    dataset = dest["dataset_id"]
    client = get_bq_client()

    load_cfg = settings.get("load", {})
    dim_tables = set(load_cfg.get("dimensions", {}).get("tables", []))
    fact_tables = set(load_cfg.get("facts", {}).get("tables", []))

    # ------------------------------------------------------------------
    # Load dimensions (TRUNCATE) and facts (APPEND)
    # ------------------------------------------------------------------
    for table_name, df in tables.items():
        if df.empty:
            logger.warning("Skipping empty table: %s", table_name)
            continue

        if table_name in dim_tables:
            disposition = "WRITE_TRUNCATE"
        elif table_name in fact_tables:
            disposition = "WRITE_APPEND"
        else:
            disposition = "WRITE_TRUNCATE"  # default for uncategorized

        tid = _full_table_id(dataset, table_name, project)
        rows = load_to_bigquery(df, tid, disposition, client=client)
        metrics.record_load(table_name, rows)

    # ------------------------------------------------------------------
    # Load utility tables (always APPEND)
    # ------------------------------------------------------------------

    # _data_quality_log
    if dq_log:
        dq_df = pd.DataFrame(dq_log)
        # Cast string columns to proper types for BigQuery compatibility
        if "check_date" in dq_df.columns:
            dq_df["check_date"] = pd.to_datetime(dq_df["check_date"]).dt.date
        tid = _full_table_id(dataset, "_data_quality_log", project)
        load_to_bigquery(dq_df, tid, "WRITE_APPEND", client=client)
        logger.info("Loaded %d DQ log entries", len(dq_df))

    # _quarantine
    if quarantine:
        q_df = pd.DataFrame(quarantine)
        tid = _full_table_id(dataset, "_quarantine", project)
        load_to_bigquery(q_df, tid, "WRITE_APPEND", client=client)
        logger.info("Loaded %d quarantine records", len(q_df))

    # _pipeline_runs — written after finalization in the orchestrator
    # (see pipeline.py)

    logger.info("Load stage complete")
