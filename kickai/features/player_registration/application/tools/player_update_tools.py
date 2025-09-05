#!/usr/bin/env python3
"""
Player Update Tools - Clean Architecture Application Layer

This module provides CrewAI tools for player information updates.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

import json

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.utils.field_validation import FieldValidator, ValidationError
from kickai.utils.native_crewai_helpers import convert_telegram_id, validate_required_strings


@tool("update_player_field")
async def update_player_field(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str, field: str, value: str
) -> str:
    """
    Modify specific player profile attribute.

    Validates and updates individual profile fields for registered players,
    ensuring data integrity and business rule compliance.

    Use when: Player profile information needs correction or update
    Required: Player registration status
    Context: Player profile management workflow

    Returns: Field modification confirmation
    """
    try:
        # Convert telegram_id using helper function
        telegram_id_int = convert_telegram_id(telegram_id)
        if not telegram_id_int:
            return "❌ Invalid telegram_id format"

        # Validate required parameters
        validation_error = validate_required_strings(
            team_id,
            telegram_username,
            chat_type,
            field,
            value,
            names=["team_id", "telegram_username", "chat_type", "field", "value"],
        )
        if validation_error:
            return validation_error

        logger.info(
            f"🔄 Updating player field: {field} = '{value}' for {telegram_username} ({telegram_id_int}) in team {team_id}"
        )

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            logger.error("PlayerService not available from container")
            return "❌ Player service is not available. Please try again later."

        # Validate field value using utility (application layer validation)
        try:
            normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                field, value, "player", current_user_is_admin=False
            )
            # Update the field and value with normalized/validated versions
            field = normalized_field
            value = validated_value
        except ValidationError as e:
            return f"❌ {e!s}"

        # Get player first, then update using existing service method
        player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)

        if not player:
            return "❌ Player not found. You may not be registered as a player."

        # Create update dictionary for the field
        updates = {field: value}

        # Execute domain operation using existing update_player method
        try:
            updated_player = await player_service.update_player(
                player.player_id, team_id, **updates
            )
            success = updated_player is not None
        except Exception as e:
            return f"❌ Failed to update {field}: {e!s}"

        if success:
            logger.info(f"✅ Player field {field} updated successfully for {telegram_username}")
            return f"✅ Successfully updated {field} to '{value}'"
        else:
            return f"❌ Failed to update {field}. Player may not exist or update failed."

    except Exception as e:
        logger.error(f"❌ Error updating player field {field} for {telegram_username}: {e}")
        return f"❌ Failed to update {field}: {e}"


@tool("update_player_multiple_fields")
async def update_player_multiple_fields(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str, updates: str
) -> str:
    """
    Modify multiple player profile attributes simultaneously.

    Executes batch updates for player profile fields in single transaction,
    maintaining data consistency and reducing processing overhead.

    Use when: Comprehensive profile update is required
    Required: Player registration status
    Context: Bulk profile management workflow

    Returns: Batch modification confirmation
    """
    try:
        # Convert telegram_id using helper function
        telegram_id_int = convert_telegram_id(telegram_id)
        if not telegram_id_int:
            return "❌ Invalid telegram_id format"

        # Validate required parameters
        validation_error = validate_required_strings(
            team_id,
            telegram_username,
            chat_type,
            updates,
            names=["team_id", "telegram_username", "chat_type", "updates"],
        )
        if validation_error:
            return validation_error

        # Parse updates JSON string
        try:
            updates_dict = json.loads(updates)
            if not isinstance(updates_dict, dict):
                return "❌ Updates must be a valid JSON object"
        except (json.JSONDecodeError, TypeError):
            return "❌ Invalid updates format. Please provide valid JSON"

        logger.info(
            f"🔄 Bulk update for {telegram_username} ({telegram_id_int}): {list(updates_dict.keys()) if updates_dict else 'No updates'}"
        )

        # Validate inputs at application boundary
        if not updates_dict or not isinstance(updates_dict, dict):
            return "❌ Updates dictionary is required for bulk update"

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            logger.error("PlayerService not available from container")
            return "❌ Player service is not available. Please try again later."

        # Validate all field values using utility (application layer validation)
        try:
            validated_updates = {}
            for field, value in updates_dict.items():
                normalized_field, validated_value = FieldValidator.validate_field_for_entity(
                    field, value, "player", current_user_is_admin=False
                )
                validated_updates[normalized_field] = validated_value
            # Use validated updates
            updates_dict = validated_updates
        except ValidationError as e:
            return f"❌ {e!s}"

        # Get player first, then update using existing service method
        player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)

        if not player:
            return "❌ Player not found. You may not be registered as a player."

        # Execute domain operation using existing update_player method
        try:
            updated_player = await player_service.update_player(
                player.player_id, team_id, **updates_dict
            )
            success = updated_player is not None
        except Exception as e:
            return f"❌ Failed to update player fields: {e!s}"

        if success:
            logger.info(
                f"✅ Bulk update completed for {telegram_username}: {len(updates_dict)} fields"
            )
            # Create formatted success message
            success_message = f"✅ Successfully updated {len(updates_dict)} fields\n"
            for field, value in updates_dict.items():
                success_message += f"   • {field}: {value}\n"
            return success_message.strip()
        else:
            return "❌ Failed to update player fields. Player may not exist or update failed."

    except Exception as e:
        logger.error(f"❌ Error in bulk update for {telegram_username}: {e}")
        return f"❌ Failed to update player fields: {e}"


@tool("get_player_update_help")
async def get_player_update_help(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str
) -> str:
    """
    Provide guidance for player profile modification operations.

    Delivers comprehensive instructions for valid field updates, business rules,
    and available modification options for player profile management.

    Use when: Player profile update guidance is needed
    Required: Player registration status
    Context: Player self-service workflow

    Returns: Profile modification guidance summary
    """
    try:
        # Convert telegram_id
        telegram_id_int = convert_telegram_id(telegram_id)
        if not telegram_id_int:
            return "❌ Invalid telegram_id format"

        logger.info(f"📖 Update help requested by {telegram_username} ({telegram_id_int})")

        # Use FieldValidator for dynamic help content generation
        help_content = FieldValidator.create_help_message("player", current_user_is_admin=False)

        logger.info(f"✅ Update help provided to {telegram_username}")
        return help_content

    except Exception as e:
        logger.error(f"❌ Error providing update help to {telegram_username}: {e}")
        return f"❌ Failed to get update help: {e}"
