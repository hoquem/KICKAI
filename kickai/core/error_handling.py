"""
Unified Error Handling and Validation Strategy for KICKAI

This module provides a comprehensive error handling system with decorators,
context managers, and utilities for consistent error management across
the agent system, including CrewAI-specific error handling.
"""

import asyncio
import functools
import traceback
import uuid
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Set, List, Union


from loguru import logger
from pydantic import BaseModel, Field

from .exceptions import (
    KICKAIError,
    create_error_context,
    format_error_message,
    is_critical_error,
)

# Try to import CrewAI exception, fallback if not available
try:
    from crewai.exceptions import CrewException
except ImportError:
    class CrewException(Exception):
        """Fallback CrewException if CrewAI is not available."""
        pass


class CrewAIErrorCategory(str, Enum):
    """Categories of CrewAI-specific errors."""
    AGENT_INITIALIZATION = "agent_initialization"
    TASK_EXECUTION = "task_execution"
    TOOL_EXECUTION = "tool_execution"
    LLM_COMMUNICATION = "llm_communication"
    MEMORY_OPERATIONS = "memory_operations"
    CREW_ORCHESTRATION = "crew_orchestration"
    CONTEXT_VALIDATION = "context_validation"
    OUTPUT_PARSING = "output_parsing"
    RATE_LIMITING = "rate_limiting"
    UNKNOWN = "unknown"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CrewAIErrorContext:
    """Context information for CrewAI error recovery."""
    agent_role: Optional[str] = None
    task_type: Optional[str] = None
    team_id: Optional[str] = None
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    chat_type: Optional[str] = None
    tool_name: Optional[str] = None
    llm_model: Optional[str] = None
    execution_step: Optional[str] = None


class CrewAIErrorInfo(BaseModel):
    """Structured CrewAI error information."""
    error_id: str = Field(description="Unique error identifier")
    category: CrewAIErrorCategory = Field(description="Error category")
    severity: ErrorSeverity = Field(description="Error severity level")
    message: str = Field(description="Human-readable error message")
    technical_details: str = Field(description="Technical error details")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    timestamp: datetime = Field(default_factory=datetime.now, description="When error occurred")
    stack_trace: Optional[str] = Field(None, description="Stack trace if available")
    recovery_suggestion: Optional[str] = Field(None, description="Suggested recovery action")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

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
    context_operation: Optional[str] = None


class ErrorHandler:
    """Centralized error handler for the KICKAI system."""

    def __init__(self, config: Optional[ErrorHandlingConfig] = None):
        self.config = config or ErrorHandlingConfig()

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
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
                operation=operation or self.config.context_operation or "unknown", **(context or {})
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


