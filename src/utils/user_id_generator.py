"""
User ID Generator Utility

This module provides utilities for generating consistent user_id values
that link Team Members and Players when a user has both roles in the system.
"""

from typing import Union


def generate_user_id(telegram_id: Union[int, str]) -> str:
    """
    Generate a consistent user_id from a Telegram ID.
    
    This function creates a standardized user_id that can be used to link
    different entity types (Team Members, Players) for the same person.
    
    Args:
        telegram_id: The Telegram user ID (can be int or string)
        
    Returns:
        A consistent user_id string in the format "user_{telegram_id}"
        
    Examples:
        >>> generate_user_id(8148917292)
        'user_8148917292'
        >>> generate_user_id("123456789")
        'user_123456789'
    """
    # Convert to string if it's an integer
    telegram_id_str = str(telegram_id)
    
    # Generate the user_id
    user_id = f"user_{telegram_id_str}"
    
    return user_id


def extract_telegram_id_from_user_id(user_id: str) -> str:
    """
    Extract the Telegram ID from a user_id.
    
    Args:
        user_id: The user_id in format "user_{telegram_id}"
        
    Returns:
        The Telegram ID as a string
        
    Examples:
        >>> extract_telegram_id_from_user_id("user_8148917292")
        '8148917292'
    """
    if not user_id.startswith("user_"):
        raise ValueError(f"Invalid user_id format: {user_id}. Expected format: 'user_{{telegram_id}}'")
    
    telegram_id = user_id[5:]  # Remove "user_" prefix
    return telegram_id


def is_valid_user_id(user_id: str) -> bool:
    """
    Check if a user_id has the correct format.
    
    Args:
        user_id: The user_id to validate
        
    Returns:
        True if the user_id has the correct format, False otherwise
        
    Examples:
        >>> is_valid_user_id("user_8148917292")
        True
        >>> is_valid_user_id("invalid_format")
        False
    """
    try:
        extract_telegram_id_from_user_id(user_id)
        return True
    except ValueError:
        return False


def get_user_entities_summary(user_id: str) -> dict:
    """
    Get a summary of what entity types a user_id is associated with.
    
    This is a helper function that can be used to determine if a user
    has multiple roles in the system.
    
    Args:
        user_id: The user_id to check
        
    Returns:
        A dictionary with entity type information
        
    Example:
        >>> get_user_entities_summary("user_8148917292")
        {
            "user_id": "user_8148917292",
            "telegram_id": "8148917292",
            "has_team_member_role": True,
            "has_player_role": True,
            "has_multiple_roles": True
        }
    """
    if not is_valid_user_id(user_id):
        raise ValueError(f"Invalid user_id: {user_id}")
    
    telegram_id = extract_telegram_id_from_user_id(user_id)
    
    return {
        "user_id": user_id,
        "telegram_id": telegram_id,
        "has_team_member_role": False,  # To be populated by calling code
        "has_player_role": False,       # To be populated by calling code
        "has_multiple_roles": False     # To be calculated by calling code
    } 