#!/usr/bin/env python3
"""
Message Handlers

Specialized handlers for different types of message processing following
the Single Responsibility Principle and Strategy Pattern.
"""

from abc import ABC, abstractmethod

from loguru import logger

# Import centralized types
from kickai.core.types import AgentResponse, TelegramMessage, UserFlowType
from kickai.core.enums import ChatType


class MessageHandler(ABC):
    """Abstract base class for message handlers."""

    @abstractmethod
    async def handle(self, message: TelegramMessage) -> AgentResponse:
        """Handle a specific type of message."""
        pass

    @abstractmethod
    def can_handle(self, message: TelegramMessage) -> bool:
        """Determine if this handler can process the message."""
        pass


class UnregisteredUserHandler(MessageHandler):
    """Handles messages from unregistered users."""

    def __init__(self, team_id: str):
        self.team_id = team_id

    def can_handle(self, message: TelegramMessage) -> bool:
        """Check if this is an unregistered user message."""
        # This will be determined by the UserFlowAgent
        return True

    async def handle(self, message: TelegramMessage) -> AgentResponse:
        """Handle unregistered user messages."""
        try:
            logger.info(f"🔄 UnregisteredUserHandler: Processing message from {message.username}")

            # Check if the message looks like a phone number
            if self._looks_like_phone_number(message.text):
                logger.info("📱 UnregisteredUserHandler: Detected phone number")
                return await self._handle_phone_number(message)

            # Show welcome message for unregistered users
            message_text = self._get_unregistered_user_message(message.chat_type, message.username)

            return AgentResponse(
                success=True,
                message=message_text,
                error=None,
                needs_contact_button=False,
            )

        except Exception as e:
            logger.error(f"❌ UnregisteredUserHandler failed: {e}")
            return AgentResponse(
                success=False,
                message="❌ System error. Please try again.",
                error=str(e)
            )

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

    async def _handle_phone_number(self, message: TelegramMessage) -> AgentResponse:
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
                phone=message.text.strip(),
                telegram_id=message.user_id,
                username=message.username
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


class ContactShareHandler(MessageHandler):
    """Handles contact sharing messages for phone number linking."""

    def __init__(self, team_id: str):
        self.team_id = team_id

    def can_handle(self, message: TelegramMessage) -> bool:
        """Check if this is a contact share message."""
        return hasattr(message, "contact_phone") and message.contact_phone is not None

    async def handle(self, message: TelegramMessage) -> AgentResponse:
        """Handle contact sharing messages."""
        try:
            logger.info(f"📱 ContactShareHandler: Processing contact share from {message.username}")

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
                phone=message.contact_phone,
                telegram_id=message.user_id,
                username=message.username
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
            logger.error(f"❌ Error in contact share handling: {e}")
            return AgentResponse(
                success=False,
                message="I encountered an error processing your contact information. Please try again.",
            )


class NewMemberWelcomeHandler(MessageHandler):
    """Handles new member welcome messages."""

    def __init__(self, team_id: str):
        self.team_id = team_id

    def can_handle(self, message: TelegramMessage) -> bool:
        """Check if this is a new member welcome message."""
        return getattr(message, "is_new_member", False)

    async def handle(self, message: TelegramMessage) -> AgentResponse:
        """Handle new member welcome messages."""
        try:
            logger.info(f"👋 NewMemberWelcomeHandler: Processing welcome for {message.username}")

            # Validate message structure
            if not message.user_id or not message.username:
                logger.error("❌ Invalid message structure: missing user_id or username")
                return self._create_fallback_welcome_message(message.username)

            # Simplified user flow determination
            try:
                # Default to registered user for new members
                user_flow_result = UserFlowType.REGISTERED_USER
                logger.info("New member - defaulting to registered user flow")
            except Exception as flow_error:
                logger.error(f"❌ Error determining user flow: {flow_error}")
                return self._create_fallback_welcome_message(message.username)

            # Generate appropriate welcome message based on user flow
            try:
                if user_flow_result == UserFlowType.REGISTERED_USER:
                    logger.info("New registered user - sending welcome back message")
                    welcome_message = f"""👋 Welcome back, {message.username}!

🎉 Great to see you in the team chat!

📋 **Quick Start:**
• Use `/help` to see available commands
• Use `/myinfo` to check your information
• Contact team leadership if you need assistance

Welcome aboard! ⚽"""
                    return AgentResponse(success=True, message=welcome_message)
                else:
                    logger.warning(f"Unknown user flow for new member: {user_flow_result}")
                    return self._create_fallback_welcome_message(message.username)

            except Exception as message_error:
                logger.error(f"❌ Error generating welcome message: {message_error}")
                return self._create_fallback_welcome_message(message.username)

        except Exception as e:
            logger.error(f"❌ Critical error in new member welcome handling: {e}")
            return self._create_fallback_welcome_message(message.username if message else "User")

    def _create_fallback_welcome_message(self, username: str) -> AgentResponse:
        """Create a fallback welcome message when the main flow fails."""
        try:
            # Sanitize username for safety
            from kickai.utils.security_utils import sanitize_username
            safe_username = sanitize_username(username)

            fallback_message = f"""👋 Welcome to the team, {safe_username}!

🎉 We're excited to have you join our football community!

📋 **Getting Started:**
• Use `/help` to see available commands
• Contact team leadership for assistance
• Check pinned messages for important updates

Welcome aboard! ⚽"""

            return AgentResponse(success=True, message=fallback_message)

        except Exception as e:
            logger.error(f"❌ Error creating fallback welcome message: {e}")
            # Ultimate fallback
            return AgentResponse(
                success=True,
                message="👋 Welcome to the team! Use /help to see available commands."
            )


