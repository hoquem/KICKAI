#!/usr/bin/env python3
"""
Player Update Tools for KICKAI System

This module provides tools for updating player information in the main chat context.
Players can update their own information with proper validation and audit logging.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from crewai.tools import tool

from kickai.core.firestore_constants import get_team_players_collection
from kickai.core.exceptions import InputValidationError
from kickai.database.firebase_client import get_firebase_client

logger = logging.getLogger(__name__)


class PlayerUpdateValidationError(Exception):
    """Exception raised for player update validation errors."""
    pass


class PlayerUpdateValidator:
    """Validator for player information updates."""
    
    # Valid positions for players
    VALID_POSITIONS = [
        "goalkeeper", "defender", "midfielder", "forward", "striker", 
        "centre-back", "left-back", "right-back", "centre-midfielder", 
        "attacking-midfielder", "defensive-midfielder", "winger", 
        "left-winger", "right-winger", "wing-back"
    ]
    
    # Fields that players can update
    UPDATABLE_FIELDS = {
        "phone": "Contact phone number",
        "position": "Football position", 
        "email": "Email address",
        "emergency_contact": "Emergency contact information",
        "medical_notes": "Medical information"
    }
    
    # Fields that cannot be updated by users
    PROTECTED_FIELDS = {
        "user_id", "team_id", "telegram_id", "status", "created_at", 
        "source", "id", "name", "full_name", "approved_at", "approved_by"
    }
    
    @classmethod
    def validate_field_name(cls, field: str) -> bool:
        """Validate that the field name is updatable."""
        if field.lower() in cls.PROTECTED_FIELDS:
            raise PlayerUpdateValidationError(
                f"Field '{field}' cannot be updated by users. "
                f"Contact team leadership for changes to protected fields."
            )
        
        if field.lower() not in cls.UPDATABLE_FIELDS:
            available_fields = ", ".join(cls.UPDATABLE_FIELDS.keys())
            raise PlayerUpdateValidationError(
                f"Invalid field '{field}'. Available fields: {available_fields}"
            )
        
        return True
    
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validate and normalize UK phone number."""
        # Remove spaces and special characters
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # UK phone number patterns
        uk_patterns = [
            r'^\+44\d{10}$',  # +44xxxxxxxxxx
            r'^44\d{10}$',    # 44xxxxxxxxxx  
            r'^07\d{9}$',     # 07xxxxxxxxx
            r'^01\d{9}$',     # 01xxxxxxxxx
            r'^020\d{8}$',    # 020xxxxxxxx (London)
            r'^011\d{8}$',    # 011xxxxxxxx (Northern Ireland)
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
        
        raise PlayerUpdateValidationError(
            f"Invalid phone number format. Please use UK format: "
            f"+44xxxxxxxxxx or 07xxxxxxxxx. Got: {phone}"
        )
    
    @classmethod
    def validate_position(cls, position: str) -> str:
        """Validate football position."""
        normalized_position = position.lower().strip()
        
        if normalized_position not in cls.VALID_POSITIONS:
            valid_positions = ", ".join(cls.VALID_POSITIONS)
            raise PlayerUpdateValidationError(
                f"Invalid position '{position}'. Valid positions: {valid_positions}"
            )
        
        # Return properly capitalized position
        return position.strip().title()
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email address format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email.strip()):
            raise PlayerUpdateValidationError(
                f"Invalid email format. Please provide a valid email address. Got: {email}"
            )
        
        return email.strip().lower()
    
    @classmethod
    def validate_emergency_contact(cls, contact: str) -> str:
        """Validate emergency contact information."""
        if len(contact.strip()) < 5:
            raise PlayerUpdateValidationError(
                "Emergency contact must be at least 5 characters long"
            )
        
        if len(contact.strip()) > 200:
            raise PlayerUpdateValidationError(
                "Emergency contact must be less than 200 characters"
            )
        
        return contact.strip()
    
    @classmethod
    def validate_medical_notes(cls, notes: str) -> str:
        """Validate medical notes."""
        if len(notes.strip()) > 500:
            raise PlayerUpdateValidationError(
                "Medical notes must be less than 500 characters"
            )
        
        return notes.strip()
    
    @classmethod
    def validate_field_value(cls, field: str, value: str) -> str:
        """Validate field value based on field type."""
        field_lower = field.lower()
        
        if field_lower == "phone":
            return cls.validate_phone(value)
        elif field_lower == "position":
            return cls.validate_position(value)
        elif field_lower == "email":
            return cls.validate_email(value)
        elif field_lower == "emergency_contact":
            return cls.validate_emergency_contact(value)
        elif field_lower == "medical_notes":
            return cls.validate_medical_notes(value)
        else:
            raise PlayerUpdateValidationError(f"Unknown field type: {field}")


