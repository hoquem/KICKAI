#!/usr/bin/env python3
"""
Message Formatting Service for KICKAI

This service provides a centralized framework for formatting all bot responses
with consistent styling, emojis, and structure. It ensures all messages follow
the same design patterns and are properly formatted for Telegram.
"""

from dataclasses import dataclass
from typing import Any

from loguru import logger

from core.enums import ChatType


@dataclass
class MessageContext:
    """Context for message formatting."""
    user_id: str
    team_id: str
    chat_type: ChatType
    user_name: str | None = None
    is_player: bool = False
    is_team_member: bool = False
    is_admin: bool = False


class MessageFormattingService:
    """
    Centralized service for formatting all bot messages.
    
    This service provides:
    - Consistent emoji usage
    - Standardized formatting patterns
    - Chat-type aware formatting
    - User context integration
    """

    def __init__(self):
        """Initialize the message formatting service."""
        logger.info("✅ MessageFormattingService initialized")

    def format_help_message(self, context: MessageContext, commands_info: dict[str, Any]) -> str:
        """Format help message based on chat type and user context."""
        if context.chat_type == ChatType.LEADERSHIP:
            return self._format_leadership_help(commands_info)
        else:
            return self._format_main_chat_help(commands_info)

    def format_welcome_message(self, context: MessageContext) -> str:
        """Format welcome message based on user context."""
        if context.chat_type == ChatType.LEADERSHIP:
            return self._format_leadership_welcome(context)
        else:
            return self._format_main_chat_welcome(context)

    def format_error_message(self, error: str, context: MessageContext | None = None) -> str:
        """Format error message with consistent styling."""
        return f"❌ Error: {error}\n\nPlease try again or contact support if the issue persists."

    def format_success_message(self, message: str, context: MessageContext | None = None) -> str:
        """Format success message with consistent styling."""
        return f"✅ Success: {message}"

    def format_info_message(self, message: str, context: MessageContext | None = None) -> str:
        """Format informational message with consistent styling."""
        return f"ℹ️ Info: {message}"

    def format_player_list(self, players: list[dict[str, Any]], context: MessageContext) -> str:
        """Format player list with consistent styling."""
        if not players:
            return "📋 No players found"

        lines = ["📋 Team Players\n"]

        for player in players:
            status_emoji = "🟢" if player.get("is_active", True) else "🔴"
            name = player.get("name", "Unknown")
            position = player.get("position", "Unknown")
            phone = player.get("phone", "No phone")

            lines.append(f"{status_emoji} {name} ({position})")
            lines.append(f"   📱 {phone}")
            lines.append("")

        return "\n".join(lines)

    def format_team_member_list(self, members: list[dict[str, Any]], context: MessageContext) -> str:
        """Format team member list with consistent styling."""
        if not members:
            return "👥 No team members found"

        lines = ["👥 Team Members\n"]

        for member in members:
            role_emoji = "👑" if member.get("is_admin", False) else "👤"
            name = member.get("name", "Unknown")
            role = member.get("role", "Member")

            lines.append(f"{role_emoji} {name} - {role}")
            lines.append("")

        return "\n".join(lines)

    def format_user_info(self, user_data: dict[str, Any], context: MessageContext) -> str:
        """Format user information display."""
        if context.is_player:
            return self._format_player_info(user_data)
        elif context.is_team_member:
            return self._format_team_member_info(user_data)
        else:
            return "👤 User Information\n\nYou are not registered yet. Contact team leadership to be added to the team."

    def _format_leadership_help(self, commands_info: dict[str, Any]) -> str:
        """Format help message for leadership chat."""
        lines = ["👔 KICKAI Leadership Commands\n"]

        # Shared Commands
        lines.append("Shared Commands:")
        for cmd in commands_info.get("features", {}).get("shared", []):
            lines.append(f"• {cmd['name']} - {cmd['description']}")

        # Player Registration Commands
        lines.append("\nPlayer Management:")
        for cmd in commands_info.get("features", {}).get("player_registration", []):
            lines.append(f"• {cmd['name']} - {cmd['description']}")

        # Communication Commands
        lines.append("\nCommunication:")
        for cmd in commands_info.get("features", {}).get("communication", []):
            lines.append(f"• {cmd['name']} - {cmd['description']}")

        lines.append("\n💡 Use /help [command] for detailed information on specific commands.")

        return "\n".join(lines)

    def _format_main_chat_help(self, commands_info: dict[str, Any]) -> str:
        """Format help message for main chat."""
        lines = ["🤖 KICKAI Commands\n"]

        # General Commands
        lines.append("General Commands:")
        for cmd in commands_info.get("features", {}).get("shared", []):
            lines.append(f"• {cmd['name']} - {cmd['description']}")

        # Player Commands
        lines.append("\nPlayer Commands:")
        for cmd in commands_info.get("features", {}).get("player_registration", []):
            lines.append(f"• {cmd['name']} - {cmd['description']}")

        # Leadership Commands (for reference)
        lines.append("\nLeadership Commands (available in leadership chat):")
        leadership_commands = [
            ("/addplayer", "Add a new player with invite link"),
            ("/addmember", "Add a new team member with invite link"),
            ("/approve", "Approve a player for team participation"),
            ("/reject", "Reject a player with reason"),
            ("/pending", "List players awaiting approval"),
            ("/announce", "Make an announcement to the team"),
            ("/remind", "Send a reminder to team members"),
            ("/broadcast", "Broadcast message to all team chats")
        ]
        for cmd_name, cmd_desc in leadership_commands:
            lines.append(f"• {cmd_name} - {cmd_desc}")

        lines.append("\n💡 Use /help [command] for detailed help on specific commands.")

        return "\n".join(lines)

    def _format_leadership_welcome(self, context: MessageContext) -> str:
        """Format welcome message for leadership chat."""
        return (
            "👔 Welcome to KICKAI Leadership!\n\n"
            "🤖 I'm your AI-powered team management assistant.\n"
            "• Manage players and team operations\n"
            "• Send announcements and reminders\n"
            "• Monitor team performance\n\n"
            "Use /help to see all available commands.\n"
            "Let's build a winning team! 🏆"
        )

    def _format_main_chat_welcome(self, context: MessageContext) -> str:
        """Format welcome message for main chat."""
        return (
            "🤖 Welcome to KICKAI!\n\n"
            "I'm your AI-powered football team assistant.\n"
            "• Register as a player\n"
            "• Check team information\n"
            "• Stay updated on matches\n\n"
            "Use /help to see what you can do!\n"
            "Let's kick off a smarter season! ⚽️"
        )

    def _format_player_info(self, player_data: dict[str, Any]) -> str:
        """Format player information display."""
        name = player_data.get("name", "Unknown")
        position = player_data.get("position", "Unknown")
        phone = player_data.get("phone", "No phone")
        is_active = player_data.get("is_active", True)

        status_emoji = "🟢" if is_active else "🔴"
        status_text = "Active" if is_active else "Inactive"

        return (
            f"👤 Player Information\n\n"
            f"Name: {name}\n"
            f"Position: {position}\n"
            f"Phone: {phone}\n"
            f"Status: {status_emoji} {status_text}\n\n"
            f"Use /help to see available commands!"
        )

    def _format_team_member_info(self, member_data: dict[str, Any]) -> str:
        """Format team member information display."""
        name = member_data.get("name", "Unknown")
        role = member_data.get("role", "Member")
        is_admin = member_data.get("is_admin", False)

        role_emoji = "👑" if is_admin else "👤"

        return (
            f"👔 Team Member Information\n\n"
            f"Name: {name}\n"
            f"Role: {role_emoji} {role}\n"
            f"Admin: {'Yes' if is_admin else 'No'}\n\n"
            f"Use /help to see leadership commands!"
        )


def get_message_formatting_service() -> MessageFormattingService:
    """Get the message formatting service instance."""
    return MessageFormattingService()