class RegisteredUserHandler(MessageHandler):
    """Handles messages from registered users."""

    def __init__(self, team_id: str, crewai_system=None):
        self.team_id = team_id
        self.crewai_system = crewai_system
        from kickai.agents.context.context_builder import ContextBuilder
        self.context_builder = ContextBuilder(team_id=team_id)

    def can_handle(self, message: TelegramMessage) -> bool:
        """Check if this is a registered user message."""
        # This will be determined by the UserFlowAgent
        return True

    async def handle(self, message: TelegramMessage) -> AgentResponse:
        """Handle registered user messages."""
        try:
            logger.info(f"🔄 RegisteredUserHandler: Processing message from {message.username}")

            # Get detailed registration status - simplified approach
            # In production, you'd want to get these services from the dependency container
            player_service = None
            team_service = None

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

            # Use ContextBuilder to determine user status and build execution context
            user_status = self.context_builder.determine_user_status(message, is_player, is_team_member)
            execution_context = await self.context_builder.build_execution_context(
                message,
                user_status["is_registered"],
                user_status["is_player"],
                user_status["is_team_member"]
            )

            logger.info(
                f"🔄 RegisteredUserHandler: User registration status - is_registered={user_status['is_registered']}, is_player={user_status['is_player']}, is_team_member={user_status['is_team_member']}"
            )

            # Use CrewAI system for registered users
            if self.crewai_system:
                logger.info("🔄 RegisteredUserHandler: Routing to CrewAI system")
                result = await self.crewai_system.execute_task(message.text, execution_context)
                return AgentResponse(message=result)
            else:
                # Use crew lifecycle manager as fallback
                logger.info("🔄 RegisteredUserHandler: Using crew lifecycle manager")
                from kickai.agents.crew_lifecycle_manager import get_crew_lifecycle_manager
                crew_lifecycle_manager = get_crew_lifecycle_manager()

                result = await crew_lifecycle_manager.execute_task(
                    team_id=self.team_id,
                    task_description=message.text,
                    execution_context=execution_context,
                )
                return AgentResponse(message=result)

        except Exception as e:
            logger.error(f"❌ Error in registered user handling: {e}")
            return AgentResponse(
                message="I encountered an error processing your request. Please try again.",
                success=False,
                error=str(e),
            )


