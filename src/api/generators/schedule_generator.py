"""Schedule / shift data generator.

Generates 18 months of daily shift records for every location with:
- 3 shifts per location per day (AM 8-12, PM 12-16, Evening 16-20)
- Seasonal staffing patterns
- Realistic callout rates (5-8%), higher on weekends
- Overtime clustered at chronically understaffed locations
- Scheduled vs actual provider/support hours
"""

from datetime import date, timedelta

from src.api.config import settings
from src.api.generators.employee_generator import get_active_employees
from src.api.generators.organization import get_locations
from src.api.generators.seed import get_seeded_random

SHIFT_WINDOWS: list[str] = ["AM", "PM", "Evening"]
SHIFT_HOURS: dict[str, int] = {"AM": 4, "PM": 4, "Evening": 4}

# Seasonal demand multiplier by month (1-indexed).
# Winter peaks (Nov-Feb), summer troughs (Jun-Aug).
SEASONAL_MULTIPLIER: dict[int, float] = {
    1: 1.15,   # January — flu season
    2: 1.10,   # February
    3: 1.00,   # March
    4: 0.95,   # April
    5: 0.90,   # May
    6: 0.85,   # June — summer trough
    7: 0.82,   # July
    8: 0.85,   # August
    9: 0.92,   # September — back to school
    10: 0.98,  # October
    11: 1.12,  # November — flu ramp
    12: 1.18,  # December — peak flu/holidays
}

# Day-of-week demand multiplier (0=Monday … 6=Sunday).
# Monday and Saturday peaks for urgent care.
DOW_MULTIPLIER: dict[int, float] = {
    0: 1.15,  # Monday
    1: 1.00,  # Tuesday
    2: 0.95,  # Wednesday
    3: 0.95,  # Thursday
    4: 1.00,  # Friday
    5: 1.10,  # Saturday
    6: 0.90,  # Sunday
}


def _required_providers(
    location_type: str,
    budgeted_fte: float,
    seasonal: float,
    dow: float,
) -> int:
    """Calculate required providers for a single shift.

    Args:
        location_type: Urban / Suburban / Rural.
        budgeted_fte: Location's budgeted provider FTE.
        seasonal: Seasonal demand multiplier.
        dow: Day-of-week demand multiplier.

    Returns:
        Integer number of required providers for the shift.
    """
    # Each shift is 1/3 of the day; budgeted_fte is daily total
    base = budgeted_fte / len(SHIFT_WINDOWS)
    return max(1, round(base * seasonal * dow))


