"""Tests for the validation module."""

from datetime import date

import pytest

from src.etl.validate import (
    _check_consistency_active,
    _check_consistency_terminated,
    _check_format,
    _check_null,
    _check_range,
    _check_referential,
    _check_uniqueness,
    validate_all,
    validate_schemas,
)


class TestNullCheck:
    def test_passes_when_present(self) -> None:
        records = [{"employee_id": "EMP-001"}, {"employee_id": "EMP-002"}]
        passed, failed = _check_null(records, "employee_id")
        assert len(passed) == 2
        assert len(failed) == 0

    def test_fails_when_null(self) -> None:
        records = [{"employee_id": None}, {"employee_id": "EMP-002"}]
        passed, failed = _check_null(records, "employee_id")
        assert len(passed) == 1
        assert len(failed) == 1


class TestUniqueness:
    def test_all_unique(self) -> None:
        records = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        passed, failed = _check_uniqueness(records, "id")
        assert len(failed) == 0

    def test_duplicates_detected(self) -> None:
        records = [{"id": "A"}, {"id": "A"}, {"id": "B"}]
        passed, failed = _check_uniqueness(records, "id")
        assert len(failed) == 1


class TestReferentialIntegrity:
    def test_valid_references(self) -> None:
        records = [{"loc": "L1"}, {"loc": "L2"}]
        ref_set = {"L1", "L2", "L3"}
        passed, failed = _check_referential(records, "loc", ref_set)
        assert len(failed) == 0

    def test_invalid_reference(self) -> None:
        records = [{"loc": "L1"}, {"loc": "MISSING"}]
        ref_set = {"L1"}
        passed, failed = _check_referential(records, "loc", ref_set)
        assert len(failed) == 1

    def test_null_passes(self) -> None:
        records = [{"loc": None}]
        ref_set = {"L1"}
        passed, failed = _check_referential(records, "loc", ref_set)
        assert len(passed) == 1


class TestRangeCheck:
    def test_in_range(self) -> None:
        records = [{"val": 5}, {"val": 10}]
        passed, failed = _check_range(records, "val", 0, 20)
        assert len(failed) == 0

    def test_below_range(self) -> None:
        records = [{"val": -1}]
        passed, failed = _check_range(records, "val", 0, 100)
        assert len(failed) == 1

    def test_above_range(self) -> None:
        records = [{"val": 25}]
        passed, failed = _check_range(records, "val", 0, 24)
        assert len(failed) == 1


class TestConsistency:
    def test_active_no_term_date(self) -> None:
        records = [{"status": "Active", "termination_date": None}]
        passed, failed = _check_consistency_active(records)
        assert len(failed) == 0

    def test_active_with_term_date_fails(self) -> None:
        records = [{"status": "Active", "termination_date": date(2025, 1, 1)}]
        passed, failed = _check_consistency_active(records)
        assert len(failed) == 1

    def test_terminated_with_term_date(self) -> None:
        records = [{"status": "Terminated", "termination_date": date(2025, 1, 1)}]
        passed, failed = _check_consistency_terminated(records)
        assert len(failed) == 0

    def test_terminated_no_term_date_fails(self) -> None:
        records = [{"status": "Terminated", "termination_date": None}]
        passed, failed = _check_consistency_terminated(records)
        assert len(failed) == 1


class TestFormatCheck:
    def test_valid_email(self) -> None:
        records = [{"email": "jane@wellnow.com"}]
        passed, failed = _check_format(records, "email", r"^.+@wellnow\.com$")
        assert len(failed) == 0

    def test_invalid_email(self) -> None:
        records = [{"email": "jane@other.com"}]
        passed, failed = _check_format(records, "email", r"^.+@wellnow\.com$")
        assert len(failed) == 1


class TestSchemaValidation:
    def test_valid_location(self, sample_locations: list[dict]) -> None:
        raw = {"locations": sample_locations}
        clean, quarantine = validate_schemas(raw)
        assert len(clean["locations"]) == 1
        assert len(quarantine) == 0

    def test_invalid_record_quarantined(self) -> None:
        raw = {"workers": [{"employee_id": "X"}]}  # Missing required fields
        clean, quarantine = validate_schemas(raw)
        assert len(clean["workers"]) == 0
        assert len(quarantine) == 1


class TestValidateAll:
    def test_full_validation_flow(
        self,
        sample_employees: list[dict],
        sample_locations: list[dict],
    ) -> None:
        raw = {
            "workers": sample_employees,
            "locations": sample_locations,
        }
        result = validate_all(raw, run_id="test-001")
        assert "clean" in result
        assert "quarantine" in result
        assert "dq_log" in result
        assert len(result["dq_log"]) > 0