@tool
def update_player_information(user_id: str, team_id: str, field: str, value: str, username: str = "Unknown") -> str:
    """
    Update specific player information field with validation and audit logging.
    
    Args:
        user_id: Telegram user ID of the player
        team_id: Team ID
        field: Field name to update (phone, position, email, emergency_contact, medical_notes)
        value: New value for the field
        username: Username of the person making the update
        
    Returns:
        Success or error message
    """
    try:
        logger.info(f"🔄 Player update request: user_id={user_id}, team_id={team_id}, field={field}")
        
        # Validate inputs
        if not user_id or not team_id or not field or not value:
            return "❌ Update Failed: Missing required parameters (user_id, team_id, field, value)"
        
        # Initialize Firebase service
        firebase_service = get_firebase_client()
        collection_name = get_team_players_collection(team_id)
        
        # Check if player exists
        logger.info(f"🔍 Checking if player exists: user_id={user_id}")
        players = asyncio.run(firebase_service.query_documents(
            collection_name, 
            [{"field": "telegram_id", "operator": "==", "value": user_id}]
        ))
        
        if not players:
            logger.warning(f"❌ Player not found: user_id={user_id}")
            return "❌ Update Failed: You are not registered as a player. Contact team leadership to be added."
        
        player = players[0]
        player_id = player.get('id', 'unknown')
        player_name = player.get('full_name', 'Unknown Player')
        
        logger.info(f"✅ Found player: {player_name} (ID: {player_id})")
        
        # Validate field name
        validator = PlayerUpdateValidator()
        validator.validate_field_name(field)
        
        # Validate and normalize field value
        validated_value = validator.validate_field_value(field, value)
        logger.info(f"✅ Field validation passed: {field} = {validated_value}")
        
        # Check for duplicate phone numbers (if updating phone)
        if field.lower() == "phone":
            existing_players = asyncio.run(firebase_service.query_documents(
                collection_name,
                [{"field": "phone", "operator": "==", "value": validated_value}]
            ))
            
            # Filter out the current player
            duplicate_players = [p for p in existing_players if p.get('telegram_id') != user_id]
            
            if duplicate_players:
                duplicate_name = duplicate_players[0].get('name', 'Unknown')
                logger.warning(f"❌ Duplicate phone number: {validated_value} already used by {duplicate_name}")
                return f"❌ Update Failed: Phone number {validated_value} is already registered to another player ({duplicate_name})"
        
        # Prepare update data
        current_time = datetime.now().isoformat()
        old_value = player.get(field, "Not set")
        
        update_data = {
            field: validated_value,
            "updated_at": current_time,
            "updated_by": username,
            f"{field}_updated_at": current_time,
            f"{field}_previous_value": old_value
        }
        
        # Update player record
        asyncio.run(firebase_service.update_document(collection_name, player_id, update_data))
        
        logger.info(f"✅ Player information updated successfully: {field} = {validated_value}")
        
        # Create audit log
        audit_data = {
            "action": "player_info_update",
            "user_id": user_id,
            "player_id": player_id,
            "player_name": player_name,
            "team_id": team_id,
            "field": field,
            "old_value": old_value,
            "new_value": validated_value,
            "updated_by": username,
            "timestamp": current_time,
            "source": "self_service_update"
        }
        
        try:
            asyncio.run(firebase_service.create_document(f"kickai_{team_id}_audit_logs", audit_data))
            logger.info(f"✅ Audit log created for player update")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create audit log: {e}")
        
        # Return success message
        field_description = validator.UPDATABLE_FIELDS.get(field, field)
        
        return f"""✅ Information Updated Successfully!

📋 Player: {player_name}
🔄 Updated Field: {field_description}
🆕 New Value: {validated_value}
🕐 Updated: {datetime.fromisoformat(current_time).strftime('%d %b %Y at %H:%M')}
👤 Updated By: {username}

💡 Use /myinfo to view your complete updated information."""
        
    except PlayerUpdateValidationError as e:
        logger.warning(f"❌ Validation error: {e}")
        return f"❌ Update Failed: {str(e)}"
        
    except Exception as e:
        logger.error(f"❌ Error updating player information: {e}", exc_info=True)
        return f"❌ Update Failed: An unexpected error occurred. Please try again or contact support."


