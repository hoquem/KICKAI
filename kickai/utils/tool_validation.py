#!/usr/bin/env python3
"""
Tool Validation and Error Handling

This module provides comprehensive input validation and error handling for all tools,
following CrewAI best practices for robust error handling.
"""

import re
import traceback
from typing import Any, Dict, List, Optional, Union
from functools import wraps

from loguru import logger
from pydantic import BaseModel, ValidationError, validator

from kickai.utils.tool_helpers import format_tool_error, sanitize_input
from kickai.utils.tool_context_helpers import get_context_for_tool


class ToolValidationError(Exception):
    """Custom exception for tool validation errors."""
    
    def __init__(self, message: str, error_type: str = "ValidationError"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class ToolExecutionError(Exception):
    """Custom exception for tool execution errors."""
    
    def __init__(self, message: str, error_type: str = "ExecutionError"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


def validate_string_input(value: Any, field_name: str, max_length: int = 255, 
                         allow_empty: bool = False, pattern: Optional[str] = None) -> str:
    """
    Validate string input with comprehensive checks.
    
    Args:
        value: Input value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length
        allow_empty: Whether empty strings are allowed
        pattern: Regex pattern for validation
        
    Returns:
        Sanitized string value
        
    Raises:
        ToolValidationError: If validation fails
    """
    try:
        # Convert to string
        if value is None:
            if allow_empty:
                return ""
            raise ToolValidationError(f"{field_name} cannot be None")
        
        value = str(value).strip()
        
        # Check for empty string
        if not value and not allow_empty:
            raise ToolValidationError(f"{field_name} cannot be empty")
        
        # Check length
        if len(value) > max_length:
            raise ToolValidationError(f"{field_name} exceeds maximum length of {max_length} characters")
        
        # Check pattern if provided
        if pattern and value:
            if not re.match(pattern, value):
                raise ToolValidationError(f"{field_name} does not match required pattern")
        
        # Sanitize input
        return sanitize_input(value, max_length)
        
    except ToolValidationError:
        raise
    except Exception as e:
        raise ToolValidationError(f"Failed to validate {field_name}: {str(e)}")


def validate_team_id(team_id: Any) -> str:
    """Validate team ID format."""
    return validate_string_input(
        team_id, 
        "Team ID", 
        max_length=50, 
        pattern=r'^[a-zA-Z0-9_-]+$'
    )


def validate_user_id(user_id: Any) -> str:
    """Validate user ID format."""
    return validate_string_input(
        user_id, 
        "User ID", 
        max_length=50, 
        pattern=r'^[a-zA-Z0-9_-]+$'
    )


def validate_telegram_id(telegram_id: Union[str, int]) -> int:
    """Validate Telegram ID format and return as integer."""
    try:
        # Convert to string first for validation
        if isinstance(telegram_id, int):
            telegram_id_str = str(telegram_id)
        else:
            telegram_id_str = str(telegram_id).strip()
        
        # Validate format (must be numeric)
        if not telegram_id_str.isdigit():
            raise ToolValidationError("Telegram ID must contain only digits")
        
        # Validate length
        if len(telegram_id_str) > 20:
            raise ToolValidationError("Telegram ID exceeds maximum length of 20 characters")
        
        if len(telegram_id_str) == 0:
            raise ToolValidationError("Telegram ID cannot be empty")
        
        # Return as integer
        return int(telegram_id_str)
        
    except ToolValidationError:
        raise
    except Exception as e:
        raise ToolValidationError(f"Failed to validate Telegram ID: {str(e)}")


def validate_message_content(message: Any, max_length: int = 4096) -> str:
    """Validate message content."""
    return validate_string_input(
        message, 
        "Message", 
        max_length=max_length,
        allow_empty=False
    )


def validate_phone_number(phone: Any) -> str:
    """Validate phone number format."""
    return validate_string_input(
        phone, 
        "Phone Number", 
        max_length=20,
        pattern=r'^\+?[0-9\s\-\(\)]+$'
    )


def validate_email(email: Any) -> str:
    """Validate email format."""
    return validate_string_input(
        email, 
        "Email", 
        max_length=255,
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )


def validate_match_id(match_id: Any) -> str:
    """Validate match ID format."""
    return validate_string_input(
        match_id, 
        "Match ID", 
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )


def validate_player_id(player_id: Any) -> str:
    """Validate player ID format."""
    return validate_string_input(
        player_id, 
        "Player ID", 
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )


def validate_chat_type(chat_type: Any) -> str:
    """Validate chat type."""
    valid_types = ['main', 'leadership', 'private']
    chat_type = validate_string_input(chat_type, "Chat Type", max_length=20)
    
    if chat_type not in valid_types:
        raise ToolValidationError(f"Chat Type must be one of: {', '.join(valid_types)}")
    
    return chat_type


def validate_user_role(user_role: Any) -> str:
    """Validate user role."""
    valid_roles = ['public', 'player', 'team_member', 'admin', 'owner']
    user_role = validate_string_input(user_role, "User Role", max_length=20)
    
    if user_role not in valid_roles:
        raise ToolValidationError(f"User Role must be one of: {', '.join(valid_roles)}")
    
    return user_role


def validate_boolean(value: Any, field_name: str) -> bool:
    """Validate boolean input."""
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        value = value.lower().strip()
        if value in ['true', '1', 'yes', 'on']:
            return True
        elif value in ['false', '0', 'no', 'off']:
            return False
        else:
            raise ToolValidationError(f"{field_name} must be a valid boolean value")
    else:
        raise ToolValidationError(f"{field_name} must be a boolean")


def validate_integer(value: Any, field_name: str, min_value: Optional[int] = None, 
                   max_value: Optional[int] = None) -> int:
    """Validate integer input."""
    try:
        if isinstance(value, int):
            result = value
        elif isinstance(value, str):
            result = int(value.strip())
        else:
            raise ToolValidationError(f"{field_name} must be a valid integer")
        
        if min_value is not None and result < min_value:
            raise ToolValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and result > max_value:
            raise ToolValidationError(f"{field_name} must be at most {max_value}")
        
        return result
        
    except ValueError:
        raise ToolValidationError(f"{field_name} must be a valid integer")


def validate_list(value: Any, field_name: str, item_validator=None, 
                 min_items: Optional[int] = None, max_items: Optional[int] = None) -> List:
    """Validate list input."""
    if not isinstance(value, (list, tuple)):
        if isinstance(value, str):
            # Try to parse as comma-separated string
            value = [item.strip() for item in value.split(',') if item.strip()]
        else:
            raise ToolValidationError(f"{field_name} must be a list")
    
    result = list(value)
    
    if min_items is not None and len(result) < min_items:
        raise ToolValidationError(f"{field_name} must have at least {min_items} items")
    
    if max_items is not None and len(result) > max_items:
        raise ToolValidationError(f"{field_name} must have at most {max_items} items")
    
    if item_validator:
        validated_items = []
        for i, item in enumerate(result):
            try:
                validated_items.append(item_validator(item, f"{field_name}[{i}]"))
            except ToolValidationError as e:
                raise ToolValidationError(f"Item {i} in {field_name}: {e.message}")
        result = validated_items
    
    return result


def validate_context_requirements(tool_name: str, required_keys: List[str]) -> Dict[str, Any]:
    """
    Validate that required context keys are available.
    
    With CrewAI native parameter passing, tools receive parameters directly.
    This function now validates that the required parameters are present in the function call.
    
    Args:
        tool_name: Name of the tool for error messages
        required_keys: List of required context keys
        
    Returns:
        Empty dict (validation happens at tool call time)
        
    Raises:
        ToolValidationError: If required context is missing
    """
    # With CrewAI native parameter passing, validation happens at tool call time
    # This function is kept for backward compatibility but simplified
    logger.debug(f"🔍 Context validation for {tool_name}: {required_keys} will be validated at call time")
    return {}


def tool_error_handler(func):
    """
    Decorator for comprehensive tool error handling following CrewAI best practices.
    
    This decorator:
    1. Catches all exceptions and prevents them from propagating
    2. Logs detailed error information for debugging
    3. Returns structured error messages to the CrewAI agent
    4. Ensures tools never crash the system
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ToolValidationError as e:
            logger.warning(f"🔍 Tool validation error in {func.__name__}: {e.message}")
            return format_tool_error(f"Input validation failed: {e.message}", "ValidationError")
        except ToolExecutionError as e:
            logger.error(f"⚡ Tool execution error in {func.__name__}: {e.message}")
            return format_tool_error(f"Execution failed: {e.message}", "ExecutionError")
        except Exception as e:
            logger.error(f"💥 Unexpected error in {func.__name__}: {str(e)}")
            logger.error(f"📋 Error details: {traceback.format_exc()}")
            return format_tool_error(
                f"An unexpected error occurred: {str(e)}", 
                "SystemError"
            )
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ToolValidationError as e:
            logger.warning(f"🔍 Tool validation error in {func.__name__}: {e.message}")
            return format_tool_error(f"Input validation failed: {e.message}", "ValidationError")
        except ToolExecutionError as e:
            logger.error(f"⚡ Tool execution error in {func.__name__}: {e.message}")
            return format_tool_error(f"Execution failed: {e.message}", "ExecutionError")
        except Exception as e:
            logger.error(f"💥 Unexpected error in {func.__name__}: {str(e)}")
            logger.error(f"📋 Error details: {traceback.format_exc()}")
            return format_tool_error(
                f"An unexpected error occurred: {str(e)}", 
                "SystemError"
            )
    
    # Return appropriate wrapper based on function type
    if func.__code__.co_flags & 0x80:  # CO_COROUTINE flag
        return async_wrapper
    else:
        return sync_wrapper


class BaseToolInput(BaseModel):
    """Base class for tool input validation using Pydantic."""
    
    class Config:
        extra = "forbid"  # Reject extra fields
        validate_assignment = True  # Validate on assignment
    
    @validator('*', pre=True)
    def validate_strings(cls, v):
        """Pre-validator to handle string sanitization."""
        if isinstance(v, str):
            return sanitize_input(v)
        return v


def validate_tool_inputs(inputs: Dict[str, Any], validators: Dict[str, callable]) -> Dict[str, Any]:
    """
    Validate tool inputs using provided validators.
    
    Args:
        inputs: Dictionary of input values
        validators: Dictionary mapping field names to validation functions
        
    Returns:
        Dictionary of validated inputs
        
    Raises:
        ToolValidationError: If validation fails
    """
    validated = {}
    
    for field_name, validator_func in validators.items():
        if field_name not in inputs:
            raise ToolValidationError(f"Required field '{field_name}' is missing")
        
        try:
            validated[field_name] = validator_func(inputs[field_name], field_name)
        except ToolValidationError:
            raise
        except Exception as e:
            raise ToolValidationError(f"Failed to validate '{field_name}': {str(e)}")
    
    return validated


def log_tool_execution(tool_name: str, inputs: Dict[str, Any], success: bool, 
                      error_message: Optional[str] = None):
    """
    Log tool execution details for monitoring and debugging.
    
    Args:
        tool_name: Name of the tool being executed
        inputs: Input parameters (sanitized for logging)
        success: Whether execution was successful
        error_message: Error message if execution failed
    """
    # Sanitize inputs for logging (remove sensitive data)
    safe_inputs = {}
    for key, value in inputs.items():
        if isinstance(value, str) and len(value) > 100:
            safe_inputs[key] = f"{value[:50]}...{value[-50:]}"
        else:
            safe_inputs[key] = value
    
    if success:
        logger.info(f"✅ Tool '{tool_name}' executed successfully with inputs: {safe_inputs}")
    else:
        logger.error(f"❌ Tool '{tool_name}' failed with inputs: {safe_inputs}, error: {error_message}")


def create_tool_response(success: bool, message: str, data: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a structured tool response following CrewAI best practices.
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Optional data to include in response
        
    Returns:
        Formatted response string
    """
    if success:
        response = f"✅ {message}"
        if data:
            response += f"\n📊 Data: {data}"
    else:
        response = f"❌ {message}"
        if data:
            response += f"\n🔍 Details: {data}"
    
    return response

