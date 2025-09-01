#!/usr/bin/env python3
"""
Native CrewAI Helpers - Simple Parameter Handling

This module provides simple utilities for native CrewAI parameter handling.
All tools should use simple string parameters for maximum compatibility.
"""

from typing import Optional, List, Dict, Any
from loguru import logger


def convert_telegram_id(telegram_id: str) -> Optional[int]:
    """
    Convert telegram_id string to integer with error handling.
    
    Args:
        telegram_id: String representation of telegram_id
        
    Returns:
        Integer telegram_id or None if invalid
    """
    try:
        telegram_id_int = int(telegram_id)
        if telegram_id_int <= 0:
            logger.warning(f"Invalid telegram_id: {telegram_id} (must be positive)")
            return None
        return telegram_id_int
    except (ValueError, TypeError):
        logger.warning(f"Invalid telegram_id format: {telegram_id}")
        return None


def validate_required_strings(*args: str, names: list[str]) -> Optional[str]:
    """
    Validate that all required string parameters are present and non-empty.
    
    Args:
        *args: String values to validate
        names: Names of the parameters for error messages
        
    Returns:
        Error message if validation fails, None if valid
    """
    for i, value in enumerate(args):
        if not value or not isinstance(value, str) or not value.strip():
            param_name = names[i] if i < len(names) else f"parameter_{i}"
            return f"❌ {param_name} is required and cannot be empty"
    return None


def create_context_string(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    additional_context: str = ""
) -> str:
    """
    Create a context string for CrewAI delegation.
    
    Args:
        telegram_id: User's telegram_id
        team_id: Team identifier
        username: User's username
        chat_type: Chat type context
        additional_context: Additional context information
        
    Returns:
        Formatted context string
    """
    context = f"User: {username}, Team: {team_id}, Chat: {chat_type}"
    if additional_context:
        context += f", Context: {additional_context}"
    return context


def validate_player_data(player_data: Dict[str, Any]) -> bool:
    """
    Validate player data to prevent hallucination.
    
    Args:
        player_data: Dictionary containing player information
        
    Returns:
        True if data is valid, False otherwise
    """
    required_fields = ['player_id', 'name', 'telegram_id']
    
    for field in required_fields:
        if field not in player_data or not player_data[field]:
            logger.warning(f"Missing required player field: {field}")
            return False
    
    # Validate telegram_id is numeric
    try:
        int(str(player_data['telegram_id']))
    except (ValueError, TypeError):
        logger.warning(f"Invalid telegram_id in player data: {player_data['telegram_id']}")
        return False
    
    return True


def validate_team_member_data(member_data: Dict[str, Any]) -> bool:
    """
    Validate team member data to prevent hallucination.
    
    Args:
        member_data: Dictionary containing team member information
        
    Returns:
        True if data is valid, False otherwise
    """
    required_fields = ['member_id', 'name', 'telegram_id']
    
    for field in required_fields:
        if field not in member_data or not member_data[field]:
            logger.warning(f"Missing required team member field: {field}")
            return False
    
    # Validate telegram_id is numeric
    try:
        int(str(member_data['telegram_id']))
    except (ValueError, TypeError):
        logger.warning(f"Invalid telegram_id in team member data: {member_data['telegram_id']}")
        return False
    
    return True


def sanitize_list_response(items: List[Any], max_items: int = 50) -> List[Any]:
    """
    Sanitize list responses to prevent excessive data or hallucination.
    
    Args:
        items: List of items to sanitize
        max_items: Maximum number of items to return
        
    Returns:
        Sanitized list
    """
    if not isinstance(items, list):
        logger.warning(f"Expected list, got {type(items)}")
        return []
    
    # Limit number of items to prevent overwhelming responses
    if len(items) > max_items:
        logger.info(f"Limiting response from {len(items)} to {max_items} items")
        return items[:max_items]
    
    return items


def validate_command_input(command: str) -> bool:
    """
    Validate command input to prevent injection attacks.
    
    Args:
        command: Command string to validate
        
    Returns:
        True if command is valid, False otherwise
    """
    if not command or not isinstance(command, str):
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        'script', 'javascript', 'eval', 'exec', 
        'import', 'os.', 'sys.', 'subprocess'
    ]
    
    command_lower = command.lower()
    for pattern in suspicious_patterns:
        if pattern in command_lower:
            logger.warning(f"Suspicious command pattern detected: {pattern}")
            return False
    
    return True


def format_safe_response(content: str, max_length: int = 2000) -> str:
    """
    Format response content safely to prevent overflow.
    
    Args:
        content: Content to format
        max_length: Maximum length allowed
        
    Returns:
        Safely formatted content
    """
    if not content or not isinstance(content, str):
        return "❌ No content available"
    
    # Truncate if too long
    if len(content) > max_length:
        truncated = content[:max_length-3] + "..."
        logger.info(f"Response truncated from {len(content)} to {len(truncated)} characters")
        return truncated
    
    return content
