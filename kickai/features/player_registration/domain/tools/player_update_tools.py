#!/usr/bin/env python3
"""
Player Update Tools

This module provides CrewAI tools for players to update their personal information.
These tools include field validation and bidirectional sync with linked TeamMember records.
"""

from typing import Dict, Any
from loguru import logger
from crewai.tools import tool

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response
from kickai.utils.field_validation import FieldValidator, ValidationError
from kickai.features.shared.domain.services.linked_record_sync_service import linked_record_sync_service


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
    
    Args:
        telegram_id: Player's Telegram ID
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat (should be 'main' for players)
        field: Field name to update (phone, email, position, emergency_contact_name, etc.)
        value: New value for the field
        
    Returns:
        JSON response with success status and details
    """
    try:
        logger.info(f"🔄 Updating player field: {field} for telegram_id: {telegram_id}")
        
        # Get player service
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
        player_service = container.get_service(IPlayerService)
        if not player_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Player service not available"
            )
        
        # Find the player
        players = await player_service.get_players_by_telegram_id(telegram_id, team_id)
        if not players:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Player not found. Please register first using /register."
            )
        
        player = players[0]  # Get the first (should be only) player
        logger.info(f"📋 Updating player {player.player_id} field: {field}")
        
        # Validate the field and value
        try:
            normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                field, value, 'player'
            )
        except ValidationError as e:
            logger.warning(f"❌ Validation error for field {field}: {e}")
            return create_json_response(
                ResponseStatus.ERROR,
                message=str(e)
            )
        
        # Update the player field
        old_value = getattr(player, normalized_field, None)
        setattr(player, normalized_field, validated_value)
        
        # Save the updated player
        updated_player = await player_service.update_player(player)
        
        logger.info(f"✅ Successfully updated player field {normalized_field}")
        
        # Sync with linked TeamMember record
        sync_result = await linked_record_sync_service.sync_player_to_team_member(
            telegram_id, {normalized_field: validated_value}
        )
        
        # Create success response
        response_data = {
            'player_id': updated_player.player_id,
            'field': normalized_field,
            'old_value': old_value,
            'new_value': validated_value,
            'sync_summary': linked_record_sync_service.create_sync_summary(
                sync_result, 'player', 'team_member'
            )
        }
        
        return create_json_response(
            ResponseStatus.SUCCESS,
            message=f"Updated {normalized_field} successfully",
            data=response_data
        )
        
    except (RuntimeError, AttributeError, KeyError, ValueError) as e:
        from kickai.features.player_registration.domain.exceptions import PlayerUpdateError
        logger.error(f"❌ Error updating player field: {e}")
        update_error = PlayerUpdateError(str(telegram_id), field, str(e))
        return create_json_response(
            ResponseStatus.ERROR,
            message=f"Failed to update field: {update_error.message}"
        )


@tool("update_player_multiple_fields", result_as_answer=True)
async def update_player_multiple_fields(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    field_updates: Dict[str, Any]
) -> str:
    """
    Update multiple fields for a player in a single operation.
    
    Args:
        telegram_id: Player's Telegram ID
        team_id: Team identifier  
        username: Player's username
        chat_type: Type of chat (should be 'main' for players)
        field_updates: Dictionary of field names to new values
        
    Returns:
        JSON response with success status and details
    """
    try:
        logger.info(f"🔄 Updating multiple player fields for telegram_id: {telegram_id}")
        logger.info(f"📝 Fields to update: {list(field_updates.keys())}")
        
        # Get player service
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
        player_service = container.get_service(IPlayerService)
        if not player_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Player service not available"
            )
        
        # Find the player
        players = await player_service.get_players_by_telegram_id(telegram_id, team_id)
        if not players:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Player not found. Please register first using /register."
            )
        
        player = players[0]
        logger.info(f"📋 Updating player {player.player_id} with {len(field_updates)} fields")
        
        # Validate all fields first
        validated_updates = {}
        validation_errors = []
        
        for field, value in field_updates.items():
            try:
                normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                    field, str(value), 'player'
                )
                validated_updates[normalized_field] = validated_value
            except ValidationError as e:
                validation_errors.append(f"{field}: {str(e)}")
        
        # If there are validation errors, return them
        if validation_errors:
            logger.warning(f"❌ Validation errors: {validation_errors}")
            return create_json_response(
                ResponseStatus.ERROR,
                message="Field validation failed",
                data={'validation_errors': validation_errors}
            )
        
        # Update all validated fields
        updated_fields = {}
        for normalized_field, validated_value in validated_updates.items():
            old_value = getattr(player, normalized_field, None)
            setattr(player, normalized_field, validated_value)
            updated_fields[normalized_field] = {
                'old_value': old_value,
                'new_value': validated_value
            }
        
        # Save the updated player
        updated_player = await player_service.update_player(player)
        
        logger.info(f"✅ Successfully updated {len(validated_updates)} player fields")
        
        # Sync with linked TeamMember record
        sync_result = await linked_record_sync_service.sync_player_to_team_member(
            telegram_id, validated_updates
        )
        
        # Create success response
        response_data = {
            'player_id': updated_player.player_id,
            'updated_fields': updated_fields,
            'sync_summary': linked_record_sync_service.create_sync_summary(
                sync_result, 'player', 'team_member'
            )
        }
        
        return create_json_response(
            ResponseStatus.SUCCESS,
            message=f"Updated {len(validated_updates)} fields successfully",
            data=response_data
        )
        
    except (RuntimeError, AttributeError, KeyError, ValueError) as e:
        from kickai.features.player_registration.domain.exceptions import PlayerUpdateError
        logger.error(f"❌ Error updating multiple player fields: {e}")
        update_error = PlayerUpdateError(str(telegram_id), "multiple_fields", str(e))
        return create_json_response(
            ResponseStatus.ERROR,
            message=f"Failed to update fields: {update_error.message}"
        )


@tool("get_player_update_help", result_as_answer=True)
async def get_player_update_help(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get help information about available player update fields.
    
    Args:
        telegram_id: Player's Telegram ID
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat
        
    Returns:
        JSON response with help information
    """
    try:
        logger.info(f"📖 Getting player update help for telegram_id: {telegram_id}")
        
        # Generate help message
        help_message = FieldValidator.create_help_message('player')
        
        # Add usage examples
        examples = [
            "/update phone +447123456789",
            "/update email newplayer@team.com",
            "/update position midfielder",
            "/update emergency_contact_name \"John Smith\"",
            "/update medical_notes \"Allergic to peanuts\""
        ]
        
        help_message += "\n\n📚 **Usage Examples:**\n"
        for example in examples:
            help_message += f"• `{example}`\n"
        
        help_message += "\n💡 **Tips:**\n"
        help_message += "• Use quotes around values with spaces\n"
        help_message += "• Phone numbers can be in UK format: +447XXXXXXXXX or 07XXXXXXXXX\n"
        help_message += "• Changes to common fields (phone, email, emergency contact) will also update your team member record if linked\n"
        
        return create_json_response(
            ResponseStatus.SUCCESS,
            message="Player update help",
            data={'help_text': help_message}
        )
        
    except (RuntimeError, AttributeError, KeyError) as e:
        from kickai.features.shared.domain.exceptions import HelpSystemError
        logger.error(f"❌ Error getting player update help: {e}")
        help_error = HelpSystemError(str(telegram_id), str(e))
        return create_json_response(
            ResponseStatus.ERROR,
            message=f"Failed to get help information: {help_error.message}"
        )


