#!/usr/bin/env python3
"""
Phone number validation utilities.

Provides secure and robust phone number validation for the KICKAI system.
Uses Google's phonenumbers library for international phone number validation.
"""

from typing import Optional
from loguru import logger
import phonenumbers

from kickai.agents.config.message_router_config import (
    PHONE_NUMBER_MAX_LENGTH,
    PHONE_NUMBER_MIN_LENGTH,
    PHONE_NUMBER_MAX_DIGITS,
    PHONE_NUMBER_MIN_DIGITS,
    PHONE_ALLOWED_CHARS,
    WARNING_MESSAGES,
)


class PhoneValidator:
    """
    Secure phone number validation with security considerations.
    
    Uses Google's phonenumbers library for robust international phone number
    validation and formatting. Validates phone numbers against international
    standards and prevents common attack vectors like DoS through oversized inputs.
    """

    @staticmethod
    def looks_like_phone_number(text: str) -> bool:
        """
        Check if text looks like a valid phone number with security considerations.

        Args:
            text: Input text to check

        Returns:
            True if text looks like a valid phone number, False otherwise
        """
        try:
            # ALL business logic here
            if not text or not isinstance(text, str):
                return False

            # Security: Limit input length to prevent DoS attacks
            if (
                len(text.strip()) > PHONE_NUMBER_MAX_LENGTH
                or len(text.strip()) < PHONE_NUMBER_MIN_LENGTH
            ):
                return False

            # Security: Only allow known safe characters
            if not all(c in PHONE_ALLOWED_CHARS for c in text):
                logger.warning(WARNING_MESSAGES["PHONE_VALIDATION_ERROR"])
                return False

            # Use Google phonenumbers library for validation
            try:
                # Try parsing with US as default country
                phone_number = phonenumbers.parse(text, "US")
                
                # Check if it's a possible number (less strict validation)
                if not phonenumbers.is_possible_number(phone_number):
                    return False
                
                # For validation, we'll be more lenient and accept possible numbers
                # rather than requiring them to be strictly valid
                return True
                
            except phonenumbers.NumberParseException:
                # Try parsing without country code
                try:
                    phone_number = phonenumbers.parse(text, None)
                    return phonenumbers.is_possible_number(phone_number)
                except phonenumbers.NumberParseException:
                    return False
            
        except Exception as e:
            logger.error(f"❌ Error in looks_like_phone_number: {e}")
            return False

    @staticmethod
    def normalize_phone_number(phone: str) -> Optional[str]:
        """
        Normalize phone number to E.164 international format.
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Normalized phone number in E.164 format (+1234567890) or None if invalid
        """
        try:
            # ALL business logic here
            if not PhoneValidator.looks_like_phone_number(phone):
                return None
                
            # Parse the phone number
            try:
                # Try parsing with US as default country
                phone_number = phonenumbers.parse(phone, "US")
            except phonenumbers.NumberParseException:
                # Try parsing without country code
                try:
                    phone_number = phonenumbers.parse(phone, None)
                except phonenumbers.NumberParseException:
                    return None
            
            # Check if it's possible (less strict than valid)
            if not phonenumbers.is_possible_number(phone_number):
                return None
                
            # Format to E.164 international format
            normalized = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            
            return normalized
            
        except Exception as e:
            logger.error(f"❌ Error in normalize_phone_number: {e}")
            return None

    @staticmethod
    def validate_phone_for_linking(phone: str) -> tuple[bool, Optional[str]]:
        """
        Validate phone number specifically for user linking operations.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, normalized_phone_or_error_message)
        """
        try:
            # ALL business logic here
            if not PhoneValidator.looks_like_phone_number(phone):
                return False, "Invalid phone number format"
                
            normalized = PhoneValidator.normalize_phone_number(phone)
            if not normalized:
                return False, "Could not normalize phone number"
                
            return True, normalized
            
        except Exception as e:
            logger.error(f"❌ Error in validate_phone_for_linking: {e}")
            return False, "Phone validation failed"

    @staticmethod
    def get_phone_info(phone: str) -> Optional[dict]:
        """
        Get detailed information about a phone number.
        
        Args:
            phone: Phone number to analyze
            
        Returns:
            Dictionary with phone number information or None if invalid
        """
        try:
            # ALL business logic here
            if not PhoneValidator.looks_like_phone_number(phone):
                return None
                
            # Parse the phone number
            try:
                phone_number = phonenumbers.parse(phone, "US")
            except phonenumbers.NumberParseException:
                try:
                    phone_number = phonenumbers.parse(phone, None)
                except phonenumbers.NumberParseException:
                    return None
            
            # Get country information
            country_code = phonenumbers.region_code_for_number(phone_number)
            
            # Get number type
            number_type = phonenumbers.number_type(phone_number)
            type_names = {
                phonenumbers.PhoneNumberType.MOBILE: "mobile",
                phonenumbers.PhoneNumberType.FIXED_LINE: "fixed-line",
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed-line-or-mobile",
                phonenumbers.PhoneNumberType.TOLL_FREE: "toll-free",
                phonenumbers.PhoneNumberType.PREMIUM_RATE: "premium-rate",
                phonenumbers.PhoneNumberType.SHARED_COST: "shared-cost",
                phonenumbers.PhoneNumberType.VOIP: "voip",
                phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "personal-number",
                phonenumbers.PhoneNumberType.PAGER: "pager",
                phonenumbers.PhoneNumberType.UAN: "uan",
                phonenumbers.PhoneNumberType.UNKNOWN: "unknown",
            }
            
            # Format in different formats
            national_format = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL)
            international_format = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            e164_format = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            
            return {
                "is_valid": phonenumbers.is_valid_number(phone_number),
                "is_possible": phonenumbers.is_possible_number(phone_number),
                "country_code": country_code,
                "country_name": country_code,  # Same as country_code for now
                "number_type": type_names.get(number_type, "unknown"),
                "national_format": national_format,
                "international_format": international_format,
                "e164_format": e164_format,
                "national_number": str(phone_number.national_number),
                "country_calling_code": phone_number.country_code,
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_phone_info: {e}")
            return None

    @staticmethod
    def is_mobile_number(phone: str) -> bool:
        """
        Check if the phone number is a mobile number.
        
        Args:
            phone: Phone number to check
            
        Returns:
            True if it's a mobile number, False otherwise
        """
        try:
            # ALL business logic here
            if not PhoneValidator.looks_like_phone_number(phone):
                return False
                
            # Parse the phone number
            try:
                phone_number = phonenumbers.parse(phone, "US")
            except phonenumbers.NumberParseException:
                try:
                    phone_number = phonenumbers.parse(phone, None)
                except phonenumbers.NumberParseException:
                    return False
            
            # Check if it's a mobile number
            number_type = phonenumbers.number_type(phone_number)
            return number_type == phonenumbers.PhoneNumberType.MOBILE
            
        except Exception as e:
            logger.error(f"❌ Error in is_mobile_number: {e}")
            return False

    @staticmethod
    def format_for_display(phone: str, format_type: str = "national") -> Optional[str]:
        """
        Format phone number for display purposes.
        
        Args:
            phone: Phone number to format
            format_type: Format type ("national", "international", "e164")
            
        Returns:
            Formatted phone number or None if invalid
        """
        try:
            # ALL business logic here
            if not PhoneValidator.looks_like_phone_number(phone):
                return None
                
            # Parse the phone number
            try:
                phone_number = phonenumbers.parse(phone, "US")
            except phonenumbers.NumberParseException:
                try:
                    phone_number = phonenumbers.parse(phone, None)
                except phonenumbers.NumberParseException:
                    return None
            
            # Format based on requested type
            format_map = {
                "national": phonenumbers.PhoneNumberFormat.NATIONAL,
                "international": phonenumbers.PhoneNumberFormat.INTERNATIONAL,
                "e164": phonenumbers.PhoneNumberFormat.E164,
            }
            
            phone_format = format_map.get(format_type.lower(), phonenumbers.PhoneNumberFormat.NATIONAL)
            return phonenumbers.format_number(phone_number, phone_format)
            
        except Exception as e:
            logger.error(f"❌ Error in format_for_display: {e}")
            return None
