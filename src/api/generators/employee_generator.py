"""Employee / clinician record generator.

Generates ~1,200 employees assigned to 80 locations with realistic:
- Role distribution: 20% Provider, 15% RN, 25% MA, 10% RadTech, 10% OfficeMgr, 20% FrontDesk
- Tenure: right-skewed distribution (many new, few very long)
- Attrition: 22% support staff, 12% providers annually
- Schedule types: Full-time, Part-time, PRN/Float
- Manager hierarchy: each location has an Office Manager who manages support staff
"""

from datetime import date, timedelta

from src.api.config import settings
from src.api.generators.organization import get_location_ids, get_locations
from src.api.generators.seed import get_seeded_faker, get_seeded_random

# ---------------------------------------------------------------------------
# Role configuration
# ---------------------------------------------------------------------------

ROLE_CONFIG: dict[str, dict] = {
    "Provider": {
        "weight": 0.20,
        "titles": [
            "Physician (MD)",
            "Physician (DO)",
            "Physician Assistant",
            "Nurse Practitioner",
        ],
        "levels": ["Senior", "Staff", "Junior"],
        "is_clinical": True,
        "attrition_rate": 0.12,
    },
    "RN": {
        "weight": 0.15,
        "titles": ["Registered Nurse"],
        "levels": ["Senior RN", "RN II", "RN I"],
        "is_clinical": True,
        "attrition_rate": 0.22,
    },
    "MA": {
        "weight": 0.25,
        "titles": ["Medical Assistant", "Certified Medical Assistant"],
        "levels": ["Senior MA", "MA II", "MA I"],
        "is_clinical": True,
        "attrition_rate": 0.22,
    },
    "RadTech": {
        "weight": 0.10,
        "titles": ["Radiology Technologist"],
        "levels": ["Senior", "Staff"],
        "is_clinical": True,
        "attrition_rate": 0.22,
    },
    "OfficeMgr": {
        "weight": 0.10,
        "titles": ["Office Manager"],
        "levels": ["Office Manager"],
        "is_clinical": False,
        "attrition_rate": 0.18,
    },
    "FrontDesk": {
        "weight": 0.20,
        "titles": [
            "Front Desk Coordinator",
            "Patient Services Representative",
            "Receptionist",
        ],
        "levels": ["Senior", "Staff", "Entry"],
        "is_clinical": False,
        "attrition_rate": 0.22,
    },
}

# Schedule type distribution by role
SCHEDULE_WEIGHTS: dict[str, list[tuple[str, float]]] = {
    "Provider": [("Full-time", 0.55), ("Part-time", 0.25), ("PRN/Float", 0.20)],
    "RN": [("Full-time", 0.60), ("Part-time", 0.25), ("PRN/Float", 0.15)],
    "MA": [("Full-time", 0.70), ("Part-time", 0.25), ("PRN/Float", 0.05)],
    "RadTech": [("Full-time", 0.75), ("Part-time", 0.20), ("PRN/Float", 0.05)],
    "OfficeMgr": [("Full-time", 0.95), ("Part-time", 0.05), ("PRN/Float", 0.00)],
    "FrontDesk": [("Full-time", 0.55), ("Part-time", 0.35), ("PRN/Float", 0.10)],
}


def _weighted_choice(
    options: list[tuple[str, float]],
    rng_inst: "random.Random",
) -> str:
    """Pick from a list of (value, weight) tuples."""
    values = [o[0] for o in options]
    weights = [o[1] for o in options]
    return rng_inst.choices(values, weights=weights, k=1)[0]


def _generate_hire_date(
    rng_inst: "random.Random",
    location_opened: date,
) -> date:
    """Generate a right-skewed hire date (many recent hires, fewer long-tenured).

    Args:
        rng_inst: Seeded random instance.
        location_opened: Earliest possible hire date.

    Returns:
        A hire date between location_opened and the reference date.
    """
    reference_date = date(2026, 2, 1)
    max_days = (reference_date - location_opened).days
    if max_days <= 0:
        return reference_date

    # Right-skewed: use beta distribution (alpha=1.5, beta=5) so most hires
    # are relatively recent.
    fraction = rng_inst.betavariate(1.5, 5.0)
    days_ago = int(fraction * max_days)
    return reference_date - timedelta(days=days_ago)


