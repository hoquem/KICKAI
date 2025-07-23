#!/usr/bin/env python3
"""
Validation Utilities

This module provides centralized validation functions for common data types
used throughout the KICKAI system. This ensures a single source of truth for
validation rules and simplifies updates.
"""

import logging
import re
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.utils.phone_utils import is_valid_phone

logger = logging.getLogger(__name__)


# ============================================================================
# PHONE NUMBER VALIDATION
# ============================================================================

def validate_phone(phone: str, region: str = "GB") -> bool:
    """
    Validate phone number format using phonenumbers library.
    
    Args:
        phone: Phone number to validate
        region: Country code for parsing local numbers (default: "GB")
        
    Returns:
        True if the phone number is valid, False otherwise
    """
    return is_valid_phone(phone, region)


def validate_phone_with_error(phone: str, region: str = "GB") -> tuple[bool, str | None]:
    """
    Validate phone number and return error message if invalid.
    
    Args:
        phone: Phone number to validate
        region: Country code for parsing local numbers (default: "GB")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone or not phone.strip():
        return False, "Phone number cannot be empty"

    if not is_valid_phone(phone, region):
        return False, "Invalid phone number format. Must be a valid UK phone number (e.g., 07123456789, +447123456789)"

    return True, None


# ============================================================================
# EMAIL VALIDATION
# ============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email format using regex pattern.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if the email format is valid, False otherwise
    """
    if not email or not email.strip():
        return False

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def validate_email_with_error(email: str) -> tuple[bool, str | None]:
    """
    Validate email format and return error message if invalid.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email address cannot be empty"

    if not validate_email(email):
        return False, "Invalid email format"

    return True, None


# ============================================================================
# NAME VALIDATION
# ============================================================================

def validate_name(name: str, min_length: int = 2, max_length: int = 100) -> bool:
    """
    Validate name format.
    
    Args:
        name: Name to validate
        min_length: Minimum length required (default: 2)
        max_length: Maximum length allowed (default: 100)
        
    Returns:
        True if the name is valid, False otherwise
    """
    if not name or not name.strip():
        return False

    name_length = len(name.strip())
    return min_length <= name_length <= max_length


def validate_name_with_error(name: str, min_length: int = 2, max_length: int = 100) -> tuple[bool, str | None]:
    """
    Validate name format and return error message if invalid.
    
    Args:
        name: Name to validate
        min_length: Minimum length required (default: 2)
        max_length: Maximum length allowed (default: 100)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name cannot be empty"

    name_length = len(name.strip())
    if name_length < min_length:
        return False, f"Name must be at least {min_length} characters long"

    if name_length > max_length:
        return False, f"Name cannot exceed {max_length} characters"

    return True, None


def validate_team_name(name: str, min_length: int = 3, max_length: int = 100) -> bool:
    """
    Validate team name format.
    
    Args:
        name: Team name to validate
        min_length: Minimum length required (default: 3)
        max_length: Maximum length allowed (default: 100)
        
    Returns:
        True if the team name is valid, False otherwise
    """
    return validate_name(name, min_length, max_length)


def validate_team_name_with_error(name: str, min_length: int = 3, max_length: int = 100) -> tuple[bool, str | None]:
    """
    Validate team name format and return error message if invalid.
    
    Args:
        name: Team name to validate
        min_length: Minimum length required (default: 3)
        max_length: Maximum length allowed (default: 100)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Team name cannot be empty"

    name_length = len(name.strip())
    if name_length < min_length:
        return False, f"Team name must be at least {min_length} characters long"

    if name_length > max_length:
        return False, f"Team name cannot exceed {max_length} characters"

    return True, None


# ============================================================================
# DATE VALIDATION
# ============================================================================

def validate_date_of_birth(dob: str) -> bool:
    """
    Validate date of birth format (DD/MM/YYYY).
    
    Args:
        dob: Date of birth string in DD/MM/YYYY format
        
    Returns:
        True if the date is valid, False otherwise
    """
    try:
        # Check format
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', dob):
            return False

        # Parse date
        day, month, year = map(int, dob.split('/'))
        datetime(year, month, day)  # This will raise ValueError if invalid

        # Check reasonable range (e.g., 16-80 years old)
        current_year = datetime.now().year
        if year < current_year - 80 or year > current_year - 16:
            return False

        return True
    except (ValueError, TypeError):
        return False


def validate_date_of_birth_with_error(dob: str) -> tuple[bool, str | None]:
    """
    Validate date of birth format and return error message if invalid.
    
    Args:
        dob: Date of birth string in DD/MM/YYYY format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dob or not dob.strip():
        return False, "Date of birth cannot be empty"

    if not validate_date_of_birth(dob):
        return False, "Invalid date of birth format. Use DD/MM/YYYY format and ensure age is between 16-80 years"

    return True, None