def generate_schedules() -> list[dict]:
    """Generate the full schedule dataset.

    Returns:
        A list of shift record dictionaries covering 18 months of history.
    """
    rng = get_seeded_random(offset=300)
    locations = get_locations()
    history_months = settings.history_months

    # Date range: 18 months back from reference date
    reference_date = date(2026, 2, 1)
    start_year = reference_date.year
    start_month = reference_date.month - history_months
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    start_date = date(start_year, start_month, 1)

    # Pre-compute location staffing context: identify chronically understaffed
    # locations (20% of locations will have higher callout/overtime)
    understaffed_locs = set(
        loc["location_id"]
        for loc in rng.sample(locations, k=max(1, len(locations) // 5))
    )

    # Count active employees per location per role type for realistic headcount
    active_employees = get_active_employees()
    providers_by_loc: dict[str, int] = {}
    support_by_loc: dict[str, int] = {}
    for emp in active_employees:
        lid = emp["location_id"]
        if emp["role_type"] == "Provider":
            providers_by_loc[lid] = providers_by_loc.get(lid, 0) + 1
        else:
            support_by_loc[lid] = support_by_loc.get(lid, 0) + 1

    records: list[dict] = []
    current = start_date

    while current < reference_date:
        month = current.month
        dow = current.weekday()
        seasonal = SEASONAL_MULTIPLIER[month]
        dow_mult = DOW_MULTIPLIER[dow]

        for loc in locations:
            loc_id = loc["location_id"]
            loc_type = loc["location_type"]
            budgeted_prov_fte = loc["budgeted_provider_fte"]
            budgeted_supp_fte = loc["budgeted_support_fte"]
            is_understaffed = loc_id in understaffed_locs
            is_weekend = dow >= 5

            # Callout rate: 5-8% baseline, higher on weekends and at
            # chronically understaffed locations
            base_callout = 0.06
            if is_weekend:
                base_callout += 0.02
            if is_understaffed:
                base_callout += 0.03

            for shift in SHIFT_WINDOWS:
                hours = SHIFT_HOURS[shift]

                # Required providers
                req_prov = _required_providers(
                    loc_type, budgeted_prov_fte, seasonal, dow_mult
                )

                # Scheduled providers — usually meets or slightly exceeds req
                avail_provs = providers_by_loc.get(loc_id, req_prov)
                shift_provs = max(1, round(avail_provs / len(SHIFT_WINDOWS)))
                sched_prov = min(shift_provs, req_prov + rng.randint(0, 1))
                sched_prov = max(1, sched_prov)

                # Callouts reduce actual from scheduled
                callout_count = 0
                actual_prov = sched_prov
                for _ in range(sched_prov):
                    if rng.random() < base_callout:
                        callout_count += 1
                        actual_prov -= 1
                actual_prov = max(0, actual_prov)

                # Support staff
                supp_avail = support_by_loc.get(loc_id, 3)
                sched_supp_per_shift = max(
                    1, round(supp_avail / len(SHIFT_WINDOWS))
                )
                actual_supp = sched_supp_per_shift
                for _ in range(sched_supp_per_shift):
                    if rng.random() < base_callout * 0.7:
                        actual_supp -= 1
                actual_supp = max(0, actual_supp)

                # Hours
                sched_prov_hrs = float(sched_prov * hours)
                actual_prov_hrs = float(actual_prov * hours)
                sched_supp_hrs = float(sched_supp_per_shift * hours)
                actual_supp_hrs = float(actual_supp * hours)

                # Overtime: when actual < required, remaining staff work extra
                overtime_hrs = 0.0
                if actual_prov < req_prov and actual_prov > 0:
                    gap_hours = float((req_prov - actual_prov) * hours)
                    # Some of the gap is covered by overtime (50-80%)
                    coverage = rng.uniform(0.5, 0.8)
                    overtime_hrs = round(gap_hours * coverage, 1)
                    actual_prov_hrs += overtime_hrs

                # Understaffed locations get extra random overtime
                if is_understaffed and rng.random() < 0.3:
                    extra_ot = round(rng.uniform(0.5, 2.0), 1)
                    overtime_hrs += extra_ot
                    actual_prov_hrs += extra_ot

                records.append(
                    {
                        "location_id": loc_id,
                        "shift_date": current,
                        "shift_window": shift,
                        "scheduled_provider_hours": round(sched_prov_hrs, 1),
                        "actual_provider_hours": round(actual_prov_hrs, 1),
                        "scheduled_support_hours": round(sched_supp_hrs, 1),
                        "actual_support_hours": round(actual_supp_hrs, 1),
                        "overtime_hours": round(overtime_hrs, 1),
                        "callout_count": callout_count,
                        "required_providers": req_prov,
                        "scheduled_providers": sched_prov,
                        "actual_providers": actual_prov,
                    }
                )

        current += timedelta(days=1)

    return records


# Module-level cache
_schedules_cache: list[dict] | None = None


def get_schedules() -> list[dict]:
    """Return the cached schedule dataset, generating on first call.

    Returns:
        Deterministic list of shift record dictionaries.
    """
    global _schedules_cache
    if _schedules_cache is None:
        _schedules_cache = generate_schedules()
    return _schedules_cache


def get_schedules_filtered(
    start_date: date | None = None,
    end_date: date | None = None,
    location_id: str | None = None,
) -> list[dict]:
    """Return schedules filtered by date range and/or location.

    Args:
        start_date: Inclusive start date filter.
        end_date: Inclusive end date filter.
        location_id: Filter to a single location.

    Returns:
        Filtered list of shift records.
    """
    data = get_schedules()
    if location_id:
        data = [r for r in data if r["location_id"] == location_id]
    if start_date:
        data = [r for r in data if r["shift_date"] >= start_date]
    if end_date:
        data = [r for r in data if r["shift_date"] <= end_date]
    return data
