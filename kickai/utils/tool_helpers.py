#!/usr/bin/env python3
"""
Tool Helper Utilities

This module provides utility functions for handling CrewAI tool inputs and
standardizing error messages across all tools.
"""

import json
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from kickai.core.enums import ResponseStatus


class ContextKeys:
    """Constants for context keys used in tool parsing."""
    
    SECURITY_CONTEXT = "security_context"
    EXECUTION_CONTEXT = "execution_context"
    CONTEXT_DELIMITER = "Context:"


def create_json_response(status: ResponseStatus, data: Any = None, message: str = None) -> str:
    """
    Create a standardized JSON response for tools.
    
    Args:
        status: ResponseStatus enum value (SUCCESS or ERROR)
        data: The data to include in the response (for success responses)
        message: Error message (for error responses)
        
    Returns:
        JSON string with standardized format
    """
    if status == ResponseStatus.SUCCESS:
        response = {"status": status.value, "data": data}
    elif status == ResponseStatus.ERROR:
        response = {"status": status.value, "message": message}
    else:
        raise ValueError(f"Status must be either {ResponseStatus.SUCCESS} or {ResponseStatus.ERROR}")
        
    return json.dumps(response, ensure_ascii=False)


def parse_json_response(json_string: str) -> Dict[str, Any]:
    """
    Parse a JSON response string and return the parsed dict.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        Parsed dictionary
        
    Raises:
        json.JSONDecodeError: If the string is not valid JSON
    """
    return json.loads(json_string)


def parse_crewai_json_input(input_value: str, expected_keys: List[str]) -> Dict[str, str]:
    """
    Parse CrewAI JSON input and extract expected keys.

    Args:
        input_value: The input value (could be JSON string or regular string)
        expected_keys: List of keys to extract from JSON

    Returns:
        Dictionary with extracted values for each expected key

    Raises:
        ValueError: If JSON parsing fails
    """
    if isinstance(input_value, str) and input_value.startswith("{"):
        try:
            parsed = json.loads(input_value)
            return {key: parsed.get(key, "") for key in expected_keys}
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

    # If not JSON, return the input value for the first key (backward compatibility)
    return {expected_keys[0]: input_value} if expected_keys else {}


def extract_single_value(input_value: Any, key: str) -> str:
    """
    Extract a single value from CrewAI input, handling various input formats.

    Args:
        input_value: The input value (could be JSON string, dict, or other types)
        key: The key to extract

    Returns:
        Extracted value or original input_value if not found
    """
    # If it's already a string, try JSON parsing
    if isinstance(input_value, str):
        try:
            parsed = parse_crewai_json_input(input_value, [key])
            return parsed.get(key, input_value)
        except ValueError:
            return input_value

    # If it's a dict, search for the key recursively
    if isinstance(input_value, dict):
        # Direct key lookup
        if key in input_value:
            return str(input_value[key])

        # Search in security_context (common pattern in CrewAI)
        if ContextKeys.SECURITY_CONTEXT in input_value:
            security_ctx = input_value[ContextKeys.SECURITY_CONTEXT]
            if isinstance(security_ctx, dict) and key in security_ctx:
                return str(security_ctx[key])

        # Search in execution_context (another common pattern)
        if ContextKeys.EXECUTION_CONTEXT in input_value:
            exec_ctx = input_value[ContextKeys.EXECUTION_CONTEXT]
            if isinstance(exec_ctx, dict) and key in exec_ctx:
                return str(exec_ctx[key])

        # Recursive search in nested dictionaries
        for k, v in input_value.items():
            if isinstance(v, dict):
                result = extract_single_value(v, key)
                # Check if we found a meaningful result (not the original input)
                if result != str(v) and result != str(input_value):
                    return result

    # Fallback: return string representation
    return str(input_value)


def format_tool_error(message: str, error_type: str = "Error") -> str:
    """
    Format consistent error messages for tools.

    Args:
        message: The error message
        error_type: The type of error (Error, Warning, Info, etc.)

    Returns:
        Formatted error message
    """
    return f"❌ {error_type}: {message}"


def format_tool_success(message: str, success_type: str = "Success") -> str:
    """
    Format consistent success messages for tools.

    Args:
        message: The success message
        success_type: The type of success (Success, Info, etc.)

    Returns:
        Formatted success message
    """
    return f"✅ {success_type}: {message}"


def validate_required_input(value: Union[str, int, Any], field_name: str) -> str:
    """
    Validate that a required input field is not empty.
    Handles strings, integers, and other types naturally.

    Args:
        value: The input value to validate (string, int, or other types)
        field_name: The name of the field for error messages

    Returns:
        Error message if validation fails, empty string if valid
    """
    # Handle integers directly
    if isinstance(value, int):
        return "" if value != 0 else format_tool_error(f"{field_name} is required")
    
    # Handle strings 
    if isinstance(value, str):
        return "" if value and value.strip() else format_tool_error(f"{field_name} is required")
    
    # Handle other types by converting to string
    str_value = str(value) if value is not None else ""
    return "" if str_value.strip() else format_tool_error(f"{field_name} is required")


def extract_context_from_task_description(task_description: str) -> Dict[str, str]:
    """
    Extract context information from CrewAI task description.

    Args:
        task_description: The task description that may contain context information

    Returns:
        Dictionary of context key-value pairs
    """
    context = {}

    try:
        # Look for context section in task description
        if ContextKeys.CONTEXT_DELIMITER in task_description:
            context_section = task_description.split(ContextKeys.CONTEXT_DELIMITER)[1].strip()

            # Parse key-value pairs
            for item in context_section.split(","):
                item = item.strip()
                if ":" in item:
                    key, value = item.split(":", 1)
                    context[key.strip()] = value.strip()

    except (AttributeError, ValueError, KeyError, IndexError) as e:
        # Log specific parsing errors but don't fail the entire operation
        logger.warning(f"Failed to parse context from task description: {e}")

    return context


def sanitize_input(value: str, max_length: int = 255) -> str:
    """
    Sanitize input string by removing/escaping dangerous characters and trimming to max length.

    Args:
        value: The input string to sanitize
        max_length: Maximum allowed length for the string

    Returns:
        Sanitized string
    """
    if not value:
        return ""

    # Convert to string if not already
    value = str(value)

    # Strip whitespace
    value = value.strip()

    # Remove or escape potentially dangerous characters
    # Remove null bytes, control characters, and other dangerous chars
    sanitized = ""
    for char in value:
        # Allow alphanumeric, spaces, and common punctuation
        if char.isprintable() and char not in ["\x00", "\x08", "\x0b", "\x0c"]:
            sanitized += char
        elif char in [" ", "\t"]:
            sanitized += char

    # Trim to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized
