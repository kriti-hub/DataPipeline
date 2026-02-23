"""Location and organizational structure generator.

Generates ~80 WellNow urgent care clinic locations across 15 states following
a Northeast + Midwest heavy geographic footprint with a mix of Urban (40%),
Suburban (45%), and Rural (15%) location types.
"""

from datetime import date

from src.api.config import settings
from src.api.generators.seed import get_seeded_faker, get_seeded_random

# ---------------------------------------------------------------------------
# Constants — geographic & operational
# ---------------------------------------------------------------------------

# WellNow operates primarily in the Northeast and Midwest.
# state: (region, [(metro_area, location_type, weight)])
STATE_CONFIG: dict[str, tuple[str, list[tuple[str, str, float]]]] = {
    "NY": (
        "Northeast",
        [
            ("New York City", "Urban", 0.30),
            ("Buffalo", "Suburban", 0.25),
            ("Syracuse", "Suburban", 0.20),
            ("Rochester", "Suburban", 0.15),
            ("Albany", "Rural", 0.10),
        ],
    ),
    "NJ": (
        "Northeast",
        [
            ("Newark", "Urban", 0.40),
            ("Jersey City", "Suburban", 0.35),
            ("Trenton", "Rural", 0.25),
        ],
    ),
    "PA": (
        "Northeast",
        [
            ("Philadelphia", "Urban", 0.35),
            ("Pittsburgh", "Suburban", 0.30),
            ("Allentown", "Suburban", 0.20),
            ("Scranton", "Rural", 0.15),
        ],
    ),
    "CT": (
        "Northeast",
        [
            ("Hartford", "Suburban", 0.50),
            ("New Haven", "Urban", 0.30),
            ("Stamford", "Suburban", 0.20),
        ],
    ),
    "MA": (
        "Northeast",
        [
            ("Boston", "Urban", 0.45),
            ("Worcester", "Suburban", 0.30),
            ("Springfield", "Rural", 0.25),
        ],
    ),
    "IL": (
        "Midwest",
        [
            ("Chicago", "Urban", 0.40),
            ("Naperville", "Suburban", 0.30),
            ("Peoria", "Rural", 0.15),
            ("Rockford", "Suburban", 0.15),
        ],
    ),
    "OH": (
        "Midwest",
        [
            ("Columbus", "Urban", 0.30),
            ("Cleveland", "Urban", 0.25),
            ("Cincinnati", "Suburban", 0.25),
            ("Dayton", "Rural", 0.20),
        ],
    ),
    "MI": (
        "Midwest",
        [
            ("Detroit", "Urban", 0.35),
            ("Grand Rapids", "Suburban", 0.30),
            ("Ann Arbor", "Suburban", 0.20),
            ("Lansing", "Rural", 0.15),
        ],
    ),
    "IN": (
        "Midwest",
        [
            ("Indianapolis", "Urban", 0.40),
            ("Fort Wayne", "Suburban", 0.30),
            ("Bloomington", "Rural", 0.30),
        ],
    ),
    "WI": (
        "Midwest",
        [
            ("Milwaukee", "Urban", 0.35),
            ("Madison", "Suburban", 0.35),
            ("Green Bay", "Rural", 0.30),
        ],
    ),
    "VA": (
        "Southeast",
        [
            ("Richmond", "Urban", 0.40),
            ("Virginia Beach", "Suburban", 0.35),
            ("Roanoke", "Rural", 0.25),
        ],
    ),
    "NC": (
        "Southeast",
        [
            ("Charlotte", "Urban", 0.40),
            ("Raleigh", "Suburban", 0.35),
            ("Asheville", "Rural", 0.25),
        ],
    ),
    "FL": (
        "Southeast",
        [
            ("Orlando", "Urban", 0.35),
            ("Tampa", "Suburban", 0.35),
            ("Jacksonville", "Suburban", 0.30),
        ],
    ),
    "TX": (
        "Southwest",
        [
            ("Dallas", "Urban", 0.35),
            ("Houston", "Urban", 0.30),
            ("Austin", "Suburban", 0.20),
            ("San Antonio", "Suburban", 0.15),
        ],
    ),
    "AZ": (
        "Southwest",
        [
            ("Phoenix", "Urban", 0.45),
            ("Tucson", "Suburban", 0.30),
            ("Scottsdale", "Suburban", 0.25),
        ],
    ),
}

