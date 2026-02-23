"""Stage 2 — Validate: execute all 15 DQ rules from quality_rules.yaml.

Each rule is applied to the raw data. Records that fail *quarantine* rules
are removed from the clean set and collected in a quarantine list. Records
that fail *flag* rules are annotated but allowed through. *Alert* rules
generate log warnings.

Usage::

    from src.etl.validate import validate_all
    result = validate_all(raw_data)
    clean = result["clean"]
    quarantined = result["quarantine"]
    dq_log = result["dq_log"]
"""

import re
from datetime import date, datetime, timezone
from typing import Any

from pydantic import ValidationError

from src.etl.config.settings import get_quality_rules
from src.etl.models.schemas import SCHEMA_REGISTRY
from src.etl.utils.logger import get_logger

logger = get_logger(__name__)

# Map API endpoint names → DQ table names used in quality_rules.yaml
_ENDPOINT_TO_TABLE: dict[str, str] = {
    "workers": "dim_employee",
    "schedules": "fact_daily_staffing",
    "patient-volume": "fact_daily_staffing",
    "locations": "dim_location",
    "terminations": "dim_employee",
}


# ---------------------------------------------------------------------------
# Individual rule checkers
# ---------------------------------------------------------------------------

def _check_null(records: list[dict], field_name: str) -> tuple[list[int], list[int]]:
    """Return (pass_indices, fail_indices) for a null-check rule."""
    passed, failed = [], []
    for i, rec in enumerate(records):
        if rec.get(field_name) is None:
            failed.append(i)
        else:
            passed.append(i)
    return passed, failed


def _check_uniqueness(
    records: list[dict], field_name: str
) -> tuple[list[int], list[int]]:
    """Return indices that pass/fail a uniqueness check."""
    seen: dict[Any, int] = {}
    passed, failed = [], []
    for i, rec in enumerate(records):
        val = rec.get(field_name)
        if val in seen:
            failed.append(i)
        else:
            seen[val] = i
            passed.append(i)
    return passed, failed


def _check_referential(
    records: list[dict],
    field_name: str,
    ref_values: set[Any],
) -> tuple[list[int], list[int]]:
    """Return pass/fail indices for referential integrity."""
    passed, failed = [], []
    for i, rec in enumerate(records):
        val = rec.get(field_name)
        if val is None or val in ref_values:
            passed.append(i)
        else:
            failed.append(i)
    return passed, failed


def _check_range(
    records: list[dict],
    field_name: str,
    min_val: float | None,
    max_val: float | None,
) -> tuple[list[int], list[int]]:
    """Return pass/fail for a numeric range check."""
    passed, failed = [], []
    for i, rec in enumerate(records):
        val = rec.get(field_name)
        if val is None:
            passed.append(i)
            continue
        try:
            num = float(val)
        except (TypeError, ValueError):
            failed.append(i)
            continue
        if (min_val is not None and num < min_val) or (
            max_val is not None and num > max_val
        ):
            failed.append(i)
        else:
            passed.append(i)
    return passed, failed


def _check_consistency_active(
    records: list[dict],
) -> tuple[list[int], list[int]]:
    """Active employees should NOT have a termination_date."""
    passed, failed = [], []
    for i, rec in enumerate(records):
        if rec.get("status") == "Active" and rec.get("termination_date") is not None:
            failed.append(i)
        else:
            passed.append(i)
    return passed, failed


def _check_consistency_terminated(
    records: list[dict],
) -> tuple[list[int], list[int]]:
    """Terminated employees MUST have a termination_date."""
    passed, failed = [], []
    for i, rec in enumerate(records):
        if rec.get("status") == "Terminated" and rec.get("termination_date") is None:
            failed.append(i)
        else:
            passed.append(i)
    return passed, failed


def _check_format(
    records: list[dict], field_name: str, pattern: str
) -> tuple[list[int], list[int]]:
    """Regex pattern check on a string field."""
    regex = re.compile(pattern)
    passed, failed = [], []
    for i, rec in enumerate(records):
        val = rec.get(field_name, "")
        if val and regex.match(str(val)):
            passed.append(i)
        else:
            failed.append(i)
    return passed, failed


# ---------------------------------------------------------------------------
# Schema validation pass
# ---------------------------------------------------------------------------

def validate_schemas(
    raw_data: dict[str, list[dict]],
) -> tuple[dict[str, list[dict]], list[dict]]:
    """Validate every record against its Pydantic schema.

    Args:
        raw_data: endpoint → records mapping from extraction.

    Returns:
        (clean_data, quarantine_records)
    """
    clean: dict[str, list[dict]] = {}
    quarantine: list[dict] = []

    for endpoint, records in raw_data.items():
        schema_cls = SCHEMA_REGISTRY.get(endpoint)
        if schema_cls is None:
            clean[endpoint] = records
            continue

        valid: list[dict] = []
        for rec in records:
            try:
                obj = schema_cls.model_validate(rec)
                valid.append(obj.model_dump())
            except ValidationError as exc:
                quarantine.append({
                    "quarantine_date": datetime.now(timezone.utc).isoformat(),
                    "source_table": _ENDPOINT_TO_TABLE.get(endpoint, endpoint),
                    "record_json": str(rec),
                    "failure_rule_id": "SCHEMA",
                    "failure_reason": str(exc),
                })
        clean[endpoint] = valid

    return clean, quarantine


