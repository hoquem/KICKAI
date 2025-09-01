#!/usr/bin/env python3
"""
Player Update Tools - Clean Architecture Application Layer

This module provides CrewAI tools for player information updates.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Dict, Any
from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.utils.field_validation import FieldValidator, ValidationError
from kickai.utils.native_crewai_helpers import (
    convert_telegram_id, 
    validate_required_strings
)


@tool("update_player_field")
async def update_player_field(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    field: str,
    value: str
) -> str:
    """
    Update a single field for a player.

    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: Player's Telegram ID (string)
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat context
        field: Field name to update (phone, email, position, etc.)
        value: New value for the field
        
    Returns:
        Formatted response with success status and details
    """
    try:
        # Simple type conversion
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"
        
        # Basic validation
        if telegram_id_int <= 0:
            return "❌ Valid telegram_id is required"
        
        if not team_id or not username or not chat_type or not field or not value:
            return "❌ All parameters are required"
        
        logger.info(f"🔄 Updating player field: {field} = '{value}' for {username} ({telegram_id_int}) in team {team_id}")

        # Get required services from container (application boundary)
        container = get_container()
        
        # Ensure container is initialized
        if not container._initialized:
            logger.warning("⚠️ Container not initialized, attempting to initialize...")
            try:
                await container.initialize()
                logger.info("✅ Container initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize container: {e}")
                return "❌ System initialization error. Please try again."
        
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            return f"""❌ System Error

Player service is currently unavailable. Please try again later.

If this problem persists, contact system administrator.

💡 Technical Details:
• Service: PlayerService
• User: {username} ({telegram_id})
• Team: {team_id}"""

        # Validate field value using utility (application layer validation)
        try:
            normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                field, value, 'player', current_user_is_admin=False
            )
            # Update the field and value with normalized/validated versions
            field = normalized_field
            value = validated_value
        except ValidationError as e:
            return f"❌ {str(e)}"

        # Get player first, then update using existing service method
        player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
        
        if not player:
            return "❌ Player not found. You may not be registered as a player."
            
        # Create update dictionary for the field
        updates = {field: value}
        
        # Execute domain operation using existing update_player method
        try:
            updated_player = await player_service.update_player(player.player_id, team_id, **updates)
            success = updated_player is not None
        except Exception as e:
            return f"❌ Failed to update {field}: {str(e)}"
        
        if success:
            response_data = {
                "field": field,
                "new_value": value,
                "telegram_id": telegram_id,
                "team_id": team_id,
                "message": f"✅ Successfully updated {field} to '{value}'"
            }
            
            logger.info(f"✅ Player field {field} updated successfully for {username}")
            return f"✅ Successfully updated {field} to '{value}'"
        else:
            return f"❌ Failed to update {field}. Player may not exist or update failed."

    except Exception as e:
        logger.error(f"❌ Error updating player field {field} for {username}: {e}")
        return f"❌ Failed to update {field}: {e}"


@tool("update_player_multiple")
async def update_player_multiple(telegram_id: str, team_id: str, username: str, chat_type: str, updates: str) -> str:
    """
    Update multiple fields for a player in a single operation.

    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: Player's Telegram ID (string)
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat context
        updates: JSON string of field names to new values
        
    Returns:
        Formatted response with success status and details
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            telegram_id, team_id, username, chat_type, updates,
            names=["telegram_id", "team_id", "username", "chat_type", "updates"]
        )
        if validation_error:
            return validation_error
        
        # Convert telegram_id
        telegram_id_int = convert_telegram_id(telegram_id)
        if not telegram_id_int:
            return "❌ Invalid telegram_id format"
        
        # Parse updates JSON string
        try:
            import json
            updates_dict = json.loads(updates)
            if not isinstance(updates_dict, dict):
                return "❌ Updates must be a valid JSON object"
        except (json.JSONDecodeError, TypeError):
            return "❌ Invalid updates format. Please provide valid JSON"
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id_int or telegram_id_int <= 0:
            return "❌ Valid telegram_id is required"
        
        if not team_id or not isinstance(team_id, str):
            return "❌ Valid team_id is required"
            
        if not username or not isinstance(username, str):
            return "❌ Valid username is required"
            
        if not chat_type or not isinstance(chat_type, str):
            return "❌ Valid chat_type is required"
        
        logger.info(f"🔄 Bulk update for {username} ({telegram_id_int}): {list(updates_dict.keys()) if updates_dict else 'No updates'}")
        
        # Validate inputs at application boundary
        if not updates_dict or not isinstance(updates_dict, dict):
            return "❌ Updates dictionary is required for bulk update"

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            return "❌ PlayerService is not available"

        # Validate all field values using utility (application layer validation)
        try:
            validated_updates = {}
            for field, value in updates_dict.items():
                normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                    field, value, 'player', current_user_is_admin=False
                )
                validated_updates[normalized_field] = validated_value
            # Use validated updates
            updates_dict = validated_updates
        except ValidationError as e:
            return f"❌ {str(e)}"

        # Get player first, then update using existing service method
        player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)
        
        if not player:
            return "❌ Player not found. You may not be registered as a player."
            
        # Execute domain operation using existing update_player method
        try:
            updated_player = await player_service.update_player(player.player_id, team_id, **updates_dict)
            success = updated_player is not None
        except Exception as e:
            return f"❌ Failed to update player fields: {str(e)}"
        
        if success:
            response_data = {
                "updated_fields": updates_dict,
                "telegram_id": telegram_id_int,
                "team_id": team_id,
                "field_count": len(updates_dict),
                "message": f"✅ Successfully updated {len(updates_dict)} fields: {', '.join(updates_dict.keys())}"
            }
            
            logger.info(f"✅ Bulk update completed for {username}: {len(updates_dict)} fields")
            # Create formatted success message
            success_message = f"✅ Successfully updated {len(updates_dict)} fields\n"
            for field, value in updates_dict.items():
                success_message += f"   • {field}: {value}\n"
            return success_message.strip()
        else:
            return "❌ Failed to update player fields. Player may not exist or update failed."

    except Exception as e:
        logger.error(f"❌ Error in bulk update for {username}: {e}")
        return f"❌ Failed to update player fields: {e}"


