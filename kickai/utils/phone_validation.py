#!/usr/bin/env python3
"""
Phone Number Validation Utilities

This module provides comprehensive phone number validation and normalization
using the phonenumbers library for robust international phone number handling.
"""

import re
from dataclasses import dataclass
from typing import Any

try:
    import phonenumbers
    from phonenumbers import NumberParseException, PhoneNumberFormat, PhoneNumberType

    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    # Fallback for environments without phonenumbers library
    NumberParseException = Exception
    PhoneNumberType = None
    PhoneNumberFormat = None

from loguru import logger


@dataclass
class PhoneValidationResult:
    """Result of phone number validation."""

    is_valid: bool
    normalized_number: str
    country_code: str
    national_number: str
    number_type: str | None = None
    error_message: str | None = None
    is_mobile: bool = False
    is_fixed_line: bool = False


class PhoneValidator:
    """
    Comprehensive phone number validator using phonenumbers library.

    Provides robust international phone number validation, normalization,
    and type detection.
    """

    def __init__(self, default_region: str = "GB"):
        """
        Initialize the phone validator.

        Args:
            default_region: Default region code for parsing numbers without country code
        """
        self.default_region = default_region.upper()

        if not PHONENUMBERS_AVAILABLE:
            logger.warning("⚠️ phonenumbers library not available, using fallback validation")

    def validate_phone_number(self, phone: str, region: str | None = None) -> PhoneValidationResult:
        """
        Validate and normalize a phone number.

        Args:
            phone: Phone number to validate
            region: Region code for parsing (defaults to self.default_region)

        Returns:
            PhoneValidationResult with validation details
        """
        if not phone or not phone.strip():
            return PhoneValidationResult(
                is_valid=False,
                normalized_number="",
                country_code="",
                national_number="",
                error_message="Phone number cannot be empty",
            )

        # Clean the input
        cleaned_phone = self._clean_phone_number(phone)

        if not PHONENUMBERS_AVAILABLE:
            return self._fallback_validation(cleaned_phone)

        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(cleaned_phone, region or self.default_region)

            # Check if the number is valid
            if not phonenumbers.is_valid_number(parsed_number):
                return PhoneValidationResult(
                    is_valid=False,
                    normalized_number="",
                    country_code="",
                    national_number="",
                    error_message="Invalid phone number format",
                )

            # Get number type
            number_type = phonenumbers.number_type(parsed_number)
            is_mobile = number_type == PhoneNumberType.MOBILE
            is_fixed_line = number_type == PhoneNumberType.FIXED_LINE

            # Format the number in international format
            normalized_number = phonenumbers.format_number(
                parsed_number, PhoneNumberFormat.INTERNATIONAL
            )

            # Extract components
            country_code = f"+{parsed_number.country_code}"
            national_number = str(parsed_number.national_number)

            # Get number type description
            type_description = self._get_number_type_description(number_type)

            return PhoneValidationResult(
                is_valid=True,
                normalized_number=normalized_number,
                country_code=country_code,
                national_number=national_number,
                number_type=type_description,
                is_mobile=is_mobile,
                is_fixed_line=is_fixed_line,
            )

        except NumberParseException as e:
            return PhoneValidationResult(
                is_valid=False,
                normalized_number="",
                country_code="",
                national_number="",
                error_message=f"Invalid phone number format: {e!s}",
            )
        except Exception as e:
            logger.error(f"Error validating phone number '{phone}': {e}")
            return PhoneValidationResult(
                is_valid=False,
                normalized_number="",
                country_code="",
                national_number="",
                error_message=f"Validation error: {e!s}",
            )

    def normalize_phone_number(self, phone: str, region: str | None = None) -> str:
        """
        Normalize a phone number to international format.

        Args:
            phone: Phone number to normalize
            region: Region code for parsing

        Returns:
            Normalized phone number in international format
        """
        result = self.validate_phone_number(phone, region)
        return result.normalized_number if result.is_valid else ""

    def get_phone_variants(self, phone: str, region: str | None = None) -> list[str]:
        """
        Get possible variants of a phone number for flexible matching.

        Args:
            phone: Phone number to generate variants for
            region: Region code for parsing

        Returns:
            List of phone number variants
        """
        variants = []

        if not PHONENUMBERS_AVAILABLE:
            # Fallback: basic variants
            cleaned = self._clean_phone_number(phone)
            variants.append(cleaned)

            # Add with/without + prefix
            if cleaned.startswith("+"):
                variants.append(cleaned[1:])
            else:
                variants.append(f"+{cleaned}")

            return variants

        try:
            parsed_number = phonenumbers.parse(phone, region or self.default_region)

            if phonenumbers.is_valid_number(parsed_number):
                # International format
                variants.append(
                    phonenumbers.format_number(parsed_number, PhoneNumberFormat.INTERNATIONAL)
                )

                # E164 format (no spaces)
                variants.append(phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164))

                # National format with country code
                variants.append(
                    phonenumbers.format_number(parsed_number, PhoneNumberFormat.NATIONAL)
                )

                # Just the number without formatting
                variants.append(f"+{parsed_number.country_code}{parsed_number.national_number}")

        except NumberParseException:
            # Fallback to basic variants
            cleaned = self._clean_phone_number(phone)
            variants.append(cleaned)
            if cleaned.startswith("+"):
                variants.append(cleaned[1:])
            else:
                variants.append(f"+{cleaned}")

        return list(set(variants))  # Remove duplicates

    def is_mobile_number(self, phone: str, region: str | None = None) -> bool:
        """
        Check if a phone number is a mobile number.

        Args:
            phone: Phone number to check
            region: Region code for parsing

        Returns:
            True if the number is a mobile number
        """
        result = self.validate_phone_number(phone, region)
        return result.is_mobile

    def get_country_info(self, phone: str, region: str | None = None) -> dict[str, Any]:
        """
        Get information about the country of a phone number.

        Args:
            phone: Phone number to analyze
            region: Region code for parsing

        Returns:
            Dictionary with country information
        """
        if not PHONENUMBERS_AVAILABLE:
            return {"country_code": "", "country_name": "Unknown"}

        try:
            parsed_number = phonenumbers.parse(phone, region or self.default_region)

            if phonenumbers.is_valid_number(parsed_number):
                from phonenumbers import region_code_for_number

                country_code = region_code_for_number(parsed_number)

                return {
                    "country_code": country_code,
                    "country_name": self._get_country_name(country_code),
                    "international_prefix": f"+{parsed_number.country_code}",
                }
        except Exception as e:
            logger.error(f"Error getting country info for '{phone}': {e}")

        return {"country_code": "", "country_name": "Unknown"}

    def _clean_phone_number(self, phone: str) -> str:
        """Clean and prepare phone number for parsing."""
        if not phone:
            return ""

        # Remove common separators but keep + for country code
        cleaned = re.sub(r"[^\d+]", "", phone.strip())

        from kickai.core.constants import LimitConstants, ValidationConstants

        # Handle common UK number patterns
        if cleaned.startswith("0") and len(cleaned) >= LimitConstants.MIN_PHONE_DIGITS:
            # Convert UK local format to international
            cleaned = ValidationConstants.UK_COUNTRY_CODE + cleaned[1:]

        return cleaned

    def _fallback_validation(self, phone: str) -> PhoneValidationResult:
        """
        Fallback validation when phonenumbers library is not available.

        Args:
            phone: Phone number to validate

        Returns:
            PhoneValidationResult with basic validation
        """
        if not phone:
            return PhoneValidationResult(
                is_valid=False,
                normalized_number="",
                country_code="",
                national_number="",
                error_message="Phone number cannot be empty",
            )

        from kickai.core.constants import LimitConstants, ValidationConstants

        # Basic validation: must have at least minimum required digits
        digits_only = re.sub(r"[^\d]", "", phone)

        if len(digits_only) < LimitConstants.MIN_PHONE_DIGITS:
            return PhoneValidationResult(
                is_valid=False,
                normalized_number="",
                country_code="",
                national_number="",
                error_message=ValidationConstants.PHONE_TOO_SHORT_MSG.format(min=LimitConstants.MIN_PHONE_DIGITS),
            )

        # Basic normalization
        if phone.startswith("+"):
            normalized = phone
            country_code = phone[:3] if phone.startswith(ValidationConstants.UK_COUNTRY_CODE) else phone[:4]
        else:
            # Assume UK number
            normalized = f"{ValidationConstants.UK_COUNTRY_CODE}{phone.lstrip('0')}"
            country_code = ValidationConstants.UK_COUNTRY_CODE

        return PhoneValidationResult(
            is_valid=True,
            normalized_number=normalized,
            country_code=country_code,
            national_number=digits_only,
            number_type="Unknown (fallback validation)",
        )

    def _get_number_type_description(self, number_type: int) -> str:
        """Get human-readable description of phone number type."""
        if not PHONENUMBERS_AVAILABLE:
            return "Unknown"

        type_map = {
            PhoneNumberType.MOBILE: "Mobile",
            PhoneNumberType.FIXED_LINE: "Fixed Line",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            PhoneNumberType.TOLL_FREE: "Toll Free",
            PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            PhoneNumberType.SHARED_COST: "Shared Cost",
            PhoneNumberType.VOIP: "VoIP",
            PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            PhoneNumberType.PAGER: "Pager",
            PhoneNumberType.UAN: "UAN",
            PhoneNumberType.UNKNOWN: "Unknown",
        }

        return type_map.get(number_type, "Unknown")

    def _get_country_name(self, country_code: str) -> str:
        """Get country name from country code."""
        if not country_code:
            return "Unknown"

        # Basic country code mapping (can be expanded)
        country_names = {
            "GB": "United Kingdom",
            "US": "United States",
            "CA": "Canada",
            "AU": "Australia",
            "DE": "Germany",
            "FR": "France",
            "IT": "Italy",
            "ES": "Spain",
            "NL": "Netherlands",
            "BE": "Belgium",
            "IE": "Ireland",
            "NZ": "New Zealand",
            "IN": "India",
            "CN": "China",
            "JP": "Japan",
            "KR": "South Korea",
            "BR": "Brazil",
            "MX": "Mexico",
            "AR": "Argentina",
            "ZA": "South Africa",
        }

        return country_names.get(country_code.upper(), f"Country {country_code}")


