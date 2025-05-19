"""Parallel execution handler for test runner."""

import asyncio
import os
from typing import Callable, List, Any, Dict, TypeVar, Coroutine

T = TypeVar('T')

class ParallelExecutor:
    """Handles parallel execution of tasks with rate limiting."""

    def __init__(self):
        """Initialize the parallel executor."""
        self.max_parallel = int(os.environ.get("MAX_PARALLEL_REQUESTS", "5"))
        self.delay_ms = int(os.environ.get("REQUEST_DELAY_MS", "500"))
        self.semaphore = asyncio.Semaphore(self.max_parallel)

    async def execute_with_rate_limit(self, func: Callable[..., Coroutine[Any, Any, T]], *args, **kwargs) -> T:
        """
        Execute a function with rate limiting.

        Args:
            func: Coroutine function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Function result
        """
        async with self.semaphore:
            result = await func(*args, **kwargs)
            # Add delay to prevent hitting rate limits
            if self.delay_ms > 0:
                await asyncio.sleep(self.delay_ms / 1000)
            return result

    async def execute_batch(self, tasks: List[Dict[str, Any]], func: Callable[..., Coroutine[Any, Any, T]]) -> List[T]:
        """
        Execute a batch of tasks in parallel with rate limiting.

        Args:
            tasks: List of task dictionaries with args and kwargs
            func: Coroutine function to execute for each task

        Returns:
            List of function results
        """
        coroutines = [
            self.execute_with_rate_limit(func, **task)
            for task in tasks
        ]

        return await asyncio.gather(*coroutines)