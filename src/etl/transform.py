"""Stage 3 — Transform: derived fields, SCD Type 2, fact aggregation.

Responsibilities per PRD Section 6 Stage 3:
- Flatten nested JSON into tabular format
- Derive calculated fields (coverage_score, patients_per_provider_hour, etc.)
- Build SCD Type 2 history for dim_employee
- Aggregate shift-level data into fact_daily_staffing
- Detect shift gaps and populate fact_shift_gap
- Standardize fields (title case names, ISO dates, consistent enums)

Usage::

    from src.etl.transform import transform_all
    tables = transform_all(clean_data)
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any

import pandas as pd

from src.etl.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Division that returns *default* when denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def _tenure_band(tenure_years: float) -> str:
    """Map a tenure in years to a labeled band."""
    if tenure_years < 1:
        return "0-1yr"
    if tenure_years < 3:
        return "1-3yr"
    if tenure_years < 5:
        return "3-5yr"
    if tenure_years < 10:
        return "5-10yr"
    return "10+yr"


# ---------------------------------------------------------------------------
# dim_employee (SCD Type 2)
# ---------------------------------------------------------------------------

def build_dim_employee(
    employees: list[dict],
    locations: list[dict],
    run_id: str,
) -> pd.DataFrame:
    """Transform raw employee records into dim_employee (SCD Type 2).

    Args:
        employees: Validated employee records.
        locations: Validated location records for location_key lookup.
        run_id: Pipeline batch ID.

    Returns:
        DataFrame ready for BigQuery load.
    """
    reference_date = date.today()
    loc_key_map = {loc["location_id"]: idx + 1 for idx, loc in enumerate(locations)}

    rows: list[dict[str, Any]] = []
    for i, emp in enumerate(employees):
        hire_date = emp["hire_date"] if isinstance(emp["hire_date"], date) else date.fromisoformat(str(emp["hire_date"]))
        term_date = None
        if emp.get("termination_date"):
            term_date = emp["termination_date"] if isinstance(emp["termination_date"], date) else date.fromisoformat(str(emp["termination_date"]))

        tenure_years = round((reference_date - hire_date).days / 365.25, 2)
        is_new_hire = (reference_date - hire_date).days <= 90
        is_provider = emp["role_type"] == "Provider"

        rows.append({
            "employee_key": i + 1,
            "employee_id": emp["employee_id"],
            "first_name": emp["first_name"].title(),
            "last_name": emp["last_name"].title(),
            "full_name": f"{emp['first_name'].title()} {emp['last_name'].title()}",
            "email": emp["email"].lower(),
            "hire_date": hire_date,
            "termination_date": term_date,
            "status": emp["status"],
            "role_type": emp["role_type"],
            "job_title": emp["job_title"],
            "job_level": emp.get("job_level"),
            "is_provider": is_provider,
            "is_people_manager": emp["is_people_manager"],
            "schedule_type": emp["schedule_type"],
            "location_key": loc_key_map.get(emp["location_id"], 0),
            "manager_employee_id": emp.get("manager_employee_id"),
            "tenure_years": tenure_years,
            "tenure_band": _tenure_band(tenure_years),
            "is_new_hire": is_new_hire,
            # SCD Type 2 fields — initial load: one row per employee
            "effective_start": hire_date,
            "effective_end": term_date,
            "is_current": emp["status"] == "Active",
            # Metadata
            "_loaded_at": datetime.now(timezone.utc),
            "_source_system": "hris_api",
            "_batch_id": run_id,
        })

    df = pd.DataFrame(rows)
    logger.info("Built dim_employee: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# dim_location
# ---------------------------------------------------------------------------

def build_dim_location(locations: list[dict]) -> pd.DataFrame:
    """Transform raw location records into dim_location.

    Args:
        locations: Validated location records.

    Returns:
        DataFrame ready for BigQuery load.
    """
    rows: list[dict[str, Any]] = []
    for i, loc in enumerate(locations):
        opened = loc["opened_date"] if isinstance(loc["opened_date"], date) else date.fromisoformat(str(loc["opened_date"]))
        rows.append({
            "location_key": i + 1,
            "location_id": loc["location_id"],
            "location_name": loc["location_name"],
            "region": loc["region"],
            "state": loc["state"],
            "metro_area": loc["metro_area"],
            "location_type": loc["location_type"],
            "operating_hours_start": loc["operating_hours_start"],
            "operating_hours_end": loc["operating_hours_end"],
            "days_open_per_week": loc["days_open_per_week"],
            "budgeted_provider_fte": loc["budgeted_provider_fte"],
            "budgeted_support_fte": loc["budgeted_support_fte"],
            "opened_date": opened,
            "is_active": loc["is_active"],
            "_loaded_at": datetime.now(timezone.utc),
        })

    df = pd.DataFrame(rows)
    logger.info("Built dim_location: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# dim_job
# ---------------------------------------------------------------------------

def build_dim_job(employees: list[dict]) -> pd.DataFrame:
    """Derive dim_job from unique (job_title, role_type) combos.

    Args:
        employees: Validated employee records.

    Returns:
        DataFrame with one row per unique job.
    """
    seen: dict[tuple[str, str], dict] = {}
    for emp in employees:
        key = (emp["job_title"], emp["role_type"])
        if key not in seen:
            is_clinical = emp["role_type"] in ("Provider", "RN", "MA", "RadTech")
            seen[key] = {
                "job_key": len(seen) + 1,
                "job_title": emp["job_title"],
                "role_type": emp["role_type"],
                "job_level": emp.get("job_level"),
                "is_clinical": is_clinical,
                "is_provider": emp["role_type"] == "Provider",
                "_loaded_at": datetime.now(timezone.utc),
            }

    df = pd.DataFrame(list(seen.values()))
    logger.info("Built dim_job: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# fact_daily_staffing
# ---------------------------------------------------------------------------

def build_fact_daily_staffing(
    schedules: list[dict],
    volumes: list[dict],
    locations: list[dict],
    run_id: str,
) -> pd.DataFrame:
    """Aggregate shift-level schedules + patient volumes into daily facts.

    Args:
        schedules: Validated schedule (shift) records.
        volumes: Validated patient volume records.
        locations: Validated locations for key lookup.
        run_id: Pipeline batch ID.

    Returns:
        DataFrame with one row per (date, location).
    """
    loc_key_map = {loc["location_id"]: idx + 1 for idx, loc in enumerate(locations)}

    # Aggregate schedules by (location, date)
    sched_agg: dict[tuple[str, str], dict[str, Any]] = {}
    for rec in schedules:
        shift_date = str(rec["shift_date"])
        key = (rec["location_id"], shift_date)
        if key not in sched_agg:
            sched_agg[key] = {
                "scheduled_provider_hours": 0.0,
                "actual_provider_hours": 0.0,
                "scheduled_support_hours": 0.0,
                "actual_support_hours": 0.0,
                "overtime_hours": 0.0,
                "callout_count": 0,
                "required_provider_hours": 0.0,
            }
        agg = sched_agg[key]
        agg["scheduled_provider_hours"] += rec["scheduled_provider_hours"]
        agg["actual_provider_hours"] += rec["actual_provider_hours"]
        agg["scheduled_support_hours"] += rec["scheduled_support_hours"]
        agg["actual_support_hours"] += rec["actual_support_hours"]
        agg["overtime_hours"] += rec["overtime_hours"]
        agg["callout_count"] += rec["callout_count"]
        # required_provider_hours = required_providers × 4 hrs per shift
        agg["required_provider_hours"] += rec["required_providers"] * 4.0

    # Index patient volumes
    vol_map: dict[tuple[str, str], dict] = {}
    for rec in volumes:
        visit_date = str(rec["visit_date"])
        key = (rec["location_id"], visit_date)
        vol_map[key] = rec

    # Build fact rows
    rows: list[dict[str, Any]] = []
    for (loc_id, snap_date), agg in sched_agg.items():
        vol = vol_map.get((loc_id, snap_date), {})
        patient_visits = vol.get("patient_visits", 0)
        avg_wait = vol.get("avg_wait_time_minutes", 0.0)
        actual_prov_hrs = agg["actual_provider_hours"]
        req_prov_hrs = agg["required_provider_hours"]

        coverage_score = round(_safe_divide(actual_prov_hrs, req_prov_hrs), 3)
        ppph = round(_safe_divide(patient_visits, actual_prov_hrs), 2)

        # Labor cost estimate: $120/hr providers, $35/hr support
        labor_cost = round(actual_prov_hrs * 120 + agg["actual_support_hours"] * 35, 2)
        lcpv = round(_safe_divide(labor_cost, patient_visits), 2)

        d = date.fromisoformat(snap_date)
        date_key = int(d.strftime("%Y%m%d"))

        rows.append({
            "date_key": date_key,
            "snapshot_date": d,
            "location_key": loc_key_map.get(loc_id, 0),
            "scheduled_provider_hours": round(agg["scheduled_provider_hours"], 1),
            "actual_provider_hours": round(actual_prov_hrs, 1),
            "required_provider_hours": round(req_prov_hrs, 1),
            "scheduled_support_hours": round(agg["scheduled_support_hours"], 1),
            "actual_support_hours": round(agg["actual_support_hours"], 1),
            "overtime_hours": round(agg["overtime_hours"], 1),
            "callout_count": agg["callout_count"],
            "patient_visits": patient_visits,
            "patients_per_provider_hour": ppph,
            "avg_wait_time_minutes": round(avg_wait, 1),
            "coverage_score": coverage_score,
            "labor_cost_total": labor_cost,
            "labor_cost_per_visit": lcpv,
            "_loaded_at": datetime.now(timezone.utc),
            "_batch_id": run_id,
        })

    df = pd.DataFrame(rows)
    logger.info("Built fact_daily_staffing: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# fact_shift_gap
# ---------------------------------------------------------------------------

def build_fact_shift_gap(
    schedules: list[dict],
    locations: list[dict],
    run_id: str,
) -> pd.DataFrame:
    """Detect per-shift understaffing and overstaffing.

    Args:
        schedules: Validated shift-level records.
        locations: Location records for key lookup.
        run_id: Pipeline batch ID.

    Returns:
        DataFrame with one row per (date, location, shift_window).
    """
    loc_key_map = {loc["location_id"]: idx + 1 for idx, loc in enumerate(locations)}

    rows: list[dict[str, Any]] = []
    for rec in schedules:
        req = rec["required_providers"]
        sched = rec["scheduled_providers"]
        actual = rec["actual_providers"]
        gap_flag = actual < req
        excess_flag = actual > req * 1.15
        gap_hours = max(0.0, (req - actual) * 4.0) if gap_flag else 0.0
        excess_hours = max(0.0, (actual - req) * 4.0) if excess_flag else 0.0

        shift_date = rec["shift_date"] if isinstance(rec["shift_date"], date) else date.fromisoformat(str(rec["shift_date"]))
        date_key = int(shift_date.strftime("%Y%m%d"))

        rows.append({
            "date_key": date_key,
            "snapshot_date": shift_date,
            "location_key": loc_key_map.get(rec["location_id"], 0),
            "shift_window": rec["shift_window"],
            "required_providers": req,
            "scheduled_providers": sched,
            "actual_providers": actual,
            "gap_flag": gap_flag,
            "excess_flag": excess_flag,
            "gap_hours": round(gap_hours, 1),
            "excess_hours": round(excess_hours, 1),
            "_loaded_at": datetime.now(timezone.utc),
            "_batch_id": run_id,
        })

    df = pd.DataFrame(rows)
    logger.info("Built fact_shift_gap: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def transform_all(
    clean_data: dict[str, list[dict]],
    run_id: str = "",
) -> dict[str, pd.DataFrame]:
    """Run all transformations and return DataFrames keyed by table name.

    Args:
        clean_data: endpoint → validated records from Stage 2.
        run_id: Pipeline batch ID.

    Returns:
        Dict mapping BigQuery table name → DataFrame.
    """
    employees = clean_data.get("workers", [])
    locations = clean_data.get("locations", [])
    schedules = clean_data.get("schedules", [])
    volumes = clean_data.get("patient-volume", [])

    tables: dict[str, pd.DataFrame] = {}

    tables["dim_employee"] = build_dim_employee(employees, locations, run_id)
    tables["dim_location"] = build_dim_location(locations)
    tables["dim_job"] = build_dim_job(employees)
    tables["fact_daily_staffing"] = build_fact_daily_staffing(
        schedules, volumes, locations, run_id
    )
    tables["fact_shift_gap"] = build_fact_shift_gap(schedules, locations, run_id)

    logger.info(
        "Transform complete: %s",
        {k: len(v) for k, v in tables.items()},
    )
    return tables
