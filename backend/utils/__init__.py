"""
retry.py
Exponential backoff retry decorator for OpenAI API calls.
Handles rate limits (429) and transient server errors (500/503).
"""

import logging
import time
import functools
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_attempts:   Maximum number of attempts (including first).
        base_delay:     Initial delay in seconds before first retry.
        backoff_factor: Multiplier applied to delay on each retry.
        exceptions:     Exception types that should trigger a retry.

    Usage:
        @with_retry(max_attempts=3, base_delay=1.0)
        def call_openai():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            raise last_exception

        return wrapper
    return decorator