@tool
def get_player_updatable_fields(user_id: str, team_id: str) -> str:
    """
    Get list of fields that a player can update with examples and validation rules.
    
    Args:
        user_id: Telegram user ID of the player
        team_id: Team ID
        
    Returns:
        List of updatable fields with descriptions and examples
    """
    try:
        logger.info(f"📋 Getting updatable fields for player: user_id={user_id}")
        
        # Check if player exists
        firebase_service = get_firebase_client()
        collection_name = get_team_players_collection(team_id)
        
        players = asyncio.run(firebase_service.query_documents(
            collection_name, 
            [{"field": "telegram_id", "operator": "==", "value": user_id}]
        ))
        
        if not players:
            return """❌ Update Not Available

🔍 You are not registered as a player in this team.

📞 To register as a player:
1. Contact someone in the team's leadership
2. Ask them to add you using /addplayer
3. They'll send you an invite link
4. Join the main chat and register with /register

💡 Need help? Use /help to see available commands."""
        
        player = players[0]
        player_name = player.get('full_name', 'Unknown Player')
        
        # Get valid positions for reference
        positions = ", ".join(PlayerUpdateValidator.VALID_POSITIONS[:10]) + "..."
        
        return f"""✅ Player Information Update

👤 {player_name} - Available Fields to Update:

📱 **phone** - Your contact phone number
   Example: /update phone 07123456789
   Format: UK numbers (+44 or 07xxx format)

⚽ **position** - Your football position
   Example: /update position midfielder
   Valid: {positions}

📧 **email** - Your email address
   Example: /update email john@example.com
   Format: Valid email address

🚨 **emergency_contact** - Emergency contact info
   Example: /update emergency_contact +44787654321
   Format: Phone number or contact details

🏥 **medical_notes** - Medical information
   Example: /update medical_notes Allergic to peanuts
   Format: Text up to 500 characters

📝 Usage: /update [field] [new value]

🔒 Security:
• Only you can update your own information
• All changes are logged for audit purposes
• Phone numbers must be unique within the team

💡 Use /myinfo to view your current information before updating."""
        
    except Exception as e:
        logger.error(f"❌ Error getting updatable fields: {e}", exc_info=True)
        return "❌ Error retrieving updatable fields. Please try again."


@tool
def validate_player_update_request(user_id: str, team_id: str, field: str, value: str) -> str:
    """
    Validate a player update request without actually performing the update.
    
    Args:
        user_id: Telegram user ID of the player
        team_id: Team ID
        field: Field name to validate
        value: Value to validate
        
    Returns:
        Validation result message
    """
    try:
        logger.info(f"🔍 Validating player update: field={field}, value={value}")
        
        # Check if player exists
        firebase_service = get_firebase_client()
        collection_name = get_team_players_collection(team_id)
        
        players = asyncio.run(firebase_service.query_documents(
            collection_name, 
            [{"field": "telegram_id", "operator": "==", "value": user_id}]
        ))
        
        if not players:
            return "❌ Validation Failed: You are not registered as a player"
        
        # Validate field and value
        validator = PlayerUpdateValidator()
        validator.validate_field_name(field)
        validated_value = validator.validate_field_value(field, value)
        
        # Check for duplicates if phone
        if field.lower() == "phone":
            existing_players = asyncio.run(firebase_service.query_documents(
                collection_name,
                [{"field": "phone", "operator": "==", "value": validated_value}]
            ))
            
            duplicate_players = [p for p in existing_players if p.get('telegram_id') != user_id]
            
            if duplicate_players:
                return f"❌ Validation Failed: Phone number already in use"
        
        field_description = validator.UPDATABLE_FIELDS.get(field, field)
        
        return f"""✅ Validation Successful

🔄 Field: {field_description}
🆕 Validated Value: {validated_value}
📋 Status: Ready to update

💡 Use /update {field} {validated_value} to apply this change."""
        
    except PlayerUpdateValidationError as e:
        return f"❌ Validation Failed: {str(e)}"
        
    except Exception as e:
        logger.error(f"❌ Error validating update request: {e}")
        return "❌ Validation Error: Please check your input and try again"