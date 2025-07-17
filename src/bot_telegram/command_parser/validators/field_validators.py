"""
Field Validators

This module contains field validation logic for command parameters.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of field validation."""
    is_valid: bool
    error_message: str = ""
    cleaned_value: Any = None


class FieldValidator:
    """Handles field validation for command parameters."""
    
    @staticmethod
    def validate_required_field(value: Any, field_name: str) -> ValidationResult:
        """Validate that a required field is present and not empty."""
        if value is None:
            return ValidationResult(False, f"{field_name} is required")
        
        if isinstance(value, str) and not value.strip():
            return ValidationResult(False, f"{field_name} cannot be empty")
        
        return ValidationResult(True, cleaned_value=value)
    
    @staticmethod
    def validate_string_field(value: Any, field_name: str, min_length: int = 1, max_length: int = 1000) -> ValidationResult:
        """Validate a string field with length constraints."""
        if not isinstance(value, str):
            return ValidationResult(False, f"{field_name} must be a string")
        
        if len(value) < min_length:
            return ValidationResult(False, f"{field_name} must be at least {min_length} characters")
        
        if len(value) > max_length:
            return ValidationResult(False, f"{field_name} must be at most {max_length} characters")
        
        return ValidationResult(True, cleaned_value=value.strip())
    
    @staticmethod
    def validate_numeric_field(value: Any, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> ValidationResult:
        """Validate a numeric field with range constraints."""
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult(False, f"{field_name} must be a number")
        
        if min_value is not None and numeric_value < min_value:
            return ValidationResult(False, f"{field_name} must be at least {min_value}")
        
        if max_value is not None and numeric_value > max_value:
            return ValidationResult(False, f"{field_name} must be at most {max_value}")
        
        return ValidationResult(True, cleaned_value=numeric_value)
    
    @staticmethod
    def validate_enum_field(value: Any, field_name: str, valid_values: List[str]) -> ValidationResult:
        """Validate a field against a list of valid values."""
        if value not in valid_values:
            return ValidationResult(False, f"{field_name} must be one of: {', '.join(valid_values)}")
        
        return ValidationResult(True, cleaned_value=value)
    
    @staticmethod
    def validate_phone_field(value: Any, field_name: str) -> ValidationResult:
        """Validate a phone number field."""
        if not isinstance(value, str):
            return ValidationResult(False, f"{field_name} must be a string")
        
        # Basic UK mobile number validation
        import re
        uk_mobile_pattern = r'^(\+44|0)7\d{9}$'
        if not re.match(uk_mobile_pattern, value):
            return ValidationResult(False, f"{field_name} must be a valid UK mobile number")
        
        return ValidationResult(True, cleaned_value=value)
    
    @staticmethod
    def validate_date_field(value: Any, field_name: str) -> ValidationResult:
        """Validate a date field."""
        if not isinstance(value, str):
            return ValidationResult(False, f"{field_name} must be a string")
        
        # Basic date format validation (YYYY-MM-DD)
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, value):
            return ValidationResult(False, f"{field_name} must be in YYYY-MM-DD format")
        
        return ValidationResult(True, cleaned_value=value)
    
    @staticmethod
    def validate_time_field(value: Any, field_name: str) -> ValidationResult:
        """Validate a time field."""
        if not isinstance(value, str):
            return ValidationResult(False, f"{field_name} must be a string")
        
        # Basic time format validation (HH:MM)
        import re
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, value):
            return ValidationResult(False, f"{field_name} must be in HH:MM format")
        
        return ValidationResult(True, cleaned_value=value) 