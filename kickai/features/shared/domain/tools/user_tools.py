#!/usr/bin/env python3
"""
User Tools

This module provides tools for user management operations.
Converted to sync functions for CrewAI compatibility.
"""

import asyncio
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    create_json_response,
    extract_single_value,
    format_tool_error,
    format_tool_success,
    validate_required_input,
)


@tool("get_user_status")
def get_user_status(telegram_id: str, team_id: str) -> str:
    """
    Get user status and information. Requires: telegram_id, team_id

    Args:
        telegram_id: The user's Telegram ID (integer)
        team_id: Team ID (required)

    Returns:
        User status information or error message
    """
    try:
        # Handle JSON string input using utility functions
        telegram_id = extract_single_value(telegram_id, "telegram_id")
        team_id = extract_single_value(team_id, "team_id")

        # Validate inputs using utility functions
        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ Error: ", ""))

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response("error", message=validation_error.replace("❌ Error: ", ""))

        # Get services from container
        container = get_container()
        player_service = container.get_service("PlayerService")
        team_service = container.get_service("TeamService")

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        if not team_service:
            raise ServiceNotAvailableError("TeamService")

        # Convert telegram_id to integer
        try:
            telegram_id_int = int(telegram_id)
        except ValueError:
            return create_json_response("error", message=f"Invalid Telegram ID format: {telegram_id}. Must be an integer.")

        # Check if user is a player (sync call via asyncio.run)
        player = asyncio.run(player_service.get_player_by_telegram_id(telegram_id_int, team_id))
        
        # Check if user is a team member (sync call via asyncio.run)
        team_member = asyncio.run(team_service.get_team_member_by_telegram_id(team_id, telegram_id_int))

        if player:
            user_status_data = {
                "user_type": "Player",
                "telegram_id": telegram_id_int,
                "team_id": team_id,
                "name": player.name,
                "position": player.position,
                "status": player.status.title(),
                "formatted_message": f"👤 **User Status**: Player\n"
                                   f"📱 **Telegram ID**: {telegram_id_int}\n"
                                   f"🏆 **Team ID**: {team_id}\n"
                                   f"📋 **Player Info**: {player.name} ({player.position})\n"
                                   f"✅ **Status**: {player.status.title()}"
            }
            return create_json_response("success", data=user_status_data)
        elif team_member:
            user_status_data = {
                "user_type": "Team Member",
                "telegram_id": telegram_id_int,
                "team_id": team_id,
                "name": team_member.name,
                "role": team_member.role.title(),
                "is_admin": team_member.is_admin,
                "formatted_message": f"👤 **User Status**: Team Member\n"
                                   f"📱 **Telegram ID**: {telegram_id_int}\n"
                                   f"🏆 **Team ID**: {team_id}\n"
                                   f"📋 **Member Info**: {team_member.name}\n"
                                   f"👑 **Role**: {team_member.role.title()}\n"
                                   f"✅ **Admin**: {'Yes' if team_member.is_admin else 'No'}"
            }
            return create_json_response("success", data=user_status_data)
        else:
            user_status_data = {
                "user_type": "Not Registered",
                "telegram_id": telegram_id_int,
                "team_id": team_id,
                "formatted_message": f"👤 **User Status**: Not Registered\n"
                                   f"📱 **Telegram ID**: {telegram_id_int}\n"
                                   f"🏆 **Team ID**: {team_id}\n"
                                   f"ℹ️ **Info**: User is not registered as a player or team member"
            }
            return create_json_response("success", data=user_status_data)

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_user_status: {e}")
        return create_json_response("error", message=f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get user status: {e}", exc_info=True)
        return create_json_response("error", message=f"Failed to get user status: {e}")
