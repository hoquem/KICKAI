#!/usr/bin/env python3
"""
Validation Utilities

This module provides comprehensive input validation for the KICKAI system.
"""

import re

# Valid football positions
VALID_POSITIONS = {
    "goalkeeper",
    "gk",
    "keeper",
    "defender",
    "def",
    "cb",
    "rb",
    "lb",
    "centre-back",
    "right-back",
    "left-back",
    "midfielder",
    "mid",
    "cm",
    "dm",
    "am",
    "centre-mid",
    "defensive-mid",
    "attacking-mid",
    "forward",
    "fwd",
    "st",
    "cf",
    "lw",
    "rw",
    "striker",
    "centre-forward",
    "left-wing",
    "right-wing",
    "winger",
    "wing",
}

# Phone number patterns for different countries
PHONE_PATTERNS = {
    "UK": r"^(\+Union[44, 0])[1-9]\d{1,4}\s?\d{3,4}\s?\d{3,4}$",
    "US": r"^(\+Union[1, 1])?[\s.-]?\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}$",
    "INTL": r"^\+[1-9]\d{1,14}$",  # International format
}


def validate_player_input(name: str, phone: str, position: str, team_id: str) -> list[str]:
    """
    Validate player input parameters.

    Args:
        name: Player's full name
        phone: Player's phone number
        position: Player's position
        team_id: Team ID

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Validate name
    if not name or not name.strip():
        errors.append("Name is required")
    elif len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters")
    elif len(name.strip()) > 100:
        errors.append("Name must be less than 100 characters")
    elif not re.match(r"^[a-zA-Z\s\-\.\']+$", name.strip()):
        errors.append("Name can only contain letters, spaces, hyphens, dots, and apostrophes")

    # Validate phone number
    if not phone or not phone.strip():
        errors.append("Phone number is required")
    elif not is_valid_phone(phone.strip()):
        errors.append("Invalid phone number format")

    # Validate position
    if not position or not position.strip():
        errors.append("Position is required")
    elif position.lower().strip() not in VALID_POSITIONS:
        errors.append(f"Position must be one of: {', '.join(sorted(VALID_POSITIONS))}")

    # Validate team_id
    if not team_id or not team_id.strip():
        errors.append("Team ID is required")
    elif len(team_id.strip()) < 2:
        errors.append("Team ID must be at least 2 characters")
    elif len(team_id.strip()) > 20:
        errors.append("Team ID must be less than 20 characters")
    elif not re.match(r"^[A-Z0-9]+$", team_id.strip()):
        errors.append("Team ID can only contain uppercase letters and numbers")

    return errors


def is_valid_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False

    # Remove all whitespace and common separators
    cleaned_phone = re.sub(r"[\s\-\(\)\.]", "", phone)

    # Check UK format first (most common)
    if re.match(PHONE_PATTERNS["UK"], phone):
        return True

    # Check US format
    if re.match(PHONE_PATTERNS["US"], phone):
        return True

    # Check international format
    if re.match(PHONE_PATTERNS["INTL"], cleaned_phone):
        return True

    return False


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to standard format.

    Args:
        phone: Phone number to normalize

    Returns:
        Normalized phone number
    """
    if not phone:
        return phone

    # Remove all whitespace and common separators
    cleaned = re.sub(r"[\s\-\(\)\.]", "", phone)

    # Handle UK numbers
    if cleaned.startswith("0") and len(cleaned) == 11:
        return "+44" + cleaned[1:]
    elif cleaned.startswith("44") and len(cleaned) == 12:
        return "+" + cleaned

    # Handle US numbers
    if cleaned.startswith("1") and len(cleaned) == 11:
        return "+" + cleaned

    # If it already starts with +, return as is
    if cleaned.startswith("+"):
        return cleaned

    # Default: assume it's a valid international number
    return cleaned


def validate_team_member_input(name: str, phone: str, role: str, team_id: str) -> list[str]:
    """
    Validate team member input parameters.

    Args:
        name: Team member's full name
        phone: Team member's phone number
        role: Team member's role
        team_id: Team ID

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Validate name (same as player)
    name_errors = validate_player_input(name, phone, "", team_id)
    errors.extend([e for e in name_errors if "position" not in e.lower()])

    # Validate role
    valid_roles = {
        "club administrator",
        "admin",
        "administrator",
        "team manager",
        "manager",
        "coach",
        "head coach",
        "assistant coach",
        "assistant",
        "captain",
        "vice captain",
        "secretary",
        "treasurer",
        "coordinator",
        "volunteer",
    }

    if not role or not role.strip():
        errors.append("Role is required")
    elif role.lower().strip() not in valid_roles:
        errors.append(f"Role must be one of: {', '.join(sorted(valid_roles))}")

    return errors


def sanitize_input(text: str, max_length: int = 100) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', "", text.strip())

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def validate_invite_link(invite_link: str) -> tuple[bool, str]:
    """
    Validate invite link format.

    Args:
        invite_link: Invite link to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not invite_link:
        return False, "Invite link is required"

    # Check if it's a valid Telegram invite link
    if not invite_link.startswith("https://t.me/+"):
        return False, "Invalid invite link format. Must be a Telegram invite link."

    # Check if it has the required hash part
    if len(invite_link.split("t.me/+")) != 2:
        return False, "Invalid invite link format. Missing invite hash."

    hash_part = invite_link.split("t.me/+")[1]
    if not hash_part or len(hash_part) < 10:
        return False, "Invalid invite link format. Invite hash too short."

    return True, ""


def validate_team_id(team_id: str) -> tuple[bool, str]:
    """
    Validate team ID format.

    Args:
        team_id: Team ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not team_id:
        return False, "Team ID is required"

    if len(team_id) < 2:
        return False, "Team ID must be at least 2 characters"

    if len(team_id) > 20:
        return False, "Team ID must be less than 20 characters"

    if not re.match(r"^[A-Z0-9]+$", team_id):
        return False, "Team ID can only contain uppercase letters and numbers"

    return True, ""
