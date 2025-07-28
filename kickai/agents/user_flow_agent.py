#!/usr/bin/env python3
"""
User Flow Agent

This agent handles all user flow management including first user registration,
unregistered user guidance, and user status determination.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from loguru import logger

from kickai.core.constants import BOT_VERSION
from kickai.core.enums import ChatType


class UserFlowDecision(Enum):
    """User flow decision types."""

    UNREGISTERED_USER = "unregistered_user"
    REGISTERED_USER = "registered_user"


@dataclass
class TelegramMessage:
    """Domain message representation."""

    user_id: str
    chat_id: str
    chat_type: ChatType
    username: str
    team_id: str
    text: str
    raw_update: Any = None
    contact_phone: str = None
    contact_user_id: str = None


@dataclass
class AgentResponse:
    """Agent response structure."""

    message: str
    success: bool = True
    error: Optional[str] = None
    needs_contact_button: bool = False


class UserFlowAgent:
    """
    Dedicated agent for user flow management following CrewAI best practices.

    This agent handles:
    - First user detection and registration flow
    - Unregistered user guidance
    - User status determination
    - Welcome message formatting
    """

    def __init__(self, team_id: str, **kwargs):
        self.team_id = team_id
        self.role = "User Flow Manager"
        self.goal = "Manage user flows and provide appropriate guidance based on user status"
        self.backstory = """You are a User Flow Manager for KICKAI, responsible for determining 
        the appropriate user experience based on user status and context. You handle first user 
        registration, unregistered user guidance, and ensure smooth user onboarding."""

        logger.info(f"🤖 UserFlowAgent initialized for team {team_id}")

    async def determine_user_flow(
        self, user_id: str, chat_type: ChatType, command: str = None
    ) -> UserFlowDecision:
        """Determine the appropriate user flow based on user status and context."""
        try:
            # Check user registration status based on CHAT CONTEXT
            is_registered = await self._check_user_registration_context_aware(user_id, chat_type)
            if not is_registered:
                logger.info(
                    f"🔍 User flow: Unregistered user detected for {user_id} in {chat_type.value} chat"
                )
                return UserFlowDecision.UNREGISTERED_USER

            # Regular registered user
            logger.info(
                f"🔍 User flow: Registered user detected for {user_id} in {chat_type.value} chat"
            )
            return UserFlowDecision.REGISTERED_USER

        except Exception as e:
            logger.error(f"User flow determination failed: {e}")
            return UserFlowDecision.UNREGISTERED_USER

    async def handle_unregistered_user_flow(self, message: TelegramMessage) -> AgentResponse:
        """Handle unregistered user guidance flow."""
        try:
            formatted_message = await self._format_unregistered_user_message(
                message.chat_type, message.team_id, message.username
            )
            return AgentResponse(message=formatted_message)
        except Exception as e:
            logger.error(f"❌ Error handling unregistered user flow: {e}")
            return AgentResponse(
                message="I encountered an error processing your request.",
                success=False,
                error=str(e),
            )

    async def handle_registered_user_flow(self, message: TelegramMessage) -> AgentResponse:
        """Handle registered user flow."""
        try:
            formatted_message = await self._format_registered_user_message(
                message.user_id, message.team_id, message.username
            )
            return AgentResponse(message=formatted_message)
        except Exception as e:
            logger.error(f"❌ Error handling registered user flow: {e}")
            return AgentResponse(
                message="I encountered an error processing your request.",
                success=False,
                error=str(e),
            )

    # Tool methods for CrewAI integration
    def _check_user_registration_tool(self, user_id: str, team_id: str = None) -> str:
        """Tool: Check if user is registered in the system."""
        try:
            # This would be called by the agent, but we need to make it async-compatible
            # For now, return a simple response
            return f"User {user_id} registration status check completed"
        except Exception as e:
            return f"Error checking user registration: {e!s}"

            message = (
                f"🎉 Welcome to KICKAI for {team_id}, {username}!\n\n"
                f"🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant\n\n"
                f"🌟 You are the first user in this leadership chat!\n\n"
                f"👑 You will be set up as the team administrator with full access to:\n"
                f"• Player management and registration\n"
                f"• Team configuration and settings\n"
                f"• Match scheduling and management\n"
                f"• Financial oversight and reporting\n\n"
                f"📝 To complete your setup, please provide your details:\n\n"
                f"Use the command:\n"
                f"/register [Your Full Name] [Your Phone Number] [Your Role]\n\n"
                f"Example:\n"
                f"/register John Smith +1234567890 Team Manager\n\n"
                f"�� Your role can be:\n"
                f"• Team Manager, Coach, Assistant Coach\n"
                f"• Club Administrator, Treasurer\n"
                f"• Volunteer Coordinator, etc.\n\n"
                f"🚀 Once registered, you can:\n"
                f"• Add other team members and players\n"
                f"• Generate invite links for chats\n"
                f"• Manage the entire team system\n\n"
                f"Ready to get started? Use the /register command above!"
            )

    def _format_unregistered_user_message_tool(
        self, chat_type: str, team_id: str, username: str
    ) -> str:
        """Tool: Format unregistered user message based on chat type."""
        try:
            if chat_type == ChatType.MAIN.value:
                # For main chat, always show linking instructions since we can't check async here
                # The actual linking check happens in the async _format_unregistered_user_message method
                message = (
                    f"👋 Welcome to KICKAI for {team_id}, {username}!\n\n"
                    f"🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant\n\n"
                    f"🔗 **Account Linking Available**\n"
                    f"I can help you link to an existing player record if you were added by team leadership.\n\n"
                    f"📱 **To link your account:**\n"
                    f"Type your phone number in international format:\n"
                    f"Example: +447123456789\n\n"
                    f"💬 **If linking doesn't work:**\n"
                    f"Contact team leadership to be added as a player using the /addplayer command.\n\n"
                    f"❓ Got here by mistake?\n"
                    f"If you're not interested in joining the team, you can leave this chat.\n\n"
                    f"🤖 Need help?\n"
                    f"Use /help to see available commands or ask me questions!"
                )
            elif chat_type == ChatType.LEADERSHIP.value:
                message = (
                    f"👋 Welcome to KICKAI Leadership for {team_id}, {username}!\n\n"
                    f"🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant\n\n"
                    f"🤔 I don't see you registered as a team member yet.\n\n"
                    f"📞 Contact Team Administrator\n"
                    f"You need to be added as a team member by the team administrator.\n\n"
                    f"💡 What to do:\n"
                    f"1. Contact the team administrator\n"
                    f"2. Ask them to add you as a team member using the /addmember command\n"
                    f"3. They'll send you an invite link to join the leadership chat\n"
                    f"4. Once added, you can access leadership functions\n\n"
                    f"🎯 Team member roles include:\n"
                    f"• Team Manager, Coach, Assistant Coach\n"
                    f"• Club Administrator, Treasurer\n"
                    f"• Volunteer Coordinator, etc.\n\n"
                    f"🚀 Once added, you can:\n"
                    f"• Add other team members and players\n"
                    f"• Generate invite links for chats\n"
                    f"• Manage the team system\n\n"
                    f"Need help? Contact the team administrator."
                )
            else:  # PRIVATE
                message = (
                    f"👋 Hi {username}!\n\n"
                    f"🤖 KICKAI v{BOT_VERSION} for {team_id} - Your AI-powered football team assistant\n\n"
                    f"📋 Joining the Team\n\n"
                    f"🎯 To join the team:\n\n"
                    f"🎯 Player Registration (Main Chat):\n"
                    f"• Contact team leadership to be added as a player\n"
                    f"• They'll use /addplayer to add you\n"
                    f"• You'll receive an invite link to join\n"
                    f"• Requires team leadership approval\n\n"
                    f"👔 Team Member Registration (Leadership Chat):\n"
                    f"• Contact team administrator to be added as a team member\n"
                    f"• They'll use /addmember to add you\n"
                    f"• For coaches, managers, volunteers\n\n"
                    f"💡 Need help?\n"
                    f"Contact the team leadership to be added to the appropriate chat."
                )
            return message
        except Exception as e:
            return f"Error formatting unregistered user message: {e!s}"

    def _format_registered_user_message_tool(
        self, user_id: str, team_id: str, username: str
    ) -> str:
        """Tool: Format registered user message."""
        try:
            message = (
                f"👋 Welcome back to KICKAI for {team_id}, {username}!\n\n"
                f"🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant\n\n"
                f"✅ You are already registered as a player in the team.\n\n"
                f"📋 Your Information:\n"
                f"• User ID: {user_id}\n"
                f"• Username: {username}\n"
                f"• Status: Active Player\n\n"
                f"💡 Need to update your information?\n"
                f"Contact the team leadership to make any changes.\n\n"
                f"🎯 What you can do:\n"
                f"• Use /myinfo to check your details\n"
                f"• Use /list to see team members\n"
                f"• Use /status to check your availability\n"
                f"• Ask me questions in natural language!"
            )
            return message
        except Exception as e:
            return f"Error formatting registered user message: {e!s}"

    def _determine_user_flow_tool(self, user_id: str, chat_type: str, team_id: str = None) -> str:
        """Tool: Determine user flow based on user status and context."""
        try:
            # This is a simplified version for the tool
            # The actual logic is in the async methods
            return f"User flow determination completed for user {user_id} in {chat_type} chat"
        except Exception as e:
            return f"Error determining user flow: {e!s}"

    # Service access helpers with proper error handling and lazy initialization
    async def _get_player_service(self):
        """Get PlayerService with proper error handling."""
        try:
            from kickai.core.dependency_container import get_container
            from kickai.features.player_registration.domain.services.player_service import (
                PlayerService,
            )

            # Get the already-initialized container
            container = get_container()

            # Try to get service directly - don't check has_service as it can return False during initialization
            try:
                return container.get_service(PlayerService)
            except RuntimeError as e:
                logger.debug(f"PlayerService not available in container: {e}")
                return None

        except Exception as e:
            logger.debug(f"PlayerService not available: {e}")
            return None

    async def _get_team_service(self):
        """Get TeamService with proper error handling."""
        try:
            from kickai.core.dependency_container import get_container
            from kickai.features.team_administration.domain.services.team_service import TeamService

            # Get the already-initialized container
            container = get_container()
            logger.info(f"🔍 [SERVICE_CHECK] Got container: {container}")

            # Try to get service directly - don't check has_service as it can return False during initialization
            try:
                service = container.get_service(TeamService)
                logger.info(f"🔍 [SERVICE_CHECK] Got TeamService: {service}")
                return service
            except RuntimeError as e:
                logger.error(f"❌ [SERVICE_CHECK] TeamService not available in container: {e}")
                return None

        except Exception as e:
            logger.error(f"❌ [SERVICE_CHECK] TeamService not available: {e}")
            import traceback

            logger.error(f"❌ [SERVICE_CHECK] Traceback: {traceback.format_exc()}")
            return None

    # Async helper methods
    async def _check_user_registration(self, user_id: str) -> bool:
        """Check if user is already registered in the system."""
        try:
            # Get services with proper error handling
            player_service = await self._get_player_service()
            team_service = await self._get_team_service()

            # If services are not available, assume unregistered (graceful degradation)
            if not player_service and not team_service:
                logger.warning(
                    f"⚠️ Services not available for user registration check, assuming unregistered for user {user_id}"
                )
                return False

            # Check if user exists as a player
            if player_service:
                try:
                    player = await player_service.get_player_by_telegram_id(user_id, self.team_id)
                    if player:
                        logger.info(f"✅ User {user_id} found as registered player")
                        return True
                except Exception as e:
                    logger.debug(f"User {user_id} not found as player: {e}")

            # Check if user exists as a team member
            if team_service:
                try:
                    logger.info(
                        f"🔍 [USER_REG_CHECK] Looking for team member with telegram_id={user_id}, team_id={self.team_id}"
                    )
                    logger.info(f"🔍 [USER_REG_CHECK] TeamService type: {type(team_service)}")
                    team_member = await team_service.get_team_member_by_telegram_id(
                        self.team_id, user_id
                    )
                    logger.info(f"🔍 [USER_REG_CHECK] TeamService returned: {team_member}")
                    if team_member:
                        logger.info(
                            f"✅ User {user_id} found as team member: {team_member.user_id} with role {team_member.role}"
                        )
                        return True
                    else:
                        logger.info(f"❌ User {user_id} not found as team member")
                except Exception as e:
                    logger.error(f"❌ Exception in team member check: {e}")
                    import traceback

                    logger.error(f"❌ Traceback: {traceback.format_exc()}")

            logger.info(f"❌ User {user_id} not registered in the system")
            return False

        except Exception as e:
            logger.warning(f"⚠️ Error checking user registration, assuming unregistered: {e}")
            return False

    async def _check_user_registration_context_aware(
        self, user_id: str, chat_type: ChatType
    ) -> bool:
        """Check if user is registered in the system based on chat context."""
        try:
            # Get services with proper error handling
            player_service = await self._get_player_service()
            team_service = await self._get_team_service()

            # If services are not available, assume unregistered (graceful degradation)
            if not player_service and not team_service:
                logger.warning(
                    f"⚠️ Services not available for user registration check, assuming unregistered for user {user_id}"
                )
                return False

            # Check registration based on CHAT CONTEXT
            if chat_type == ChatType.MAIN:
                # In main chat, only players are considered registered
                if player_service:
                    try:
                        player = await player_service.get_player_by_telegram_id(
                            user_id, self.team_id
                        )
                        if player:
                            logger.info(
                                f"✅ User {user_id} found as registered player in main chat"
                            )
                            return True
                    except Exception as e:
                        logger.debug(f"User {user_id} not found as player: {e}")

                # Check if there are pending players that could be linked
                try:
                    from kickai.features.player_registration.domain.services.player_linking_service import (
                        PlayerLinkingService,
                    )

                    linking_service = PlayerLinkingService(self.team_id)
                    pending_players = (
                        await linking_service.get_pending_players_without_telegram_id()
                    )

                    if pending_players:
                        logger.info(
                            f"🔗 Found {len(pending_players)} pending players that could be linked for user {user_id}"
                        )
                        # Don't return True here - let the user flow handle the linking
                except Exception as e:
                    logger.debug(f"Could not check pending players: {e}")

                logger.info(f"❌ User {user_id} not registered as player in main chat")
                return False

            elif chat_type == ChatType.LEADERSHIP:
                # In leadership chat, only team members are considered registered
                if team_service:
                    try:
                        logger.info(
                            f"🔍 [USER_REG_CHECK] Looking for team member with telegram_id={user_id}, team_id={self.team_id}"
                        )
                        team_member = await team_service.get_team_member_by_telegram_id(
                            self.team_id, user_id
                        )
                        if team_member:
                            logger.info(
                                f"✅ User {user_id} found as team member in leadership chat: {team_member.user_id} with role {team_member.role}"
                            )
                            return True
                    except Exception as e:
                        logger.error(f"❌ Exception in team member check: {e}")
                        import traceback

                        logger.error(f"❌ Traceback: {traceback.format_exc()}")

                logger.info(f"❌ User {user_id} not registered as team member in leadership chat")
                return False
            else:
                # Unknown chat type, assume unregistered
                logger.warning(
                    f"⚠️ Unknown chat type {chat_type}, assuming unregistered for user {user_id}"
                )
                return False

        except Exception as e:
            logger.warning(f"⚠️ Error checking user registration, assuming unregistered: {e}")
            return False

    async def _format_unregistered_user_message(
        self, chat_type: ChatType, team_id: str, username: str
    ) -> str:
        """Format unregistered user message based on chat type."""
        try:
            if chat_type == ChatType.MAIN:
                # Check for pending players that could be linked
                try:
                    from kickai.features.player_registration.domain.services.player_linking_service import (
                        PlayerLinkingService,
                    )
                    
                    linking_service = PlayerLinkingService(team_id)
                    pending_players = await linking_service.get_pending_players_without_telegram_id()
                    
                    if pending_players:
                        # Use the specific linking prompt message
                        message = await linking_service.create_linking_prompt_message("")
                        return message
                except Exception as e:
                    logger.debug(f"Could not check pending players for linking prompt: {e}")
                
                # Fallback to generic message if no pending players or error
                return self._format_unregistered_user_message_tool(chat_type.value, team_id, username)
            else:
                # For other chat types, use the tool method
                return self._format_unregistered_user_message_tool(chat_type.value, team_id, username)
        except Exception as e:
            logger.error(f"Error formatting unregistered user message: {e}")
            return self._format_unregistered_user_message_tool(chat_type.value, team_id, username)

    async def _format_registered_user_message(
        self, user_id: str, team_id: str, username: str
    ) -> str:
        """Format registered user message."""
        return self._format_registered_user_message_tool(user_id, team_id, username)
