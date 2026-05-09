"""
core/utils/retry.py

DRY: common retry logic applied to all LLM/external API calls.
"""
import time
import logging
from typing import TypeVar, Callable

logger = logging.getLogger(__name__)
T = TypeVar("T")


def with_retry(
    fn: Callable[[], T],
    max_retries: int = 3,
    backoff_base: float = 2.0,
    exceptions: tuple = (Exception,),
) -> T:
    """Exponential backoff retry."""
    last_exc = None
    for attempt in range(max_retries):
        try:
            return fn()
        except exceptions as e:
            last_exc = e
            if attempt == max_retries - 1:
                logger.error(f"Max retries exceeded ({max_retries}): {e}")
                raise
            wait = backoff_base ** attempt
            logger.warning(f"Retry {attempt+1}/{max_retries}, waiting {wait}s: {e}")
            time.sleep(wait)
    raise last_exc
