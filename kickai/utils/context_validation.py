"""
Context validation utilities for CrewAI native context passing.

This module provides utilities for validating and handling context data
throughout the system with proper error handling and logging.
"""

import json
from typing import Any

from loguru import logger

from kickai.core.models.context_models import BaseContext
from kickai.core.value_objects.entity_context import EntityContext


class ContextValidationError(Exception):
    """Raised when context validation fails."""

    pass


def validate_context_requirements(required_fields: list[str]) -> None:
    """
    Validate that required context fields are present.


        required_fields: List of required field names


        ContextValidationError: If any required field is missing
    """
    if not required_fields:
        return

    missing_fields = []
    for field in required_fields:
        if not field or not field.strip():
            missing_fields.append(field)

    if missing_fields:
        raise ContextValidationError(f"Missing required context fields: {missing_fields}")


def validate_context_data(context_data: dict[str, Any], required_fields: list[str] | None = None) -> bool:
    """
    Validate context data structure and required fields.


        context_data: Context data dictionary
        required_fields: List of required field names


    :return: True if validation passes
    :rtype: str  # TODO: Fix type


        ContextValidationError: If validation fails
    """
    if not isinstance(context_data, dict):
        raise ContextValidationError("Context data must be a dictionary")

    # Validate required fields if specified
    if required_fields:
        missing_fields = []
        for field in required_fields:
            if field not in context_data or not context_data[field]:
                missing_fields.append(field)

        if missing_fields:
            raise ContextValidationError(f"Missing required fields: {missing_fields}")

    return True


def validate_entity_context(context: EntityContext, required_fields: list[str] | None = None) -> bool:
    """
    Validate EntityContext object.


        context: EntityContext to validate
        required_fields: List of required field names


    :return: True if validation passes
    :rtype: str  # TODO: Fix type


        ContextValidationError: If validation fails
    """
    if not isinstance(context, EntityContext):
        raise ContextValidationError("Context must be an EntityContext instance")

    # Validate required fields if specified
    if required_fields:
        missing_fields = []
        for field in required_fields:
            if not hasattr(context, field) or not getattr(context, field):
                missing_fields.append(field)

        if missing_fields:
            raise ContextValidationError(f"Missing required fields: {missing_fields}")

    return True


def validate_base_context(context: BaseContext, required_fields: list[str] | None = None) -> bool:
    """
    Validate BaseContext object.


        context: BaseContext to validate
        required_fields: List of required field names


    :return: True if validation passes
    :rtype: str  # TODO: Fix type


        ContextValidationError: If validation fails
    """
    if not isinstance(context, BaseContext):
        raise ContextValidationError("Context must be a BaseContext instance")

    # Validate required fields if specified
    if required_fields:
        missing_fields = []
        for field in required_fields:
            if not hasattr(context, field) or not getattr(context, field):
                missing_fields.append(field)

        if missing_fields:
            raise ContextValidationError(f"Missing required fields: {missing_fields}")

    return True


def log_context_validation(tool_name: str, context: Any, input_data: dict[str, Any] | None = None) -> None:
    """
    Log context validation for debugging.


        tool_name: Name of the tool being validated
        context: Context object
        input_data: Input data dictionary
    """
    try:
        # Extract context information
        if hasattr(context, 'telegram_id') and hasattr(context, 'team_id'):
            logger.info(
                f"✅ Context validation successful for {tool_name}: team_id={context.team_id}, telegram_id={context.telegram_id}"
            )
        elif hasattr(context, 'to_dict'):
            context_dict = context.to_dict()
            logger.info(
                f"✅ Context validation successful for {tool_name}: {json.dumps(context_dict, default=str)}"
            )
        else:
            logger.info(f"✅ Context validation successful for {tool_name}")

        # Log input data if provided
        if input_data:
            logger.debug(f"📥 Input data for {tool_name}: {json.dumps(input_data, default=str)}")

    except Exception as e:
        logger.warning(f"⚠️ Could not log context validation for {tool_name}: {e}")