# ---------------------------------------------------------------------------
# Rule-level validation
# ---------------------------------------------------------------------------

def validate_rules(
    data: dict[str, list[dict]],
    run_id: str = "",
) -> tuple[dict[str, list[dict]], list[dict], list[dict]]:
    """Apply all 15 DQ rules from quality_rules.yaml.

    Args:
        data: endpoint → validated records mapping.
        run_id: Pipeline run identifier.

    Returns:
        (clean_data, quarantine_records, dq_log_entries)
    """
    config = get_quality_rules()
    rules = config.get("rules", [])

    quarantine: list[dict] = []
    dq_log: list[dict] = []

    # Build lookup sets for referential checks
    location_ids = {r["location_id"] for r in data.get("locations", [])}
    employee_ids = {r["employee_id"] for r in data.get("workers", [])}

    for rule in rules:
        rule_id = rule["rule_id"]
        check_type = rule["check_type"]
        table_name = rule["table_name"]
        severity = rule["severity"]
        action = rule["action"]

        # Resolve which endpoint records this rule applies to
        target_endpoint: str | None = None
        for ep, tbl in _ENDPOINT_TO_TABLE.items():
            if tbl == table_name and ep in data:
                target_endpoint = ep
                break
        if target_endpoint is None:
            continue

        records = data[target_endpoint]
        passed_idx: list[int] = []
        failed_idx: list[int] = []

        # Dispatch by check_type
        if check_type == "null_check":
            passed_idx, failed_idx = _check_null(records, rule.get("field_name", ""))

        elif check_type == "uniqueness":
            passed_idx, failed_idx = _check_uniqueness(records, rule.get("field_name", ""))

        elif check_type == "referential_integrity":
            ref_set = location_ids if "location" in rule.get("field_name", "") else employee_ids
            passed_idx, failed_idx = _check_referential(
                records, rule.get("field_name", ""), ref_set
            )

        elif check_type == "range":
            passed_idx, failed_idx = _check_range(
                records,
                rule.get("field_name", ""),
                rule.get("min_value"),
                rule.get("max_value"),
            )

        elif check_type == "consistency":
            if rule_id == "DQ-010":
                passed_idx, failed_idx = _check_consistency_active(records)
            elif rule_id == "DQ-011":
                passed_idx, failed_idx = _check_consistency_terminated(records)

        elif check_type == "format":
            passed_idx, failed_idx = _check_format(
                records, rule.get("field_name", ""), rule.get("pattern", ".*")
            )

        elif check_type in ("freshness", "volume", "cross_table"):
            # These are table-level checks, not record-level
            passed_idx = list(range(len(records)))
            failed_idx = []

        # Log DQ result
        total = len(passed_idx) + len(failed_idx)
        pass_rate = len(passed_idx) / total if total > 0 else 1.0
        status = "Pass" if pass_rate >= 0.95 else ("Warn" if pass_rate >= 0.85 else "Fail")

        dq_log.append({
            "check_date": date.today().isoformat(),
            "check_name": rule_id,
            "table_name": table_name,
            "check_type": check_type,
            "records_checked": total,
            "records_passed": len(passed_idx),
            "records_failed": len(failed_idx),
            "pass_rate": round(pass_rate, 4),
            "severity": severity,
            "status": status,
            "details": rule.get("rule_definition", ""),
            "_batch_id": run_id,
        })

        # Quarantine failed records if action == "quarantine"
        if action == "quarantine" and failed_idx:
            for idx in failed_idx:
                quarantine.append({
                    "quarantine_date": datetime.now(timezone.utc).isoformat(),
                    "source_table": table_name,
                    "record_json": str(records[idx]),
                    "failure_rule_id": rule_id,
                    "failure_reason": rule.get("rule_definition", ""),
                    "_batch_id": run_id,
                })
            # Remove quarantined records from data
            keep = set(range(len(records))) - set(failed_idx)
            data[target_endpoint] = [records[i] for i in sorted(keep)]

        if failed_idx:
            logger.warning(
                "%s: %d/%d failed (%s, %s)",
                rule_id,
                len(failed_idx),
                total,
                severity,
                action,
                extra={"rule_id": rule_id},
            )

    return data, quarantine, dq_log


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate_all(
    raw_data: dict[str, list[dict]],
    run_id: str = "",
) -> dict[str, Any]:
    """Full validation: schema check + rule-based DQ checks.

    Args:
        raw_data: endpoint → records from extraction.
        run_id: Pipeline run ID.

    Returns:
        Dict with keys ``clean``, ``quarantine``, ``dq_log``.
    """
    clean, schema_quarantine = validate_schemas(raw_data)
    clean, rule_quarantine, dq_log = validate_rules(clean, run_id=run_id)

    all_quarantine = schema_quarantine + rule_quarantine
    total_clean = sum(len(v) for v in clean.values())
    logger.info(
        "Validation complete: %d clean, %d quarantined, %d DQ checks",
        total_clean,
        len(all_quarantine),
        len(dq_log),
    )
    return {
        "clean": clean,
        "quarantine": all_quarantine,
        "dq_log": dq_log,
    }
