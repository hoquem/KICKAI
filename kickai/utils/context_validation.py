#!/usr/bin/env python3
"""
Context validation utilities for KICKAI CrewAI integration.

Simplified context validation for CrewAI native parameter passing.
"""

from typing import Any, Type

from loguru import logger
from pydantic import ValidationError

from kickai.core.models.context_models import BaseContext


class ContextError(Exception):
    """Exception raised when context validation fails."""

    def __init__(self, message: str, context_data: dict[str, Any] = None):
        super().__init__(message)
        self.context_data = context_data or {}


def validate_context_for_tool(
    context_data: dict[str, Any], context_model: Type[BaseContext], tool_name: str
) -> BaseContext:
    """
    Validate context data for a specific tool.
    
    Args:
        context_data: Raw context data
        context_model: Pydantic model for validation
        tool_name: Name of the tool for error reporting
        
    Returns:
        Validated context model instance
        
    Raises:
        ContextError: If validation fails
    """
    try:
        # Basic validation first
        if not context_data:
            raise ContextError(f"Empty context data for tool '{tool_name}'")
            
        # Create validated context model
        validated_context = context_model(**context_data)
        return validated_context
        
    except ValidationError as e:
        error_msg = f"Context validation failed for tool '{tool_name}': {e}"
        logger.error(error_msg)
        raise ContextError(error_msg, context_data)
    except Exception as e:
        error_msg = f"Unexpected error validating context for tool '{tool_name}': {e}"
        logger.error(error_msg)
        raise ContextError(error_msg, context_data)


def log_context_validation_success(tool_name: str, context: BaseContext) -> None:
    """Log successful context validation."""
    logger.debug(f"✅ Context validated for tool '{tool_name}' - Team: {context.team_id}")


def log_context_validation_failure(tool_name: str, error: ContextError) -> None:
    """Log context validation failure."""
    logger.error(f"❌ Context validation failed for tool '{tool_name}': {error}")


def validate_context_data_with_fallback(
    context_data: dict[str, Any], 
    context_type: str,
    tool_name: str = "unknown"
) -> bool:
    """
    Validate context data with fallback validation.
    
    Args:
        context_data: Context data to validate
        context_type: Type of context
        tool_name: Tool name for logging
        
    Returns:
        True if valid, False otherwise
    """
    try:
        from kickai.core.models.context_models import validate_context_data
        
        if validate_context_data(context_data, context_type):
            logger.debug(f"✅ Context validation passed for {tool_name}")
            return True
        else:
            logger.warning(f"⚠️ Context validation failed for {tool_name}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Context validation error for {tool_name}: {e}")
        return False