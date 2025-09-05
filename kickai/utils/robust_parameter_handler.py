#!/usr/bin/env python3
"""
Robust parameter handling for CrewAI tools.

This module handles the issue where CrewAI's delegation tools may pass 
dict objects instead of individual string parameters to tools. It provides
a unified way to extract context parameters from various input formats.

Handles:
1. Standard keyword arguments: telegram_id="123", team_id="ABC", ...
2. Dict as first positional argument: {'telegram_id': 1003, 'team_id': ...}
3. Context kwarg with dict: context={'telegram_id': 1003, ...}
4. Context kwarg with string: context="User: john, Team: ABC"
5. JSON string as first argument: '{"chat_type": "main", "username": "john"}'

IMPORTANT: This function extracts ONLY what the agent provided.
It does NOT apply defaults for missing parameters.
Tools must handle missing parameters themselves.
"""

import json
from typing import Any

from loguru import logger


def extract_context_parameters(*args, **kwargs) -> dict[str, Any]:
    """
    Extract context parameters from various input formats.

    This function handles multiple input formats that CrewAI agents might use:
    - JSON string as first positional argument: '{"chat_type": "main", "username": "john"}'
    - Dict as first positional argument: {"chat_type": "main", "username": "john"}
    - Context dict in kwargs: context={"chat_type": "main", "username": "john"}
    - Standard keyword arguments: chat_type="main", username="john"

    Args:
        *args: Positional arguments (may contain JSON string or dict)
        **kwargs: Keyword arguments

    Returns:
        Dict with ONLY the parameters that were actually provided by the agent.
        No defaults are applied for missing parameters.
    """
    result = {}

    logger.debug("🔍 DEBUG: extract_context_parameters called with:")
    logger.debug(f"🔍 DEBUG: args = {args}")
    logger.debug(f"🔍 DEBUG: kwargs = {kwargs}")

    try:
        # Case 1: JSON string as first positional argument (most common from CrewAI)
        if args and isinstance(args[0], str):
            first_arg = args[0].strip()
            logger.debug(f"🔍 DEBUG: First arg is string: '{first_arg}'")
            if first_arg.startswith("{") and first_arg.endswith("}"):
                try:
                    parsed_json = json.loads(first_arg)
                    logger.debug(f"🔍 DEBUG: Successfully parsed JSON: {parsed_json}")
                    if isinstance(parsed_json, dict):
                        logger.debug(f"🔧 Parsed JSON from first arg: {list(parsed_json.keys())}")
                        extracted = _extract_from_dict(parsed_json)
                        logger.debug(f"🔧 Extracted from JSON: {extracted}")
                        result.update(extracted)
                    else:
                        logger.debug(f"🔍 DEBUG: Parsed JSON is not a dict: {type(parsed_json)}")
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.debug(f"🔧 Not valid JSON in first arg: {e}")
            else:
                logger.debug(
                    f"🔍 DEBUG: String doesn't look like JSON: starts with '{first_arg[:10]}...'"
                )

        # Case 2: Dict as first positional argument
        elif args and isinstance(args[0], dict):
            context_dict = args[0]
            logger.debug(f"🔧 Extracting from positional dict: {list(context_dict.keys())}")
            extracted = _extract_from_dict(context_dict)
            logger.debug(f"🔧 Extracted from dict: {extracted}")
            result.update(extracted)

        # Case 3: Context in kwargs as dict
        if "context" in kwargs and isinstance(kwargs["context"], dict):
            context_dict = kwargs["context"]
            logger.debug(f"🔧 Extracting from context dict: {list(context_dict.keys())}")
            extracted = _extract_from_dict(context_dict)
            logger.debug(f"🔧 Extracted from context dict: {extracted}")
            result.update(extracted)

        # Case 4: Context in kwargs as string
        elif "context" in kwargs and isinstance(kwargs["context"], str):
            context_str = kwargs["context"]
            logger.debug(f"🔧 Extracting from context string: {context_str[:50]}...")
            extracted = _parse_context_string(context_str)
            logger.debug(f"🔧 Extracted from context string: {extracted}")
            result.update(extracted)

        # Case 5: Standard keyword arguments
        logger.debug("🔧 Extracting from standard kwargs")
        extracted = _extract_from_kwargs(kwargs)
        logger.debug(f"🔧 Extracted from kwargs: {extracted}")
        result.update(extracted)

        # Convert telegram_id to int if it's a string (but only if it exists)
        if "telegram_id" in result and isinstance(result["telegram_id"], str):
            try:
                result["telegram_id"] = int(result["telegram_id"])
                logger.debug(f"🔧 Converted telegram_id to int: {result['telegram_id']}")
            except (ValueError, TypeError):
                logger.warning(f"Could not convert telegram_id to int: {result['telegram_id']}")
                # Keep as string if conversion fails

        logger.debug(f"🔧 Final extracted parameters: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Error extracting context parameters: {e}")
        logger.error(f"❌ Args: {args}, Kwargs: {kwargs}")
        return {}


