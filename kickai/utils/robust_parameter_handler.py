#!/usr/bin/env python3
"""
Robust parameter handling for CrewAI tools.

This module handles the issue where CrewAI's delegation tools may pass 
dict objects instead of individual string parameters to tools. It provides
a unified way to extract context parameters from various input formats.

Handles:
1. Standard keyword arguments: telegram_id="123", team_id="ABC", ...
2. Dict as first positional argument: {'user_id': 1003, 'team_id': ...}
3. Context kwarg with dict: context={'user_id': 1003, ...}
4. Context kwarg with string: context="User: john, Team: ABC"
"""

from typing import Any, Dict, Union, Optional, Tuple
from loguru import logger


def extract_context_parameters(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context parameters from various input formats.
    
    This function handles the different ways CrewAI might pass parameters:
    1. Individual kwargs: telegram_id="123", team_id="ABC"
    2. Dict as first arg: ({'user_id': 1003, 'team_id': 'ABC'})
    3. Context dict: context={'user_id': 1003, 'team_id': 'ABC'}
    4. Context string: context="User: john, Team: ABC, Chat: main"
    
    Args:
        *args: Positional arguments (may contain dict)
        **kwargs: Keyword arguments (standard or with 'context')
        
    Returns:
        Dict with normalized context parameters:
        - telegram_id: int or None
        - team_id: str
        - username: str  
        - chat_type: str
    """
    # Default values
    result = {
        'telegram_id': None,
        'team_id': '',
        'username': 'user',
        'chat_type': 'main'
    }
    
    try:
        # Case 1: Dict as first positional argument
        if args and isinstance(args[0], dict):
            context_dict = args[0]
            logger.debug(f"🔧 Extracting from positional dict: {list(context_dict.keys())}")
            result.update(_extract_from_dict(context_dict))
            
        # Case 2: Context in kwargs as dict
        elif 'context' in kwargs and isinstance(kwargs['context'], dict):
            context_dict = kwargs['context']
            logger.debug(f"🔧 Extracting from context dict: {list(context_dict.keys())}")
            result.update(_extract_from_dict(context_dict))
            
        # Case 3: Context in kwargs as string
        elif 'context' in kwargs and isinstance(kwargs['context'], str):
            context_str = kwargs['context']
            logger.debug(f"🔧 Extracting from context string: {context_str[:50]}...")
            result.update(_parse_context_string(context_str))
        
        # Case 4: Standard keyword arguments (current implementation)
        else:
            logger.debug("🔧 Extracting from standard kwargs")
            result.update(_extract_from_kwargs(kwargs))
        
        # Convert telegram_id to int if it's a string
        if result['telegram_id'] and isinstance(result['telegram_id'], str):
            try:
                result['telegram_id'] = int(result['telegram_id'])
            except (ValueError, TypeError):
                logger.warning(f"Could not convert telegram_id to int: {result['telegram_id']}")
                result['telegram_id'] = None
        
        logger.debug(f"🔧 Extracted context: telegram_id={result['telegram_id']}, team_id='{result['team_id']}', username='{result['username']}', chat_type='{result['chat_type']}'")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error extracting context parameters: {e}")
        # Return default values on error
        return result


def _extract_from_dict(context_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Extract context from a dictionary."""
    # Handle both 'user_id' and 'telegram_id' keys
    telegram_id = context_dict.get('telegram_id') or context_dict.get('user_id')
    
    return {
        'telegram_id': telegram_id,
        'team_id': str(context_dict.get('team_id', '')),
        'username': str(context_dict.get('username', 'user')),
        'chat_type': str(context_dict.get('chat_type', 'main'))
    }


def _extract_from_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract context from standard keyword arguments."""
    return {
        'telegram_id': kwargs.get('telegram_id'),
        'team_id': str(kwargs.get('team_id', '')),
        'username': str(kwargs.get('username', 'user')),
        'chat_type': str(kwargs.get('chat_type', 'main'))
    }


def _parse_context_string(context_str: str) -> Dict[str, Any]:
    """
    Parse a context string like 'User: john, Team: ABC, Chat: main'.
    
    This handles context strings created by create_context_string() helper.
    """
    result = {
        'telegram_id': None,
        'team_id': '',
        'username': 'user',
        'chat_type': 'main'
    }
    
    try:
        # Parse key-value pairs from string
        parts = context_str.split(',')
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'user':
                    result['username'] = value
                elif key == 'team':
                    result['team_id'] = value
                elif key == 'chat':
                    result['chat_type'] = value
                elif key in ['id', 'user id', 'telegram id', 'userid']:
                    try:
                        result['telegram_id'] = int(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not parse telegram_id from string: {value}")
        
    except Exception as e:
        logger.error(f"Error parsing context string '{context_str}': {e}")
    
    return result


def extract_tool_parameters(*args, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extract both context parameters and tool-specific parameters.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Tuple of (context_params, tool_params)
        - context_params: Dict with telegram_id, team_id, username, chat_type
        - tool_params: Dict with remaining parameters for the tool
    """
    # Extract context parameters
    context_params = extract_context_parameters(*args, **kwargs)
    
    # Extract tool-specific parameters (everything not in context)
    context_keys = {'telegram_id', 'team_id', 'username', 'chat_type', 'context'}
    tool_params = {
        key: value for key, value in kwargs.items() 
        if key not in context_keys
    }
    
    # If we had a dict as first arg, also check for tool params in there
    if args and isinstance(args[0], dict):
        context_dict = args[0]
        for key, value in context_dict.items():
            if key not in context_keys:
                tool_params[key] = value
    
    return context_params, tool_params


def validate_required_context(context_params: Dict[str, Any], 
                             required_fields: Optional[list] = None) -> Optional[str]:
    """
    Validate that required context parameters are present.
    
    Args:
        context_params: Context parameters dict
        required_fields: List of required field names (default: ['telegram_id', 'team_id'])
        
    Returns:
        Error message if validation fails, None if valid
    """
    if required_fields is None:
        required_fields = ['telegram_id', 'team_id']
    
    missing_fields = []
    for field in required_fields:
        if field not in context_params or not context_params[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return f"❌ Missing required context parameters: {', '.join(missing_fields)}"
    
    return None


# Convenience functions for common use cases

def extract_telegram_context(*args, **kwargs) -> Tuple[int, str, str, str]:
    """
    Extract telegram context parameters and return as tuple.
    
    Returns:
        Tuple of (telegram_id, team_id, username, chat_type)
    """
    context = extract_context_parameters(*args, **kwargs)
    return (
        context.get('telegram_id'),
        context.get('team_id', ''),
        context.get('username', 'user'),
        context.get('chat_type', 'main')
    )


def create_error_response(message: str) -> str:
    """Create a standardized error response."""
    return f"❌ {message}"


def create_success_response(message: str, data: Any = None) -> str:
    """Create a standardized success response."""
    if data:
        return f"✅ {message}: {data}"
    return f"✅ {message}"