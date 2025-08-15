#!/usr/bin/env python3
"""
Player Management Tools for Team Administration

This module provides tools for player management by team administrators,
including adding new players with invite link generation.
"""

from datetime import datetime
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ChatType, ResponseStatus, UserStatus
from kickai.core.exceptions import ServiceNotAvailableError, TeamNotFoundError, TeamNotConfiguredError
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.utils.constants import ERROR_MESSAGES, MAX_NAME_LENGTH, MAX_PHONE_LENGTH, MAX_TEAM_ID_LENGTH
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import format_tool_error, validate_required_input, create_json_response
from kickai.utils.validation_utils import normalize_phone, sanitize_input, is_valid_phone
from kickai.utils.id_generator import generate_member_id


@tool("add_player", result_as_answer=True)
async def add_player(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_name: str,
    phone_number: str
) -> str:
    """
    Add a new player to the team and generate invite link for them to join the main chat.

    Args:
        telegram_id: Admin's telegram ID (required, from context)
        team_id: Team ID (required, from context)
        username: Admin's username (required, from context)
        chat_type: Chat type (required, from context)
        player_name: Full name of the player (required)
        phone_number: Player's phone number in UK format (required)

    Returns:
        Formatted response with player details, invite link, and instructions
    """
    try:
        # Validate required inputs
        validations = [
            validate_required_input(player_name, "player_name"),
            validate_required_input(phone_number, "phone_number"),
            validate_required_input(team_id, "team_id"),
            validate_required_input(telegram_id, "telegram_id"),
            validate_required_input(username, "username"),
            validate_required_input(chat_type, "chat_type"),
        ]
        
        validation_errors = [error for error in validations if error]
        if validation_errors:
            return create_json_response(ResponseStatus.ERROR, message=f"❌ **Missing Information**\n\n💡 I need complete details to add a player:\n{'; '.join(validation_errors)}")

        # Validate chat type is leadership
        if chat_type.lower() != ChatType.LEADERSHIP.value:
            return create_json_response(ResponseStatus.ERROR, message="❌ **Permission Required**\n\n🔒 Adding players is a leadership function. Please use this command in the leadership chat.")

        # Sanitize inputs
        player_name = sanitize_input(player_name, MAX_NAME_LENGTH)
        phone_number = sanitize_input(phone_number, MAX_PHONE_LENGTH)
        team_id = sanitize_input(team_id, MAX_TEAM_ID_LENGTH)

        # Validate phone number format
        if not is_valid_phone(phone_number):
            return create_json_response(ResponseStatus.ERROR, message=f"❌ **Invalid Phone Number**\n\n📱 Please use UK format:\n• +447123456789 (with country code)\n• 07123456789 (without country code)\n\n🔍 You provided: {phone_number}")

        # Normalize phone number
        normalized_phone = normalize_phone(phone_number)

        # Generate player ID
        player_id = generate_member_id(player_name)

        logger.info(f"🏃‍♂️ Adding player: {player_name} ({normalized_phone}) to team {team_id}")

        # Get services from container
        container = get_container()
        if not container:
            raise ServiceNotAvailableError("Dependency container not available")
            
        team_service = container.get_service(TeamService)
        if not team_service:
            raise ServiceNotAvailableError("Team service not available")
            
        player_service = container.get_service(PlayerService)
        if not player_service:
            raise ServiceNotAvailableError("Player service not available")
        
        # Check if phone number already exists using domain service
        existing_player = await player_service.get_player_by_phone(normalized_phone, team_id)
        if existing_player:
            return create_json_response(
                ResponseStatus.ERROR,
                message=f"❌ **Phone Number Already Registered**\n\n📱 {normalized_phone} is already used by: **{existing_player.player_name}**\n\n💡 Each player needs a unique phone number. Please check with the existing player or use a different number."
            )

        # Get team using domain service  
        team = await team_service.get_team(team_id=team_id)
        if not team:
            raise TeamNotFoundError(f"Team not found for team_id: {team_id}")
        
        if not team.main_chat_id:
            raise TeamNotConfiguredError("Main chat not configured for invite links")

        team_name = team.name or f"Team {team_id}"

        # Create player using domain service
        from kickai.features.player_registration.domain.entities.player import Player
        
        player = Player(
            player_id=player_id,
            player_name=player_name,
            phone_number=normalized_phone,
            team_id=team_id,
            status=UserStatus.PENDING,
            position="",  # Will be set via /update command
            created_by_telegram_id=telegram_id,
            created_by_username=username
        )
        
        # Save player using service layer
        created_player = await player_service.create_player(player)
        logger.info(f"✅ Created player record: {created_player.player_id}")

        # Generate invite link using InviteLinkService  
        database = container.get_database()  # Get database for invite service
        invite_service = InviteLinkService(bot_token=team.bot_token, database=database)
        
        # Create player invite link
        invite_data = await invite_service.create_player_invite_link(
            team_id=team_id,
            player_name=player_name,
            player_phone=normalized_phone,
            player_position="",  # Empty initially
            main_chat_id=team.main_chat_id,
            player_id=player_id
        )

        invite_link = invite_data["invite_link"]
        expires_at = invite_data["expires_at"]
        
        logger.info(f"✅ Generated invite link for {player_name}: {invite_data['invite_id']}")

        # Format success response
        success_response = f"""✅ **Player Added Successfully!**

👤 **Player Details:**
• **Name:** {player_name}
• **Phone:** {normalized_phone}
• **Status:** Pending Activation

📱 **Send this message to {player_name}:**
"Hi {player_name}! You've been added to {team_name}. Click this link to join our main chat: {invite_link}"

🔗 **Invite Link:** {invite_link}
⏰ **Expires:** {expires_at}
🔄 **Usage:** One-time use only

📋 **Next Steps:**
1. Send the invite link to {player_name}
2. Player joins main chat via link
3. Player uses /update to set position and details
4. Player is ready to participate!"""

        return create_json_response(ResponseStatus.SUCCESS, data=success_response)

    except Exception as e:
        logger.error(f"❌ Error in add_player tool: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"❌ **System Error**\n\n🛠️ Failed to add player: {str(e)}\n\n💬 Please try again or contact your system administrator.")