class CommandHandler(MessageHandler):
    """Handles command messages."""

    def __init__(self, team_id: str, crewai_system=None):
        self.team_id = team_id
        self.crewai_system = crewai_system

    def can_handle(self, message: TelegramMessage) -> bool:
        """Check if this is a command message."""
        return message.text.startswith("/")

    async def handle(self, message: TelegramMessage) -> AgentResponse:
        """Handle command messages."""
        try:
            command_name = message.text.split()[0]  # Get the first word (the command)
            logger.info(f"🔄 CommandHandler: Processing command {command_name} in {message.chat_type.value}")

            # Check if command is available for this chat type
            try:
                from kickai.core.command_registry_initializer import (
                    get_initialized_command_registry,
                )

                registry = get_initialized_command_registry()
                chat_type_str = message.chat_type.value
                available_command = registry.get_command_for_chat(command_name, chat_type_str)
            except RuntimeError as e:
                if "Command registry not initialized" in str(e):
                    logger.critical(
                        "💥 CRITICAL SYSTEM ERROR: Command registry not accessible in CommandHandler - this is a major system failure"
                    )
                    logger.critical(
                        "🚨 The system cannot function without the command registry. This indicates a serious initialization failure."
                    )
                    logger.critical(
                        "🛑 Failing fast to prevent unsafe command execution without validation"
                    )
                    raise RuntimeError(
                        f"CRITICAL SYSTEM ERROR: Command registry not accessible in CommandHandler. "
                        f"This is a major system failure that prevents safe command execution. "
                        f"Original error: {e}"
                    )
                else:
                    raise

            if not available_command:
                # Command not found - this is NOT a critical error, just an unrecognized command
                logger.info(f"ℹ️ Command {command_name} not found in registry - treating as unrecognized command")
                return await self._handle_unrecognized_command(command_name, message.chat_type, message.username)

            # For commands, use simplified user flow determination
            # Default to registered user for commands
            user_flow = UserFlowType.REGISTERED_USER

            # Handle unregistered user flows
            if user_flow == UserFlowType.UNREGISTERED_USER:
                logger.info("🔄 CommandHandler: Unregistered user command flow")
                # Simplified unregistered user handling
                return AgentResponse(
                    message="Please register first before using commands. Contact team leadership for assistance.",
                    success=False,
                    error="User not registered"
                )

            else:  # REGISTERED_USER
                # For registered users, route commands to CrewAI system
                logger.info("🔄 CommandHandler: Registered user command flow")
                registered_handler = RegisteredUserHandler(self.team_id, self.crewai_system)
                return await registered_handler.handle(message)

        except Exception as e:
            logger.error(f"❌ Error handling command: {e}")
            return AgentResponse(
                message="I encountered an error processing your command. Please try again.",
                success=False,
                error=str(e),
            )

    async def _handle_unrecognized_command(self, command_name: str, chat_type: ChatType, username: str) -> AgentResponse:
        """Handle unrecognized commands with helpful information."""
        try:
            logger.info(f"ℹ️ Handling unrecognized command: {command_name} in {chat_type.value} chat")
            
            # Get available commands for this chat type
            try:
                from kickai.core.command_registry_initializer import get_initialized_command_registry
                registry = get_initialized_command_registry()
                available_commands = registry.get_commands_for_chat_type(chat_type.value)
                
                # Format the response
                message_parts = [
                    f"❓ **Unrecognized Command: {command_name}**",
                    "",
                    f"🤖 I don't recognize the command `{command_name}`.",
                    "",
                    "📋 **Available Commands in this chat:**"
                ]
                
                # Group commands by feature
                commands_by_feature = {}
                for cmd in available_commands:
                    feature = cmd.feature.replace('_', ' ').title()
                    if feature not in commands_by_feature:
                        commands_by_feature[feature] = []
                    commands_by_feature[feature].append(cmd)
                
                # Add commands by feature
                for feature, commands in commands_by_feature.items():
                    message_parts.append(f"\n**{feature}:**")
                    for cmd in commands:
                        message_parts.append(f"• `{cmd.name}` - {cmd.description}")
                
                message_parts.extend([
                    "",
                    "💡 **Need Help?**",
                    f"• Use `/help` to see all available commands",
                    f"• Use `/help {command_name}` for detailed help on a specific command",
                    "• Contact team leadership for assistance",
                    "",
                    "🔍 **Did you mean?**",
                    "• Check for typos in the command name",
                    "• Some commands are only available in specific chat types",
                    "• Leadership commands are only available in leadership chat"
                ])
                
                return AgentResponse(
                    message="\n".join(message_parts),
                    success=False,
                    error="Unrecognized command"
                )
                
            except Exception as e:
                logger.error(f"❌ Error getting available commands for unrecognized command handling: {e}")
                # Fallback response
                return AgentResponse(
                    message=f"❓ **Unrecognized Command: {command_name}**\n\n"
                           f"🤖 I don't recognize the command `{command_name}`.\n\n"
                           f"💡 **Try these:**\n"
                           f"• Use `/help` to see all available commands\n"
                           f"• Check for typos in the command name\n"
                           f"• Contact team leadership for assistance",
                    success=False,
                    error="Unrecognized command"
                )
                
        except Exception as e:
            logger.error(f"❌ Error in unrecognized command handler: {e}")
            return AgentResponse(
                message=f"❓ **Unrecognized Command: {command_name}**\n\n"
                       f"🤖 I don't recognize this command. Use `/help` to see available commands.",
                success=False,
                error="Unrecognized command"
            )