@tool("get_player_update_help")
async def get_player_update_help(telegram_id: str, team_id: str, username: str, chat_type: str) -> str:
    """
    Get help information for player field updates.

    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: Player's Telegram ID (string)
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat context
        
    Returns:
        Formatted help information for player updates
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            telegram_id, team_id, username, chat_type,
            names=["telegram_id", "team_id", "username", "chat_type"]
        )
        if validation_error:
            return validation_error
        
        # Convert telegram_id
        telegram_id_int = convert_telegram_id(telegram_id)
        if not telegram_id_int:
            return "❌ Invalid telegram_id format"
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id_int or telegram_id_int <= 0:
            return "❌ Valid telegram_id is required"
        
        if not team_id or not isinstance(team_id, str):
            return "❌ Valid team_id is required"
            
        if not username or not isinstance(username, str):
            return "❌ Valid username is required"
            
        if not chat_type or not isinstance(chat_type, str):
            return "❌ Valid chat_type is required"
        
        logger.info(f"📖 Update help requested by {username} ({telegram_id_int})")
        
        # Use FieldValidator for dynamic help content generation
        from kickai.utils.field_validation import FieldValidator
        
        help_content = FieldValidator.create_help_message('player', current_user_is_admin=False)
        available_fields = FieldValidator.get_updatable_fields('player')
        
        # Create validation rules dynamically
        validation_rules = {}
        for field in available_fields:
            validation_rules[field] = FieldValidator.get_field_description(field)

        response_data = {
            "help_content": help_content,
            "available_fields": available_fields,
            "validation_rules": validation_rules
        }
        
        logger.info(f"✅ Update help provided to {username}")
        return help_content

    except Exception as e:
        logger.error(f"❌ Error providing update help to {username}: {e}")
        return f"❌ Failed to get update help: {e}"

