#!/usr/bin/env python3
"""
Phone Number Utilities

This module provides simple phone number utilities using the phonenumbers library
(Google's libphonenumber port) directly without custom validation logic.
"""

import phonenumbers
from phonenumbers import PhoneNumberFormat, NumberParseException
from loguru import logger


def normalize_phone(phone: str, region: str = "GB") -> str | None:
    """
    Normalize a phone number to E.164 format using phonenumbers library.

    :param phone: Phone number in any format (e.g., "07871521581", "+447871521581")
    :type phone: str
    :param region: Country code for parsing local numbers (default: "GB")
    :type region: str
    :return: Normalized phone number in E.164 format (e.g., "+447871521581") or None if invalid
    :rtype: str | None
    """
    if not phone or not phone.strip():
        return None

    try:
        # Parse the phone number
        number = phonenumbers.parse(phone.strip(), region)

        # Check if it's a valid number
        if not phonenumbers.is_valid_number(number):
            logger.warning(f"Invalid phone number: {phone}")
            return None

        # Format to E.164 (international format with +)
        normalized = phonenumbers.format_number(number, PhoneNumberFormat.E164)

        logger.debug(f"Normalized phone {phone} -> {normalized}")
        return normalized

    except NumberParseException as e:
        logger.warning(f"Could not parse phone number {phone}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error normalizing phone number {phone}: {e}")
        return None


def get_phone_variants(phone: str, region: str = "GB") -> list[str]:
    """
    Get all possible variants of a phone number for matching using phonenumbers library.

    :param phone: Phone number in any format
    :type phone: str
    :param region: Country code for parsing local numbers (default: "GB")
    :type region: str
    :return: List of phone number variants including the normalized version
    :rtype: list[str]
    """
    variants = set()

    # Add the original phone number (cleaned)
    if phone:
        variants.add(phone.strip())

    # Add the normalized version
    normalized = normalize_phone(phone, region)
    if normalized:
        variants.add(normalized)

    # For UK numbers, also add common local formats
    if region == "GB" and normalized and normalized.startswith("+44"):
        # Remove +44 and add 0 prefix
        local_format = "0" + normalized[3:]
        variants.add(local_format)

        # Also add without leading 0 (some systems might store this way)
        no_zero = normalized[3:]
        variants.add(no_zero)

    return list(variants)


def is_valid_phone(phone: str, region: str = "GB") -> bool:
    """
    Check if a phone number is valid using phonenumbers library.

    :param phone: Phone number to validate
    :type phone: str
    :param region: Country code for parsing local numbers (default: "GB")
    :type region: str
    :return: True if the phone number is valid, False otherwise
    :rtype: bool
    """
    return normalize_phone(phone, region) is not None


def format_phone_display(phone: str, region: str = "GB") -> str | None:
    """
    Format a phone number for display (national format) using phonenumbers library.

    :param phone: Phone number to format
    :type phone: str
    :param region: Country code for parsing local numbers (default: "GB")
    :type region: str
    :return: Formatted phone number for display or None if invalid
    :rtype: str | None
    """
    if not phone or not phone.strip():
        return None

    try:
        number = phonenumbers.parse(phone.strip(), region)

        if not phonenumbers.is_valid_number(number):
            return None

        # Format to national format (e.g., "07871 521 581" for UK)
        return phonenumbers.format_number(number, PhoneNumberFormat.NATIONAL)

    except NumberParseException:
        return None
    except Exception as e:
        logger.error(f"Error formatting phone number {phone}: {e}")
        return None


def get_phone_info(phone: str, region: str = "GB") -> dict | None:
    """
    Get detailed information about a phone number using phonenumbers library.

    :param phone: Phone number to analyze
    :type phone: str
    :param region: Country code for parsing local numbers (default: "GB")
    :type region: str
    :return: Dictionary with phone number information or None if invalid
    :rtype: dict | None
    """
    if not phone or not phone.strip():
        return None

    try:
        number = phonenumbers.parse(phone.strip(), region)

        if not phonenumbers.is_valid_number(number):
            return None

        return {
            "e164": phonenumbers.format_number(number, PhoneNumberFormat.E164),
            "national": phonenumbers.format_number(number, PhoneNumberFormat.NATIONAL),
            "international": phonenumbers.format_number(
                number, PhoneNumberFormat.INTERNATIONAL
            ),
            "country_code": number.country_code,
            "national_number": number.national_number,
            "is_valid": phonenumbers.is_valid_number(number),
            "is_possible": phonenumbers.is_possible_number(number),
            "number_type": phonenumbers.number_type(number),
        }

    except NumberParseException:
        return None
    except Exception as e:
        logger.error(f"Error getting phone info for {phone}: {e}")
        return None
