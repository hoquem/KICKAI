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
from kickai.utils.tool_validation import create_tool_response
from kickai.utils.tool_validation import create_tool_response
from kickai.utils.field_validation import FieldValidator, ValidationError


# Note: Pydantic schemas removed to avoid conflicts with CrewAI's automatic schema generation
# CrewAI will automatically generate schemas from function signatures


# Note: Parameter extraction logic removed - CrewAI handles parameter passing automatically


@tool("update_player_field", result_as_answer=True)
async def update_player_field(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    field: str,
    value: str
) -> str:
    """
    Update a single field for a player.

    This tool serves as the application boundary for player field updates.
    It handles framework concerns and delegates business logic to the domain service.
    
    Args:
        telegram_id: Player's Telegram ID or dictionary with all parameters
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat context
        field: Field name to update (phone, email, position, emergency_contact_name, etc.)
        value: New value for the field
        
    Returns:
        JSON formatted response with success status and details
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            field = params.get('field', '')
            value = params.get('value', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(
                        False, 
                        "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(
                False, 
                "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(
                False, 
                "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(
                False, 
                "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(
                False, 
                "Valid chat_type is required"
            )
            
        if not field or not isinstance(field, str):
            return create_tool_response(
                False, 
                "Valid field name is required"
            )
            
        if not value or not isinstance(value, str):
            return create_tool_response(
                False, 
                "Valid field value is required"
            )
        
        logger.info(f"🔄 Updating player field: {field} = '{value}' for {username} ({telegram_id}) in team {team_id}")

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
                return create_tool_response(
                    False, 
                    "System initialization error. Please try again."
                )
        
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            return create_tool_response(
                False, 
                "PlayerService is not available"
            )

        # Validate field value using utility (application layer validation)
        try:
            normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                field, value, 'player', current_user_is_admin=False
            )
            # Update the field and value with normalized/validated versions
            field = normalized_field
            value = validated_value
        except ValidationError as e:
            return create_tool_response(False, str(e))

        # Get player first, then update using existing service method
        player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
        
        if not player:
            return create_tool_response(
                False, 
                "Player not found. You may not be registered as a player."
            )
            
        # Create update dictionary for the field
        updates = {field: value}
        
        # Execute domain operation using existing update_player method
        try:
            updated_player = await player_service.update_player(player.player_id, team_id, **updates)
            success = updated_player is not None
        except Exception as e:
            return create_tool_response(
                False, 
                f"Failed to update {field}: {str(e)}"
            )
        
        if success:
            response_data = {
                "field": field,
                "new_value": value,
                "telegram_id": telegram_id,
                "team_id": team_id,
                "message": f"✅ Successfully updated {field} to '{value}'"
            }
            
            logger.info(f"✅ Player field {field} updated successfully for {username}")
            return create_tool_response(True, f"✅ Successfully updated {field} to '{value}'", response_data)
        else:
            return create_tool_response(
                False, 
                f"Failed to update {field}. Player may not exist or update failed."
            )

    except Exception as e:
        logger.error(f"❌ Error updating player field {field} for {username}: {e}")
        return create_tool_response(False, f"Failed to update {field}: {e}")


@tool("update_player_multiple_fields", result_as_answer=True)
async def update_player_multiple_fields(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    updates: Dict[str, str]
) -> str:
    """
    Update multiple fields for a player in a single operation.

    This tool serves as the application boundary for bulk player updates.
    It handles framework concerns and delegates business logic to the domain service.
    
    Args:
        telegram_id: Player's Telegram ID or dictionary with all parameters
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat context
        updates: Dictionary of field names to new values
        
    Returns:
        JSON formatted response with success status and details
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            updates = params.get('updates', {})
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(False, "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(False, "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(False, "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(False, "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(False, "Valid chat_type is required"
            )
        
        logger.info(f"🔄 Bulk update for {username} ({telegram_id}): {list(updates.keys()) if updates else 'No updates'}")
        
        # Validate inputs at application boundary
        if not updates or not isinstance(updates, dict):
            return create_tool_response(False, "Updates dictionary is required for bulk update"
            )

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            return create_tool_response(False, "PlayerService is not available"
            )

        # Validate all field values using utility (application layer validation)
        try:
            validated_updates = {}
            for field, value in updates.items():
                normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                    field, value, 'player', current_user_is_admin=False
                )
                validated_updates[normalized_field] = validated_value
            # Use validated updates
            updates = validated_updates
        except ValidationError as e:
            return create_tool_response(False, str(e))

        # Get player first, then update using existing service method
        player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
        
        if not player:
            return create_tool_response(False, "Player not found. You may not be registered as a player."
            )
            
        # Execute domain operation using existing update_player method
        try:
            updated_player = await player_service.update_player(player.player_id, team_id, **updates)
            success = updated_player is not None
        except Exception as e:
            return create_tool_response(False, f"Failed to update player fields: {str(e)}"
            )
        
        if success:
            response_data = {
                "updated_fields": updates,
                "telegram_id": telegram_id,
                "team_id": team_id,
                "field_count": len(updates),
                "message": f"✅ Successfully updated {len(updates)} fields: {', '.join(updates.keys())}"
            }
            
            logger.info(f"✅ Bulk update completed for {username}: {len(updates)} fields")
            return create_tool_response(True, "Operation completed successfully", data=response_data)
        else:
            return create_tool_response(False, "Failed to update player fields. Player may not exist or update failed."
            )

    except Exception as e:
        logger.error(f"❌ Error in bulk update for {username}: {e}")
        return create_tool_response(False, f"Failed to update player fields: {e}")


@tool("get_player_update_help", result_as_answer=True)
async def get_player_update_help(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get help information for player field updates.

    This tool serves as the application boundary for update help functionality.
    It provides guidance on available fields and update formats.
    
    Args:
        telegram_id: Player's Telegram ID or dictionary with all parameters
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat context
        
    Returns:
        JSON formatted help information for player updates
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(False, "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(False, "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(False, "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(False, "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(False, "Valid chat_type is required"
            )
        
        logger.info(f"📖 Update help requested by {username} ({telegram_id})")
        
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
        return create_tool_response(True, "Operation completed successfully", data=response_data)

    except Exception as e:
        logger.error(f"❌ Error providing update help to {username}: {e}")
        return create_tool_response(False, f"Failed to get update help: {e}")


@tool("get_player_current_info", result_as_answer=True)
async def get_player_current_info(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get the player's current information for review before updates.

    This tool serves as the application boundary for player info retrieval.
    It handles framework concerns and delegates business logic to the domain service.
    
    Args:
        telegram_id: Player's Telegram ID or dictionary with all parameters
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat context
        
    Returns:
        JSON formatted current player information
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_tool_response(False, "Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_tool_response(False, "Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_tool_response(False, "Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_tool_response(False, "Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_tool_response(False, "Valid chat_type is required"
            )
        
        logger.info(f"📋 Current info request from {username} ({telegram_id})")

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            return create_tool_response(False, "PlayerService is not available"
            )

        # Execute domain operation
        player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
        
        if not player:
            return create_tool_response(False, "Player not found. You may not be registered as a player."
            )

        # Format current information at application boundary
        current_info = f"""📋 YOUR CURRENT INFORMATION

👤 BASIC INFO:
• Name: {player.name or 'Not set'}
• Position: {player.position or 'Not set'}
• Status: {player.status.title() if hasattr(player.status, 'title') else str(player.status)}
• Player ID: {player.player_id or 'Not assigned'}

📞 CONTACT INFO:
• Phone: {getattr(player, 'phone_number', 'Not set')}
• Email: {getattr(player, 'email', 'Not set')}

🆘 EMERGENCY CONTACT:
• Name: {getattr(player, 'emergency_contact_name', 'Not set')}
• Phone: {getattr(player, 'emergency_contact_phone', 'Not set')}

🏥 MEDICAL NOTES:
{getattr(player, 'medical_notes', 'No medical notes recorded')}

💡 To update any field, just ask: "Update my [field] to [new value]" """

        response_data = {
            "current_info": current_info,
            "player_data": {
                "name": player.name,
                "position": player.position,
                "status": str(player.status),
                "player_id": player.player_id,
                "phone_number": getattr(player, 'phone_number', None),
                "email": getattr(player, 'email', None),
                "emergency_contact_name": getattr(player, 'emergency_contact_name', None),
                "emergency_contact_phone": getattr(player, 'emergency_contact_phone', None),
                "medical_notes": getattr(player, 'medical_notes', None)
            }
        }
        
        logger.info(f"✅ Current info provided to {username}")
        return create_tool_response(True, "Operation completed successfully", data=response_data)

    except Exception as e:
        logger.error(f"❌ Error getting current info for {username}: {e}")
        return create_tool_response(False, f"Failed to get current info: {e}")