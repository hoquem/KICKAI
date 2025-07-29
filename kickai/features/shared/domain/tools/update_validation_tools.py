#!/usr/bin/env python3
"""
Shared Update Validation Tools for KICKAI System

This module provides common validation utilities for update operations
across different entity types (players, team members).
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from crewai.tools import tool

logger = logging.getLogger(__name__)


class UpdateValidationError(Exception):
    """Exception raised for update validation errors."""
    pass


class CommonUpdateValidator:
    """Common validation utilities for update operations."""
    
    @staticmethod
    def validate_phone_format(phone: str) -> str:
        """
        Validate and normalize UK phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Normalized phone number in +44 format
            
        Raises:
            UpdateValidationError: If phone format is invalid
        """
        # Remove spaces and special characters except +
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # UK phone number patterns
        uk_patterns = [
            r'^\+44\d{10}$',  # +44xxxxxxxxxx
            r'^44\d{10}$',    # 44xxxxxxxxxx  
            r'^07\d{9}$',     # 07xxxxxxxxx
            r'^01\d{9}$',     # 01xxxxxxxxx
            r'^020\d{8}$',    # 020xxxxxxxx (London)
            r'^011\d{8}$',    # 011xxxxxxxx (Northern Ireland)
            r'^03\d{9}$',     # 03xxxxxxxxx (non-geographic)
        ]
        
        # Try to match patterns
        for pattern in uk_patterns:
            if re.match(pattern, cleaned_phone):
                # Normalize to +44 format
                if cleaned_phone.startswith('0'):
                    return f"+44{cleaned_phone[1:]}"
                elif cleaned_phone.startswith('44'):
                    return f"+{cleaned_phone}"
                else:
                    return cleaned_phone
        
        raise UpdateValidationError(
            f"Invalid phone number format. Please use UK format: "
            f"+44xxxxxxxxxx or 07xxxxxxxxx. Got: {phone}"
        )
    
    @staticmethod
    def validate_email_format(email: str) -> str:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Normalized email address (lowercase)
            
        Raises:
            UpdateValidationError: If email format is invalid
        """
        # Basic email validation pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        email_stripped = email.strip()
        
        if not email_stripped:
            raise UpdateValidationError("Email address cannot be empty")
        
        if len(email_stripped) > 254:  # RFC 5321 limit
            raise UpdateValidationError("Email address is too long (max 254 characters)")
        
        if not re.match(email_pattern, email_stripped):
            raise UpdateValidationError(
                f"Invalid email format. Please provide a valid email address. Got: {email}"
            )
        
        return email_stripped.lower()
    
    @staticmethod
    def validate_text_field(text: str, field_name: str, min_length: int = 1, max_length: int = 200) -> str:
        """
        Validate text field with length constraints.
        
        Args:
            text: Text to validate
            field_name: Name of the field for error messages
            min_length: Minimum length (default: 1)
            max_length: Maximum length (default: 200)
            
        Returns:
            Stripped text
            
        Raises:
            UpdateValidationError: If text doesn't meet constraints
        """
        text_stripped = text.strip()
        
        if len(text_stripped) < min_length:
            raise UpdateValidationError(
                f"{field_name} must be at least {min_length} character{'s' if min_length > 1 else ''} long"
            )
        
        if len(text_stripped) > max_length:
            raise UpdateValidationError(
                f"{field_name} must be less than {max_length} characters"
            )
        
        return text_stripped
    
    @staticmethod
    def validate_choice_field(value: str, field_name: str, valid_choices: List[str], case_sensitive: bool = False) -> str:
        """
        Validate that a value is in a list of valid choices.
        
        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            valid_choices: List of valid choices
            case_sensitive: Whether comparison should be case sensitive
            
        Returns:
            Validated value (with proper capitalization if applicable)
            
        Raises:
            UpdateValidationError: If value is not in valid choices
        """
        value_stripped = value.strip()
        
        if not case_sensitive:
            value_lower = value_stripped.lower()
            valid_choices_lower = [choice.lower() for choice in valid_choices]
            
            if value_lower not in valid_choices_lower:
                choices_display = ", ".join(valid_choices)
                raise UpdateValidationError(
                    f"Invalid {field_name} '{value}'. Valid options: {choices_display}"
                )
            
            # Return the original case from valid_choices
            index = valid_choices_lower.index(value_lower)
            return valid_choices[index]
        else:
            if value_stripped not in valid_choices:
                choices_display = ", ".join(valid_choices)
                raise UpdateValidationError(
                    f"Invalid {field_name} '{value}'. Valid options: {choices_display}"
                )
            
            return value_stripped


