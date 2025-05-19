"""Retry handler for API calls."""

import asyncio
import time
from typing import Callable, Any, TypeVar, Coroutine, Optional

T = TypeVar('T')

class RetryHandler:
    """Handles retrying failed API calls."""

    def __init__(self, max_retries: int = 3, base_delay: float = 2.0, max_delay: float = 30.0):
        """
        Initialize the retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def with_retry(self, func: Callable[..., Coroutine[Any, Any, T]], *args, **kwargs) -> T:
        """
        Execute a function with exponential backoff retry logic.

        Args:
            func: Coroutine function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Function result

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == self.max_retries:
                    break

                # Calculate delay with exponential backoff and jitter
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                jitter = delay * 0.2 * (time.time() % 1)  # Add up to 20% jitter
                await asyncio.sleep(delay + jitter)

        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise Exception("All retry attempts failed")