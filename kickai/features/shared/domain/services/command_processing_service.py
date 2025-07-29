#!/usr/bin/env python3
"""
Command Processing Service for KICKAI

This service provides a framework for processing commands with proper user validation,
status checking, and context-aware responses. It follows the feature-based architecture
and uses agents and tools for complex operations.
"""

from dataclasses import dataclass
from typing import Any

from loguru import logger

from kickai.core.enums import ChatType
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.system_infrastructure.domain.services.permission_service import (
    PermissionService,
    UserPermissions,
)
from kickai.features.team_administration.domain.services.team_service import TeamService


@dataclass
class UserContext:
    """Complete user context for command processing."""

    user_id: str
    team_id: str
    chat_id: str
    chat_type: ChatType
    telegram_username: str
    telegram_name: str
    user_permissions: UserPermissions | None = None
    player_data: dict[str, Any] | None = None
    team_member_data: dict[str, Any] | None = None
    is_registered: bool = False
    is_player: bool = False
    is_team_member: bool = False


@dataclass
class CommandResponse:
    """Standardized command response."""

    message: str
    success: bool
    requires_action: bool = False
    action_type: str | None = None
    action_data: dict[str, Any] | None = None


class CommandProcessingService:
    """
    Centralized service for command processing with user validation.

    This service follows the feature-based architecture and provides:
    - User status validation
    - Context-aware responses
    - Proper user registration flows
    - Message formatting
    """

    def __init__(self):
        """Initialize the command processing service."""
        try:
            from kickai.core.dependency_container import get_service

            self.permission_service = get_service(PermissionService)
            self.player_service = get_service(PlayerService)
            self.team_service = get_service(TeamService)

            logger.info("✅ CommandProcessingService initialized with dependency injection")

        except Exception as e:
            logger.error(f"❌ Failed to initialize CommandProcessingService: {e}")
            raise

    async def process_command(
        self,
        command_name: str,
        user_id: str,
        team_id: str,
        chat_id: str,
        chat_type: ChatType,
        telegram_username: str,
        telegram_name: str,
        **kwargs,
    ) -> CommandResponse:
        """
        Process a command with full user validation and context.

        Args:
            command_name: Name of the command being processed
            user_id: Telegram user ID
            team_id: Team ID
            chat_id: Chat ID
            chat_type: Type of chat (main/leadership)
            telegram_username: Telegram username
            telegram_name: Telegram display name
            **kwargs: Additional command-specific parameters

        Returns:
            CommandResponse with appropriate message and action requirements
        """
        try:
            # Step 1: Build user context
            user_context = await self._build_user_context(
                user_id, team_id, chat_id, chat_type, telegram_username, telegram_name
            )

            # Step 2: Validate user status and handle registration flows
            validation_result = await self._validate_user_status(user_context, command_name)
            if not validation_result.success:
                return validation_result

            # Step 3: Process the command based on type
            if command_name == "/help":
                return await self._process_help_command(user_context, **kwargs)
            elif command_name == "/myinfo":
                return await self._process_myinfo_command(user_context, **kwargs)
            elif command_name == "/list":
                return await self._process_list_command(user_context, **kwargs)
            elif command_name == "/status":
                return await self._process_status_command(user_context, **kwargs)
            else:
                return CommandResponse(
                    message="❌ Command not implemented in processing service", success=False
                )

        except Exception as e:
            logger.error(f"❌ Error processing command {command_name}: {e}")
            return CommandResponse(
                message="❌ An error occurred while processing your command. Please try again.",
                success=False,
            )

    async def _build_user_context(
        self,
        user_id: str,
        team_id: str,
        chat_id: str,
        chat_type: ChatType,
        telegram_username: str,
        telegram_name: str,
    ) -> UserContext:
        """Build complete user context with all necessary information."""
        try:
            # Get user permissions
            user_permissions = await self.permission_service.get_user_permissions(user_id, team_id)

            # Get player data if user is a player
            player_data = None
            if user_permissions.is_player:
                try:
                    player_data = await self.player_service.get_player_by_telegram_id(
                        user_id, team_id
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Could not get player data for {user_id}: {e}")

            # Get team member data if user is a team member
            team_member_data = None
            if user_permissions.is_team_member:
                try:
                    team_member_data = await self.team_service.get_team_member_by_telegram_id(
                        user_id, team_id
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Could not get team member data for {user_id}: {e}")

            return UserContext(
                user_id=user_id,
                team_id=team_id,
                chat_id=chat_id,
                chat_type=chat_type,
                telegram_username=telegram_username,
                telegram_name=telegram_name,
                user_permissions=user_permissions,
                player_data=player_data,
                team_member_data=team_member_data,
                is_registered=user_permissions.is_player or user_permissions.is_team_member,
                is_player=user_permissions.is_player,
                is_team_member=user_permissions.is_team_member,
            )

        except Exception as e:
            logger.error(f"❌ Error building user context: {e}")
            # Return minimal context on error
            return UserContext(
                user_id=user_id,
                team_id=team_id,
                chat_id=chat_id,
                chat_type=chat_type,
                telegram_username=telegram_username,
                telegram_name=telegram_name,
                is_registered=False,
                is_player=False,
                is_team_member=False,
            )

    async def _validate_user_status(
        self, user_context: UserContext, command_name: str
    ) -> CommandResponse:
        """
        Validate user status and handle registration flows.

        This implements the user validation rules:
        - Main chat: Must be a player
        - Leadership chat: Must be a team member
        """
        try:
            # Check if user is registered
            if not user_context.is_registered:
                if user_context.chat_type == ChatType.MAIN:
                    # Main chat: User must be a player
                    return CommandResponse(
                        message=self._format_player_registration_message(user_context),
                        success=False,
                        requires_action=True,
                        action_type="player_registration",
                    )
                elif user_context.chat_type == ChatType.LEADERSHIP:
                    # Leadership chat: Team member registration
                    return CommandResponse(
                        message=self._format_team_member_registration_message(user_context),
                        success=False,
                        requires_action=True,
                        action_type="team_member_registration",
                    )

            # User is registered, check chat-specific requirements
            if user_context.chat_type == ChatType.MAIN and not user_context.is_player:
                return CommandResponse(
                    message="❌ You must be registered as a player to use commands in the main chat. Please contact a team member.",
                    success=False,
                )

            if user_context.chat_type == ChatType.LEADERSHIP and not user_context.is_team_member:
                return CommandResponse(
                    message="❌ You must be a team member to use commands in the leadership chat.",
                    success=False,
                )

            # All validations passed
            return CommandResponse(
                message="",  # Empty message indicates success
                success=True,
            )

        except Exception as e:
            logger.error(f"❌ Error validating user status: {e}")
            return CommandResponse(
                message="❌ Error validating your status. Please try again.", success=False
            )

    def _format_player_registration_message(self, user_context: UserContext) -> str:
        """Format message asking user to contact leadership for player registration."""
        return (
            f"👋 Welcome to KICKAI, {user_context.telegram_name}!\n\n"
            f"🤔 I don't see you registered as a player yet.\n\n"
            f"📞 Please contact a member of the leadership team to add you as a player to this team.\n\n"
            f"💡 Once you're registered, you'll be able to use all player commands!"
        )

    def _format_team_member_registration_message(self, user_context: UserContext) -> str:
        """Format message for team member registration."""
        return (
            f"👋 Welcome to KICKAI Leadership, {user_context.telegram_name}!\n\n"
            f"🤔 I don't see you registered as a team member yet.\n\n"
            f"📝 Please provide your details so I can add you to the team members collection.\n\n"
            f"💡 They can use: /addmember [name] [phone] [role]"
        )

    async def _process_help_command(self, user_context: UserContext, **kwargs) -> CommandResponse:
        """Process the help command using the new HelpAssistantAgent."""
        try:
            from kickai.features.shared.domain.agents.help_assistant_agent import (
                get_help_assistant_agent,
            )

            # Get help assistant agent instance
            help_assistant = get_help_assistant_agent()

            # Use the normalized chat type from constants
            from kickai.core.constants import normalize_chat_type

            # Handle chat type conversion properly
            if hasattr(user_context.chat_type, "value"):
                # It's an enum, get the value directly
                chat_type = user_context.chat_type.value
            else:
                # It's a string, normalize it
                chat_type_enum = normalize_chat_type(str(user_context.chat_type))
                chat_type = chat_type_enum.value

            # Build robust context with comprehensive fallbacks
            context = self._build_robust_help_context(user_context, chat_type)

            # DEBUG: Log the final context being sent
            logger.info(f"🔧 [HELP COMMAND] Final context being sent: {context}")

            # Process help request using HelpAssistantAgent
            help_message = help_assistant.process_help_request(context)

            return CommandResponse(message=help_message, success=True)

        except Exception as e:
            logger.error(f"❌ Error processing help command: {e}")
            return CommandResponse(
                message="❌ Error generating help information. Please try again.", success=False
            )

    def _build_robust_help_context(
        self, user_context: UserContext, chat_type: str
    ) -> dict[str, str]:
        """
        Build a robust context for help requests with comprehensive fallbacks.

        This ensures that all required parameters are never None and have sensible defaults.
        """
        # Build username with multiple fallbacks
        username = (
            user_context.telegram_username
            or user_context.telegram_name
            or f"User_{user_context.user_id}"
            or "Unknown User"
        )

        # Ensure username is not empty or just whitespace
        if not username or not username.strip():
            username = f"User_{user_context.user_id}"

        # Build the context with guaranteed non-None values
        context = {
            "user_id": str(user_context.user_id) if user_context.user_id else "unknown",
            "team_id": str(user_context.team_id) if user_context.team_id else "unknown",
            "chat_type": str(chat_type) if chat_type else "main",
            "username": str(username).strip(),
            "message_text": "help request",
        }

        # Validate that no values are None or empty
        for key, value in context.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                logger.warning(
                    f"🔧 [HELP COMMAND] Context value for {key} is None or empty: {value}"
                )
                if key == "username":
                    context[key] = f"User_{user_context.user_id}"
                elif key in ["user_id", "team_id"]:
                    context[key] = "unknown"
                elif key == "chat_type":
                    context[key] = "main"
                else:
                    context[key] = "unknown"

        # Final validation - ensure all required fields have valid values
        required_fields = ["user_id", "team_id", "chat_type", "username"]
        for field in required_fields:
            if field not in context or not context[field] or context[field] == "unknown":
                logger.error(
                    f"🔧 [HELP COMMAND] Required field {field} is missing or invalid: {context.get(field)}"
                )
                if field == "user_id":
                    context[field] = "12345"  # Fallback user ID
                elif field == "team_id":
                    context[field] = "DEFAULT"  # Fallback team ID
                elif field == "chat_type":
                    context[field] = "main"  # Default to main chat
                elif field == "username":
                    context[field] = "User"  # Fallback username

        logger.info(f"🔧 [HELP COMMAND] Final robust context: {context}")
        return context

    async def _get_available_commands_for_user(self, user_context: UserContext) -> dict[str, Any]:
        """Get available commands for the specific user context."""
        try:
            from kickai.features.shared.application.commands.help_commands import (
                get_available_commands,
            )

            return get_available_commands(
                chat_type=user_context.chat_type,
                user_id=user_context.user_id,
                team_id=user_context.team_id,
            )

        except Exception as e:
            logger.error(f"❌ Error getting available commands: {e}")
            return {
                "error": f"Failed to get commands: {e!s}",
                "chat_type": user_context.chat_type.value,
                "total_commands": 0,
                "features": {},
            }

    # Note: Old help formatting methods removed - now using HelpAssistantAgent

    async def _process_myinfo_command(self, user_context: UserContext, **kwargs) -> CommandResponse:
        """Process the myinfo command."""
        try:
            if user_context.chat_type == ChatType.MAIN and user_context.player_data:
                return self._format_player_info(user_context)
            elif user_context.chat_type == ChatType.LEADERSHIP and user_context.team_member_data:
                return self._format_team_member_info(user_context)
            else:
                return CommandResponse(
                    message="❌ No information available for your account.", success=False
                )

        except Exception as e:
            logger.error(f"❌ Error processing myinfo command: {e}")
            return CommandResponse(
                message="❌ Error retrieving your information. Please try again.", success=False
            )

    def _format_player_info(self, user_context: UserContext) -> CommandResponse:
        """Format player information."""
        player_data = user_context.player_data
        player_id = player_data.get("id", "Unknown")
        name = player_data.get("name", "Unknown")
        phone = player_data.get("phone", "Unknown")
        position = player_data.get("position", "Unknown")

        message = (
            f"👤 Player Information\n\n"
            f"Name: {name}\n"
            f"Player ID: {player_id}\n"
            f"Phone: {phone}\n"
            f"Position: {position}\n"
            f"Status: Active"
        )

        return CommandResponse(message=message, success=True)

    def _format_team_member_info(self, user_context: UserContext) -> CommandResponse:
        """Format team member information."""
        member_data = user_context.team_member_data
        member_id = member_data.get("id", "Unknown")
        name = member_data.get("name", "Unknown")
        phone = member_data.get("phone", "Unknown")
        roles = member_data.get("roles", [])

        roles_text = ", ".join(roles) if roles else "No roles assigned"

        message = (
            f"👔 Team Member Information\n\n"
            f"Name: {name}\n"
            f"Member ID: {member_id}\n"
            f"Phone: {phone}\n"
            f"Roles: {roles_text}\n"
            f"Status: Active"
        )

        return CommandResponse(message=message, success=True)

    async def _process_list_command(self, user_context: UserContext, **kwargs) -> CommandResponse:
        """Process the list command."""
        # This would be implemented with actual data retrieval
        return CommandResponse(message="📋 List command - implementation pending", success=True)

    async def _process_status_command(self, user_context: UserContext, **kwargs) -> CommandResponse:
        """Process the status command."""
        # This would be implemented with actual data retrieval
        return CommandResponse(message="📊 Status command - implementation pending", success=True)


def get_command_processing_service() -> CommandProcessingService:
    """Get the command processing service instance."""
    return CommandProcessingService()
