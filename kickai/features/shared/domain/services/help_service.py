#!/usr/bin/env python3
"""
Help Service

This service provides help functionality by interfacing with the CommandRegistry
and providing user-friendly help information.
"""

from typing import Any

from loguru import logger

from kickai.core.command_registry_initializer import get_initialized_command_registry


class HelpService:
    """Service for providing help and command information."""

    def __init__(self):
        self.command_registry = get_initialized_command_registry()

    def get_available_commands_sync(self, team_id: str, chat_type: str) -> list[dict[str, Any]]:
        """
        Get available commands for a specific chat type.


            team_id: Team ID (for context)
            chat_type: Chat type (main, leadership, private)


    :return: List of command dictionaries with name, description, etc.
    :rtype: str  # TODO: Fix type
        """
        try:
            # Normalize chat type
            if chat_type.lower() == "main":
                chat_type_filter = "main"
            elif chat_type.lower() == "leadership":
                chat_type_filter = "leadership"
            else:
                chat_type_filter = "private"

            # Get commands for this chat type
            commands = self.command_registry.get_commands_by_chat_type(chat_type_filter)

            # Convert to dict format expected by tools
            result = []
            for cmd in commands:
                result.append({
                    'name': cmd.name,
                    'description': cmd.description,
                    'feature': cmd.feature,
                    'permission_level': cmd.permission_level.value if cmd.permission_level else 'PUBLIC',
                    'examples': cmd.examples or [],
                    'help_text': cmd.help_text
                })

            logger.info(f"Retrieved {len(result)} commands for chat type '{chat_type}'")
            return result

        except Exception as e:
            logger.error(f"Failed to get available commands: {e}")
            return []

    def get_command_help_sync(self, command_name: str, team_id: str) -> dict[str, Any] | None:
        """
        Get detailed help for a specific command.


            command_name: Name of the command
            team_id: Team ID (for context)


    :return: Dictionary with detailed command help information
    :rtype: str  # TODO: Fix type
        """
        try:
            # Remove leading slash if present
            if command_name.startswith('/'):
                command_name = command_name[1:]

            # Get command metadata
            command = self.command_registry.get_command(command_name)

            if not command:
                logger.warning(f"Command '{command_name}' not found")
                return None

            # Generate help text
            help_text = self.command_registry.generate_help_text(command_name)

            result = {
                'name': command.name,
                'description': command.description,
                'usage': f"/{command.name}" + (" [parameters]" if command.parameters else ""),
                'examples': command.examples or [],
                'parameters': command.parameters or {},
                'feature': command.feature,
                'permission_level': command.permission_level.value if command.permission_level else 'PUBLIC',
                'help_text': help_text,
                'notes': command.help_text
            }

            logger.info(f"Retrieved help for command '{command_name}'")
            return result

        except Exception as e:
            logger.error(f"Failed to get command help for '{command_name}': {e}")
            return None

    def get_welcome_message_sync(self, telegram_id: int, chat_type: str, team_id: str) -> str:
        """
        Get a welcome message for new users.


            telegram_id: User's Telegram ID
            chat_type: Chat type (main, leadership, private)
            team_id: Team ID


    :return: Welcome message string
    :rtype: str  # TODO: Fix type
        """
        try:
            # Get available commands for context
            self.get_available_commands_sync(team_id, chat_type)

            # Build welcome message based on chat type
            if chat_type.lower() == "leadership":
                welcome_msg = """
🎉 **Welcome to KICKAI Leadership Chat!**

👋 Hello! I'm KICKAI, your AI-powered team management assistant.

🔧 **Leadership Features Available:**
• Team member management
• Match creation and squad selection
• Administrative commands
• Full system access

📋 **Quick Start:**
• Use `/help` to see all available commands
• Try `/list` to see team overview
• Use `/addmember` to add new team members

💪 **You have administrative privileges** in this chat!

⚽ Let's build something great together!
                """.strip()
            elif chat_type.lower() == "main":
                welcome_msg = """
🎉 **Welcome to KICKAI Team Chat!**

👋 Hello! I'm KICKAI, your AI-powered team management assistant.

⚽ **Main Features Available:**
• Match attendance tracking
• Team information
• Player status updates
• Match schedules

📋 **Quick Start:**
• Use `/help` to see available commands
• Try `/myinfo` to check your status
• Use `/attendance` to mark your availability

🤝 **Team Chat Features** are active here!

⚽ Ready to get started!
                """.strip()
            else:
                welcome_msg = """
🎉 **Welcome to KICKAI!**

👋 Hello! I'm KICKAI, your AI-powered team management assistant.

📱 **Private Chat Features:**
• Personal status checking
• Individual help and support
• Registration assistance

📋 **Getting Started:**
• Use `/help` to see what I can do
• Try `/myinfo` to check your registration status
• Ask me any questions about the team

💬 **Private chat** - just you and me!

⚽ How can I help you today?
                """.strip()

            logger.info(f"Generated welcome message for chat type '{chat_type}'")
            return welcome_msg

        except Exception as e:
            logger.error(f"Failed to generate welcome message: {e}")
            return """
🎉 **Welcome to KICKAI!**

👋 Hello! I'm KICKAI, your AI-powered team management assistant.

Use `/help` to see what I can do!

⚽ Ready to get started!
            """.strip()
