"""
Unified Error Handling and Validation Strategy for KICKAI

This module provides a comprehensive error handling system with decorators,
context managers, and utilities for consistent error management across
the agent system.
"""

import functools
import traceback
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Union, Union

from loguru import logger

from .exceptions import (
    KICKAIError,
    create_error_context,
    format_error_message,
    is_critical_error,
)

# logger = logging.getLogger(__name__) # Remove this, use loguru's logger


@dataclass
class ErrorHandlingConfig:
    """Configuration for error handling behavior."""
    log_errors: bool = True
    log_level: str = "ERROR"
    include_traceback: bool = False
    retry_on_retryable: bool = True
    max_retries: int = 3
    user_friendly_messages: bool = True
    raise_on_critical: bool = True
    context_operation: Union[str, None] = None


class ErrorHandler:
    """Centralized error handler for the KICKAI system."""

    def __init__(self, config: Union[ErrorHandlingConfig, None] = None):
        self.config = config or ErrorHandlingConfig()

    def handle_error(
        self,
        error: Exception,
        context: Union[dict[str, Any], None] = None,
        operation: Union[str, None] = None
    ) -> str:
        """
        Handle an error and return a user-friendly message.

        Args:
            error: The exception that occurred
            context: Additional context information
            operation: The operation that failed

        Returns:
            User-friendly error message
        """
        try:
            # Create error context
            error_context = create_error_context(
                operation=operation or self.config.context_operation or "unknown",
                **(context or {})
            )

            # Log the error if configured
            if self.config.log_errors:
                self._log_error(error, error_context)

            # Check if this is a critical error
            if is_critical_error(error) and self.config.raise_on_critical:
                raise error

            # Return user-friendly message
            if self.config.user_friendly_messages:
                return self._get_user_friendly_message(error, error_context)
            else:
                return str(error)

        except Exception as handling_error:
            logger.error(f"Error in error handler: {handling_error}")
            return "❌ An unexpected error occurred. Please try again."

    def _log_error(self, error: Exception, context: Any) -> None:
        """Log an error with appropriate level and details."""
        error_msg = f"Error in {context.operation}: {error!s}"

        if self.config.include_traceback:
            error_msg += f"\nTraceback:\n{traceback.format_exc()}"

        logger.log(self.config.log_level, error_msg, exc_info=True)

    def _get_user_friendly_message(self, error: Exception, context: Any) -> str:
        """Get a user-friendly error message."""
        if isinstance(error, KICKAIError):
            return format_error_message(error, include_context=True)

        # Map common exceptions to user-friendly messages
        error_mapping = {
            ValueError: "❌ Invalid input provided. Please check your request and try again.",
            TypeError: "❌ Invalid data type. Please check your input and try again.",
            KeyError: "❌ Missing required information. Please provide all necessary details.",
            IndexError: "❌ Invalid selection. Please choose a valid option.",
            PermissionError: "❌ You don't have permission to perform this action.",
            FileNotFoundError: "❌ Required resource not found. Please contact support.",
            ConnectionError: "❌ Connection failed. Please check your internet connection and try again.",
            TimeoutError: "❌ Request timed out. Please try again.",
        }

        error_type = type(error)
        if error_type in error_mapping:
            return error_mapping[error_type]

        # Default message for unknown errors
        return "❌ Sorry, I encountered an error processing your request. Please try again."


# Global error handler instance
_global_error_handler = ErrorHandler()


def set_global_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler."""
    global _global_error_handler
    _global_error_handler = handler


def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler."""
    return _global_error_handler


def handle_agent_errors(
    operation: Union[str, None] = None,
    config: Union[ErrorHandlingConfig, None] = None
) -> Callable:
    """
    Decorator for handling agent execution errors.

    Args:
        operation: The operation being performed
        config: Error handling configuration

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler(config) if config else _global_error_handler
                context = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                return error_handler.handle_error(e, context, operation)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler(config) if config else _global_error_handler
                context = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                return error_handler.handle_error(e, context, operation)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def handle_tool_errors(
    tool_name: Union[str, None] = None,
    config: Union[ErrorHandlingConfig, None] = None
) -> Callable:
    """
    Decorator for handling tool execution errors.

    Args:
        tool_name: The name of the tool
        config: Error handling configuration

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler(config) if config else _global_error_handler
                context = {
                    'tool': tool_name or func.__name__,
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                return error_handler.handle_error(e, context, f"tool_execution_{tool_name or func.__name__}")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler(config) if config else _global_error_handler
                context = {
                    'tool': tool_name or func.__name__,
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                return error_handler.handle_error(e, context, f"tool_execution_{tool_name or func.__name__}")

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


@contextmanager
def error_context(
    operation: str,
    context: Union[dict[str, Any], None] = None,
    config: Union[ErrorHandlingConfig, None] = None,
    reraise: bool = False
):
    """
    Context manager for error handling.

    Args:
        operation: The operation being performed
        context: Additional context information
        config: Error handling configuration
        reraise: Whether to reraise the exception after handling

    Yields:
        None
    """
    try:
        yield
    except Exception as e:
        error_handler = ErrorHandler(config) if config else _global_error_handler
        result = error_handler.handle_error(e, context, operation)

        if reraise:
            raise e

        return result


def validate_input(
    value: Any,
    expected_type: type,
    field_name: str,
    required: bool = True,
    validator: Union[Callable, None] = None
) -> None:
    """
    Validate input parameters.

    Args:
        value: The value to validate
        expected_type: Expected type
        field_name: Name of the field for error messages
        required: Whether the field is required
        validator: Optional custom validation function

    Raises:
        InputValidationError: If validation fails
    """
    from .exceptions import InputValidationError

    # Check if required field is present
    if required and value is None:
        raise InputValidationError(
            f"Required field '{field_name}' is missing",
            create_error_context("input_validation", additional_info={'field': field_name})
        )

    # Check type
    if value is not None and not isinstance(value, expected_type):
        raise InputValidationError(
            f"Field '{field_name}' must be of type {expected_type.__name__}, got {type(value).__name__}",
            create_error_context("input_validation", additional_info={'field': field_name, 'expected_type': expected_type.__name__})
        )

    # Run custom validator if provided
    if validator and value is not None:
        try:
            validator(value)
        except Exception as e:
            raise InputValidationError(
                f"Validation failed for field '{field_name}': {e!s}",
                create_error_context("input_validation", additional_info={'field': field_name, 'validator_error': str(e)})
            )


def safe_execute(
    func: Callable,
    *args,
    operation: str = "unknown",
    context: Union[dict[str, Any], None] = None,
    config: Union[ErrorHandlingConfig, None] = None,
    default_return: Any = None,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        operation: Operation name for error context
        context: Additional context
        config: Error handling configuration
        default_return: Default return value on error
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler = ErrorHandler(config) if config else _global_error_handler
        error_handler.handle_error(e, context, operation)
        return default_return


async def safe_execute_async(
    func: Callable,
    *args,
    operation: str = "unknown",
    context: Union[dict[str, Any], None] = None,
    config: Union[ErrorHandlingConfig, None] = None,
    default_return: Any = None,
    **kwargs
) -> Any:
    """
    Safely execute an async function with error handling.

    Args:
        func: Async function to execute
        operation: Operation name for error context
        context: Additional context
        config: Error handling configuration
        default_return: Default return value on error
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Function result or default_return on error
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        error_handler = ErrorHandler(config) if config else _global_error_handler
        error_handler.handle_error(e, context, operation)
        return default_return