def _extract_from_dict(context_dict: dict[str, Any]) -> dict[str, Any]:
    """Extract context from a dictionary. Only include parameters that are actually present."""
    result = {}

    logger.debug(f"🔍 DEBUG: _extract_from_dict called with: {context_dict}")

    # Handle all parameters that are present (not just predefined ones)
    for key, value in context_dict.items():
        logger.debug(f"🔍 DEBUG: Processing key '{key}' with value '{value}'")
        if key == "telegram_id":
            result["telegram_id"] = value
        elif key == "team_id":
            result["team_id"] = str(value)
        elif key == "username":
            result["username"] = str(value)
        elif key == "chat_type":
            result["chat_type"] = str(value)
        else:
            # Handle any other parameter (like 'command', 'member_identifier', etc.)
            result[key] = value

    logger.debug(f"🔍 DEBUG: _extract_from_dict returning: {result}")
    return result


def _extract_from_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Extract context from standard keyword arguments. Only include parameters that are actually present."""
    result = {}

    # Handle all parameters that are present (not just predefined ones)
    for key, value in kwargs.items():
        if key == "telegram_id":
            result["telegram_id"] = value
        elif key == "team_id":
            result["team_id"] = str(value)
        elif key == "username":
            result["username"] = str(value)
        elif key == "chat_type":
            result["chat_type"] = str(value)
        else:
            # Handle any other parameter (like 'command', 'member_identifier', etc.)
            result[key] = value

    return result


def _parse_context_string(context_str: str) -> dict[str, Any]:
    """
    Parse a context string like 'User: john, Team: ABC, Chat: main'.

    This handles context strings created by create_context_string() helper.
    Only includes parameters that are actually found in the string.
    """
    result = {}

    try:
        parts = context_str.split(",")
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "user":
                    result["username"] = value
                elif key == "team":
                    result["team_id"] = value
                elif key == "chat":
                    result["chat_type"] = value
                elif key in ["telegram id", "telegram_id"]:
                    try:
                        result["telegram_id"] = int(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not parse telegram_id from string: {value}")

    except Exception as e:
        logger.error(f"Error parsing context string '{context_str}': {e}")

    return result


def validate_required_context(context_params: dict[str, Any], required_fields: list) -> str | None:
    """
    Validate that required context parameters are present.

    Args:
        context_params: Context parameters dict (only what agent provided)
        required_fields: List of required field names for this specific tool

    Returns:
        Error message if validation fails, None if valid
    """
    missing_fields = []
    for field in required_fields:
        if field not in context_params or not context_params[field]:
            missing_fields.append(field)

    if missing_fields:
        # Create helpful error message
        provided_info = ""
        if context_params:
            provided_keys = list(context_params.keys())
            provided_info = f"\n\n📋 Parameters you provided: {', '.join(provided_keys)}"
        else:
            provided_info = "\n\n📋 No parameters provided"

        # Create guidance for missing parameters
        guidance = ""
        if "telegram_id" in missing_fields:
            guidance += "\n• telegram_id: The user's Telegram ID (numeric)"
        if "team_id" in missing_fields:
            guidance += "\n• team_id: The team identifier (e.g., 'KTI')"
        if "chat_type" in missing_fields:
            guidance += "\n• chat_type: Chat context ('main', 'leadership', or 'private')"
        if "username" in missing_fields:
            guidance += "\n• username: The user's name or username"
        if "command" in missing_fields:
            guidance += "\n• command: The specific command to get help for"
        if "member_identifier" in missing_fields:
            guidance += "\n• member_identifier: Member ID, phone number, name, or username"

        return f"❌ Missing required parameters: {', '.join(missing_fields)}{provided_info}\n\n🔧 Please provide:{guidance}"

    return None


def extract_tool_parameters(*args, **kwargs) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Extract both context parameters and tool-specific parameters.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Tuple of (context_params, tool_params)
        - context_params: Dict with context parameters (only what agent provided)
        - tool_params: Dict with remaining parameters for the tool
    """
    # Extract context parameters (only what agent provided)
    context_params = extract_context_parameters(*args, **kwargs)

    # Extract tool-specific parameters (everything not in context)
    context_keys = {"telegram_id", "team_id", "username", "chat_type", "context"}
    tool_params = {key: value for key, value in kwargs.items() if key not in context_keys}

    # If we had a dict as first arg, also check for tool params in there
    if args and isinstance(args[0], dict):
        context_dict = args[0]
        for key, value in context_dict.items():
            if key not in context_keys:
                tool_params[key] = value

    return context_params, tool_params


# Convenience functions for common use cases


def extract_telegram_context(*args, **kwargs) -> dict[str, Any]:
    """
    Extract telegram context parameters.

    Returns:
        Dict with only the parameters that were actually provided
    """
    return extract_context_parameters(*args, **kwargs)


def create_error_response(message: str) -> str:
    """Create a standardized error response."""
    return f"❌ {message}"


def create_success_response(message: str, data: Any = None) -> str:
    """Create a standardized success response."""
    if data:
        return f"✅ {message}: {data}"
    return f"✅ {message}"
