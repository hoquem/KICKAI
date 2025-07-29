"""
Command Help Service

Provides command-specific help and guidance to users.
"""

from typing import Any

from loguru import logger

from kickai.features.helper_system.domain.interfaces.command_help_service_interface import (
    ICommandHelpService,
)


class CommandHelpService(ICommandHelpService):
    """Service for providing command-specific help and guidance."""

    def __init__(self):
        # Command help content library
        self._command_help_content = self._initialize_command_help_content()

    async def get_command_help(self, command_name: str, user_level: str = "beginner") -> str:
        """
        Get contextual help for a command based on user level.

        Args:
            command_name: The command to get help for
            user_level: The user's experience level

        Returns:
            Formatted help content
        """
        try:
            # Get base help content
            help_content = self._command_help_content.get(command_name, {})
            if not help_content:
                return f"❌ No help content available for command '{command_name}'."

            # Build response based on user level
            response = f"📖 **Help for {command_name}**\n\n"

            # Add description
            description = help_content.get("description", "No description available")
            response += f"**Description**: {description}\n\n"

            # Add usage examples
            examples = help_content.get("examples", [])
            if examples:
                response += "**Examples**:\n"
                for example in examples:
                    response += f"• {example}\n"
                response += "\n"

            # Add level-specific tips
            tips = help_content.get("tips", {}).get(user_level, [])
            if tips:
                response += "**💡 Tips**:\n"
                for tip in tips:
                    response += f"• {tip}\n"
                response += "\n"

            # Add related commands
            related = help_content.get("related", [])
            if related:
                response += "**🔗 Related Commands**:\n"
                for cmd in related:
                    response += f"• {cmd}\n"

            return response

        except Exception as e:
            logger.error(f"Error getting command help for {command_name}: {e}")
            return f"❌ Sorry, I encountered an error while getting help for '{command_name}'."

    async def get_command_examples(self, command_name: str) -> list[str]:
        """
        Get examples for a specific command.

        Args:
            command_name: The command to get examples for

        Returns:
            List of command examples
        """
        try:
            help_content = self._command_help_content.get(command_name, {})
            return help_content.get("examples", [])
        except Exception as e:
            logger.error(f"Error getting command examples for {command_name}: {e}")
            return []

    async def get_command_tips(self, command_name: str, user_level: str) -> list[str]:
        """
        Get tips for a specific command based on user level.

        Args:
            command_name: The command to get tips for
            user_level: The user's experience level

        Returns:
            List of command tips
        """
        try:
            help_content = self._command_help_content.get(command_name, {})
            tips = help_content.get("tips", {})
            return tips.get(user_level, [])
        except Exception as e:
            logger.error(f"Error getting command tips for {command_name}: {e}")
            return []

    async def get_related_commands(self, command_name: str) -> list[str]:
        """
        Get related commands for a specific command.

        Args:
            command_name: The command to get related commands for

        Returns:
            List of related commands
        """
        try:
            help_content = self._command_help_content.get(command_name, {})
            return help_content.get("related", [])
        except Exception as e:
            logger.error(f"Error getting related commands for {command_name}: {e}")
            return []

    def _initialize_command_help_content(self) -> dict[str, Any]:
        """Initialize the command help content library."""
        return {
            "/addplayer": {
                "description": "Add a new player to the team",
                "examples": [
                    "/addplayer John Smith +447123456789 Forward",
                    "/addplayer Sarah Johnson +447987654321 Defender",
                ],
                "tips": {
                    "beginner": [
                        "Always include the player's position for better team management",
                        "Use the player's preferred name for easier identification",
                    ],
                    "intermediate": [
                        "Consider adding notes about player preferences",
                        "Use consistent naming conventions",
                    ],
                    "advanced": [
                        "Batch add multiple players for efficiency",
                        "Use player tags for better organization",
                    ],
                },
                "related": ["/list", "/status", "/update"],
            },
            "/list": {
                "description": "List all team members",
                "examples": ["/list", "/list --status active"],
                "tips": {
                    "beginner": [
                        "Use filters to find specific players quickly",
                        "Check the status column to see who's active",
                    ],
                    "intermediate": [
                        "Use sorting options for better organization",
                        "Export the list for external use",
                    ],
                    "advanced": [
                        "Create custom views for different purposes",
                        "Use advanced filtering options",
                    ],
                },
                "related": ["/status", "/addplayer", "/update"],
            },
            "/status": {
                "description": "Check player availability status",
                "examples": ["/status +447123456789", "/status MH"],
                "tips": {
                    "beginner": [
                        "You can search by phone number or player ID",
                        "Use this to quickly check player availability",
                    ],
                    "intermediate": [
                        "Set up status alerts for important players",
                        "Use status history for trend analysis",
                    ],
                    "advanced": [
                        "Integrate with calendar systems",
                        "Use status predictions based on patterns",
                    ],
                },
                "related": ["/list", "/addplayer", "/update"],
            },
        }