def generate_employees() -> list[dict]:
    """Generate the full employee roster.

    Returns:
        A list of employee dictionaries ready for API serialization.
    """
    fake = get_seeded_faker(offset=200)
    rng = get_seeded_random(offset=200)

    locations = get_locations()
    num_employees = settings.num_employees

    # Build role list according to weights
    role_types: list[str] = []
    for role, cfg in ROLE_CONFIG.items():
        count = round(cfg["weight"] * num_employees)
        role_types.extend([role] * count)

    # Pad or trim to exact employee count
    while len(role_types) < num_employees:
        role_types.append(rng.choice(list(ROLE_CONFIG.keys())))
    role_types = role_types[:num_employees]
    rng.shuffle(role_types)

    # Distribute employees across locations proportionally to budgeted FTE
    total_fte = sum(
        loc["budgeted_provider_fte"] + loc["budgeted_support_fte"]
        for loc in locations
    )
    loc_weights = [
        (loc["budgeted_provider_fte"] + loc["budgeted_support_fte"]) / total_fte
        for loc in locations
    ]

    # Assign each employee to a location
    location_assignments: list[int] = rng.choices(
        range(len(locations)), weights=loc_weights, k=num_employees
    )

    # Track office managers per location for manager assignment
    office_managers: dict[str, str] = {}
    employees: list[dict] = []

    for i in range(num_employees):
        emp_id = f"EMP-{i + 1:05d}"
        role_type = role_types[i]
        loc_idx = location_assignments[i]
        loc = locations[loc_idx]
        location_id = loc["location_id"]

        # Location opened_date is already a date object
        opened = loc["opened_date"]

        # Name & email
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@wellnow.com"

        # Job title and level
        cfg = ROLE_CONFIG[role_type]
        job_title = rng.choice(cfg["titles"])
        job_level = rng.choice(cfg["levels"])

        # Schedule type
        schedule_type = _weighted_choice(SCHEDULE_WEIGHTS[role_type], rng)

        # Hire date (right-skewed toward recent)
        hire_date = _generate_hire_date(rng, opened)

        # Determine if terminated (based on annualized attrition rate)
        tenure_days = (date(2026, 2, 1) - hire_date).days
        tenure_years = tenure_days / 365.25
        annual_rate = cfg["attrition_rate"]
        # Probability of having left = 1 - (1 - annual_rate)^tenure_years
        survival_prob = (1 - annual_rate) ** tenure_years
        is_terminated = rng.random() > survival_prob

        termination_date = None
        status = "Active"
        if is_terminated:
            # Termination happened somewhere during tenure
            term_offset = rng.randint(1, max(1, tenure_days - 1))
            termination_date = hire_date + timedelta(days=term_offset)
            if termination_date > date(2026, 2, 1):
                termination_date = date(2026, 1, 15)
            status = "Terminated"

        # Is people manager?
        is_people_manager = role_type == "OfficeMgr"

        # Track office managers for this location
        if role_type == "OfficeMgr" and status == "Active":
            office_managers[location_id] = emp_id

        # Manager assignment — will be set in second pass
        manager_employee_id = None

        employees.append(
            {
                "employee_id": emp_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "hire_date": hire_date,
                "termination_date": termination_date,
                "status": status,
                "role_type": role_type,
                "job_title": job_title,
                "job_level": job_level,
                "schedule_type": schedule_type,
                "location_id": location_id,
                "manager_employee_id": manager_employee_id,
                "is_people_manager": is_people_manager,
            }
        )

    # Second pass: assign managers (office manager at same location, or None)
    for emp in employees:
        if emp["role_type"] == "OfficeMgr":
            # Office managers report to no one at the location level
            emp["manager_employee_id"] = None
        else:
            mgr = office_managers.get(emp["location_id"])
            emp["manager_employee_id"] = mgr

    return employees


# Module-level cache
_employees_cache: list[dict] | None = None


def get_employees() -> list[dict]:
    """Return the cached employee list, generating on first call.

    Returns:
        Deterministic list of employee dictionaries.
    """
    global _employees_cache
    if _employees_cache is None:
        _employees_cache = generate_employees()
    return _employees_cache


def get_active_employees() -> list[dict]:
    """Return only currently active employees.

    Returns:
        Filtered list of employees with status 'Active'.
    """
    return [e for e in get_employees() if e["status"] == "Active"]


def get_employees_by_location(location_id: str) -> list[dict]:
    """Return employees assigned to a specific location.

    Args:
        location_id: The location ID to filter by.

    Returns:
        Filtered list of employees at the given location.
    """
    return [e for e in get_employees() if e["location_id"] == location_id]
