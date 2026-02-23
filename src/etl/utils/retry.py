"""Exponential back-off retry decorator for HTTP calls.

Usage::

    from src.etl.utils.retry import with_retries

    @with_retries(max_retries=3, base_delay=1.0)
    def fetch_page(url: str) -> dict:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
"""

import functools
import time
from typing import Any, Callable, TypeVar

from src.etl.utils.logger import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def with_retries(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator: retry a function with exponential back-off.

    Args:
        max_retries: Maximum number of retry attempts after the first failure.
        base_delay: Initial delay in seconds before the first retry.
        backoff_factor: Multiplier applied to the delay after each retry.
        retryable_exceptions: Tuple of exception types that should trigger a retry.

    Returns:
        Wrapped function with retry logic.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            last_exc: Exception | None = None
            for attempt in range(1, max_retries + 2):  # attempt 1 = initial call
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    last_exc = exc
                    if attempt > max_retries:
                        logger.error(
                            "All %d retries exhausted for %s: %s",
                            max_retries,
                            func.__name__,
                            exc,
                        )
                        raise
                    logger.warning(
                        "Attempt %d/%d for %s failed (%s). Retrying in %.1fs…",
                        attempt,
                        max_retries + 1,
                        func.__name__,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
            # Should not reach here, but satisfy type checker
            raise last_exc  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator
