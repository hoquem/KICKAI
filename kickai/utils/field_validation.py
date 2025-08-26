#!/usr/bin/env python3
"""
Field Validation Service

This module provides comprehensive field validation for the /update command system.
It builds on existing utilities but provides specific validation for player and
team member field updates with enhanced error messaging.
"""

import re
from typing import Optional, List, Tuple, Any
from enum import Enum

# Import existing utilities
from kickai.utils.phone_utils import is_valid_phone, normalize_phone
from kickai.core.enums import PlayerPosition, MemberRole


class ValidationError(Exception):
    """Custom exception for validation errors with user-friendly messages."""
    pass


class FieldValidator:
    """Comprehensive field validator for update operations."""

    # Valid team member roles (expanded from existing validation_utils)
    VALID_ROLES = {
        "team_member",
        "club_administrator", 
        "admin",
        "administrator",
        "team_manager",
        "manager",
        "coach",
        "head_coach",
        "assistant_coach",
        "assistant",
        "captain",
        "vice_captain",
        "secretary",
        "treasurer",
        "coordinator",
        "volunteer",
        "physio",
        "kit_manager",
        "media_manager"
    }

    @staticmethod
    def validate_phone(phone: str) -> str:
        """
        Validate and normalize phone number to UK format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Normalized phone number in E.164 format
            
        Raises:
            ValidationError: If phone number is invalid
        """
        if not phone or not phone.strip():
            raise ValidationError("Phone number cannot be empty")
            
        phone_clean = phone.strip()
        
        # Use existing phone utilities
        if not is_valid_phone(phone_clean):
            raise ValidationError(
                "Invalid phone number format. Please use UK format: "
                "+447XXXXXXXXX or 07XXXXXXXXX"
            )
        
        normalized = normalize_phone(phone_clean)
        if not normalized:
            raise ValidationError(
                "Could not normalize phone number. Please check the format."
            )
            
        return normalized

    @staticmethod  
    def validate_email(email: str) -> str:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Normalized email address (lowercase)
            
        Raises:
            ValidationError: If email format is invalid
        """
        if not email or not email.strip():
            raise ValidationError("Email address cannot be empty")
            
        email_clean = email.strip().lower()
        
        # RFC 5322 compliant email validation (simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email_clean):
            raise ValidationError(
                "Invalid email format. Please provide a valid email address "
                "(e.g., user@example.com)"
            )
            
        # Additional checks for common issues
        if email_clean.count('@') != 1:
            raise ValidationError("Email must contain exactly one @ symbol")
            
        local_part, domain = email_clean.split('@')
        
        if len(local_part) == 0:
            raise ValidationError("Email local part (before @) cannot be empty")
            
        if len(domain) == 0:
            raise ValidationError("Email domain (after @) cannot be empty")
            
        if len(email_clean) > 254:  # RFC limit
            raise ValidationError("Email address is too long (maximum 254 characters)")
            
        return email_clean

    @staticmethod
    def validate_position(position: str) -> str:
        """
        Validate football player position.
        
        Args:
            position: Position to validate
            
        Returns:
            Normalized position (lowercase)
            
        Raises:
            ValidationError: If position is invalid
        """
        if not position or not position.strip():
            raise ValidationError("Position cannot be empty")
            
        position_clean = position.strip().lower()
        
        # Get valid positions from enum
        valid_positions = [pos.value for pos in PlayerPosition]
        
        if position_clean not in valid_positions:
            raise ValidationError(
                f"Invalid position '{position}'. Valid positions are: "
                f"{', '.join(valid_positions)}"
            )
            
        return position_clean

    @staticmethod
    def validate_role(role: str, allow_admin: bool = True) -> str:
        """
        Validate team member role.
        
        Args:
            role: Role to validate
            allow_admin: Whether admin role is allowed for this operation
            
        Returns:
            Normalized role (lowercase with underscores)
            
        Raises:
            ValidationError: If role is invalid or not allowed
        """
        if not role or not role.strip():
            raise ValidationError("Role cannot be empty")
            
        # Normalize role: lowercase and replace spaces with underscores
        role_clean = role.strip().lower().replace(" ", "_")
        
        if role_clean not in FieldValidator.VALID_ROLES:
            sorted_roles = sorted(FieldValidator.VALID_ROLES)
            raise ValidationError(
                f"Invalid role '{role}'. Valid roles are: "
                f"{', '.join(sorted_roles)}"
            )
            
        # Special handling for admin role
        if role_clean in ['admin', 'administrator'] and not allow_admin:
            raise ValidationError(
                "Setting admin role requires admin privileges. "
                "Only administrators can grant admin access."
            )
            
        return role_clean

    @staticmethod
    def validate_emergency_contact_name(name: str) -> str:
        """
        Validate emergency contact name.
        
        Args:
            name: Contact name to validate
            
        Returns:
            Validated name (trimmed)
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name or not name.strip():
            raise ValidationError("Emergency contact name cannot be empty")
            
        name_clean = name.strip()
        
        # Length validation
        if len(name_clean) < 2:
            raise ValidationError(
                "Emergency contact name must be at least 2 characters long"
            )
            
        if len(name_clean) > 50:
            raise ValidationError(
                "Emergency contact name cannot exceed 50 characters"
            )
            
        # Character validation - allow letters, spaces, hyphens, apostrophes
        if not re.match(r"^[a-zA-Z\s\-\.\']+$", name_clean):
            raise ValidationError(
                "Emergency contact name can only contain letters, spaces, "
                "hyphens, dots, and apostrophes"
            )
            
        return name_clean

    @staticmethod
    def validate_emergency_contact_phone(phone: str) -> str:
        """
        Validate emergency contact phone number.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Normalized phone number
            
        Raises:
            ValidationError: If phone number is invalid
        """
        # Use same validation as main phone number
        try:
            return FieldValidator.validate_phone(phone)
        except ValidationError as e:
            # Re-raise with emergency contact context
            raise ValidationError(f"Emergency contact {str(e).lower()}")

    @staticmethod
    def validate_medical_notes(notes: str) -> str:
        """
        Validate medical notes content.
        
        Args:
            notes: Medical notes to validate
            
        Returns:
            Validated notes (trimmed)
            
        Raises:
            ValidationError: If notes are invalid
        """
        if not notes or not notes.strip():
            raise ValidationError("Medical notes cannot be empty")
            
        notes_clean = notes.strip()
        
        # Length validation
        if len(notes_clean) > 500:
            raise ValidationError(
                "Medical notes cannot exceed 500 characters"
            )
            
        # Basic content validation - no HTML tags or suspicious content
        if re.search(r'<[^>]*>', notes_clean):
            raise ValidationError(
                "Medical notes cannot contain HTML tags"
            )
            
        # Check for suspicious patterns that might indicate injection attempts
        suspicious_patterns = [
            r'javascript:',
            r'<script',
            r'onclick=',
            r'onerror=',
            r'eval\(',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, notes_clean, re.IGNORECASE):
                raise ValidationError(
                    "Medical notes contain invalid content. "
                    "Please use plain text only."
                )
                
        return notes_clean


    @staticmethod
    def validate_field_for_entity(field: str, value: str, entity_type: str,
                                  current_user_is_admin: bool = False) -> Tuple[str, Any]:
        """
        Validate a field value based on entity type and field name.
        
        Args:
            field: Field name to validate
            value: Field value to validate
            entity_type: 'player' or 'team_member'
            current_user_is_admin: Whether current user has admin privileges
            
        Returns:
            Tuple of (normalized_field_name, validated_value)
            Note: validated_value may be str, int, or other types depending on field
            
        Raises:
            ValidationError: If field or value is invalid
        """
        field_clean = field.lower().strip()
        
        # Common fields for both players and team members
        if field_clean == 'phone' or field_clean == 'phone_number':
            return 'phone_number', FieldValidator.validate_phone(value)
            
        elif field_clean == 'email':
            return 'email', FieldValidator.validate_email(value)
            
        elif field_clean == 'emergency_contact_name':
            return 'emergency_contact_name', FieldValidator.validate_emergency_contact_name(value)
            
        elif field_clean == 'emergency_contact_phone':
            return 'emergency_contact_phone', FieldValidator.validate_emergency_contact_phone(value)
            
        # Player-specific fields
        elif entity_type == 'player':
            if field_clean == 'position':
                return 'position', FieldValidator.validate_position(value)
                
            elif field_clean == 'medical_notes':
                return 'medical_notes', FieldValidator.validate_medical_notes(value)
                
            else:
                raise ValidationError(
                    f"Field '{field}' is not updatable for players. "
                    f"Available fields: phone, email, position, medical_notes, "
                    f"emergency_contact_name, emergency_contact_phone"
                )
                
        # Team member-specific fields  
        elif entity_type == 'team_member':
            if field_clean == 'role':
                return 'role', FieldValidator.validate_role(value, allow_admin=current_user_is_admin)
                
            else:
                raise ValidationError(
                    f"Field '{field}' is not updatable for team members. "
                    f"Available fields: phone, email, role, "
                    f"emergency_contact_name, emergency_contact_phone"
                )
                
        else:
            raise ValidationError(f"Unknown entity type: {entity_type}")

    @staticmethod
    def get_updatable_fields(entity_type: str) -> List[str]:
        """
        Get list of updatable fields for an entity type.
        
        Args:
            entity_type: 'player' or 'team_member'
            
        Returns:
            List of updatable field names
        """
        common_fields = [
            'phone',
            'email', 
            'emergency_contact_name',
            'emergency_contact_phone'
        ]
        
        if entity_type == 'player':
            return common_fields + ['position', 'medical_notes']
        elif entity_type == 'team_member':
            return common_fields + ['role']
        else:
            return common_fields

    @staticmethod
    def get_field_description(field: str) -> str:
        """
        Get user-friendly description of a field.
        
        Args:
            field: Field name
            
        Returns:
            Human-readable field description
        """
        descriptions = {
            'phone': 'Contact phone number (UK format: +447XXXXXXXXX or 07XXXXXXXXX)',
            'phone_number': 'Contact phone number (UK format: +447XXXXXXXXX or 07XXXXXXXXX)',
            'email': 'Email address (e.g., user@example.com)',
            'position': 'Football position (goalkeeper, defender, midfielder, forward, utility, winger, striker)',
            'role': 'Administrative role (team_manager, coach, assistant_coach, etc.)',
            'medical_notes': 'Medical information and notes (max 500 characters)',
            'emergency_contact_name': 'Emergency contact person\'s name',
            'emergency_contact_phone': 'Emergency contact phone number (UK format)',
        }
        
        return descriptions.get(field.lower(), f'Field: {field}')

    @staticmethod
    def create_help_message(entity_type: str, current_user_is_admin: bool = False) -> str:
        """
        Create a help message showing available fields for update.
        
        Args:
            entity_type: 'player' or 'team_member'
            current_user_is_admin: Whether current user has admin privileges
            
        Returns:
            Formatted help message
        """
        fields = FieldValidator.get_updatable_fields(entity_type)
        
        title = "Player" if entity_type == 'player' else "Team Member"
        help_text = f"📝 **{title} Update Fields:**\n\n"
        
        for field in fields:
            description = FieldValidator.get_field_description(field)
            
            # Add admin note for role field if user is not admin
            if field == 'role' and not current_user_is_admin:
                description += " ⚠️ *Admin privileges required for 'admin' role*"
                
            help_text += f"• **{field}** - {description}\n"
            
        help_text += f"\n💡 **Usage:** `/update <field> <value>`\n"
        help_text += f"**Example:** `/update email user@newdomain.com`"
        
        return help_text