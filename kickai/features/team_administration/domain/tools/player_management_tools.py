#!/usr/bin/env python3
"""
Player Management Tools for Team Administration

This module provides tools for player management by team administrators,
including adding new players with invite link generation.
"""

import asyncio
from datetime import datetime
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.constants import ERROR_MESSAGES, MAX_NAME_LENGTH, MAX_PHONE_LENGTH, MAX_TEAM_ID_LENGTH
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import format_tool_error, validate_required_input, create_json_response
from kickai.utils.validation_utils import normalize_phone, sanitize_input, is_valid_phone
from kickai.utils.id_generator import generate_member_id


@tool("add_player", result_as_answer=True)
def add_player(
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
            return create_json_response("error", message=f"❌ **Missing Information**\n\n💡 I need complete details to add a player:\n{'; '.join(validation_errors)}")

        # Validate chat type is leadership
        if chat_type.lower() != "leadership":
            return create_json_response("error", message="❌ **Permission Required**\n\n🔒 Adding players is a leadership function. Please use this command in the leadership chat.")

        # Sanitize inputs
        player_name = sanitize_input(player_name, MAX_NAME_LENGTH)
        phone_number = sanitize_input(phone_number, MAX_PHONE_LENGTH)
        team_id = sanitize_input(team_id, MAX_TEAM_ID_LENGTH)

        # Validate phone number format
        if not is_valid_phone(phone_number):
            return create_json_response("error", message=f"❌ **Invalid Phone Number**\n\n📱 Please use UK format:\n• +447123456789 (with country code)\n• 07123456789 (without country code)\n\n🔍 You provided: {phone_number}")

        # Normalize phone number
        normalized_phone = normalize_phone(phone_number)

        # Generate player ID
        player_id = generate_member_id(player_name)

        logger.info(f"🏃‍♂️ Adding player: {player_name} ({normalized_phone}) to team {team_id}")

        # Run async operations
        return asyncio.run(_add_player_async(
            player_id=player_id,
            player_name=player_name,
            phone_number=normalized_phone,
            team_id=team_id,
            admin_telegram_id=telegram_id,
            admin_username=username
        ))

    except Exception as e:
        logger.error(f"❌ Error in add_player tool: {e}")
        return create_json_response("error", message=f"❌ **System Error**\n\n🛠️ Failed to add player: {str(e)}\n\n💬 Please try again or contact your system administrator.")


async def _add_player_async(
    player_id: str,
    player_name: str,
    phone_number: str,
    team_id: str,
    admin_telegram_id: int,
    admin_username: str
) -> str:
    """
    Async implementation of add player functionality.
    
    Args:
        player_id: Generated player ID
        player_name: Player's full name
        phone_number: Normalized phone number
        team_id: Team ID
        admin_telegram_id: Admin's telegram ID
        admin_username: Admin's username
        
    Returns:
        Formatted response with invite link and instructions
    """
    try:
        # Get services from container
        container = get_container()
        database = container.get_database()
        
        # Check if phone number already exists
        existing_players = await database.query_documents(
            "kickai_players",
            [
                {"field": "phone_number", "operator": "==", "value": phone_number},
                {"field": "team_id", "operator": "==", "value": team_id}
            ]
        )
        
        if existing_players:
            existing_player = existing_players[0]
            return create_json_response(
                "error",
                message=f"❌ **Phone Number Already Registered**\n\n📱 {phone_number} is already used by: **{existing_player.get('player_name', 'Unknown')}**\n\n💡 Each player needs a unique phone number. Please check with the existing player or use a different number."
            )

        # Get team configuration for main chat ID
        team_config = await database.get_document("kickai_teams", team_id)
        if not team_config:
            return create_json_response(
                "error",
                message="❌ **Team Setup Issue**\n\n🔧 Team configuration not found. This shouldn't happen!\n\n💬 Please contact your system administrator to resolve this issue."
            )
        
        main_chat_id = team_config.get("main_chat_id")
        if not main_chat_id:
            return create_json_response(
                "error",
                message="❌ **Main Chat Not Configured**\n\n📱 Your team's main chat isn't set up yet.\n\n💬 Please contact your system administrator to configure the main chat for invite links."
            )

        team_name = team_config.get("team_name", f"Team {team_id}")

        # Create player record
        player_data = {
            "player_id": player_id,
            "player_name": player_name,
            "phone_number": phone_number,
            "team_id": team_id,
            "status": "pending_activation",
            "position": "",  # Will be set via /update command
            "created_at": datetime.now().isoformat(),
            "created_by": admin_telegram_id,
            "created_by_username": admin_username,
            "activated_at": None,
            "telegram_id": None  # Will be set when player joins via invite
        }

        # Save player record
        await database.set_document("kickai_players", player_id, player_data)
        logger.info(f"✅ Created player record: {player_id}")

        # Generate invite link using InviteLinkService
        from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
        
        # Get bot token from team config or environment
        bot_token = team_config.get("bot_token")
        invite_service = InviteLinkService(bot_token=bot_token, database=database)
        
        # Create player invite link
        invite_data = await invite_service.create_player_invite_link(
            team_id=team_id,
            player_name=player_name,
            player_phone=phone_number,
            player_position="",  # Empty initially
            main_chat_id=main_chat_id,
            player_id=player_id
        )

        invite_link = invite_data["invite_link"]
        expires_at = invite_data["expires_at"]
        
        logger.info(f"✅ Generated invite link for {player_name}: {invite_data['invite_id']}")

        # Format success response
        success_response = f"""✅ **Player Added Successfully!**

👤 **Player Details:**
• **Name:** {player_name}
• **Phone:** {phone_number}
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

        return create_json_response("success", data=success_response)

    except ImportError as e:
        logger.error(f"❌ Import error in add_player: {e}")
        return create_json_response(
            "error",
            message="❌ **System Component Unavailable**\n\n🔗 Invite link generation is temporarily unavailable.\n\n⏱️ Please try again in a moment, or contact your system administrator if the issue persists."
        )
    except ServiceNotAvailableError as e:
        logger.error(f"❌ Service not available in add_player: {e}")
        return create_json_response(
            "error",
            message="❌ **Service Temporarily Unavailable**\n\n⏱️ A required service is currently unavailable.\n\n🔄 Please try again in a few moments."
        )
    except Exception as e:
        logger.error(f"❌ Error in _add_player_async: {e}")
        return create_json_response(
            "error",
            message=f"❌ **System Error**\n\n🛠️ Something went wrong while adding the player.\n\n📝 Error details: {str(e)}\n\n💬 Please try again or contact your system administrator."
        )