def create_context_summary(context: Any) -> dict[str, Any]:
    """
    Create a summary of context information for logging.


        context: Context object


    :return: Dictionary with context summary
    :rtype: str  # TODO: Fix type
    """
    try:
        if hasattr(context, 'to_dict'):
            return context.to_dict()
        elif hasattr(context, '__dict__'):
            return context.__dict__
        else:
            return {"context_type": type(context).__name__}
    except Exception as e:
        logger.warning(f"⚠️ Could not create context summary: {e}")
        return {"error": str(e)}


def validate_context_for_tool(tool_name: str, context: Any, required_fields: list[str] | None = None) -> bool:
    """
    Comprehensive context validation for tools.


        tool_name: Name of the tool
        context: Context object
        required_fields: List of required fields


    :return: True if validation passes
    :rtype: str  # TODO: Fix type


        ContextValidationError: If validation fails
    """
    try:
        # Validate context type
        if isinstance(context, EntityContext):
            validate_entity_context(context, required_fields)
        elif isinstance(context, BaseContext):
            validate_base_context(context, required_fields)
        else:
            raise ContextValidationError(f"Unsupported context type: {type(context)}")

        # Log successful validation
        log_context_validation(tool_name, context)

        return True

    except Exception as e:
        logger.error(f"❌ Context validation failed for {tool_name}: {e}")
        raise ContextValidationError(f"Context validation failed for {tool_name}: {e}")


def extract_context_data(context: Any) -> dict[str, Any]:
    """
    Extract context data for tool processing.


        context: Context object


    :return: Dictionary with context data
    :rtype: str  # TODO: Fix type
    """
    try:
        if hasattr(context, 'to_dict'):
            return context.to_dict()
        elif hasattr(context, '__dict__'):
            return context.__dict__
        else:
            return {"context_type": type(context).__name__}
    except Exception as e:
        logger.warning(f"⚠️ Could not extract context data: {e}")
        return {"error": str(e)}


def validate_context_requirements_for_tool(tool_name: str, context_data: dict[str, Any], required_fields: list[str]) -> None:
    """
    Validate context requirements for a specific tool.


        tool_name: Name of the tool
        context_data: Context data dictionary
        required_fields: List of required fields


        ContextValidationError: If validation fails
    """
    try:
        validate_context_data(context_data, required_fields)
        logger.info(f"✅ Context requirements validated for {tool_name}")
    except Exception as e:
        logger.error(f"❌ Context requirements validation failed for {tool_name}: {e}")
        raise ContextValidationError(f"Context requirements validation failed for {tool_name}: {e}")


def log_context_validation_failure(tool_name: str, error: Exception) -> None:
    """
    Log context validation failure for debugging.


        tool_name: Name of the tool that failed validation
        error: The validation error that occurred
    """
    logger.error(f"❌ Context validation failed for {tool_name}: {error}")


def log_context_validation_success(tool_name: str, context: Any) -> None:
    """
    Log successful context validation for debugging.


        tool_name: Name of the tool that passed validation
        context: The validated context object
    """
    try:
        if hasattr(context, 'telegram_id') and hasattr(context, 'team_id'):
            logger.info(
                f"✅ Context validation successful for {tool_name}: team_id={context.team_id}, telegram_id={context.telegram_id}"
            )
        else:
            logger.info(f"✅ Context validation successful for {tool_name}")
    except Exception as e:
        logger.warning(f"⚠️ Could not log context validation success for {tool_name}: {e}")


def create_context_log_entry(tool_name: str, context: Any, action: str = "execution") -> dict[str, Any]:
    """
    Create a structured log entry for context operations.


        tool_name: Name of the tool
        context: Context object
        action: Action being performed


    :return: Dictionary with log entry data
    :rtype: str  # TODO: Fix type
    """
    context_data = extract_context_data(context)

    return {
        "tool_name": tool_name,
        "action": action,
        "timestamp": context_data.get("timestamp"),
        "telegram_id": context_data.get("telegram_id", "UNKNOWN"),
        "team_id": context_data.get("team_id", "UNKNOWN"),
        "context_type": type(context).__name__,
        "metadata": context_data.get("metadata", {})
    }
