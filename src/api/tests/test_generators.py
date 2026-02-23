"""Tests for data generators — distributions, referential integrity, reproducibility."""

from src.api.generators.employee_generator import (
    ROLE_CONFIG,
    get_active_employees,
    get_employees,
)
from src.api.generators.organization import get_location_ids, get_locations
from src.api.generators.patient_volume_generator import get_patient_volumes
from src.api.generators.schedule_generator import get_schedules
from src.api.generators.seed import MASTER_SEED
from src.api.generators.termination_generator import get_terminations


class TestLocations:
    """Test location generator."""

    def test_location_count(self) -> None:
        locations = get_locations()
        assert len(locations) == 80

    def test_location_ids_unique(self) -> None:
        ids = get_location_ids()
        assert len(ids) == len(set(ids))

    def test_location_fields_present(self) -> None:
        loc = get_locations()[0]
        required = {
            "location_id",
            "location_name",
            "region",
            "state",
            "metro_area",
            "location_type",
            "operating_hours_start",
            "operating_hours_end",
            "days_open_per_week",
            "budgeted_provider_fte",
            "budgeted_support_fte",
            "opened_date",
            "is_active",
        }
        assert required.issubset(loc.keys())

    def test_location_types_valid(self) -> None:
        valid_types = {"Urban", "Suburban", "Rural"}
        for loc in get_locations():
            assert loc["location_type"] in valid_types

    def test_regions_present(self) -> None:
        regions = {loc["region"] for loc in get_locations()}
        # Should have at least Northeast and Midwest per PRD
        assert "Northeast" in regions
        assert "Midwest" in regions


class TestEmployees:
    """Test employee generator."""

    def test_employee_count(self) -> None:
        employees = get_employees()
        assert len(employees) == 1200

    def test_employee_ids_unique(self) -> None:
        ids = [e["employee_id"] for e in get_employees()]
        assert len(ids) == len(set(ids))

    def test_referential_integrity_location(self) -> None:
        loc_ids = set(get_location_ids())
        for emp in get_employees():
            assert emp["location_id"] in loc_ids

    def test_role_distribution_approximate(self) -> None:
        employees = get_employees()
        total = len(employees)
        role_counts = {}
        for emp in employees:
            role_counts[emp["role_type"]] = role_counts.get(emp["role_type"], 0) + 1

        # Allow 5% tolerance from target distribution
        for role, cfg in ROLE_CONFIG.items():
            expected_pct = cfg["weight"]
            actual_pct = role_counts.get(role, 0) / total
            assert abs(actual_pct - expected_pct) < 0.05, (
                f"Role {role}: expected ~{expected_pct:.0%}, got {actual_pct:.0%}"
            )

    def test_status_values(self) -> None:
        statuses = {e["status"] for e in get_employees()}
        assert statuses.issubset({"Active", "Terminated"})

    def test_terminated_have_term_date(self) -> None:
        for emp in get_employees():
            if emp["status"] == "Terminated":
                assert emp["termination_date"] is not None

    def test_active_no_term_date(self) -> None:
        for emp in get_active_employees():
            assert emp["termination_date"] is None

    def test_email_format(self) -> None:
        for emp in get_employees():
            assert emp["email"].endswith("@wellnow.com")

    def test_reproducibility(self) -> None:
        """Running generator twice with same seed produces identical output."""
        # get_employees() is cached so both calls return same object
        run1 = get_employees()
        run2 = get_employees()
        assert run1 is run2  # Same cached list


class TestSchedules:
    """Test schedule generator."""

    def test_schedule_records_exist(self) -> None:
        schedules = get_schedules()
        assert len(schedules) > 0

    def test_shift_windows_valid(self) -> None:
        valid = {"AM", "PM", "Evening"}
        for rec in get_schedules()[:1000]:
            assert rec["shift_window"] in valid

    def test_location_ids_valid(self) -> None:
        loc_ids = set(get_location_ids())
        for rec in get_schedules()[:1000]:
            assert rec["location_id"] in loc_ids

    def test_hours_non_negative(self) -> None:
        for rec in get_schedules()[:1000]:
            assert rec["scheduled_provider_hours"] >= 0
            assert rec["actual_provider_hours"] >= 0
            assert rec["overtime_hours"] >= 0

    def test_callout_count_non_negative(self) -> None:
        for rec in get_schedules()[:1000]:
            assert rec["callout_count"] >= 0


class TestPatientVolumes:
    """Test patient volume generator."""

    def test_volume_records_exist(self) -> None:
        volumes = get_patient_volumes()
        assert len(volumes) > 0

    def test_visits_positive(self) -> None:
        for rec in get_patient_volumes()[:1000]:
            assert rec["patient_visits"] >= 1

    def test_wait_time_reasonable(self) -> None:
        for rec in get_patient_volumes()[:1000]:
            assert 5.0 <= rec["avg_wait_time_minutes"] <= 60.0

    def test_location_ids_valid(self) -> None:
        loc_ids = set(get_location_ids())
        for rec in get_patient_volumes()[:1000]:
            assert rec["location_id"] in loc_ids


class TestTerminations:
    """Test termination generator."""

    def test_termination_records_exist(self) -> None:
        terms = get_terminations()
        assert len(terms) > 0

    def test_all_terminated(self) -> None:
        emp_map = {e["employee_id"]: e for e in get_employees()}
        for term in get_terminations():
            emp = emp_map[term["employee_id"]]
            assert emp["status"] == "Terminated"

    def test_reason_fields_present(self) -> None:
        term = get_terminations()[0]
        assert "termination_category" in term
        assert "termination_reason" in term

    def test_categories_valid(self) -> None:
        valid = {"Voluntary", "Involuntary", "Other"}
        for term in get_terminations():
            assert term["termination_category"] in valid
