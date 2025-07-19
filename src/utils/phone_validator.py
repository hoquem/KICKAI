"""
Phone Number Validation and Formatting Utilities

This module provides utilities for validating and formatting phone numbers
using Google's libphonenumber library to E.164 international format.
"""

import re
import logging
from typing import Optional, Tuple
from phonenumbers import parse, is_valid_number, NumberParseException, format_number, PhoneNumberFormat, PhoneNumberType, number_type

logger = logging.getLogger(__name__)


class PhoneValidator:
    """Phone number validation and formatting utilities using Google's libphonenumber."""
    
    @staticmethod
    def validate_and_format_phone(phone_input: str, default_region: str = "GB") -> Tuple[bool, Optional[str], str]:
        """
        Validate and format a phone number to E.164 format using Google's libphonenumber.
        
        Args:
            phone_input: Raw phone number input from user
            default_region: Default region code (e.g., "GB", "US") for parsing
            
        Returns:
            Tuple of (is_valid, formatted_number, error_message)
        """
        try:
            # Clean the input
            cleaned_input = re.sub(r'[^\d+\-\(\)\s]', '', phone_input.strip())
            
            # Parse the phone number
            phone_number = parse(cleaned_input, default_region)
            
            # Validate the number
            if not is_valid_number(phone_number):
                return False, None, "Invalid phone number format"
            
            # Check if it's a mobile number (optional validation)
            number_type_result = number_type(phone_number)
            if number_type_result not in [PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE, PhoneNumberType.FIXED_LINE_OR_MOBILE]:
                logger.warning(f"Phone number type: {number_type_result} - may not be a mobile number")
            
            # Format to E.164
            formatted_number = format_number(phone_number, PhoneNumberFormat.E164)
            
            return True, formatted_number, ""
            
        except NumberParseException as e:
            return False, None, f"Could not parse phone number: {str(e)}"
        except Exception as e:
            logger.error(f"Error validating phone number: {e}")
            return False, None, "Phone number validation failed"
    
    @staticmethod
    def is_valid_phone_format(phone_input: str, default_region: str = "GB") -> bool:
        """
        Quick validation check for phone number format.
        
        Args:
            phone_input: Raw phone number input
            default_region: Default region code
            
        Returns:
            True if valid format, False otherwise
        """
        try:
            phone_number = parse(phone_input, default_region)
            return is_valid_number(phone_number)
        except:
            return False
    
    @staticmethod
    def format_to_e164(phone_input: str, default_region: str = "GB") -> Optional[str]:
        """
        Format phone number to E.164 without validation.
        
        Args:
            phone_input: Raw phone number input
            default_region: Default region code
            
        Returns:
            E.164 formatted number or None if parsing fails
        """
        try:
            phone_number = parse(phone_input, default_region)
            return format_number(phone_number, PhoneNumberFormat.E164)
        except:
            return None
    
    @staticmethod
    def is_valid_uk_mobile(phone_input: str) -> bool:
        """Check if the phone number is a valid UK mobile number."""
        try:
            cleaned = PhoneValidator._clean_phone_input(phone_input)
            phone_number = parse(cleaned, "GB")
            
            if not is_valid_number(phone_number):
                return False
            
            # Check if it's a mobile number (starts with 7)
            national_number = str(phone_number.national_number)
            return national_number.startswith('7') and len(national_number) == 10
            
        except Exception:
            return False
    
    @staticmethod
    def format_for_display(phone_input: str) -> str:
        """Format phone number for display purposes."""
        try:
            cleaned = PhoneValidator._clean_phone_input(phone_input)
            phone_number = parse(cleaned, None)
            
            if is_valid_number(phone_number):
                return format_number(phone_number, PhoneNumberFormat.INTERNATIONAL)
            else:
                return phone_input
                
        except Exception:
            return phone_input


class NameValidator:
    """Name validation utilities."""
    
    @staticmethod
    def validate_name(name_input: str) -> Tuple[bool, str]:
        """
        Validate a person's name.
        
        Args:
            name_input: Raw name input from user
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name_input:
            return False, "Name cannot be empty"
        
        name = name_input.strip()
        
        # Check minimum length
        if len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        # Check maximum length
        if len(name) > 100:
            return False, "Name is too long (maximum 100 characters)"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Check for consecutive spaces
        if re.search(r'\s{2,}', name):
            return False, "Name cannot contain consecutive spaces"
        
        # Check for proper capitalization
        words = name.split()
        for word in words:
            if not word[0].isupper():
                return False, "Each word in the name should start with a capital letter"
        
        return True, ""
    
    @staticmethod
    def format_name(name_input: str) -> str:
        """Format name with proper capitalization."""
        if not name_input:
            return ""
        
        # Clean and capitalize
        words = name_input.strip().split()
        formatted_words = []
        
        for word in words:
            if word:
                # Handle special cases like "Mc", "Mac", "O'", etc.
                if word.lower().startswith(('mc', 'mac', "o'")):
                    formatted_word = word[0].upper() + word[1:2].lower() + word[2:].title()
                else:
                    formatted_word = word.title()
                formatted_words.append(formatted_word)
        
        return ' '.join(formatted_words) 