def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        format: Expected date format (default: "%Y-%m-%d")
        
    Returns:
        True if the date format is valid, False otherwise
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_time_format(time_str: str, format: str = "%H:%M") -> bool:
    """
    Validate time string format.
    
    Args:
        time_str: Time string to validate
        format: Expected time format (default: "%H:%M")
        
    Returns:
        True if the time format is valid, False otherwise
    """
    try:
        datetime.strptime(time_str, format)
        return True
    except ValueError:
        return False


# ============================================================================
# EMERGENCY CONTACT VALIDATION
# ============================================================================

def validate_emergency_contact(contact: str) -> bool:
    """
    Validate emergency contact format.
    Expected format: "Name, Phone"
    
    Args:
        contact: Emergency contact string
        
    Returns:
        True if the emergency contact format is valid, False otherwise
    """
    if not contact or not contact.strip():
        return False

    # Expected format: "Name, Phone"
    parts = contact.split(',')
    if len(parts) != 2:
        return False

    name, phone = parts[0].strip(), parts[1].strip()
    if not name or not phone:
        return False

    # Validate phone number
    return validate_phone(phone)


def validate_emergency_contact_with_error(contact: str) -> tuple[bool, str | None]:
    """
    Validate emergency contact format and return error message if invalid.
    
    Args:
        contact: Emergency contact string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not contact or not contact.strip():
        return False, "Emergency contact cannot be empty"

    # Expected format: "Name, Phone"
    parts = contact.split(',')
    if len(parts) != 2:
        return False, "Emergency contact must be in format: 'Name, Phone'"

    name, phone = parts[0].strip(), parts[1].strip()
    if not name:
        return False, "Emergency contact name cannot be empty"

    if not phone:
        return False, "Emergency contact phone cannot be empty"

    # Validate phone number
    is_valid, error_msg = validate_phone_with_error(phone)
    if not is_valid:
        return False, f"Emergency contact phone: {error_msg}"

    return True, None


# ============================================================================
# ID VALIDATION
# ============================================================================

def validate_id_format(id_str: str, prefix: str = "", min_length: int = 3) -> bool:
    """
    Validate ID format.
    
    Args:
        id_str: ID string to validate
        prefix: Expected prefix (optional)
        min_length: Minimum length required (default: 3)
        
    Returns:
        True if the ID format is valid, False otherwise
    """
    if not id_str or not id_str.strip():
        return False

    if prefix and not id_str.startswith(prefix):
        return False

    return len(id_str.strip()) >= min_length


def validate_id_format_with_error(id_str: str, prefix: str = "", min_length: int = 3) -> tuple[bool, str | None]:
    """
    Validate ID format and return error message if invalid.
    
    Args:
        id_str: ID string to validate
        prefix: Expected prefix (optional)
        min_length: Minimum length required (default: 3)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not id_str or not id_str.strip():
        return False, "ID cannot be empty"

    if prefix and not id_str.startswith(prefix):
        return False, f"ID must start with '{prefix}'"

    if len(id_str.strip()) < min_length:
        return False, f"ID must be at least {min_length} characters long"

    return True, None


# ============================================================================
# TEAM ID VALIDATION
# ============================================================================

def validate_team_id(team_id: str) -> bool:
    """
    Validate team ID format.
    
    Args:
        team_id: Team ID to validate
        
    Returns:
        True if the team ID is valid, False otherwise
    """
    return validate_id_format(team_id, min_length=1)


