"""Export dashboard-ready JSON files to Cloud Storage (or local).

Computes KPI summaries, coverage data, shift-gap heatmaps, overtime
hotspots, labor-cost trends, and DQ scores — then writes each as a
JSON file consumable by the React dashboard.

Usage::

    from src.etl.export_dashboard_data import export_all
    export_all(tables, dq_log, metrics_summary)
"""

from datetime import date, timedelta
from typing import Any

import pandas as pd

from src.etl.config.settings import get_destination_config, get_settings
from src.etl.utils.gcp import upload_to_gcs
from src.etl.utils.logger import get_logger

logger = get_logger(__name__)


def _compute_kpis(fact_staffing: pd.DataFrame) -> dict:
    """Aggregate top-level KPI cards from fact_daily_staffing."""
    if fact_staffing.empty:
        return {}

    last_30 = fact_staffing[
        fact_staffing["snapshot_date"] >= (date.today() - timedelta(days=30))
    ]
    if last_30.empty:
        last_30 = fact_staffing.tail(2400)  # fallback

    return {
        "avg_coverage_score": round(float(last_30["coverage_score"].mean()), 3),
        "total_overtime_hours_30d": round(float(last_30["overtime_hours"].sum()), 1),
        "avg_cost_per_visit": round(float(last_30["labor_cost_per_visit"].mean()), 2),
        "shift_gap_rate": None,  # computed from fact_shift_gap
        "avg_wait_time": round(float(last_30["avg_wait_time_minutes"].mean()), 1),
        "total_patient_visits_30d": int(last_30["patient_visits"].sum()),
    }


def _compute_staffing_coverage(
    fact_staffing: pd.DataFrame,
    dim_location: pd.DataFrame,
) -> list[dict]:
    """Per-location coverage summary for the geo-bubble chart."""
    if fact_staffing.empty or dim_location.empty:
        return []

    agg = (
        fact_staffing.groupby("location_key")
        .agg(
            avg_coverage=("coverage_score", "mean"),
            total_visits=("patient_visits", "sum"),
            avg_wait=("avg_wait_time_minutes", "mean"),
        )
        .reset_index()
    )
    merged = agg.merge(
        dim_location[["location_key", "location_name", "region", "state",
                       "location_type", "metro_area"]],
        on="location_key",
        how="left",
    )
    merged["avg_coverage"] = merged["avg_coverage"].round(3)
    merged["avg_wait"] = merged["avg_wait"].round(1)
    return merged.to_dict(orient="records")


def _compute_shift_gaps(fact_gap: pd.DataFrame) -> list[dict]:
    """Shift-gap heatmap data: location × day_of_week × gap_frequency."""
    if fact_gap.empty:
        return []

    fact_gap = fact_gap.copy()
    fact_gap["dow"] = pd.to_datetime(fact_gap["snapshot_date"]).dt.dayofweek

    agg = (
        fact_gap.groupby(["location_key", "dow"])
        .agg(
            total_shifts=("gap_flag", "count"),
            understaffed=("gap_flag", "sum"),
        )
        .reset_index()
    )
    agg["gap_frequency"] = (agg["understaffed"] / agg["total_shifts"]).round(3)
    return agg.to_dict(orient="records")


def _compute_overtime_hotspots(
    fact_staffing: pd.DataFrame,
    dim_location: pd.DataFrame,
) -> list[dict]:
    """Top 15 locations by overtime hours for the waterfall chart."""
    if fact_staffing.empty:
        return []

    agg = (
        fact_staffing.groupby("location_key")
        .agg(total_overtime=("overtime_hours", "sum"))
        .reset_index()
        .sort_values("total_overtime", ascending=False)
        .head(15)
    )
    merged = agg.merge(
        dim_location[["location_key", "location_name", "region"]],
        on="location_key",
        how="left",
    )
    merged["total_overtime"] = merged["total_overtime"].round(1)
    return merged.to_dict(orient="records")


def _compute_labor_cost_trends(fact_staffing: pd.DataFrame) -> list[dict]:
    """Monthly labor-cost-per-visit by region for the trend chart."""
    if fact_staffing.empty:
        return []

    df = fact_staffing.copy()
    df["month"] = pd.to_datetime(df["snapshot_date"]).dt.to_period("M").astype(str)

    agg = (
        df.groupby("month")
        .agg(
            total_labor=("labor_cost_total", "sum"),
            total_visits=("patient_visits", "sum"),
        )
        .reset_index()
    )
    agg["cost_per_visit"] = (agg["total_labor"] / agg["total_visits"].replace(0, 1)).round(2)
    return agg.to_dict(orient="records")


def _compute_dq_scores(dq_log: list[dict]) -> dict:
    """Aggregate DQ scores by severity for the quality dashboard."""
    if not dq_log:
        return {}

    by_severity: dict[str, list[float]] = {}
    for entry in dq_log:
        sev = entry.get("severity", "Unknown")
        by_severity.setdefault(sev, []).append(entry.get("pass_rate", 1.0))

    severity_scores = {
        sev: round(sum(rates) / len(rates), 4)
        for sev, rates in by_severity.items()
    }

    # Weighted overall score
    weights = {"Critical": 0.40, "High": 0.30, "Medium": 0.20, "Low": 0.10}
    overall = sum(
        severity_scores.get(sev, 1.0) * w
        for sev, w in weights.items()
    )

    return {
        "overall_score": round(overall, 4),
        "severity_scores": severity_scores,
        "total_checks": len(dq_log),
        "status": (
            "Healthy" if overall >= 0.95
            else "Warning" if overall >= 0.85
            else "Alert"
        ),
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def export_all(
    tables: dict[str, pd.DataFrame],
    dq_log: list[dict],
    metrics_summary: dict[str, Any],
) -> None:
    """Compute and export all dashboard JSON files.

    Args:
        tables: Transformed DataFrames (dim_location, fact_daily_staffing, etc.).
        dq_log: DQ check results.
        metrics_summary: Pipeline run summary dict.
    """
    dest = get_destination_config()
    settings = get_settings()
    bucket = dest.get("dashboard_bucket", "")

    dim_loc = tables.get("dim_location", pd.DataFrame())
    fact_staff = tables.get("fact_daily_staffing", pd.DataFrame())
    fact_gap = tables.get("fact_shift_gap", pd.DataFrame())

    # Compute each JSON payload
    kpis = _compute_kpis(fact_staff)
    if not fact_gap.empty:
        gap_rate = float(fact_gap["gap_flag"].mean())
        kpis["shift_gap_rate"] = round(gap_rate, 3)

    coverage = _compute_staffing_coverage(fact_staff, dim_loc)
    gaps = _compute_shift_gaps(fact_gap)
    overtime = _compute_overtime_hotspots(fact_staff, dim_loc)
    labor = _compute_labor_cost_trends(fact_staff)
    dq_scores = _compute_dq_scores(dq_log)

    # Export
    exports = {
        "data/kpis.json": kpis,
        "data/staffing_coverage.json": coverage,
        "data/shift_gaps.json": gaps,
        "data/overtime_hotspots.json": overtime,
        "data/labor_cost_trends.json": labor,
        "data/pipeline_runs.json": [metrics_summary],
        "data/dq_scores.json": dq_scores,
    }

    for blob_path, payload in exports.items():
        upload_to_gcs(payload, bucket, blob_path)

    logger.info("Exported %d dashboard JSON files", len(exports))
