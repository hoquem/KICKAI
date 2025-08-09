"""
Context validation utilities for CrewAI native context passing.

This module provides utilities for validating and handling context data
throughout the system with proper error handling and logging.
"""

from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import ValidationError

from kickai.core.models.context_models import BaseContext, validate_context_data


class ContextError(Exception):
    """Raised when context validation fails."""

    def __init__(self, message: str, context_data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.context_data = context_data
        super().__init__(self.message)


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""

    def __init__(self, message: str, tool_name: str, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.tool_name = tool_name
        self.context = context
        super().__init__(self.message)


def handle_context_error(error: ValidationError) -> str:
    """
    Format context validation errors for user consumption.

    Args:
        error: Pydantic ValidationError

    Returns:
        Formatted error message
    """
    error_messages = []

    for error_detail in error.errors():
        field = error_detail["loc"][0] if error_detail["loc"] else "unknown"
        message = error_detail["msg"]
        error_messages.append(f"{field}: {message}")

    return f"Context validation failed: {'; '.join(error_messages)}"


def handle_tool_error(error: Exception, context: Dict[str, Any]) -> str:
    """
    Handle tool execution errors with context.

    Args:
        error: The exception that occurred
        context: Context data for debugging

    Returns:
        Formatted error message
    """
    logger.error(f"Tool execution failed: {error}", extra={"context": context})

    if isinstance(error, ContextError):
        return f"Context error: {error!s}"
    elif isinstance(error, ValidationError):
        return handle_context_error(error)
    else:
        return f"Tool execution failed: {error!s}"


def validate_context_for_tool(
    context_data: Dict[str, Any], context_model: type[BaseContext], tool_name: str
) -> BaseContext:
    """
    Validate context data for a specific tool.

    Args:
        context_data: Context data to validate
        context_model: Pydantic model to validate against
        tool_name: Name of the tool for logging

    Returns:
        Validated context object

    Raises:
        ContextError: If validation fails
    """
    try:
        return context_model(**context_data)
    except ValidationError as e:
        error_message = handle_context_error(e)
        logger.error(f"Context validation failed for {tool_name}: {error_message}")
        raise ContextError(error_message, context_data)


def extract_context_from_crewai_input(input_data: Any) -> Dict[str, Any]:
    """
    Extract context from CrewAI's complex input format.

    Args:
        input_data: Input data from CrewAI

    Returns:
        Extracted context dictionary
    """
    if isinstance(input_data, dict):
        # Direct context
        if "team_id" in input_data and "user_id" in input_data:
            return input_data

        # Nested context
        if "security_context" in input_data:
            security_ctx = input_data["security_context"]
            if isinstance(security_ctx, dict):
                return security_ctx

        # Execution context
        if "execution_context" in input_data:
            exec_ctx = input_data["execution_context"]
            if isinstance(exec_ctx, dict):
                return exec_ctx

    return {}


def ensure_context_has_required_fields(
    context_data: Dict[str, Any], required_fields: List[str]
) -> bool:
    """
    Ensure context has all required fields.

    Args:
        context_data: Context data to check
        required_fields: List of required field names

    Returns:
        True if all required fields are present and non-empty
    """
    for field in required_fields:
        if field not in context_data:
            logger.warning(f"Missing required context field: {field}")
            return False

        value = context_data[field]
        if not value or not str(value).strip():
            logger.warning(f"Required context field is empty: {field}")
            return False

    return True


def log_context_validation_success(tool_name: str, context: BaseContext) -> None:
    """
    Log successful context validation.

    Args:
        tool_name: Name of the tool
        context: Validated context object
    """
    logger.debug(
        f"✅ Context validation successful for {tool_name}: team_id={context.team_id}, user_id={context.user_id}"
    )


def log_context_validation_failure(tool_name: str, error: Exception) -> None:
    """
    Log context validation failure.

    Args:
        tool_name: Name of the tool
        error: Validation error
    """
    logger.error(f"❌ Context validation failed for {tool_name}: {error}")


def create_safe_context_fallback(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a safe context fallback when validation fails.

    Args:
        context_data: Original context data

    Returns:
        Safe fallback context
    """
    return {
        "team_id": context_data.get("team_id", "UNKNOWN"),
        "user_id": context_data.get("user_id", "UNKNOWN"),
        "timestamp": context_data.get("timestamp"),
        "metadata": context_data.get("metadata", {}),
    }


def validate_context_data_with_fallback(
    context_data: Dict[str, Any], context_type: str = "base"
) -> Dict[str, Any]:
    """
    Validate context data with fallback to safe context.

    Args:
        context_data: Context data to validate
        context_type: Type of context to validate against

    Returns:
        Validated context data or safe fallback
    """
    try:
        if validate_context_data(context_data, context_type):
            return context_data
        else:
            logger.warning(f"Context validation failed for type {context_type}, using fallback")
            return create_safe_context_fallback(context_data)
    except Exception as e:
        logger.error(f"Context validation error: {e}, using fallback")
        return create_safe_context_fallback(context_data)