@tool("validate_update_field_generic")
def validate_update_field_generic(field_type: str, field_value: str, validation_params: str = "{}") -> str:
    """
    Generic field validation tool that can be used by different entity types.
    
    Args:
        field_type: Type of field (phone, email, text, choice)
        field_value: Value to validate
        validation_params: JSON string with validation parameters
        
    Returns:
        Validation result message
    """
    try:
        import json
        
        # Parse validation parameters
        try:
            params = json.loads(validation_params) if validation_params else {}
        except json.JSONDecodeError:
            params = {}
        
        validator = CommonUpdateValidator()
        
        if field_type == "phone":
            validated_value = validator.validate_phone_format(field_value)
            return f"✅ Valid phone number: {validated_value}"
            
        elif field_type == "email":
            validated_value = validator.validate_email_format(field_value)
            return f"✅ Valid email address: {validated_value}"
            
        elif field_type == "text":
            field_name = params.get("field_name", "field")
            min_length = params.get("min_length", 1)
            max_length = params.get("max_length", 200)
            
            validated_value = validator.validate_text_field(
                field_value, field_name, min_length, max_length
            )
            return f"✅ Valid {field_name}: {validated_value}"
            
        elif field_type == "choice":
            field_name = params.get("field_name", "field")
            valid_choices = params.get("valid_choices", [])
            case_sensitive = params.get("case_sensitive", False)
            
            if not valid_choices:
                return "❌ Validation Error: No valid choices provided"
            
            validated_value = validator.validate_choice_field(
                field_value, field_name, valid_choices, case_sensitive
            )
            return f"✅ Valid {field_name}: {validated_value}"
            
        else:
            return f"❌ Validation Error: Unknown field type '{field_type}'"
            
    except UpdateValidationError as e:
        return f"❌ Validation Error: {str(e)}"
        
    except Exception as e:
        logger.error(f"❌ Error in generic field validation: {e}")
        return f"❌ Validation Error: An unexpected error occurred during validation"


@tool("check_field_uniqueness")
def check_field_uniqueness(collection_name: str, field_name: str, field_value: str, exclude_user_id: str = None) -> str:
    """
    Check if a field value is unique within a collection (excluding current user).
    
    Args:
        collection_name: Firestore collection name
        field_name: Name of the field to check
        field_value: Value to check for uniqueness
        exclude_user_id: User ID to exclude from uniqueness check
        
    Returns:
        Uniqueness check result message
    """
    try:
        from kickai.database.firebase_client import get_firebase_client
        
        firebase_service = get_firebase_client()
        
        # Query for existing records with this field value
        existing_records = firebase_service.query_documents(
            collection_name,
            [(field_name, "==", field_value)]
        )
        
        # Filter out the current user if specified
        if exclude_user_id:
            existing_records = [
                record for record in existing_records 
                if record.get("user_id") != exclude_user_id
            ]
        
        if existing_records:
            return f"❌ Field '{field_name}' with value '{field_value}' already exists in {collection_name}"
        else:
            return f"✅ Field '{field_name}' with value '{field_value}' is unique in {collection_name}"
            
    except Exception as e:
        logger.error(f"❌ Error checking field uniqueness: {e}")
        return f"❌ Error checking field uniqueness: {str(e)}"


