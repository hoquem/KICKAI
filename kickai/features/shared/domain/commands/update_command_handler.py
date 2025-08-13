#!/usr/bin/env python3
"""
Update Command Handler for KICKAI System

This module provides context-aware routing for the /update command to the appropriate agent
based on chat type. Players in main chat update player info, team members in leadership
chat update team member info.
"""

import logging
from typing import Any

from kickai.core.enums import ChatType
from kickai.features.shared.domain.services.command_processing_service import (
    CommandResponse,
    UserContext,
)

logger = logging.getLogger(__name__)


class UpdateCommandHandler:
    """Context-aware handler for /update commands."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def handle_update_command(
        self, user_context: UserContext, command_args: list[str], crewai_system: Any = None
    ) -> CommandResponse:
        """
        Handle /update command with context-aware routing.

        Args:
            user_context: Complete user context including chat type
            command_args: Command arguments [field, value]
            crewai_system: CrewAI system for agent execution

        Returns:
            CommandResponse with success/error message
        """
        try:
            self.logger.info(
                f"🔄 Processing /update command: chat_type={user_context.chat_type.value}, args={command_args}"
            )

            # Validate command arguments
            if len(command_args) < 2:
                return self._get_usage_help_response(user_context.chat_type)

            field = command_args[0].lower()
            value = " ".join(command_args[1:])  # Support multi-word values

            # Route based on chat type
            if user_context.chat_type == ChatType.MAIN:
                return await self._handle_player_update(user_context, field, value, crewai_system)
            elif user_context.chat_type == ChatType.LEADERSHIP:
                return await self._handle_team_member_update(
                    user_context, field, value, crewai_system
                )
            else:
                return CommandResponse(
                    message="❌ Update command is not available in this chat type.", success=False
                )

        except Exception as e:
            self.logger.error(f"❌ Error handling update command: {e}", exc_info=True)
            return CommandResponse(
                message="❌ An error occurred processing your update request. Please try again.",
                success=False,
            )

    async def _handle_player_update(
        self, user_context: UserContext, field: str, value: str, crewai_system: Any
    ) -> CommandResponse:
        """Handle player information update in main chat."""
        try:
            self.logger.info(f"👤 Player update: user_id={user_context.user_id}, field={field}")

            # Check if user is registered as a player
            if not user_context.is_registered or not user_context.is_player:
                return CommandResponse(
                    message="""❌ Update Not Available

🔍 You are not registered as a player in this team.

📞 To register as a player:
1. Contact someone in the team's leadership
2. Ask them to add you using /addplayer
3. They'll send you an invite link
4. Join the main chat and ask leadership to add you with /addplayer

💡 Need help? Use /help to see available commands.""",
                    success=False,
                )

            # Create task for PlayerCoordinatorAgent
            task_description = f"/update {field} {value}"

            execution_context = {
                "user_id": user_context.user_id,
                "team_id": user_context.team_id,
                "chat_id": user_context.chat_id,
                "is_leadership_chat": False,
                "username": user_context.telegram_username or user_context.telegram_name,
                "message_text": task_description,
                "field": field,
                "value": value,
                "entity_type": "player",
            }

            # Execute with PlayerCoordinatorAgent via CrewAI
            if crewai_system:
                result = await crewai_system.execute_task(task_description, execution_context)
                return CommandResponse(message=result, success="✅" in result)
            else:
                return CommandResponse(
                    message="❌ System temporarily unavailable. Please try again.", success=False
                )

        except Exception as e:
            self.logger.error(f"❌ Error handling player update: {e}", exc_info=True)
            return CommandResponse(
                message="❌ Error updating player information. Please try again.", success=False
            )

    async def _handle_team_member_update(
        self, user_context: UserContext, field: str, value: str, crewai_system: Any
    ) -> CommandResponse:
        """Handle team member information update in leadership chat."""
        try:
            self.logger.info(
                f"👔 Team member update: user_id={user_context.user_id}, field={field}"
            )

            # Check if user is registered as a team member
            if not user_context.is_registered or not user_context.is_team_member:
                return CommandResponse(
                    message="""❌ Update Not Available

🔍 You are not registered as a team member in this team.

📝 To register as a team member:
1. Ask leadership to use /addmember [name] [phone] [role]
2. Example: /addmember John Smith +447123456789 Assistant Coach
3. You'll be added to the team members collection