def validate_team_id_with_error(team_id: str) -> tuple[bool, str | None]:
    """
    Validate team ID format and return error message if invalid.
    
    Args:
        team_id: Team ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not team_id or not team_id.strip():
        return False, "Team ID cannot be empty"

    return True, None


# ============================================================================
# PLAYER DATA VALIDATION
# ============================================================================

def validate_player_data(name: str, phone: str, team_id: str, email: str | None = None) -> tuple[bool, list[str]]:
    """
    Validate complete player data.
    
    Args:
        name: Player name
        phone: Player phone number
        email: Player email (optional)
        team_id: Team ID
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Validate name
    is_valid, error_msg = validate_name_with_error(name)
    if not is_valid:
        errors.append(f"Name: {error_msg}")

    # Validate phone
    is_valid, error_msg = validate_phone_with_error(phone)
    if not is_valid:
        errors.append(f"Phone: {error_msg}")

    # Validate email (if provided)
    if email:
        is_valid, error_msg = validate_email_with_error(email)
        if not is_valid:
            errors.append(f"Email: {error_msg}")

    # Validate team ID
    is_valid, error_msg = validate_team_id_with_error(team_id)
    if not is_valid:
        errors.append(f"Team ID: {error_msg}")

    return len(errors) == 0, errors


# ============================================================================
# TEAM DATA VALIDATION
# ============================================================================

def validate_team_data(name: str, description: str | None = None) -> tuple[bool, list[str]]:
    """
    Validate complete team data.
    
    Args:
        name: Team name
        description: Team description (optional)
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Validate team name
    is_valid, error_msg = validate_team_name_with_error(name)
    if not is_valid:
        errors.append(f"Team name: {error_msg}")

    # Validate description (if provided)
    if description and len(description.strip()) > 500:
        errors.append("Team description cannot exceed 500 characters")

    return len(errors) == 0, errors


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def sanitize_string(value: str) -> str:
    """
    Sanitize a string by removing leading/trailing whitespace.
    
    Args:
        value: String to sanitize
        
    Returns:
        Sanitized string
    """
    return value.strip() if value else ""


def validate_required_field(value: str, field_name: str) -> tuple[bool, str | None]:
    """
    Validate that a required field is not empty.
    
    Args:
        value: Field value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty"

    return True, None


def validate_field_length(value: str, field_name: str, min_length: int = 1, max_length: int = 1000) -> tuple[bool, str | None]:
    """
    Validate field length constraints.
    
    Args:
        value: Field value to validate
        field_name: Name of the field for error messages
        min_length: Minimum length required
        max_length: Maximum length allowed
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value:
        return True, None  # Empty values are handled by required field validation

    length = len(value.strip())
    if length < min_length:
        return False, f"{field_name} must be at least {min_length} characters long"

    if length > max_length:
        return False, f"{field_name} cannot exceed {max_length} characters"

    return True, None


def validate_payment_details(payment_data: dict[str, Any]) -> None:
    """
    Validate payment details dict. Raises ValueError if invalid.
    Required fields: payer_id, payee_id, amount, currency, payment_date
    """
    required_fields = ["payer_id", "payee_id", "amount", "currency", "payment_date"]
    for field in required_fields:
        if field not in payment_data:
            raise ValueError(f"Missing required payment field: {field}")

    if not isinstance(payment_data["payer_id"], str) or not payment_data["payer_id"].strip():
        raise ValueError("payer_id must be a non-empty string")
    if not isinstance(payment_data["payee_id"], str) or not payment_data["payee_id"].strip():
        raise ValueError("payee_id must be a non-empty string")
    try:
        amount = Decimal(str(payment_data["amount"]))
        if amount <= 0:
            raise ValueError
    except Exception:
        raise ValueError("amount must be a positive decimal number")
    if not isinstance(payment_data["currency"], str) or not payment_data["currency"].strip():
        raise ValueError("currency must be a non-empty string")
    try:
        datetime.fromisoformat(payment_data["payment_date"])
    except Exception:
        raise ValueError("payment_date must be a valid ISO format datetime string")
