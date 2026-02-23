"""Tests for the transformation module."""

from datetime import date

import pytest

from src.etl.transform import (
    _safe_divide,
    _tenure_band,
    build_dim_employee,
    build_dim_job,
    build_dim_location,
    build_fact_daily_staffing,
    build_fact_shift_gap,
    transform_all,
)


class TestHelpers:
    def test_safe_divide_normal(self) -> None:
        assert _safe_divide(10, 2) == 5.0

    def test_safe_divide_zero(self) -> None:
        assert _safe_divide(10, 0) == 0.0

    def test_tenure_band_new(self) -> None:
        assert _tenure_band(0.5) == "0-1yr"

    def test_tenure_band_mid(self) -> None:
        assert _tenure_band(4.0) == "3-5yr"

    def test_tenure_band_long(self) -> None:
        assert _tenure_band(12.0) == "10+yr"


class TestDimEmployee:
    def test_row_count(
        self, sample_employees: list[dict], sample_locations: list[dict]
    ) -> None:
        df = build_dim_employee(sample_employees, sample_locations, "run-1")
        assert len(df) == 3

    def test_derived_fields(
        self, sample_employees: list[dict], sample_locations: list[dict]
    ) -> None:
        df = build_dim_employee(sample_employees, sample_locations, "run-1")
        assert "full_name" in df.columns
        assert "tenure_band" in df.columns
        assert "is_new_hire" in df.columns
        assert "is_provider" in df.columns


class TestDimLocation:
    def test_row_count(self, sample_locations: list[dict]) -> None:
        df = build_dim_location(sample_locations)
        assert len(df) == 1
        assert df.iloc[0]["location_key"] == 1

    def test_fields(self, sample_locations: list[dict]) -> None:
        df = build_dim_location(sample_locations)
        assert "region" in df.columns
        assert "is_active" in df.columns


class TestDimJob:
    def test_unique_jobs(self, sample_employees: list[dict]) -> None:
        df = build_dim_job(sample_employees)
        assert len(df) == 3  # 3 different (title, role) combos

    def test_clinical_flag(self, sample_employees: list[dict]) -> None:
        df = build_dim_job(sample_employees)
        provider_row = df[df["role_type"] == "Provider"].iloc[0]
        assert provider_row["is_clinical"] == True
        assert provider_row["is_provider"] == True


class TestFactDailyStaffing:
    def test_aggregation(
        self,
        sample_schedules: list[dict],
        sample_volumes: list[dict],
        sample_locations: list[dict],
    ) -> None:
        df = build_fact_daily_staffing(
            sample_schedules, sample_volumes, sample_locations, "run-1"
        )
        # Two shifts on same date+loc aggregate into one row
        assert len(df) == 1
        row = df.iloc[0]
        assert row["patient_visits"] == 60
        assert row["coverage_score"] > 0

    def test_derived_metrics(
        self,
        sample_schedules: list[dict],
        sample_volumes: list[dict],
        sample_locations: list[dict],
    ) -> None:
        df = build_fact_daily_staffing(
            sample_schedules, sample_volumes, sample_locations, "run-1"
        )
        row = df.iloc[0]
        assert "patients_per_provider_hour" in df.columns
        assert "labor_cost_per_visit" in df.columns
        assert row["labor_cost_per_visit"] > 0


class TestFactShiftGap:
    def test_gap_detection(
        self, sample_schedules: list[dict], sample_locations: list[dict]
    ) -> None:
        df = build_fact_shift_gap(sample_schedules, sample_locations, "run-1")
        assert len(df) == 2  # One per shift

        # PM shift has actual_providers=1 < required=2 → gap_flag=True
        pm_row = df[df["shift_window"] == "PM"].iloc[0]
        assert pm_row["gap_flag"] == True
        assert pm_row["gap_hours"] > 0

        # AM shift is fully staffed
        am_row = df[df["shift_window"] == "AM"].iloc[0]
        assert am_row["gap_flag"] == False


class TestTransformAll:
    def test_returns_all_tables(
        self,
        sample_employees: list[dict],
        sample_locations: list[dict],
        sample_schedules: list[dict],
        sample_volumes: list[dict],
    ) -> None:
        clean = {
            "workers": sample_employees,
            "locations": sample_locations,
            "schedules": sample_schedules,
            "patient-volume": sample_volumes,
        }
        tables = transform_all(clean, run_id="run-test")
        assert "dim_employee" in tables
        assert "dim_location" in tables
        assert "dim_job" in tables
        assert "fact_daily_staffing" in tables
        assert "fact_shift_gap" in tables