# Approximate location distribution per state (must sum to num_locations)
# Northeast + Midwest heavy per PRD requirement
STATE_LOCATION_COUNTS: dict[str, int] = {
    "NY": 14,
    "NJ": 6,
    "PA": 8,
    "CT": 4,
    "MA": 5,
    "IL": 9,
    "OH": 7,
    "MI": 6,
    "IN": 4,
    "WI": 4,
    "VA": 3,
    "NC": 3,
    "FL": 3,
    "TX": 2,
    "AZ": 2,
}

# Budgeted FTE by location type
BUDGETED_FTE: dict[str, tuple[float, float]] = {
    "Urban": (4.0, 8.0),       # (provider_fte, support_fte)
    "Suburban": (3.0, 6.0),
    "Rural": (2.0, 4.0),
}


def _pick_metro(
    metros: list[tuple[str, str, float]],
    rng_inst: "random.Random",
) -> tuple[str, str]:
    """Weighted random pick of (metro_area, location_type)."""
    names = [m[0] for m in metros]
    types = [m[1] for m in metros]
    weights = [m[2] for m in metros]
    idx = rng_inst.choices(range(len(names)), weights=weights, k=1)[0]
    return names[idx], types[idx]


def generate_locations() -> list[dict]:
    """Generate all WellNow clinic locations.

    Returns:
        A list of location dictionaries ready for API serialization.
    """
    import random as _rand_mod  # only for type hint in _pick_metro

    fake = get_seeded_faker(offset=100)
    rng_inst = get_seeded_random(offset=100)
    locations: list[dict] = []
    loc_index = 1

    for state, count in STATE_LOCATION_COUNTS.items():
        region, metros = STATE_CONFIG[state]
        for _ in range(count):
            metro_area, location_type = _pick_metro(metros, rng_inst)
            provider_fte, support_fte = BUDGETED_FTE[location_type]
            # Small random variation in budgeted FTE
            provider_fte = round(
                provider_fte + rng_inst.uniform(-0.5, 0.5), 1
            )
            support_fte = round(
                support_fte + rng_inst.uniform(-1.0, 1.0), 1
            )
            # Opened date: spread across 2018-2024
            opened_year = rng_inst.randint(2018, 2024)
            opened_month = rng_inst.randint(1, 12)
            opened_day = rng_inst.randint(1, 28)

            locations.append(
                {
                    "location_id": f"LOC-{loc_index:03d}",
                    "location_name": f"WellNow {metro_area} {loc_index}",
                    "region": region,
                    "state": state,
                    "metro_area": metro_area,
                    "location_type": location_type,
                    "operating_hours_start": "08:00",
                    "operating_hours_end": "20:00",
                    "days_open_per_week": 7,
                    "budgeted_provider_fte": max(1.0, provider_fte),
                    "budgeted_support_fte": max(2.0, support_fte),
                    "opened_date": date(
                        opened_year, opened_month, opened_day
                    ),
                    "is_active": True,
                }
            )
            loc_index += 1

    return locations


# Module-level cached locations — generated once, reused by all routers
_locations_cache: list[dict] | None = None


def get_locations() -> list[dict]:
    """Return the cached location list, generating on first call.

    Returns:
        Deterministic list of location dictionaries.
    """
    global _locations_cache
    if _locations_cache is None:
        _locations_cache = generate_locations()
    return _locations_cache


def get_location_ids() -> list[str]:
    """Return a list of all location IDs.

    Returns:
        Sorted list of location_id strings.
    """
    return [loc["location_id"] for loc in get_locations()]
