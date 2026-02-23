"""Patient volume data generator.

Generates daily patient visit counts per location correlated with:
- Season: winter peaks (Nov-Feb), summer troughs (Jun-Aug)
- Day of week: Monday + Saturday peaks for urgent care
- Location type: Urban > Suburban > Rural base volumes
- Staffing levels: wait times increase when understaffed
"""

from datetime import date, timedelta

from src.api.config import settings
from src.api.generators.organization import get_locations
from src.api.generators.seed import get_seeded_random

# Base daily patient visits by location type
BASE_DAILY_VISITS: dict[str, int] = {
    "Urban": 85,
    "Suburban": 55,
    "Rural": 30,
}

# Seasonal multiplier (same as schedule_generator for consistency)
SEASONAL_MULTIPLIER: dict[int, float] = {
    1: 1.15,
    2: 1.10,
    3: 1.00,
    4: 0.95,
    5: 0.90,
    6: 0.85,
    7: 0.82,
    8: 0.85,
    9: 0.92,
    10: 0.98,
    11: 1.12,
    12: 1.18,
}

# Day-of-week multiplier
DOW_MULTIPLIER: dict[int, float] = {
    0: 1.15,  # Monday
    1: 1.00,
    2: 0.95,
    3: 0.95,
    4: 1.00,
    5: 1.10,  # Saturday
    6: 0.90,  # Sunday
}

# Base wait time by location type (minutes)
BASE_WAIT_TIME: dict[str, float] = {
    "Urban": 22.0,
    "Suburban": 18.0,
    "Rural": 14.0,
}


def generate_patient_volumes() -> list[dict]:
    """Generate 18 months of daily patient volume records per location.

    Returns:
        A list of daily volume dictionaries.
    """
    rng = get_seeded_random(offset=400)
    locations = get_locations()
    history_months = settings.history_months

    reference_date = date(2026, 2, 1)
    start_year = reference_date.year
    start_month = reference_date.month - history_months
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    start_date = date(start_year, start_month, 1)

    records: list[dict] = []
    current = start_date

    while current < reference_date:
        month = current.month
        dow = current.weekday()
        seasonal = SEASONAL_MULTIPLIER[month]
        dow_mult = DOW_MULTIPLIER[dow]

        for loc in locations:
            loc_type = loc["location_type"]
            base = BASE_DAILY_VISITS[loc_type]
            base_wait = BASE_WAIT_TIME[loc_type]

            # Add random noise (±15%)
            noise = rng.uniform(0.85, 1.15)
            visits = max(1, round(base * seasonal * dow_mult * noise))

            # Wait time correlates with volume: higher volume = longer waits
            # Also add noise
            volume_ratio = visits / base
            wait_noise = rng.uniform(0.8, 1.2)
            wait_time = round(base_wait * volume_ratio * wait_noise, 1)
            wait_time = max(5.0, min(60.0, wait_time))  # clamp 5-60 min

            records.append(
                {
                    "location_id": loc["location_id"],
                    "visit_date": current,
                    "patient_visits": visits,
                    "avg_wait_time_minutes": wait_time,
                }
            )

        current += timedelta(days=1)

    return records


# Module-level cache
_volumes_cache: list[dict] | None = None


def get_patient_volumes() -> list[dict]:
    """Return the cached patient volume dataset, generating on first call.

    Returns:
        Deterministic list of daily volume dictionaries.
    """
    global _volumes_cache
    if _volumes_cache is None:
        _volumes_cache = generate_patient_volumes()
    return _volumes_cache


def get_volumes_filtered(
    start_date: date | None = None,
    end_date: date | None = None,
    location_id: str | None = None,
) -> list[dict]:
    """Return patient volumes filtered by date range and/or location.

    Args:
        start_date: Inclusive start date filter.
        end_date: Inclusive end date filter.
        location_id: Filter to a single location.

    Returns:
        Filtered list of volume records.
    """
    data = get_patient_volumes()
    if location_id:
        data = [r for r in data if r["location_id"] == location_id]
    if start_date:
        data = [r for r in data if r["visit_date"] >= start_date]
    if end_date:
        data = [r for r in data if r["visit_date"] <= end_date]
    return data