@tool("get_player_current_info", result_as_answer=True)
async def get_player_current_info(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get current player information before making updates.
    
    Args:
        telegram_id: Player's Telegram ID
        team_id: Team identifier
        username: Player's username
        chat_type: Type of chat
        
    Returns:
        JSON response with current player information
    """
    try:
        logger.info(f"📋 Getting current player info for telegram_id: {telegram_id}")
        
        # Get player service
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
        player_service = container.get_service(IPlayerService)
        if not player_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Player service not available"
            )
        
        # Find the player
        players = await player_service.get_players_by_telegram_id(telegram_id, team_id)
        if not players:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Player not found. Please register first using /register."
            )
        
        player = players[0]
        logger.info(f"📋 Retrieved info for player {player.player_id}")
        
        # Create safe info dictionary (excluding sensitive data)
        player_info = {
            'player_id': player.player_id,
            'name': player.name,
            'phone_number': player.phone_number,
            'email': player.email,
            'position': player.position,
            'emergency_contact_name': getattr(player, 'emergency_contact_name', 'Not set'),
            'emergency_contact_phone': getattr(player, 'emergency_contact_phone', 'Not set'),
            'medical_notes': getattr(player, 'medical_notes', 'Not set'),
            'team_id': player.team_id,
            'status': player.status
        }
        
        return create_json_response(
            ResponseStatus.SUCCESS,
            message="Current player information",
            data={'player_info': player_info}
        )
        
    except (RuntimeError, AttributeError, KeyError, ValueError) as e:
        from kickai.features.player_registration.domain.exceptions import PlayerLookupError
        logger.error(f"❌ Error getting player current info: {e}")
        lookup_error = PlayerLookupError(str(telegram_id), team_id, str(e))
        return create_json_response(
            ResponseStatus.ERROR,
            message=f"Failed to get player information: {lookup_error.message}"
        )