💡 Need help? Use /help to see available commands.""",
                    success=False,
                )

            # Create task for TeamManagerAgent
            task_description = f"/update {field} {value}"

            execution_context = {
                "user_id": user_context.user_id,
                "team_id": user_context.team_id,
                "chat_id": user_context.chat_id,
                "is_leadership_chat": True,
                "username": user_context.telegram_username or user_context.telegram_name,
                "message_text": task_description,
                "field": field,
                "value": value,
                "entity_type": "team_member",
            }

            # Execute with TeamManagerAgent via CrewAI
            if crewai_system:
                result = await crewai_system.execute_task(task_description, execution_context)
                return CommandResponse(message=result, success="✅" in result)
            else:
                return CommandResponse(
                    message="❌ System temporarily unavailable. Please try again.", success=False
                )

        except Exception as e:
            self.logger.error(f"❌ Error handling team member update: {e}", exc_info=True)
            return CommandResponse(
                message="❌ Error updating team member information. Please try again.",
                success=False,
            )

    def _get_usage_help_response(self, chat_type: ChatType) -> CommandResponse:
        """Get usage help response based on chat type."""
        if chat_type == ChatType.MAIN:
            message = """❌ Invalid Usage

📝 Player Update Command Usage:
/update [field] [new value]

📋 Available Fields:
• phone - Your contact phone number
• position - Your football position  
• email - Your email address
• emergency_contact - Emergency contact info
• medical_notes - Medical information

💡 Examples:
• /update phone 07123456789
• /update position midfielder
• /update email john@example.com

📖 For more details, try: /update (no arguments)"""

        else:  # Leadership chat
            message = """❌ Invalid Usage

📝 Team Member Update Command Usage:
/update [field] [new value]

📋 Available Fields:
• phone - Your contact phone number
• email - Your email address
• emergency_contact - Emergency contact info
• role - Your administrative role (requires admin approval)

💡 Examples:
• /update phone 07123456789
• /update email admin@example.com
• /update role Assistant Coach

📖 For more details, try: /update (no arguments)"""

        return CommandResponse(message=message, success=False)

    async def get_update_help(
        self, user_context: UserContext, crewai_system: Any = None
    ) -> CommandResponse:
        """Get detailed help for update command based on user context."""
        try:
            if user_context.chat_type == ChatType.MAIN:
                # Route to PlayerCoordinatorAgent for player update help
                task_description = "get_player_updatable_fields"

                execution_context = {
                    "user_id": user_context.user_id,
                    "team_id": user_context.team_id,
                    "chat_id": user_context.chat_id,
                    "is_leadership_chat": False,
                    "username": user_context.telegram_username or user_context.telegram_name,
                    "message_text": task_description,
                    "entity_type": "player",
                }

                if crewai_system:
                    result = await crewai_system.execute_task(task_description, execution_context)
                    return CommandResponse(message=result, success=True)

            elif user_context.chat_type == ChatType.LEADERSHIP:
                # Route to TeamManagerAgent for team member update help
                task_description = "get_team_member_updatable_fields"

                execution_context = {
                    "user_id": user_context.user_id,
                    "team_id": user_context.team_id,
                    "chat_id": user_context.chat_id,
                    "is_leadership_chat": True,
                    "username": user_context.telegram_username or user_context.telegram_name,
                    "message_text": task_description,
                    "entity_type": "team_member",
                }

                if crewai_system:
                    result = await crewai_system.execute_task(task_description, execution_context)
                    return CommandResponse(message=result, success=True)

            # Fallback response
            return self._get_usage_help_response(user_context.chat_type)

        except Exception as e:
            self.logger.error(f"❌ Error getting update help: {e}", exc_info=True)
            return self._get_usage_help_response(user_context.chat_type)


# Global instance for use across the system
update_command_handler = UpdateCommandHandler()


async def handle_update_command(
    user_context: UserContext, command_args: list[str], crewai_system: Any = None
) -> CommandResponse:
    """Global function to handle update commands."""
    return await update_command_handler.handle_update_command(
        user_context, command_args, crewai_system
    )


async def get_update_help(user_context: UserContext, crewai_system: Any = None) -> CommandResponse:
    """Global function to get update command help."""
    return await update_command_handler.get_update_help(user_context, crewai_system)