# Global validator instance
_phone_validator = None


def get_phone_validator() -> PhoneValidator:
    """Get the global phone validator instance."""
    global _phone_validator
    if _phone_validator is None:
        _phone_validator = PhoneValidator()
    return _phone_validator


def validate_phone_number(phone: str, region: str | None = None) -> PhoneValidationResult:
    """
    Validate a phone number using the global validator.

    Args:
        phone: Phone number to validate
        region: Region code for parsing

    Returns:
        PhoneValidationResult with validation details
    """
    validator = get_phone_validator()
    return validator.validate_phone_number(phone, region)


def normalize_phone_number(phone: str, region: str | None = None) -> str:
    """
    Normalize a phone number using the global validator.

    Args:
        phone: Phone number to normalize
        region: Region code for parsing

    Returns:
        Normalized phone number in international format
    """
    validator = get_phone_validator()
    return validator.normalize_phone_number(phone, region)


def get_phone_variants(phone: str, region: str | None = None) -> list[str]:
    """
    Get phone number variants using the global validator.

    Args:
        phone: Phone number to generate variants for
        region: Region code for parsing

    Returns:
        List of phone number variants
    """
    validator = get_phone_validator()
    return validator.get_phone_variants(phone, region)


def is_mobile_number(phone: str, region: str | None = None) -> bool:
    """
    Check if a phone number is a mobile number.

    Args:
        phone: Phone number to check
        region: Region code for parsing

    Returns:
        True if the number is a mobile number
    """
    validator = get_phone_validator()
    return validator.is_mobile_number(phone, region)
