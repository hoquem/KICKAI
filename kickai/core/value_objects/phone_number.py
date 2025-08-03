"""
Phone number value object with validation and formatting using libphonenumber.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import phonenumbers
from phonenumbers import PhoneNumberFormat

from kickai.core.exceptions import ValidationError


@dataclass(frozen=True)
class PhoneNumber:
    """Represents a validated phone number using Google's libphonenumber."""
    
    value: str  # Always stored in E.164 format
    
    @classmethod
    def from_string(cls, phone_str: str, region: str = "GB") -> PhoneNumber:
        """
        Create PhoneNumber from string with validation.
        
        Args:
            phone_str: Phone number string in any format
            region: Default region for parsing (ISO 3166-1 alpha-2)
            
        Returns:
            Validated PhoneNumber instance
            
        Raises:
            ValidationError: If phone number is invalid
        """
        if not phone_str or not phone_str.strip():
            raise ValidationError("Phone number cannot be empty")
        
        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone_str.strip(), region)
            
            # Validate the parsed number
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError(f"Invalid phone number: {phone_str}")
            
            # Format to E.164 standard
            e164_format = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
            
            # Use object.__new__ to bypass __post_init__ validation
            instance = object.__new__(cls)
            object.__setattr__(instance, 'value', e164_format)
            return instance
            
        except phonenumbers.NumberParseException as e:
            raise ValidationError(f"Cannot parse phone number '{phone_str}': {e}")
    
    @classmethod  
    def try_parse(cls, phone_str: str, region: str = "GB") -> Optional[PhoneNumber]:
        """
        Try to parse phone number, return None if invalid.
        
        Args:
            phone_str: Phone number string
            region: Default region for parsing
            
        Returns:
            PhoneNumber instance or None if parsing fails
        """
        try:
            return cls.from_string(phone_str, region)
        except ValidationError:
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
        """Return user-friendly display format."""
        return self.formatted
    
    @property
    def region_code(self) -> Optional[str]:
        """Get the region code for this number."""
        try:
            parsed = phonenumbers.parse(self.value, None)
            return phonenumbers.region_code_for_number(parsed)
        except phonenumbers.NumberParseException:
            return None
    
    @property
    def number_type(self) -> str:
        """Get the type of this phone number (mobile, fixed_line, etc.)."""
        try:
            parsed = phonenumbers.parse(self.value, None)
            number_type = phonenumbers.number_type(parsed)
            return str(number_type).split('.')[-1].lower()
        except phonenumbers.NumberParseException:
            return "unknown"
    
    def is_mobile(self) -> bool:
        """Check if this is a mobile number."""
        return self.number_type == "mobile"
    
    def is_landline(self) -> bool:
        """Check if this is a fixed line number."""
        return self.number_type == "fixed_line"
    
    def __str__(self) -> str:
        """String representation."""
        return self.formatted
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"PhoneNumber('{self.value}')"