#!/usr/bin/env python3
"""
Error Handling Utilities

This module provides centralized error handling decorators and utilities
to reduce code duplication and ensure consistent error handling patterns.
"""

import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from loguru import logger

# Type variables for generic function signatures
T = TypeVar("T")
P = ParamSpec("P")


def critical_system_error_handler(
    operation_name: str, re_raise_runtime: bool = True, re_raise_connection: bool = True
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator for handling critical system errors with consistent logging and re-raising.

    This decorator handles the common pattern of catching RuntimeError and ConnectionError,
    logging them as critical system errors, and optionally re-raising them.

    Args:
        operation_name: Human-readable name of the operation for logging
        re_raise_runtime: Whether to re-raise RuntimeError exceptions
        re_raise_connection: Whether to re-raise ConnectionError exceptions

    Returns:
        Decorated function with consistent error handling
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except RuntimeError as e:
                logger.critical(f"💥 CRITICAL SYSTEM ERROR in {operation_name}: {e}")
                logger.critical(
                    "🚨 This indicates a serious system configuration or initialization failure"
                )
                if re_raise_runtime:
                    raise RuntimeError(f"CRITICAL SYSTEM ERROR in {operation_name}: {e}")
                else:
                    raise
            except ConnectionError as e:
                logger.critical(
                    f"💥 CRITICAL SYSTEM ERROR in {operation_name}: Database connection failed - {e}"
                )
                logger.critical("🚨 This indicates a serious database connectivity failure")
                if re_raise_connection:
                    raise ConnectionError(
                        f"CRITICAL SYSTEM ERROR in {operation_name}: Database connection failed - {e}"
                    )
                else:
                    raise
            except Exception as e:
                logger.critical(
                    f"💥 CRITICAL SYSTEM ERROR in {operation_name}: Unexpected error - {e}"
                )
                logger.critical("🚨 This indicates an unexpected system failure")
                raise RuntimeError(
                    f"CRITICAL SYSTEM ERROR in {operation_name}: Unexpected error - {e}"
                )

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except RuntimeError as e:
                logger.critical(f"💥 CRITICAL SYSTEM ERROR in {operation_name}: {e}")
                logger.critical(
                    "🚨 This indicates a serious system configuration or initialization failure"
                )
                if re_raise_runtime:
                    raise RuntimeError(f"CRITICAL SYSTEM ERROR in {operation_name}: {e}")
                else:
                    raise
            except ConnectionError as e:
                logger.critical(
                    f"💥 CRITICAL SYSTEM ERROR in {operation_name}: Database connection failed - {e}"
                )
                logger.critical("🚨 This indicates a serious database connectivity failure")
                if re_raise_connection:
                    raise ConnectionError(
                        f"CRITICAL SYSTEM ERROR in {operation_name}: Database connection failed - {e}"
                    )
                else:
                    raise
            except Exception as e:
                logger.critical(
                    f"💥 CRITICAL SYSTEM ERROR in {operation_name}: Unexpected error - {e}"
                )
                logger.critical("🚨 This indicates an unexpected system failure")
                raise RuntimeError(
                    f"CRITICAL SYSTEM ERROR in {operation_name}: Unexpected error - {e}"
                )

        # Return async wrapper if the function is async, otherwise sync wrapper
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:  # CO_COROUTINE flag
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def user_registration_check_handler(func: Callable[P, T]) -> Callable[P, T]:
    """
    Specialized decorator for user registration status checks.

    This decorator handles the specific error patterns for user registration
    checks, which are critical system operations that require fail-fast behavior.
    """

    @functools.wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except RuntimeError as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Failed to check user registration status - {e}"
            )
            logger.critical(
                "🚨 This indicates a serious system configuration or initialization failure"
            )
            logger.critical("🛑 Failing fast to prevent unsafe operation without user validation")
            raise RuntimeError(
                f"CRITICAL SYSTEM ERROR: Failed to check user registration status. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )
        except ConnectionError as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Database connection failed during user registration check - {e}"
            )
            logger.critical("🚨 This indicates a serious database connectivity failure")
            logger.critical("🛑 Failing fast to prevent unsafe operation without database access")
            raise ConnectionError(
                f"CRITICAL SYSTEM ERROR: Database connection failed during user registration check. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )
        except Exception as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Unexpected error during user registration check - {e}"
            )
            logger.critical("🚨 This indicates an unexpected system failure")
            logger.critical("🛑 Failing fast to prevent unsafe operation")
            raise RuntimeError(
                f"CRITICAL SYSTEM ERROR: Unexpected error during user registration check. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Failed to check user registration status - {e}"
            )
            logger.critical(
                "🚨 This indicates a serious system configuration or initialization failure"
            )
            logger.critical("🛑 Failing fast to prevent unsafe operation without user validation")
            raise RuntimeError(
                f"CRITICAL SYSTEM ERROR: Failed to check user registration status. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )
        except ConnectionError as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Database connection failed during user registration check - {e}"
            )
            logger.critical("🚨 This indicates a serious database connectivity failure")
            logger.critical("🛑 Failing fast to prevent unsafe operation without database access")
            raise ConnectionError(
                f"CRITICAL SYSTEM ERROR: Database connection failed during user registration check. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )
        except Exception as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Unexpected error during user registration check - {e}"
            )
            logger.critical("🚨 This indicates an unexpected system failure")
            logger.critical("🛑 Failing fast to prevent unsafe operation")
            raise RuntimeError(
                f"CRITICAL SYSTEM ERROR: Unexpected error during user registration check. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )

    # Return async wrapper if the function is async, otherwise sync wrapper
    if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:  # CO_COROUTINE flag
        return async_wrapper
    else:
        return sync_wrapper


def command_registry_error_handler(func: Callable[P, T]) -> Callable[P, T]:
    """
    Specialized decorator for command registry operations.

    This decorator handles the specific error patterns for command registry
    operations, which are critical system operations that require fail-fast behavior.
    """

    @functools.wraps(func)
    async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except RuntimeError as e:
            if "Command registry not initialized" in str(e):
                logger.critical(
                    "💥 CRITICAL SYSTEM ERROR: Command registry not accessible - this is a major system failure"
                )
                logger.critical(
                    "🚨 The system cannot function without the command registry. This indicates a serious initialization failure."
                )
                logger.critical(
                    "🛑 Failing fast to prevent unsafe operation without command validation"
                )
                raise RuntimeError(
                    f"CRITICAL SYSTEM ERROR: Command registry not accessible. "
                    f"This is a major system failure that prevents safe operation. "
                    f"Original error: {e}"
                )
            else:
                raise
        except Exception as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Unexpected error in command registry operation - {e}"
            )
            logger.critical("🚨 This indicates an unexpected system failure")
            raise RuntimeError(
                f"CRITICAL SYSTEM ERROR: Unexpected error in command registry operation. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            if "Command registry not initialized" in str(e):
                logger.critical(
                    "💥 CRITICAL SYSTEM ERROR: Command registry not accessible - this is a major system failure"
                )
                logger.critical(
                    "🚨 The system cannot function without the command registry. This indicates a serious initialization failure."
                )
                logger.critical(
                    "🛑 Failing fast to prevent unsafe operation without command validation"
                )
                raise RuntimeError(
                    f"CRITICAL SYSTEM ERROR: Command registry not accessible. "
                    f"This is a major system failure that prevents safe operation. "
                    f"Original error: {e}"
                )
            else:
                raise
        except Exception as e:
            logger.critical(
                f"💥 CRITICAL SYSTEM ERROR: Unexpected error in command registry operation - {e}"
            )
            logger.critical("🚨 This indicates an unexpected system failure")
            raise RuntimeError(
                f"CRITICAL SYSTEM ERROR: Unexpected error in command registry operation. "
                f"This is a major system failure that prevents safe operation. "
                f"Original error: {e}"
            )

    # Return async wrapper if the function is async, otherwise sync wrapper
    if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:  # CO_COROUTINE flag
        return async_wrapper
    else:
        return sync_wrapper
