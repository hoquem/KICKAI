from typing import Optional, Tuple
#!/usr/bin/env python3
"""
Security Utilities for KICKAI System

This module provides security-related utilities including input sanitization
and validation functions to prevent injection attacks and ensure data safety.
"""

import html
import re

from loguru import logger


def sanitize_username(username: str) -> str:
    """
    Sanitize username to prevent injection attacks.

    Args:
        username: Raw username from user input

    Returns:
        Sanitized username safe for display and processing

    Security measures:
    - HTML entity escaping
    - Markdown formatting removal
    - Length limiting
    - Special character filtering
    """
    try:
        if not username:
            return "Unknown User"

        # Convert to string if needed
        username = str(username).strip()

        # Remove HTML tags and escape entities
        sanitized = html.escape(username)

        # Remove markdown formatting characters
        sanitized = re.sub(r'[*_`~\[\]()#+\-|!]', '', sanitized)

        # Remove any remaining HTML-like patterns
        sanitized = re.sub(r'<[^>]*>', '', sanitized)

        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)

        # Limit length to prevent abuse
        sanitized = sanitized[:50]

        # Ensure we have a valid username
        if not sanitized or sanitized.isspace():
            return "Unknown User"

        return sanitized

    except Exception as e:
        logger.error(f"❌ Error sanitizing username '{username}': {e}")
        return "Unknown User"


def validate_telegram_update(update) -> Tuple[bool, Optional[str]]:
    """
    Validate Telegram update structure and content.

    Args:
        update: Telegram update object

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if update exists
        if not update:
            return False, "Update object is None or empty"

        # Check for required attributes
        if not hasattr(update, 'effective_chat'):
            return False, "Update missing effective_chat attribute"

        if not hasattr(update, 'effective_user'):
            return False, "Update missing effective_user attribute"

        # Validate chat object
        chat = update.effective_chat
        if not chat or not hasattr(chat, 'id'):
            return False, "Invalid chat object or missing chat ID"

        # Validate user object
        user = update.effective_user
        if not user or not hasattr(user, 'id'):
            return False, "Invalid user object or missing user ID"

        # Check for message object if this is a message update
        if hasattr(update, 'message'):
            message = update.message
            if message and not hasattr(message, 'text'):
                return False, "Message object missing text attribute"

        return True, None

    except Exception as e:
        logger.error(f"❌ Error validating Telegram update: {e}")
        return False, f"Validation error: {e!s}"


def validate_new_chat_members_update(update) -> Tuple[bool, Optional[str]]:
    """
    Validate new chat members update specifically.

    Args:
        update: Telegram update object

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if update exists
        if not update:
            return False, "Update object is None or empty"

        # Check for message object
        if not hasattr(update, 'message') or not update.message:
            return False, "Update missing message object"

        # Check for new_chat_members
        if not hasattr(update.message, 'new_chat_members'):
            return False, "Message missing new_chat_members attribute"

        # Validate new_chat_members - handle different possible types
        new_members = update.message.new_chat_members

        # Check if it's None or empty
        if new_members is None:
            return False, "new_chat_members is None"

        # Check if it's a list
        if not isinstance(new_members, list):
            # Try to convert to list if it's not already
            try:
                if hasattr(new_members, '__iter__'):
                    new_members = list(new_members)
                else:
                    return False, f"new_chat_members is not a list (type: {type(new_members)})"
            except Exception as e:
                return False, f"new_chat_members cannot be converted to list: {e!s}"

        # Check if list is empty
        if len(new_members) == 0:
            return False, "new_chat_members list is empty"

        # Validate each member
        for i, member in enumerate(new_members):
            if not member:
                return False, f"Member {i} is None or empty"

            if not hasattr(member, 'id'):
                return False, f"Member {i} missing ID attribute"

            if not hasattr(member, 'is_bot'):
                return False, f"Member {i} missing is_bot attribute"

            # Additional validation for user attributes
            if not hasattr(member, 'username') and not hasattr(member, 'first_name'):
                return False, f"Member {i} missing username and first_name attributes"

        return True, None

    except Exception as e:
        logger.error(f"❌ Error validating new chat members update: {e}")
        return False, f"Validation error: {e!s}"


def sanitize_message_text(text: str) -> str:
    """
    Sanitize message text to prevent injection attacks.

    Args:
        text: Raw message text

    Returns:
        Sanitized text safe for processing
    """
    try:
        if not text:
            return ""

        # Convert to string
        text = str(text).strip()

        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)

        # Escape HTML entities
        text = html.escape(text)

        # Limit length
        text = text[:1000]

        return text

    except Exception as e:
        logger.error(f"❌ Error sanitizing message text: {e}")
        return ""


def validate_chat_id(chat_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate chat ID format and content.

    Args:
        chat_id: Chat ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not chat_id:
            return False, "Chat ID is empty"

        chat_id = str(chat_id).strip()

        # Check if it's a valid integer or string format
        if not re.match(r'^-?\d+$', chat_id):
            return False, "Chat ID must be a valid integer"

        # Check reasonable bounds
        try:
            chat_id_int = int(chat_id)
            if chat_id_int < -999999999999999 or chat_id_int > 999999999999999:
                return False, "Chat ID out of reasonable bounds"
        except ValueError:
            return False, "Chat ID cannot be converted to integer"

        return True, None

    except Exception as e:
        logger.error(f"❌ Error validating chat ID '{chat_id}': {e}")
        return False, f"Validation error: {e!s}"
