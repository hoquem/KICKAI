"""
Async Utilities for KICKAI

This module provides common async patterns and utilities for I/O-bound operations.
"""

import asyncio
import time
from collections.abc import Callable, Coroutine
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, TypeVar

from loguru import logger

logger = logger

T = TypeVar('T')


class AsyncRetryError(Exception):
    """Exception raised when async retry operations fail."""
    pass


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.2f}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            raise AsyncRetryError(f"Function {func.__name__} failed after {max_attempts} attempts") from last_exception

        return wrapper
    return decorator


def async_timeout(timeout_seconds: float):
    """
    Decorator for adding timeout to async functions.

    Args:
        timeout_seconds: Timeout in seconds
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout_seconds}s")
                raise AsyncRetryError(f"Function {func.__name__} timed out") from None

        return wrapper
    return decorator


@asynccontextmanager
async def async_operation_context(operation_name: str, **context):
    """
    Context manager for async operations with logging and error handling.

    Args:
        operation_name: Name of the operation for logging
        **context: Additional context information
    """
    start_time = time.time()
    logger.info(f"Starting async operation: {operation_name} with context: {context}")

    try:
        yield
        duration = time.time() - start_time
        logger.info(f"Completed async operation: {operation_name} in {duration:.3f}s")
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed async operation: {operation_name} after {duration:.3f}s: {e}")
        raise


async def run_in_executor(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a synchronous function in a thread pool executor.

    Args:
        func: Synchronous function to run
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Result of the function execution
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


async def gather_with_concurrency_limit(
    coroutines: list[Coroutine[Any, Any, T]],
    max_concurrent: int = 10
) -> list[T]:
    """
    Execute coroutines with a concurrency limit using semaphore.

    Args:
        coroutines: List of coroutines to execute
        max_concurrent: Maximum number of concurrent executions

    Returns:
        List of results from the coroutines
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_coroutine(coro: Coroutine[Any, Any, T]) -> T:
        async with semaphore:
            return await coro

    limited_coroutines = [limited_coroutine(coro) for coro in coroutines]
    return await asyncio.gather(*limited_coroutines)


async def execute_with_fallback(
    primary_func: Callable[..., Coroutine[Any, Any, T]],
    fallback_func: Callable[..., Coroutine[Any, Any, T]],
    *args,
    **kwargs
) -> T:
    """
    Execute a primary function with a fallback if it fails.

    Args:
        primary_func: Primary function to try first
        fallback_func: Fallback function to use if primary fails
        *args: Arguments to pass to both functions
        **kwargs: Keyword arguments to pass to both functions

    Returns:
        Result from either primary or fallback function
    """
    try:
        return await primary_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Primary function failed: {e}. Using fallback...")
        try:
            return await fallback_func(*args, **kwargs)
        except Exception as fallback_e:
            logger.error(f"Both primary and fallback functions failed: {fallback_e}")
            raise


class AsyncBatchProcessor:
    """Utility class for processing items in batches asynchronously."""

    def __init__(self, batch_size: int = 100, max_concurrent: int = 10):
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent

    async def process_batches(
        self,
        items: list[Any],
        processor_func: Callable[[list[Any]], Coroutine[Any, Any, list[T]]]
    ) -> list[T]:
        """
        Process items in batches asynchronously.

        Args:
            items: List of items to process
            processor_func: Function to process each batch

        Returns:
            List of results from all batches
        """
        batches = [
            items[i:i + self.batch_size]
            for i in range(0, len(items), self.batch_size)
        ]

        batch_coroutines = [processor_func(batch) for batch in batches]
        batch_results = await gather_with_concurrency_limit(
            batch_coroutines,
            self.max_concurrent
        )

        # Flatten results
        all_results = []
        for batch_result in batch_results:
            all_results.extend(batch_result)

        return all_results


class AsyncRateLimiter:
    """Rate limiter for async operations."""

    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a call."""
        async with self._lock:
            now = time.time()

            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

            if len(self.calls) >= self.max_calls:
                # Wait until we can make another call
                sleep_time = self.calls[0] + self.time_window - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    return await self.acquire()

            self.calls.append(now)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def create_async_context_manager(func: Callable[..., Coroutine[Any, Any, T]]):
    """
    Create an async context manager from an async function.

    Args:
        func: Async function to wrap

    Returns:
        Async context manager
    """
    @asynccontextmanager
    async def context_manager(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            yield result
        finally:
            # Cleanup if needed
            pass

    return context_manager


# Utility functions for common async patterns

async def safe_async_call(
    func: Callable[..., Coroutine[Any, Any, T]],
    *args,
    default_value: T | None = None,
    **kwargs
) -> T | None:
    """
    Safely call an async function with error handling.

    Args:
        func: Async function to call
        *args: Function arguments
        default_value: Default value to return on error
        **kwargs: Function keyword arguments

    Returns:
        Function result or default value on error
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in safe async call to {func.__name__}: {e}")
        return default_value


async def async_map(
    func: Callable[[Any], Coroutine[Any, Any, T]],
    items: list[Any],
    max_concurrent: int = 10
) -> list[T]:
    """
    Apply an async function to each item in a list with concurrency control.

    Args:
        func: Async function to apply
        items: List of items to process
        max_concurrent: Maximum number of concurrent executions

    Returns:
        List of results
    """
    coroutines = [func(item) for item in items]
    return await gather_with_concurrency_limit(coroutines, max_concurrent)


async def async_filter(
    func: Callable[[Any], Coroutine[Any, Any, bool]],
    items: list[Any],
    max_concurrent: int = 10
) -> list[Any]:
    """
    Filter items using an async predicate function.

    Args:
        func: Async predicate function
        items: List of items to filter
        max_concurrent: Maximum number of concurrent executions

    Returns:
        Filtered list of items
    """
    results = await async_map(func, items, max_concurrent)
    return [item for item, keep in zip(items, results, strict=False) if keep]
