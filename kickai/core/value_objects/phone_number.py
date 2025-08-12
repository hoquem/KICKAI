from __future__ import annotations

"""
Phone number value object with validation and formatting using libphonenumber.
"""

from dataclasses import dataclass

import phonenumbers
from phonenumbers import PhoneNumberFormat

from kickai.core.exceptions import PlayerValidationError


@dataclass(frozen=True)
class PhoneNumber:
    """Represents a validated phone number using Google's libphonenumber."""

    value: str  # Always stored in E.164 format

    @classmethod
    def from_string(cls, phone_str: str, region: str = "GB") -> PhoneNumber:
        """
        Create PhoneNumber from string with validation.


            phone_str: Phone number string in any format
            region: Default region for parsing (ISO 3166-1 alpha-2)


    :return: Validated PhoneNumber instance
    :rtype: str  # TODO: Fix type


            PlayerValidationError: If phone number is invalid
        """
        if not phone_str or not phone_str.strip():
            raise PlayerValidationError(["Phone number cannot be empty"])

        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone_str.strip(), region)

            # Validate the parsed number
            if not phonenumbers.is_valid_number(parsed_number):
                raise PlayerValidationError([f"Invalid phone number: {phone_str}"])

            # Format to E.164 standard
            e164_format = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)

            # Use object.__new__ to bypass __post_init__ validation
            instance = object.__new__(cls)
            object.__setattr__(instance, 'value', e164_format)
            return instance

        except phonenumbers.NumberParseException as e:
            raise PlayerValidationError([f"Cannot parse phone number '{phone_str}': {e}"])

    @classmethod
    def try_parse(cls, phone_str: str, region: str = "GB") -> PhoneNumber | None:
        """
        Try to parse phone number, return None if invalid.


            phone_str: Phone number string
            region: Default region for parsing


    :return: PhoneNumber instance or None if parsing fails
    :rtype: str  # TODO: Fix type
        """
        try:
            return cls.from_string(phone_str, region)
        except PlayerValidationError:
            return None

    @property
    def formatted(self) -> str:
        """Return formatted phone number for display (international format)."""
        try:
            parsed = phonenumbers.parse(self.value, None)
            return phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
        except phonenumbers.NumberParseException:
            return self.value

    @property
    def national_format(self) -> str:
        """Return national format (without country code)."""
        try:
            parsed = phonenumbers.parse(self.value, None)
            return phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL)
        except phonenumbers.NumberParseException:
            return self.value

    @property
    def international_format(self) -> str:
        """Return international format (E.164)."""
        return self.value

    @property
    def display_format(self) -> str:
        """Return formatted phone number for display."""
        return self.formatted

    @property
    def region_code(self) -> str | None:
        """Return the region code for this phone number."""
        try:
            parsed = phonenumbers.parse(self.value, None)
            return phonenumbers.region_code_for_number(parsed)
        except phonenumbers.NumberParseException:
            return None

    @property
    def number_type(self) -> str:
        """Return the type of phone number (mobile, landline, etc.)."""
        try:
            parsed = phonenumbers.parse(self.value, None)
            number_type = phonenumbers.number_type(parsed)

            type_map = {
                phonenumbers.PhoneNumberType.MOBILE: "mobile",
                phonenumbers.PhoneNumberType.FIXED_LINE: "landline",
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_or_mobile",
                phonenumbers.PhoneNumberType.TOLL_FREE: "toll_free",
                phonenumbers.PhoneNumberType.PREMIUM_RATE: "premium_rate",
                phonenumbers.PhoneNumberType.SHARED_COST: "shared_cost",
                phonenumbers.PhoneNumberType.VOIP: "voip",
                phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "personal",
                phonenumbers.PhoneNumberType.PAGER: "pager",
                phonenumbers.PhoneNumberType.UAN: "uan",
                phonenumbers.PhoneNumberType.UNKNOWN: "unknown",
                phonenumbers.PhoneNumberType.EMERGENCY: "emergency",
                phonenumbers.PhoneNumberType.VOICEMAIL: "voicemail",
                phonenumbers.PhoneNumberType.SHORT_CODE: "short_code",
                phonenumbers.PhoneNumberType.STANDARD_RATE: "standard_rate"
            }

            return type_map.get(number_type, "unknown")
        except phonenumbers.NumberParseException:
            return "unknown"

    def is_mobile(self) -> bool:
        """Check if this is a mobile number."""
        return self.number_type == "mobile"

    def is_landline(self) -> bool:
        """Check if this is a landline number."""
        return self.number_type == "landline"

    def __str__(self) -> str:
        """Return the E.164 formatted phone number."""
        return self.value

    def __repr__(self) -> str:
        """Return a string representation of the phone number."""
        return f"PhoneNumber(value='{self.value}')"
