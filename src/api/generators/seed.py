"""Master seed and deterministic random-number helpers.

Every generator derives its Faker instance and stdlib Random from this module
so that the full dataset is reproducible across runs.
"""

import random

from faker import Faker

from src.api.config import settings

MASTER_SEED: int = settings.master_seed

# Global deterministic Faker instance (locale-aware for US names)
fake = Faker("en_US")
Faker.seed(MASTER_SEED)

# Global deterministic stdlib Random instance
rng = random.Random(MASTER_SEED)


def get_seeded_faker(offset: int = 0) -> Faker:
    """Return a new Faker instance with a derived seed.

    Args:
        offset: Added to MASTER_SEED so each generator gets a unique but
                reproducible stream.

    Returns:
        A seeded Faker instance.
    """
    f = Faker("en_US")
    Faker.seed(MASTER_SEED + offset)
    return f


def get_seeded_random(offset: int = 0) -> random.Random:
    """Return a new stdlib Random with a derived seed.

    Args:
        offset: Added to MASTER_SEED for uniqueness.

    Returns:
        A seeded random.Random instance.
    """
    return random.Random(MASTER_SEED + offset)
