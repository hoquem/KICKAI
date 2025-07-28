"""
Help tools for KICKAI system.

This module provides tools for help and command information.
"""

import logging
from typing import Optional

from kickai.utils.crewai_tool_decorator import tool
from pydantic import BaseModel

from kickai.core.command_registry_initializer import get_initialized_command_registry
from kickai.core.enums import ChatType, PermissionLevel

logger = logging.getLogger(__name__)


class GetAvailableCommandsInput(BaseModel):
    """Input model for get_available_commands tool."""

    chat_type: str
    user_id: Optional[str] = None
    team_id: Optional[str] = None


@tool("get_available_commands")
def get_available_commands(
    chat_type: str,
    user_id: Optional[str] = None,
    team_id: Optional[str] = None,
    is_registered: bool = None,
    is_player: bool = None,
    is_team_member: bool = None,
) -> str:
    """
    Get list of available commands for a user in the given chat type.

    Args:
        chat_type: The chat type ("main_chat" or "leadership_chat")
        user_id: Optional user ID for permission checking
        team_id: Optional team ID for context
        is_registered: Whether the user is registered in the system (REQUIRED - no default)
        is_player: Whether the user is a registered player (REQUIRED - no default)
        is_team_member: Whether the user is a team member (REQUIRED - no default)

    Returns:
        Formatted string with available commands
    """
    try:
        # Validate that user registration status is provided (no defaults allowed)
        if is_registered is None:
            return "❌ Error: is_registered parameter is required and must be explicitly set"
        if is_player is None:
            return "❌ Error: is_player parameter is required and must be explicitly set"
        if is_team_member is None:
            return "❌ Error: is_team_member parameter is required and must be explicitly set"

        logger.info(
            f"🔍 Getting available commands for chat_type={chat_type}, user_id={user_id}, team_id={team_id}, is_registered={is_registered}, is_player={is_player}, is_team_member={is_team_member}"
        )

        # Get the command registry
        registry = get_initialized_command_registry()

        # Convert chat_type string to enum
        chat_type_enum = None
        if chat_type == "main_chat":
            chat_type_enum = ChatType.MAIN
        elif chat_type == "leadership_chat":
            chat_type_enum = ChatType.LEADERSHIP
        else:
            return f"❌ Invalid chat type: {chat_type}. Must be 'main_chat' or 'leadership_chat'"

        # Get commands for this chat type
        commands = registry.get_commands_by_chat_type(chat_type)

        if not commands:
            return f"❌ No commands found for chat type: {chat_type}"

        # Filter commands based on user registration status
        available_commands = []

        for cmd in commands:
            # Always show public commands
            if cmd.permission_level == PermissionLevel.PUBLIC:
                available_commands.append(cmd)
            # Show player commands only if user is registered as player
            elif cmd.permission_level == PermissionLevel.PLAYER and is_player:
                available_commands.append(cmd)
            # Show leadership commands only if user is team member
            elif cmd.permission_level == PermissionLevel.LEADERSHIP and is_team_member:
                available_commands.append(cmd)
            # Show admin commands only if user is team member
            elif cmd.permission_level == PermissionLevel.ADMIN and is_team_member:
                available_commands.append(cmd)

        # Group filtered commands by permission level
        public_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PUBLIC
        ]
        player_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PLAYER
        ]
        leadership_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.LEADERSHIP
        ]
        admin_commands = [
            cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.ADMIN
        ]

        # Build response
        response = f"📋 Available Commands for {chat_type.replace('_', ' ').title()}\n\n"

        if public_commands:
            response += "🌐 Public Commands (Available to everyone):\n"
            for cmd in public_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        if player_commands:
            response += "👤 Player Commands (Available to registered players):\n"
            for cmd in player_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        if leadership_commands:
            response += "👔 Leadership Commands (Available to team leadership):\n"
            for cmd in leadership_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        if admin_commands:
            response += "🔧 Admin Commands (Available to team admins):\n"
            for cmd in admin_commands:
                response += f"• {cmd.name} - {cmd.description}\n"
            response += "\n"

        # Add registration guidance for unregistered users
        if not is_registered:
            if chat_type == "main_chat":
                response += "📞 **To access more commands, contact team leadership to be added as a player.**\n\n"
            elif chat_type == "leadership_chat":
                response += (
                    "📝 **To access more commands, use /register to become a team member.**\n\n"
                )

        response += "💡 Tip: You can also ask me questions in natural language!"

        logger.info(
            f"✅ Retrieved {len(available_commands)} commands for {chat_type} (filtered from {len(commands)} total)"
        )
        return response

    except Exception as e:
        logger.error(f"❌ Error getting available commands: {e}")
        return f"❌ Error retrieving available commands: {e!s}"
