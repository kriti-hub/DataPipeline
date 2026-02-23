"""Termination event generator.

Extracts termination records from the employee dataset and enriches them
with exit reasons following realistic distributions:
- Voluntary (60%): Resignation, Better Opportunity, Relocation, Personal
- Involuntary (25%): Performance, Attendance, Policy Violation
- Other (15%): Retirement, End of Contract, Mutual Agreement
"""

from datetime import date

from src.api.generators.employee_generator import get_employees
from src.api.generators.seed import get_seeded_random
from src.api.models.common import PaginationMeta

# Termination reason distribution
TERMINATION_REASONS: list[tuple[str, str, float]] = [
    # (category, reason, weight)
    ("Voluntary", "Resignation", 0.25),
    ("Voluntary", "Better Opportunity", 0.15),
    ("Voluntary", "Relocation", 0.10),
    ("Voluntary", "Personal Reasons", 0.10),
    ("Involuntary", "Performance", 0.10),
    ("Involuntary", "Attendance", 0.10),
    ("Involuntary", "Policy Violation", 0.05),
    ("Other", "Retirement", 0.05),
    ("Other", "End of Contract", 0.05),
    ("Other", "Mutual Agreement", 0.05),
]


def generate_terminations() -> list[dict]:
    """Generate termination records from the employee dataset.

    Returns:
        A list of termination event dictionaries.
    """
    rng = get_seeded_random(offset=500)
    employees = get_employees()

    reasons = [r[1] for r in TERMINATION_REASONS]
    categories = [r[0] for r in TERMINATION_REASONS]
    weights = [r[2] for r in TERMINATION_REASONS]

    records: list[dict] = []

    for emp in employees:
        if emp["status"] != "Terminated" or emp["termination_date"] is None:
            continue

        idx = rng.choices(range(len(reasons)), weights=weights, k=1)[0]

        records.append(
            {
                "employee_id": emp["employee_id"],
                "first_name": emp["first_name"],
                "last_name": emp["last_name"],
                "role_type": emp["role_type"],
                "location_id": emp["location_id"],
                "hire_date": emp["hire_date"],
                "termination_date": emp["termination_date"],
                "termination_category": categories[idx],
                "termination_reason": reasons[idx],
            }
        )

    # Sort by termination date descending (most recent first)
    records.sort(key=lambda r: r["termination_date"], reverse=True)
    return records


# Module-level cache
_terminations_cache: list[dict] | None = None


def get_terminations() -> list[dict]:
    """Return the cached termination dataset, generating on first call.

    Returns:
        Deterministic list of termination event dictionaries.
    """
    global _terminations_cache
    if _terminations_cache is None:
        _terminations_cache = generate_terminations()
    return _terminations_cache


def get_terminations_filtered(
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    """Return terminations filtered by date range.

    Args:
        start_date: Inclusive start date filter.
        end_date: Inclusive end date filter.

    Returns:
        Filtered list of termination records.
    """
    data = get_terminations()
    if start_date:
        data = [r for r in data if r["termination_date"] >= start_date]
    if end_date:
        data = [r for r in data if r["termination_date"] <= end_date]
    return data