class CrewAIErrorHandler:
    """CrewAI-specific error handler with recovery strategies."""
    
    def __init__(self):
        self.error_callbacks: List[Callable[[CrewAIErrorInfo], None]] = []
        self.recovery_strategies: Dict[CrewAIErrorCategory, Callable[[CrewAIErrorInfo, CrewAIErrorContext], str]] = {}
        self.error_counts: Dict[CrewAIErrorCategory, int] = {}
        
        # Setup default recovery strategies
        self._setup_default_recovery_strategies()
    
    def add_error_callback(self, callback: Callable[[CrewAIErrorInfo], None]):
        """Add callback to be executed when errors occur."""
        self.error_callbacks.append(callback)
    
    def register_recovery_strategy(
        self,
        category: CrewAIErrorCategory,
        strategy: Callable[[CrewAIErrorInfo, CrewAIErrorContext], str]
    ):
        """Register custom recovery strategy for error category."""
        self.recovery_strategies[category] = strategy
    
    def handle_crewai_error(
        self,
        exception: Exception,
        context: Optional[CrewAIErrorContext] = None,
        fallback_message: str = "An unexpected error occurred"
    ) -> str:
        """
        Handle CrewAI-specific errors with proper categorization and recovery.
        
        Args:
            exception: The exception that occurred
            context: Context information for recovery
            fallback_message: Fallback message if recovery fails
            
        Returns:
            User-friendly response message
        """
        try:
            # Categorize and structure the error
            crew_error = self._categorize_error(exception, context or CrewAIErrorContext())
            
            # Update error statistics
            self.error_counts[crew_error.category] = self.error_counts.get(crew_error.category, 0) + 1
            
            # Log the error
            self._log_error(crew_error)
            
            # Execute callbacks
            for callback in self.error_callbacks:
                try:
                    callback(crew_error)
                except Exception as callback_error:
                    logger.error(f"Error in CrewAI error callback: {callback_error}")
            
            # Attempt recovery
            recovery_response = self._attempt_recovery(crew_error, context or CrewAIErrorContext())
            
            if recovery_response:
                logger.info(f"✅ CrewAI error recovery successful for {crew_error.category.value}")
                return recovery_response
            else:
                logger.warning(f"⚠️ No recovery strategy available for {crew_error.category.value}")
                return fallback_message
                
        except Exception as handler_error:
            logger.error(f"❌ Error in CrewAI error handler: {handler_error}")
            return fallback_message
    
    def _categorize_error(self, exception: Exception, context: CrewAIErrorContext) -> CrewAIErrorInfo:
        """Categorize exception into structured error information."""
        error_id = str(uuid.uuid4())[:8]
        
        # Determine category based on exception type and context
        category = self._determine_category(exception, context)
        
        # Determine severity
        severity = self._determine_severity(exception, category)
        
        # Create structured error
        crew_error = CrewAIErrorInfo(
            error_id=error_id,
            category=category,
            severity=severity,
            message=self._create_user_message(exception, category),
            technical_details=str(exception),
            context={
                "agent_role": context.agent_role,
                "task_type": context.task_type,
                "team_id": context.team_id,
                "telegram_id": context.telegram_id,
                "username": context.username,
                "chat_type": context.chat_type,
                "tool_name": context.tool_name,
                "llm_model": context.llm_model,
                "execution_step": context.execution_step,
                "exception_type": type(exception).__name__
            },
            stack_trace=traceback.format_exc(),
            recovery_suggestion=self._get_recovery_suggestion(category)
        )
        
        return crew_error
    
    def _determine_category(self, exception: Exception, context: CrewAIErrorContext) -> CrewAIErrorCategory:
        """Determine error category based on exception type and context."""
        exception_type = type(exception).__name__
        exception_str = str(exception).lower()
        
        # CrewAI-specific errors
        if isinstance(exception, CrewException):
            return CrewAIErrorCategory.CREW_ORCHESTRATION
        
        # Context validation errors
        if "context" in exception_str or "missing" in exception_str:
            if context.execution_step == "validation":
                return CrewAIErrorCategory.CONTEXT_VALIDATION
        
        # Tool execution errors
        if context.tool_name or "tool" in exception_str:
            return CrewAIErrorCategory.TOOL_EXECUTION
        
        # LLM communication errors
        if any(keyword in exception_str for keyword in ["llm", "model", "api", "token", "groq", "openai", "gemini"]):
            return CrewAIErrorCategory.LLM_COMMUNICATION
        
        # Rate limiting errors
        if any(keyword in exception_str for keyword in ["rate", "limit", "quota", "429"]):
            return CrewAIErrorCategory.RATE_LIMITING
        
        # Agent initialization errors
        if context.execution_step == "agent_creation" or "agent" in exception_str:
            return CrewAIErrorCategory.AGENT_INITIALIZATION
        
        # Task execution errors
        if context.task_type or "task" in exception_str:
            return CrewAIErrorCategory.TASK_EXECUTION
        
        # Memory operations
        if "memory" in exception_str or "embedding" in exception_str:
            return CrewAIErrorCategory.MEMORY_OPERATIONS
        
        # Output parsing errors
        if any(keyword in exception_str for keyword in ["json", "parse", "format", "output"]):
            return CrewAIErrorCategory.OUTPUT_PARSING
        
        return CrewAIErrorCategory.UNKNOWN
    
    def _determine_severity(self, exception: Exception, category: CrewAIErrorCategory) -> ErrorSeverity:
        """Determine error severity based on exception and category."""
        exception_str = str(exception).lower()
        
        # Critical errors that break core functionality
        if category in [CrewAIErrorCategory.AGENT_INITIALIZATION, CrewAIErrorCategory.CREW_ORCHESTRATION]:
            return ErrorSeverity.CRITICAL
        
        # High severity for LLM and context issues
        if category in [CrewAIErrorCategory.LLM_COMMUNICATION, CrewAIErrorCategory.CONTEXT_VALIDATION]:
            if any(keyword in exception_str for keyword in ["auth", "key", "permission", "forbidden"]):
                return ErrorSeverity.CRITICAL
            return ErrorSeverity.HIGH
        
        # Medium severity for tool and task issues
        if category in [CrewAIErrorCategory.TOOL_EXECUTION, CrewAIErrorCategory.TASK_EXECUTION]:
            return ErrorSeverity.MEDIUM
        
        # Low severity for rate limiting and parsing (recoverable)
        if category in [CrewAIErrorCategory.RATE_LIMITING, CrewAIErrorCategory.OUTPUT_PARSING]:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM
    
    def _create_user_message(self, exception: Exception, category: CrewAIErrorCategory) -> str:
        """Create user-friendly error message based on category."""
        messages = {
            CrewAIErrorCategory.AGENT_INITIALIZATION: "Unable to initialize the AI agent. Please try again.",
            CrewAIErrorCategory.TASK_EXECUTION: "Task execution encountered an issue. Please retry your request.",
            CrewAIErrorCategory.TOOL_EXECUTION: "A required tool is temporarily unavailable. Please try again.",
            CrewAIErrorCategory.LLM_COMMUNICATION: "AI service is temporarily unavailable. Please try again shortly.",
            CrewAIErrorCategory.MEMORY_OPERATIONS: "Memory system encountered an issue. Your request may not be remembered.",
            CrewAIErrorCategory.CREW_ORCHESTRATION: "System coordination issue occurred. Please try again.",
            CrewAIErrorCategory.CONTEXT_VALIDATION: "Request information is incomplete or invalid. Please check your input.",
            CrewAIErrorCategory.OUTPUT_PARSING: "Response formatting issue occurred. Please try again.",
            CrewAIErrorCategory.RATE_LIMITING: "Service is busy. Please wait a moment and try again.",
            CrewAIErrorCategory.UNKNOWN: "An unexpected issue occurred. Please try again."
        }
        
        return messages.get(category, "An unexpected error occurred. Please try again.")
    
    def _get_recovery_suggestion(self, category: CrewAIErrorCategory) -> str:
        """Get recovery suggestion for error category."""
        suggestions = {
            CrewAIErrorCategory.AGENT_INITIALIZATION: "Verify agent configuration and LLM availability",
            CrewAIErrorCategory.TASK_EXECUTION: "Check task description and agent tools",
            CrewAIErrorCategory.TOOL_EXECUTION: "Verify tool configuration and dependencies",
            CrewAIErrorCategory.LLM_COMMUNICATION: "Check API keys and model availability",
            CrewAIErrorCategory.MEMORY_OPERATIONS: "Verify memory configuration and storage",
            CrewAIErrorCategory.CREW_ORCHESTRATION: "Check crew configuration and agent compatibility",
            CrewAIErrorCategory.CONTEXT_VALIDATION: "Ensure all required context fields are provided",
            CrewAIErrorCategory.OUTPUT_PARSING: "Check expected output format and validation",
            CrewAIErrorCategory.RATE_LIMITING: "Implement exponential backoff retry strategy",
            CrewAIErrorCategory.UNKNOWN: "Enable verbose logging for detailed diagnosis"
        }
        
        return suggestions.get(category, "Review logs for detailed error information")
    
    def _setup_default_recovery_strategies(self):
        """Setup default recovery strategies for different error categories."""
        
        def rate_limit_recovery(error: CrewAIErrorInfo, context: CrewAIErrorContext) -> str:
            """Recovery strategy for rate limiting errors."""
            return "⏳ Service is temporarily busy. Please wait a moment and try your request again."
        
        def context_validation_recovery(error: CrewAIErrorInfo, context: CrewAIErrorContext) -> str:
            """Recovery strategy for context validation errors."""
            missing_fields = []
            if not context.team_id:
                missing_fields.append("team information")
            if not context.username:
                missing_fields.append("user information")
            
            if missing_fields:
                return f"❌ Missing required information: {', '.join(missing_fields)}. Please ensure you're registered and try again."
            return "❌ Request information is incomplete. Please check your input and try again."
        
        def tool_execution_recovery(error: CrewAIErrorInfo, context: CrewAIErrorContext) -> str:
            """Recovery strategy for tool execution errors."""
            if context.tool_name:
                return f"⚠️ The {context.tool_name} tool is temporarily unavailable. Please try again in a moment."
            return "⚠️ A required service is temporarily unavailable. Please try again shortly."
        
        def llm_communication_recovery(error: CrewAIErrorInfo, context: CrewAIErrorContext) -> str:
            """Recovery strategy for LLM communication errors."""
            if "auth" in error.technical_details.lower() or "key" in error.technical_details.lower():
                return "🔑 Authentication issue with AI service. Please contact support if this persists."
            if "model" in error.technical_details.lower():
                return "🤖 AI model is temporarily unavailable. Please try again shortly."
            return "🔌 AI service connection issue. Please try again in a moment."
        
        # Register default strategies
        self.recovery_strategies[CrewAIErrorCategory.RATE_LIMITING] = rate_limit_recovery
        self.recovery_strategies[CrewAIErrorCategory.CONTEXT_VALIDATION] = context_validation_recovery
        self.recovery_strategies[CrewAIErrorCategory.TOOL_EXECUTION] = tool_execution_recovery
        self.recovery_strategies[CrewAIErrorCategory.LLM_COMMUNICATION] = llm_communication_recovery
    
    def _attempt_recovery(self, error: CrewAIErrorInfo, context: CrewAIErrorContext) -> Optional[str]:
        """Attempt to recover from error using registered strategies."""
        if error.category in self.recovery_strategies:
            try:
                return self.recovery_strategies[error.category](error, context)
            except Exception as recovery_error:
                logger.error(f"Error in recovery strategy for {error.category}: {recovery_error}")
        return None
    
    def _log_error(self, error: CrewAIErrorInfo):
        """Log error with appropriate level based on severity."""
        log_message = f"[{error.error_id}] {error.category.value}: {error.message}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
            logger.critical(f"Technical details: {error.technical_details}")
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
            logger.error(f"Technical details: {error.technical_details}")
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
            logger.debug(f"Technical details: {error.technical_details}")
        else:
            logger.info(log_message)
            logger.debug(f"Technical details: {error.technical_details}")
    
    def get_error_statistics(self) -> Dict[str, int]:
        """Get error statistics by category."""
        return dict(self.error_counts)
    
    def reset_statistics(self):
        """Reset error statistics."""
        self.error_counts.clear()


