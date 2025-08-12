#!/usr/bin/env python3
"""
Telegram ID Conversion Utilities

This module provides robust utilities for handling Telegram ID conversions
between string and integer formats, ensuring consistent database queries
and preventing type mismatch issues.
"""

from typing import Any, Union
from loguru import logger


def normalize_telegram_id_for_query(telegram_id: Union[str, int, None]) -> Union[int, None]:
    """
    Normalize telegram_id to integer format for consistent database queries.
    
    Uses Telegram's native integer format which is more efficient and
    consistent with Telegram's API specification.
    
    Args:
        telegram_id: Telegram ID in string or integer format
        
    Returns:
        Integer telegram_id or None if invalid
        
    Examples:
        >>> normalize_telegram_id_for_query("1001")
        1001
        >>> normalize_telegram_id_for_query(1001)
        1001
        >>> normalize_telegram_id_for_query(None)
        None
        >>> normalize_telegram_id_for_query("")
        None
    """
    if telegram_id is None:
        return None
        
    if isinstance(telegram_id, int):
        return telegram_id if telegram_id > 0 else None
        
    if isinstance(telegram_id, str):
        if not telegram_id.strip():
            return None
        try:
            # Convert to integer and validate it's positive
            int_id = int(telegram_id)
            return int_id if int_id > 0 else None
        except ValueError:
            logger.warning(f"Invalid telegram_id format: '{telegram_id}' - not a valid integer")
            return None
    
    logger.warning(f"Unexpected telegram_id type: {type(telegram_id)} - value: {telegram_id}")
    return None


def normalize_telegram_id_for_storage(telegram_id: Union[str, int, None]) -> Union[int, None]:
    """
    Normalize telegram_id to integer format for consistent database storage.
    
    Uses the same integer format as query normalization to maintain consistency.
    Firestore handles integers natively and efficiently.
    
    Args:
        telegram_id: Telegram ID in string or integer format
        
    Returns:
        Integer telegram_id or None if invalid
    """
    return normalize_telegram_id_for_query(telegram_id)


def safe_telegram_id_to_int(telegram_id: Union[str, int, None]) -> int:
    """
    Safely convert telegram_id to integer, raising ValueError if invalid.
    
    Use this when you need to guarantee an integer result or fail explicitly.
    
    Args:
        telegram_id: Telegram ID in string or integer format
        
    Returns:
        Integer telegram_id
        
    Raises:
        ValueError: If telegram_id cannot be converted to valid integer
    """
    normalized = normalize_telegram_id_for_query(telegram_id)
    if normalized is None:
        raise ValueError(f"Cannot convert telegram_id to integer: {telegram_id}")
    return normalized


def safe_telegram_id_to_string(telegram_id: Union[str, int, None]) -> str:
    """
    Safely convert telegram_id to string, raising ValueError if invalid.
    
    Kept for backward compatibility with existing code.
    
    Args:
        telegram_id: Telegram ID in string or integer format
        
    Returns:
        String telegram_id
        
    Raises:
        ValueError: If telegram_id cannot be converted to valid string
    """
    normalized = normalize_telegram_id_for_query(telegram_id)
    if normalized is None:
        raise ValueError(f"Cannot convert telegram_id to string: {telegram_id}")
    return str(normalized)


def is_valid_telegram_id(telegram_id: Any) -> bool:
    """
    Check if a value is a valid telegram_id.
    
    Args:
        telegram_id: Value to check
        
    Returns:
        True if valid telegram_id, False otherwise
    """
    try:
        normalized = normalize_telegram_id_for_query(telegram_id)
        return normalized is not None and normalized > 0
    except Exception:
        return False