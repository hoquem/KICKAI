#!/usr/bin/env python3
"""
User Tools

This module provides tools for user management operations.
Converted to sync functions for CrewAI compatibility.
"""

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


@tool("get_user_status", result_as_answer=True)
async def get_user_status(telegram_id: int, team_id: str, username: str, chat_type: str, target_name: str) -> str:
    """
    Get user status and information by name lookup.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required)
        username: Username of the requesting user
        chat_type: Chat type context
        target_name: Name of the user to look up

    Returns:
        User status information or error message
    """
    
    async def _async_get_user_status():
        """Internal async implementation."""
        try:
            # Handle JSON string input using utility functions
            telegram_id = extract_single_value(telegram_id, "telegram_id")
            team_id = extract_single_value(team_id, "team_id")

            # Validate inputs using utility functions
            validation_error = validate_required_input(telegram_id, "Telegram ID")
            if validation_error:
                return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ Error: ", ""))

            validation_error = validate_required_input(team_id, "Team ID")
            if validation_error:
                return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ Error: ", ""))

            # Get services from container
            container = get_container()
            player_service = container.get_service("PlayerService")
            team_service = container.get_service("TeamService")

            if not player_service:
                return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

            if not team_service:
                return create_json_response(ResponseStatus.ERROR, message="TeamService is not available")

            # Convert telegram_id to integer
            try:
                telegram_id_int = int(telegram_id)
            except ValueError:
                return create_json_response(ResponseStatus.ERROR, message=f"Invalid Telegram ID format: {telegram_id}. Must be an integer.")

            # Check if user is a player
            player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)
            
            # Check if user is a team member
            team_member = await team_service.get_team_member_by_telegram_id(team_id, telegram_id_int)

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
                return create_json_response(ResponseStatus.SUCCESS, data=user_status_data)
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
                return create_json_response(ResponseStatus.SUCCESS, data=user_status_data)
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
                return create_json_response(ResponseStatus.SUCCESS, data=user_status_data)

        except Exception as e:
            logger.error(f"❌ Error in get_user_status tool: {e}")
            return create_json_response(ResponseStatus.ERROR, message="Failed to get user status")
    
    # Bridge sync/async using asyncio.run() (CrewAI standard pattern)
    try:
        return asyncio.run(_async_get_user_status())
    except Exception as e:
        logger.error(f"❌ Async bridge error in get_user_status: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"System error: {str(e)}")
