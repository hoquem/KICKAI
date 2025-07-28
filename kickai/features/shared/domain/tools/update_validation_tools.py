#!/usr/bin/env python3
"""
Shared Update Validation Tools for KICKAI System

This module provides common validation utilities for update operations
across different entity types (players, team members).
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from crewai import tool

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


@tool
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


@tool
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
        from kickai.database.firebase_service import FirebaseService
        
        firebase_service = FirebaseService()
        
        # Query for existing records with this field value
        existing_records = firebase_service.query_documents(
            collection_name,
            [(field_name, "==", field_value)]
        )
        
        # Filter out the current user if specified
        if exclude_user_id:
            existing_records = [
                record for record in existing_records 
                if record.get('user_id') != exclude_user_id
            ]
        
        if existing_records:
            # Field value is not unique
            existing_name = existing_records[0].get('name', 'Unknown')
            return f"❌ {field_name.title()} '{field_value}' is already in use by {existing_name}"
        else:
            # Field value is unique
            return f"✅ {field_name.title()} '{field_value}' is available"
            
    except Exception as e:
        logger.error(f"❌ Error checking field uniqueness: {e}")
        return f"❌ Error checking uniqueness: Please try again"


@tool
def get_validation_rules_for_field(entity_type: str, field_name: str) -> str:
    """
    Get validation rules and examples for a specific field and entity type.
    
    Args:
        entity_type: Type of entity (player, team_member)
        field_name: Name of the field
        
    Returns:
        Validation rules and examples for the field
    """
    try:
        rules = {
            "player": {
                "phone": {
                    "description": "Contact phone number",
                    "format": "UK phone numbers (+44 or 07xxx format)",
                    "examples": ["+447123456789", "07123456789", "+441234567890"],
                    "validation": "Must be valid UK phone number"
                },
                "position": {
                    "description": "Football position",
                    "format": "Valid football position name",
                    "examples": ["Goalkeeper", "Defender", "Midfielder", "Forward", "Striker"],
                    "validation": "Must be from predefined list of positions"
                },
                "email": {
                    "description": "Email address",
                    "format": "Valid email format",
                    "examples": ["player@example.com", "john.smith@gmail.com"],
                    "validation": "Must be valid email format (max 254 characters)"
                },
                "emergency_contact": {
                    "description": "Emergency contact information",
                    "format": "Phone number or contact details",
                    "examples": ["+44787654321", "Parent: Jane Smith +44712345678"],
                    "validation": "5-200 characters"
                },
                "medical_notes": {
                    "description": "Medical information",
                    "format": "Free text",
                    "examples": ["Allergic to peanuts", "Asthma - carries inhaler"],
                    "validation": "Max 500 characters"
                }
            },
            "team_member": {
                "phone": {
                    "description": "Contact phone number",
                    "format": "UK phone numbers (+44 or 07xxx format)",
                    "examples": ["+447123456789", "07123456789"],
                    "validation": "Must be valid UK phone number"
                },
                "email": {
                    "description": "Email address",
                    "format": "Valid email format",
                    "examples": ["admin@example.com", "coach@teamname.com"],
                    "validation": "Must be valid email format (max 254 characters)"
                },
                "emergency_contact": {
                    "description": "Emergency contact information",
                    "format": "Phone number or contact details",
                    "examples": ["+44787654321", "Spouse: Sarah +44712345678"],
                    "validation": "5-200 characters"
                },
                "role": {
                    "description": "Administrative role (requires admin approval)",
                    "format": "Valid team role",
                    "examples": ["Team Manager", "Coach", "Assistant Coach", "Volunteer"],
                    "validation": "Must be from predefined list of roles, requires admin approval"
                }
            }
        }
        
        entity_rules = rules.get(entity_type)
        if not entity_rules:
            return f"❌ Unknown entity type: {entity_type}"
        
        field_rules = entity_rules.get(field_name)
        if not field_rules:
            available_fields = ", ".join(entity_rules.keys())
            return f"❌ Unknown field '{field_name}' for {entity_type}. Available fields: {available_fields}"
        
        examples_text = "\n".join([f"   • {example}" for example in field_rules["examples"]])
        
        return f"""📋 Validation Rules for {entity_type.title()} - {field_name.title()}

📝 Description: {field_rules["description"]}
📐 Format: {field_rules["format"]}
✅ Validation: {field_rules["validation"]}

💡 Examples:
{examples_text}

📝 Usage: /update {field_name} [new_value]"""
        
    except Exception as e:
        logger.error(f"❌ Error getting validation rules: {e}")
        return f"❌ Error retrieving validation rules for {field_name}"


@tool
def format_update_success_message(entity_type: str, entity_name: str, field_name: str, 
                                new_value: str, updated_by: str, timestamp: str) -> str:
    """
    Format a standardized success message for update operations.
    
    Args:
        entity_type: Type of entity (player, team_member)
        entity_name: Name of the entity being updated
        field_name: Name of the field updated
        new_value: New value that was set
        updated_by: Username who performed the update
        timestamp: ISO timestamp of the update
        
    Returns:
        Formatted success message
    """
    try:
        from datetime import datetime
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime('%d %b %Y at %H:%M')
        except:
            formatted_time = timestamp
        
        # Determine entity icon
        entity_icon = "👤" if entity_type == "player" else "👔"
        
        # Field descriptions
        field_descriptions = {
            "phone": "Contact Phone",
            "email": "Email Address", 
            "position": "Football Position",
            "role": "Administrative Role",
            "emergency_contact": "Emergency Contact",
            "medical_notes": "Medical Information"
        }
        
        field_desc = field_descriptions.get(field_name, field_name.title())
        
        return f"""✅ Information Updated Successfully!

{entity_icon} {entity_type.title()}: {entity_name}
🔄 Updated Field: {field_desc}
🆕 New Value: {new_value}
🕐 Updated: {formatted_time}
👤 Updated By: {updated_by}

💡 Use /myinfo to view your complete updated information."""
        
    except Exception as e:
        logger.error(f"❌ Error formatting success message: {e}")
        return f"✅ Update completed successfully!"


@tool
def format_approval_request_message(entity_type: str, entity_name: str, field_name: str,
                                  new_value: str, requested_by: str, timestamp: str) -> str:
    """
    Format a standardized approval request message for fields requiring admin approval.
    
    Args:
        entity_type: Type of entity (player, team_member)
        entity_name: Name of the entity requesting update
        field_name: Name of the field to be updated
        new_value: Requested new value
        requested_by: Username who made the request
        timestamp: ISO timestamp of the request
        
    Returns:
        Formatted approval request message
    """
    try:
        from datetime import datetime
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime('%d %b %Y at %H:%M')
        except:
            formatted_time = timestamp
        
        # Field descriptions
        field_descriptions = {
            "role": "Administrative Role",
            "status": "Account Status",
            "permissions": "Access Permissions"
        }
        
        field_desc = field_descriptions.get(field_name, field_name.title())
        
        return f"""⏳ Approval Request Submitted

📋 Requested Change: {field_desc} → {new_value}
👤 Requested By: {requested_by}
📅 Requested: {formatted_time}

🔒 This change requires admin approval.
📧 You'll be notified when the request is processed.

💡 Contact a team admin to expedite the approval."""
        
    except Exception as e:
        logger.error(f"❌ Error formatting approval request message: {e}")
        return f"⏳ Approval request submitted successfully!"