@tool("get_validation_rules_for_field")
def get_validation_rules_for_field(entity_type: str, field_name: str) -> str:
    """
    Get validation rules for a specific field in an entity type.
    
    Args:
        entity_type: Type of entity (player, team_member)
        field_name: Name of the field to get rules for
        
    Returns:
        JSON string with validation rules
    """
    try:
        import json
        
        # Define validation rules for different entity types and fields
        validation_rules = {
            "player": {
                "name": {
                    "type": "text",
                    "min_length": 2,
                    "max_length": 50,
                    "required": True,
                    "pattern": r"^[a-zA-Z\s\-']+$"
                },
                "phone": {
                    "type": "phone",
                    "required": True,
                    "format": "UK"
                },
                "position": {
                    "type": "choice",
                    "required": True,
                    "valid_choices": ["goalkeeper", "defender", "midfielder", "forward", "utility"]
                },
                "email": {
                    "type": "email",
                    "required": False
                },
                "emergency_contact": {
                    "type": "text",
                    "min_length": 5,
                    "max_length": 200,
                    "required": False
                },
                "medical_notes": {
                    "type": "text",
                    "min_length": 0,
                    "max_length": 500,
                    "required": False
                }
            },
            "team_member": {
                "name": {
                    "type": "text",
                    "min_length": 2,
                    "max_length": 50,
                    "required": True,
                    "pattern": r"^[a-zA-Z\s\-']+$"
                },
                "phone": {
                    "type": "phone",
                    "required": True,
                    "format": "UK"
                },
                "role": {
                    "type": "choice",
                    "required": True,
                    "valid_choices": [
                        "team manager", "coach", "assistant coach", "head coach",
                        "club administrator", "treasurer", "secretary", 
                        "volunteer coordinator", "volunteer", "parent helper",
                        "first aid coordinator", "equipment manager", "transport coordinator"
                    ]
                },
                "email": {
                    "type": "email",
                    "required": False
                },
                "emergency_contact": {
                    "type": "text",
                    "min_length": 5,
                    "max_length": 200,
                    "required": False
                }
            }
        }
        
        # Get rules for the specified entity type and field
        entity_rules = validation_rules.get(entity_type.lower(), {})
        field_rules = entity_rules.get(field_name.lower(), {})
        
        if not field_rules:
            return json.dumps({
                "error": f"No validation rules found for field '{field_name}' in entity type '{entity_type}'"
            })
        
        return json.dumps(field_rules, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error getting validation rules: {e}")
        return json.dumps({"error": f"Error getting validation rules: {str(e)}"})


@tool("format_update_success_message")
def format_update_success_message(entity_type: str, entity_name: str, field_name: str, 
                                new_value: str, updated_by: str, timestamp: str) -> str:
    """
    Format a success message for field updates.
    
    Args:
        entity_type: Type of entity (player, team_member)
        entity_name: Name of the entity
        field_name: Name of the field that was updated
        new_value: New value of the field
        updated_by: Username of who made the update
        timestamp: Timestamp of the update
        
    Returns:
        Formatted success message
    """
    try:
        # Format the success message
        success_message = f"""
✅ **UPDATE SUCCESSFUL!**

📝 **Details:**
• **Entity:** {entity_type.title()} - {entity_name}
• **Field Updated:** {field_name.replace('_', ' ').title()}
• **New Value:** {new_value}
• **Updated By:** {updated_by}
• **Timestamp:** {timestamp}

🎉 The {entity_type} information has been successfully updated!
        """
        
        return success_message.strip()
        
    except Exception as e:
        logger.error(f"❌ Error formatting success message: {e}")
        return f"✅ Update successful! Field '{field_name}' updated to '{new_value}'"


@tool("format_approval_request_message")
def format_approval_request_message(entity_type: str, entity_name: str, field_name: str,
                                  new_value: str, requested_by: str, timestamp: str) -> str:
    """
    Format an approval request message for field updates that require admin approval.
    
    Args:
        entity_type: Type of entity (player, team_member)
        entity_name: Name of the entity
        field_name: Name of the field that needs approval
        new_value: Requested new value
        requested_by: Username of who requested the change
        timestamp: Timestamp of the request
        
    Returns:
        Formatted approval request message
    """
    try:
        # Format the approval request message
        approval_message = f"""
⏳ **APPROVAL REQUEST PENDING**

📋 **Request Details:**
• **Entity:** {entity_type.title()} - {entity_name}
• **Field:** {field_name.replace('_', ' ').title()}
• **Requested Value:** {new_value}
• **Requested By:** {requested_by}
• **Requested At:** {timestamp}

🔍 **Next Steps:**
• This change requires admin approval
• You'll be notified when the request is reviewed
• Contact team leadership for urgent requests

⏰ **Status:** Pending Approval
        """
        
        return approval_message.strip()
        
    except Exception as e:
        logger.error(f"❌ Error formatting approval message: {e}")
        return f"⏳ Approval request submitted for field '{field_name}' with value '{new_value}'"