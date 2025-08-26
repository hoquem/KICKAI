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
        data: The data to include in the response
        message: Message to include in the response (can be success or error message)
        
    Returns:
        JSON string with standardized format
    """
    response = {"status": status.value}
    
    if message:
        response["message"] = message
    
    if data:
        response["data"] = data
        
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
    Extract a single value from input, handling both string and dict inputs.

    Args:
        input_value: Input value (string or dict)
        key: Key to extract

    Returns:
        Extracted value as string
    """
    if isinstance(input_value, dict):
        return str(input_value.get(key, ""))
    elif isinstance(input_value, str):
        return input_value
    else:
        return str(input_value)


def validate_required_input(value: Any, field_name: str) -> Optional[str]:
    """
    Validate that a required input field is present and not empty.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    if value is None:
        return f"❌ {field_name} is required"
    
    if isinstance(value, str) and not value.strip():
        return f"❌ {field_name} cannot be empty"
    
    if isinstance(value, (list, dict)) and not value:
        return f"❌ {field_name} cannot be empty"
    
    return None


def format_tool_error(error: Exception, tool_name: str, context: Dict[str, Any] = None) -> str:
    """
    Format tool errors consistently across the system.
    
    Args:
        error: The exception that occurred
        tool_name: Name of the tool that failed
        context: Optional context information
        
    Returns:
        Formatted error message
    """
    error_msg = f"❌ Tool '{tool_name}' failed: {str(error)}"
    
    if context:
        error_msg += f" (Context: {context})"
    
    logger.error(error_msg)
    return error_msg


def sanitize_input(input_value: str, max_length: int = 100) -> str:
    """
    Sanitize user input to prevent injection attacks and ensure data quality.
    
    Args:
        input_value: The input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not input_value:
        return ""
    
    # Convert to string and strip whitespace
    sanitized = str(input_value).strip()
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '{', '}', '[', ']', '(', ')']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (basic UK format validation).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # UK phone number patterns
    uk_patterns = [
        r'^\+447\d{9}$',  # +447123456789
        r'^07\d{9}$',     # 07123456789
        r'^447\d{9}$',    # 447123456789
    ]
    
    import re
    for pattern in uk_patterns:
        if re.match(pattern, cleaned):
            return True
    
    return False


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to standard UK format.
    
    Args:
        phone: Phone number to normalize
        
    Returns:
        Normalized phone number in +447 format
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Convert to +447 format
    if cleaned.startswith('07'):
        return '+44' + cleaned[1:]
    elif cleaned.startswith('447'):
        return '+' + cleaned
    elif cleaned.startswith('+447'):
        return cleaned
    else:
        return cleaned