# Global error handler instances
_global_error_handler = ErrorHandler()
_global_crewai_error_handler = CrewAIErrorHandler()


def set_global_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler."""
    global _global_error_handler
    _global_error_handler = handler


def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler."""
    return _global_error_handler


def handle_agent_errors(
    operation: Optional[str] = None, config: Optional[ErrorHandlingConfig] = None
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
                context = {"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
                return error_handler.handle_error(e, context, operation)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler(config) if config else _global_error_handler
                context = {"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
                return error_handler.handle_error(e, context, operation)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def handle_tool_errors(
    tool_name: Optional[str] = None, config: Optional[ErrorHandlingConfig] = None
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
                    "tool": tool_name or func.__name__,
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                }
                return error_handler.handle_error(
                    e, context, f"tool_execution_{tool_name or func.__name__}"
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler(config) if config else _global_error_handler
                context = {
                    "tool": tool_name or func.__name__,
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                }
                return error_handler.handle_error(
                    e, context, f"tool_execution_{tool_name or func.__name__}"
                )

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


@contextmanager
def error_context(
    operation: str,
    context: Optional[Dict[str, Any]] = None,
    config: Optional[ErrorHandlingConfig] = None,
    reraise: bool = False,
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
    validator: Optional[Callable] = None,
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
            create_error_context("input_validation", additional_info={"field": field_name}),
        )

    # Check type
    if value is not None and not isinstance(value, expected_type):
        raise InputValidationError(
            f"Field '{field_name}' must be of type {expected_type.__name__}, got {type(value).__name__}",
            create_error_context(
                "input_validation",
                additional_info={"field": field_name, "expected_type": expected_type.__name__},
            ),
        )

    # Run custom validator if provided
    if validator and value is not None:
        try:
            validator(value)
        except Exception as e:
            raise InputValidationError(
                f"Validation failed for field '{field_name}': {e!s}",
                create_error_context(
                    "input_validation",
                    additional_info={"field": field_name, "validator_error": str(e)},
                ),
            )


def safe_execute(
    func: Callable,
    *args,
    operation: str = "unknown",
    context: Optional[Dict[str, Any]] = None,
    config: Optional[ErrorHandlingConfig] = None,
    default_return: Any = None,
    **kwargs,
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
    context: Optional[Dict[str, Any]] = None,
    config: Optional[ErrorHandlingConfig] = None,
    default_return: Any = None,
    **kwargs,
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


# CrewAI-specific convenience functions and decorators
def get_crewai_error_handler() -> CrewAIErrorHandler:
    """Get the global CrewAI error handler instance."""
    return _global_crewai_error_handler


def set_crewai_error_handler(handler: CrewAIErrorHandler) -> None:
    """Set the global CrewAI error handler."""
    global _global_crewai_error_handler
    _global_crewai_error_handler = handler


def handle_crewai_error(
    exception: Exception,
    context: Optional[CrewAIErrorContext] = None,
    fallback_message: str = "An unexpected error occurred"
) -> str:
    """
    Convenience function for handling CrewAI errors.
    
    Args:
        exception: The exception that occurred
        context: Optional context information
        fallback_message: Fallback message if recovery fails
        
    Returns:
        User-friendly response message
    """
    handler = get_crewai_error_handler()
    return handler.handle_crewai_error(exception, context, fallback_message)


def create_crewai_error_context(
    agent_role: Optional[str] = None,
    task_type: Optional[str] = None,
    team_id: Optional[str] = None,
    telegram_id: Optional[int] = None,
    username: Optional[str] = None,
    chat_type: Optional[str] = None,
    tool_name: Optional[str] = None,
    llm_model: Optional[str] = None,
    execution_step: Optional[str] = None
) -> CrewAIErrorContext:
    """Convenience function for creating CrewAI error context."""
    return CrewAIErrorContext(
        agent_role=agent_role,
        task_type=task_type,
        team_id=team_id,
        telegram_id=telegram_id,
        username=username,
        chat_type=chat_type,
        tool_name=tool_name,
        llm_model=llm_model,
        execution_step=execution_step
    )


def crewai_error_handler(
    fallback_message: str = "An unexpected error occurred",
    context_factory: Optional[Callable[..., CrewAIErrorContext]] = None
):
    """
    Decorator for automatic CrewAI error handling.
    
    Args:
        fallback_message: Default fallback message
        context_factory: Function to create error context from function args
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = None
                if context_factory:
                    try:
                        context = context_factory(*args, **kwargs)
                    except Exception:
                        pass
                
                return handle_crewai_error(e, context, fallback_message)
        return wrapper
    return decorator


def async_crewai_error_handler(
    fallback_message: str = "An unexpected error occurred",
    context_factory: Optional[Callable[..., CrewAIErrorContext]] = None
):
    """
    Decorator for automatic async CrewAI error handling.
    
    Args:
        fallback_message: Default fallback message
        context_factory: Function to create error context from function args
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = None
                if context_factory:
                    try:
                        context = context_factory(*args, **kwargs)
                    except Exception:
                        pass
                
                return handle_crewai_error(e, context, fallback_message)
        return wrapper
    return decorator
