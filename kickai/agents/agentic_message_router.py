#!/usr/bin/env python3
"""
Agentic Message Router

This module provides centralized agentic message routing following CrewAI best practices.
ALL messages go through agents - no direct processing bypasses the agentic system.
"""

from dataclasses import dataclass
from typing import Any

from loguru import logger

from kickai.agents.crew_agents import TeamManagementSystem
from kickai.agents.crew_lifecycle_manager import get_crew_lifecycle_manager
from kickai.agents.user_flow_agent import (
    AgentResponse,
    TelegramMessage,
    UserFlowAgent,
    UserFlowDecision,
)
from kickai.core.context_types import create_context_from_telegram_message
from kickai.core.enums import ChatType


@dataclass
class IntentResult:
    """Intent classification result."""

    intent: str
    confidence: float
    entities: dict[str, Any]


class AgenticMessageRouter:
    """
    Centralized agentic message routing following CrewAI best practices.

    This router ensures that ALL messages go through the agentic system.
    No direct processing bypasses agents.
    """

    def __init__(self, team_id: str, crewai_system: TeamManagementSystem = None):
        self.team_id = team_id
        self.crewai_system = crewai_system
        self.user_flow_agent = UserFlowAgent(team_id=team_id)
        self.crew_lifecycle_manager = get_crew_lifecycle_manager()
        self._setup_router()

    def _setup_router(self):
        """Set up the router configuration."""
        logger.info(f"🤖 AgenticMessageRouter initialized for team {self.team_id}")

    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """
        Route ALL messages through the agentic system.
        No direct processing bypasses agents.

        Args:
            message: Telegram message to route

        Returns:
            AgentResponse with the processed result
        """
        try:
            logger.info(
                f"🔄 AgenticMessageRouter: Routing message from {message.username} in {message.chat_type.value}"
            )

            # Extract command from message text if it's a slash command
            command = None
            if message.text.startswith("/"):
                command = message.text.split()[0]  # Get the first word (the command)
                logger.info(f"🔄 AgenticMessageRouter: Detected command: {command}")

            # Determine user flow
            user_flow_result = await self.user_flow_agent.determine_user_flow(
                user_id=message.user_id, chat_type=message.chat_type, command=command
            )

            # Handle unregistered users
            if user_flow_result == UserFlowDecision.UNREGISTERED_USER:
                logger.info("🔄 AgenticMessageRouter: Unregistered user flow detected")

                # Check if the message looks like a phone number
                if self._looks_like_phone_number(message.text):
                    logger.info(
                        "📱 AgenticMessageRouter: Detected phone number in message from unregistered user"
                    )
                    return await self._handle_phone_number_from_unregistered_user(message)

                # Show welcome message for unregistered users
                message_text = self._get_unregistered_user_message(
                    message.chat_type, message.username
                )

                return AgentResponse(
                    success=True,
                    message=message_text,
                    error=None,
                    # Contact sharing button only works in private chats, not group chats
                    needs_contact_button=False,
                )

            # Handle registered users - normal agentic processing
            logger.info("🔄 AgenticMessageRouter: Registered user flow detected")
            return await self._process_with_crewai_system(message)

        except Exception as e:
            logger.error(f"AgenticMessageRouter failed: {e}")
            return AgentResponse(
                success=False, message="❌ System error. Please try again.", error=str(e)
            )

    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """
        Route contact sharing messages for phone number linking.

        Args:
            message: Telegram message with contact information

        Returns:
            AgentResponse with the linking result
        """
        try:
            logger.info(
                f"📱 AgenticMessageRouter: Processing contact share from {message.username}"
            )

            # Check if message has contact information
            if not hasattr(message, "contact_phone") or not message.contact_phone:
                return AgentResponse(
                    success=False,
                    message="❌ No contact information found in message.",
                    error="Missing contact phone",
                )

            # Use the phone linking service to link the user
            from kickai.features.player_registration.domain.services.player_linking_service import (
                PlayerLinkingService,
            )

            linking_service = PlayerLinkingService(self.team_id)

            # Attempt to link the user
            linked_player = await linking_service.link_telegram_user_by_phone(
                phone=message.contact_phone, telegram_id=message.user_id, username=message.username
            )

            if linked_player:
                return AgentResponse(
                    success=True,
                    message=f"✅ Successfully linked to your player record: {linked_player.full_name} ({linked_player.player_id})",
                    error=None,
                )
            else:
                return AgentResponse(
                    success=False,
                    message="❌ No player record found with that phone number. Please contact team leadership.",
                    error="No matching player record",
                )

        except Exception as e:
            logger.error(f"AgenticMessageRouter contact share failed: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error linking account. Please try again or contact team leadership.",
                error=str(e),
            )

    def _parse_registration_command(self, text: str) -> dict[str, str] | None:
        """Parse /register command and extract name, phone, and role."""
        try:
            parts = text.split()
            if len(parts) < 4:
                return None

            # Extract components
            name = parts[1]
            phone = parts[2]
            role = " ".join(parts[3:])

            return {"name": name, "phone": phone, "role": role}
        except Exception as e:
            logger.error(f"Registration command parsing failed: {e}")
            return None

    def _get_unregistered_user_message(self, chat_type: ChatType, username: str) -> str:
        """Get message for unregistered users based on chat type."""
        from kickai.core.constants import BOT_VERSION

        if chat_type == ChatType.LEADERSHIP:
            return f"""👋 Welcome to KICKAI Leadership for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🤔 You're not registered as a team member yet.

📝 To register as a team member, please provide your details:

💡 Use this command:
/register [name] [phone] [role]

Example:
/register John Smith +1234567890 Assistant Coach

🎯 Available roles:
• Team Manager, Coach, Assistant Coach
• Club Administrator, Treasurer
• Volunteer Coordinator, etc.

🚀 Once registered, you can:
• Add other team members and players
• Generate invite links for chats
• Manage the team system

❓ Got here by mistake?
If you're not part of the team leadership, please leave this chat.

Ready to get started? Use the /register command above!"""
        else:
            return f"""👋 Welcome to KICKAI for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🤔 You're not registered as a player yet.

📞 Contact Team Leadership
You need to be added as a player by someone in the team's leadership.

💬 What to do:
1. Reach out to someone in the team's leadership chat
2. Ask them to add you as a player using the `/addplayer` command
3. They'll send you an invite link to join the main chat
4. Once added, you can register with your full details

❓ Got here by mistake?
If you're not interested in joining the team, you can leave this chat.

🤖 Need help?
Use /help to see available commands or ask me questions!"""

    async def _process_with_crewai_system(self, message: TelegramMessage) -> AgentResponse:
        """
        Route registered user messages to specialized agents.

        Args:
            message: Telegram message to route

        Returns:
            AgentResponse with the processed result
        """
        try:
            # Get detailed registration status
            player_service = await self.user_flow_agent._get_player_service()
            team_service = await self.user_flow_agent._get_team_service()

            is_player = False
            is_team_member = False

            if player_service:
                try:
                    player = await player_service.get_player_by_telegram_id(
                        message.user_id, message.team_id
                    )
                    is_player = player is not None
                except Exception:
                    pass

            if team_service:
                try:
                    team_member = await team_service.get_team_member_by_telegram_id(
                        message.team_id, message.user_id
                    )
                    is_team_member = team_member is not None
                except Exception:
                    pass

            # SIMPLIFIED LOGIC: Chat type determines user type
            if message.chat_type == ChatType.MAIN:
                # In main chat, treat as player
                is_registered = is_player
                is_team_member = False  # Force team member to False in main chat
                logger.info(
                    f"🔄 AgenticMessageRouter: Main chat - treating as player, is_player={is_player}, is_registered={is_registered}"
                )
            elif message.chat_type == ChatType.LEADERSHIP:
                # In leadership chat, treat as team member
                is_registered = is_team_member
                is_player = False  # Force player to False in leadership chat
                logger.info(
                    f"🔄 AgenticMessageRouter: Leadership chat - treating as team member, is_team_member={is_team_member}, is_registered={is_registered}"
                )
            else:
                # Unknown chat type, assume unregistered
                is_registered = False
                is_player = False
                is_team_member = False
                logger.warning(
                    f"⚠️ AgenticMessageRouter: Unknown chat type {message.chat_type}, assuming unregistered"
                )

            # Create standardized context for CrewAI system
            standardized_context = create_context_from_telegram_message(
                user_id=message.user_id,
                team_id=message.team_id,
                chat_id=message.chat_id,
                chat_type=message.chat_type,
                message_text=message.text,
                username=message.username,
                telegram_name=message.username,  # Use username as telegram_name for now
                is_registered=is_registered,
                is_player=is_player,
                is_team_member=is_team_member,
            )

            # Convert to execution context for backward compatibility
            execution_context = standardized_context.to_dict()
            execution_context.update(
                {
                    "chat_type": message.chat_type.value,  # Add chat_type for simplified logic
                    "is_leadership_chat": message.chat_type == ChatType.LEADERSHIP,
                    "is_main_chat": message.chat_type == ChatType.MAIN,
                }
            )

            logger.info(
                f"🔄 AgenticMessageRouter: User registration status - is_registered={is_registered}, is_player={is_player}, is_team_member={is_team_member}"
            )

            # Use CrewAI system for registered users
            if self.crewai_system:
                logger.info("🔄 AgenticMessageRouter: Routing to CrewAI system")
                result = await self.crewai_system.execute_task(message.text, execution_context)
                return AgentResponse(message=result)
            else:
                # Use crew lifecycle manager as fallback
                logger.info("🔄 AgenticMessageRouter: Using crew lifecycle manager")
                result = await self.crew_lifecycle_manager.execute_task(
                    team_id=self.team_id,
                    task_description=message.text,
                    execution_context=execution_context,
                )
                return AgentResponse(message=result)

        except Exception as e:
            logger.error(f"❌ Error routing to specialized agent: {e}")
            return AgentResponse(
                message="I encountered an error processing your request. Please try again.",
                success=False,
                error=str(e),
            )

    async def route_command(self, command_name: str, message: TelegramMessage) -> AgentResponse:
        """
        Route command messages through the agentic system with chat-type awareness.

        Args:
            command_name: Name of the command (e.g., "/help", "/myinfo")
            message: Telegram message to route

        Returns:
            AgentResponse with the processed result
        """
        try:
            logger.info(
                f"🔄 AgenticMessageRouter: Routing command {command_name} in {message.chat_type.value}"
            )

            # Check if command is available for this chat type
            # Handle context isolation by ensuring registry is accessible
            try:
                from kickai.core.command_registry_initializer import (
                    get_initialized_command_registry,
                )

                registry = get_initialized_command_registry()
                chat_type_str = message.chat_type.value
                available_command = registry.get_command_for_chat(command_name, chat_type_str)
            except RuntimeError as e:
                if "Command registry not initialized" in str(e):
                    # Fallback: try to initialize the registry in this context
                    logger.warning(
                        "⚠️ Command registry not accessible in current context, attempting to initialize..."
                    )
                    try:
                        from kickai.core.command_registry_initializer import (
                            initialize_command_registry,
                        )

                        registry = initialize_command_registry()
                        chat_type_str = message.chat_type.value
                        available_command = registry.get_command_for_chat(
                            command_name, chat_type_str
                        )
                        logger.info(
                            "✅ Successfully initialized command registry in current context"
                        )
                    except Exception as init_error:
                        logger.error(
                            f"❌ Failed to initialize command registry in current context: {init_error}"
                        )
                        # Last resort: allow command to proceed without validation
                        available_command = True
                        logger.warning(
                            f"⚠️ Allowing command {command_name} to proceed without registry validation"
                        )
                else:
                    raise

            if not available_command:
                logger.warning(f"⚠️ Command {command_name} not available in {chat_type_str} chat")
                return AgentResponse(
                    message=f"❌ Command {command_name} is not available in this chat type.",
                    success=False,
                    error="Command not available in chat type",
                )

            # For commands, we still check user flow first
            user_flow = await self.user_flow_agent.determine_user_flow(
                message.user_id, message.chat_type, command_name
            )

            # Handle unregistered user flows
            if user_flow == UserFlowDecision.UNREGISTERED_USER:
                logger.info("🔄 AgenticMessageRouter: Unregistered user command flow")
                return await self.user_flow_agent.handle_unregistered_user_flow(message)

            else:  # REGISTERED_USER
                # For registered users, route commands to CrewAI system
                logger.info("🔄 AgenticMessageRouter: Registered user command flow")
                return await self._process_with_crewai_system(message)

        except Exception as e:
            logger.error(f"❌ Error routing command: {e}")
            return AgentResponse(
                message="I encountered an error processing your command. Please try again.",
                success=False,
                error=str(e),
            )

    def convert_telegram_update_to_message(
        self, update: Any, command_name: str = None
    ) -> TelegramMessage:
        """
        Convert Telegram update to domain message.

        Args:
            update: Telegram update object
            command_name: Optional command name for command messages

        Returns:
            TelegramMessage domain object
        """
        try:
            user_id = str(update.effective_user.id)
            chat_id = str(update.effective_chat.id)
            username = update.effective_user.username or update.effective_user.first_name

            # Determine chat type
            chat_type = self._determine_chat_type(chat_id)

            # Get message text
            if command_name:
                # For commands, build the full command string
                args = (
                    update.message.text.split()[1:] if len(update.message.text.split()) > 1 else []
                )
                text = f"{command_name} {' '.join(args)}".strip()
            else:
                # For natural language, use the message text
                text = update.message.text.strip()

            # Extract contact information if available
            contact_phone = None
            contact_user_id = None
            if hasattr(update.message, "contact") and update.message.contact:
                contact_phone = update.message.contact.phone_number
                contact_user_id = (
                    str(update.message.contact.user_id)
                    if update.message.contact.user_id
                    else user_id
                )

            return TelegramMessage(
                user_id=user_id,
                chat_id=chat_id,
                chat_type=chat_type,
                username=username,
                team_id=self.team_id,
                text=text,
                raw_update=update,
                contact_phone=contact_phone,
                contact_user_id=contact_user_id,
            )

        except Exception as e:
            logger.error(f"❌ Error converting Telegram update to message: {e}")
            raise

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Determine the chat type based on chat ID."""
        # Use configured chat IDs if available
        if hasattr(self, "main_chat_id") and hasattr(self, "leadership_chat_id"):
            return self._determine_chat_type_with_ids(chat_id)

        # Fallback to simple heuristic
        if chat_id.startswith("-100"):
            # Group chat - we'd need to know which is main vs leadership
            # This should be configured in the router
            return ChatType.MAIN  # Default to main chat
        else:
            return ChatType.PRIVATE

    def set_chat_ids(self, main_chat_id: str, leadership_chat_id: str):
        """Set the chat IDs for proper chat type determination."""
        self.main_chat_id = main_chat_id
        self.leadership_chat_id = leadership_chat_id

    def _looks_like_phone_number(self, text: str) -> bool:
        """Check if text looks like a phone number."""
        if not text or len(text.strip()) < 10:
            return False

        # Remove common separators and check if it's mostly digits
        cleaned = "".join(c for c in text if c.isdigit() or c in "+()-")

        # Must have at least 10 digits
        digit_count = sum(1 for c in cleaned if c.isdigit())
        if digit_count < 10:
            return False

        # Must start with + or be all digits
        if (
            cleaned.startswith("+")
            or cleaned.replace("+", "").replace("-", "").replace("(", "").replace(")", "").isdigit()
        ):
            return True

        return False

    async def _handle_phone_number_from_unregistered_user(
        self, message: TelegramMessage
    ) -> AgentResponse:
        """Handle phone number input from unregistered users."""
        try:
            logger.info(f"📱 Processing phone number from unregistered user: {message.username}")

            # Use the phone linking service to link the user
            from kickai.features.player_registration.domain.services.player_linking_service import (
                PlayerLinkingService,
            )

            linking_service = PlayerLinkingService(self.team_id)

            # Attempt to link the user
            linked_player = await linking_service.link_telegram_user_by_phone(
                phone=message.text.strip(), telegram_id=message.user_id, username=message.username
            )

            if linked_player:
                return AgentResponse(
                    success=True,
                    message=f"✅ Successfully linked to your player record: {linked_player.full_name} ({linked_player.player_id})\n\n🎉 Welcome to the team! You can now use all team features.",
                    error=None,
                )
            else:
                return AgentResponse(
                    success=False,
                    message="❌ No player record found with that phone number.\n\n💡 **What to do:**\n1. Make sure you were added by team leadership using /addplayer\n2. Check that the phone number matches what was used when you were added\n3. Contact team leadership if you need help",
                    error="No matching player record",
                )

        except Exception as e:
            logger.error(f"❌ Error processing phone number from unregistered user: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your phone number. Please try again or contact team leadership.",
                error=str(e),
            )

    def _determine_chat_type_with_ids(self, chat_id: str) -> ChatType:
        """Determine chat type using configured chat IDs."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.PRIVATE
