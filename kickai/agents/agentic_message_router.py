#!/usr/bin/env python3
"""
Agentic Message Router

This module provides centralized agentic message routing following CrewAI best practices.
ALL messages go through agents - no direct processing bypasses the agentic system.
"""

import asyncio
import time
from typing import Any, Protocol
from weakref import WeakSet

from loguru import logger

# Lazy imports to avoid circular dependencies
from kickai.core.context_types import create_context_from_telegram_message
from kickai.core.enums import ChatType
from kickai.core.types import AgentResponse, TelegramMessage, UserFlowType
from kickai.core.dependency_container import get_container
from kickai.utils.error_handling import (
    command_registry_error_handler,
    critical_system_error_handler,
    user_registration_check_handler,
)


class MessageRouterProtocol(Protocol):
    """Protocol for message routing to enable better testing and extensibility."""

    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """Route a message through the system."""
        ...

    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """Handle contact sharing messages."""
        ...


class ResourceManager:
    """Handles resource management and cleanup for the message router."""

    def __init__(self, max_concurrent: int = 10, max_requests_per_minute: int = 60):
        self.active_requests: WeakSet = WeakSet()
        self.request_timestamps: list[float] = []
        self.max_concurrent_requests = max_concurrent
        self.max_requests_per_minute = max_requests_per_minute
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        self.request_count = 0

    def add_request(self) -> object:
        """Add a new request and return a tracker."""
        tracker = type('RequestTracker', (), {})()  # Create a proper object that can be weak referenced
        self.active_requests.add(tracker)
        self.request_count += 1
        return tracker

    def remove_request(self, tracker: object) -> None:
        """Remove a request tracker."""
        self.active_requests.discard(tracker)

    def check_rate_limit(self) -> bool:
        """Check if within rate limits."""
        current_time = time.time()

        # Clean old timestamps
        self.request_timestamps = [
            ts for ts in self.request_timestamps
            if current_time - ts < 60
        ]

        if len(self.request_timestamps) >= self.max_requests_per_minute:
            return False

        self.request_timestamps.append(current_time)
        return True

    def check_concurrent_limit(self) -> bool:
        """Check if within concurrent request limits."""
        return len(self.active_requests) < self.max_concurrent_requests

    async def cleanup(self, force: bool = False) -> None:
        """Clean up resources periodically."""
        current_time = time.time()
        if not force and current_time - self.last_cleanup < self.cleanup_interval:
            return

        # Clean up old timestamps
        self.request_timestamps = [
            ts for ts in self.request_timestamps
            if current_time - ts < 60
        ]

        self.last_cleanup = current_time


class AgenticMessageRouter:
    """
    Centralized agentic message routing following CrewAI best practices.

    This router ensures that ALL messages go through the agentic system.
    No direct processing bypasses agents.
    """

    def __init__(
        self,
        team_id: str,
        crewai_system=None,
        resource_manager: ResourceManager | None = None
    ):
        # Input validation
        if not team_id or not isinstance(team_id, str):
            raise ValueError(f"team_id must be a non-empty string, got: {type(team_id).__name__}")

        self.team_id = team_id.strip()
        self.crewai_system = crewai_system
        # Simplified for 5-agent architecture - removed user_flow_agent and helper_agent
        # Lazy initialization to avoid circular dependencies
        self._crew_lifecycle_manager = None

        # Initialize state tracking for better error handling
        self._last_telegram_id: int | None = None
        self._last_username: str | None = None
        self._main_chat_id: str | None = None
        self._leadership_chat_id: str | None = None

        # Resource management (use dependency injection for testability)
        self._resource_manager = resource_manager or ResourceManager()

        self._setup_router()

    @property
    def crew_lifecycle_manager(self):
        """Lazy load crew lifecycle manager to avoid circular imports."""
        if self._crew_lifecycle_manager is None:
            from kickai.agents.crew_lifecycle_manager import get_crew_lifecycle_manager

            self._crew_lifecycle_manager = get_crew_lifecycle_manager()
        return self._crew_lifecycle_manager

    # Removed helper_agent property - functionality moved to HelpAssistantAgent in 5-agent system

    def _setup_router(self):
        """Set up the router configuration."""
        logger.info(f"🤖 AgenticMessageRouter initialized for team {self.team_id}")

    async def _check_rate_limits(self, telegram_id: int) -> bool:
        """
        Check if request is within rate limits.


            telegram_id: User's Telegram ID


    :return: True if request is allowed, False if rate limited
    :rtype: str  # TODO: Fix type
        """
        if not self._resource_manager.check_rate_limit():
            logger.warning(f"⚠️ Rate limit exceeded for team {self.team_id}, user {telegram_id}")
            return False
        return True

    async def _check_concurrent_requests(self) -> bool:
        """
        Check if we're within concurrent request limits.


    :return: True if request can be processed, False if limit exceeded
    :rtype: str  # TODO: Fix type
        """
        if not self._resource_manager.check_concurrent_limit():
            logger.warning(f"⚠️ Concurrent request limit exceeded for team {self.team_id}")
            return False
        return True

    async def _cleanup_resources(self, force: bool = False):
        """
        Clean up resources periodically.


            force: Force cleanup regardless of time
        """
        await self._resource_manager.cleanup(force)
        if force:
            logger.debug(f"🧹 Force cleaned up resources for team {self.team_id}")
        else:
            logger.debug(f"🧹 Cleaned up resources for team {self.team_id}")

    @critical_system_error_handler("AgenticMessageRouter.route_message")
    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """
        Route ALL messages through the agentic system.
        No direct processing bypasses agents.


            message: Telegram message to route


    :return: AgentResponse with the processed result
    :rtype: str  # TODO: Fix type
        """
        # Validate input message
        if not isinstance(message, TelegramMessage):
            raise TypeError(f"Expected TelegramMessage, got {type(message).__name__}")

        if not message.text or not isinstance(message.text, str):
            return AgentResponse(
                success=False,
                message="❌ Invalid message: missing or empty text",
                error="Invalid message format"
            )

        # Ensure telegram_id is properly typed
        if not isinstance(message.telegram_id, int):
            logger.warning(f"⚠️ telegram_id should be int, got {type(message.telegram_id)}")
            try:
                message.telegram_id = int(message.telegram_id)
            except (ValueError, TypeError):
                return AgentResponse(
                    success=False,
                    message="❌ Invalid user ID format",
                    error="Invalid telegram_id"
                )

        logger.info(
            f"🔄 AgenticMessageRouter: Routing message from {message.username} in {message.chat_type.value}"
        )

        # Check rate limits
        if not await self._check_rate_limits(message.telegram_id):
            return AgentResponse(
                success=False,
                message="⏰ Too many requests. Please wait a moment and try again.",
                error="Rate limit exceeded"
            )

        # Check concurrent request limits
        if not await self._check_concurrent_requests():
            return AgentResponse(
                success=False,
                message="🚦 System busy. Please try again in a moment.",
                error="Concurrent limit exceeded"
            )

        # Track this request
        request_tracker = self._resource_manager.add_request()

        try:
            # Periodic cleanup
            await self._cleanup_resources()

            # Check for new chat members event (invite link processing)
            if hasattr(message, 'raw_update') and message.raw_update:
                if self._is_new_chat_members_event(message.raw_update):
                    logger.info("🔗 AgenticMessageRouter: Detected new_chat_members event")
                    return await self.route_new_chat_members(message)

            # Extract command from message text if it's a slash command
            command = None
            if message.text.startswith("/"):
                command = message.text.split()[0]  # Get the first word (the command)
                logger.info(f"🔄 AgenticMessageRouter: Detected command: {command}")

            # Check if this is a helper system command
            if self._is_helper_command(command):
                logger.info(f"🔄 AgenticMessageRouter: Routing to Helper Agent: {command}")
                return await self.route_help_request(message)

            # Check if command is available for this chat type (for registered users)
            if command and not self._is_helper_command(command):
                await self._check_command_availability(command, message.chat_type, message.username)

            # Determine user flow - check if user is registered
            user_flow_result = await self._check_user_registration_status(message.telegram_id)

            # Handle unregistered users
            if user_flow_result == UserFlowType.UNREGISTERED_USER:
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

        finally:
            # Always clean up request tracking
            try:
                self._resource_manager.remove_request(request_tracker)
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Error cleaning up request tracker: {cleanup_error}")

    @command_registry_error_handler
    async def _check_command_availability(self, command: str, chat_type: ChatType, username: str) -> None:
        """
        Check if a command is available for the given chat type.


            command: Command to check
            chat_type: Type of chat
            username: Username for context


    :return: None if command is available, raises exception if not found
    :rtype: str  # TODO: Fix type
        """
        from kickai.core.command_registry_initializer import get_initialized_command_registry

        registry = get_initialized_command_registry()
        chat_type_str = chat_type.value
        available_command = registry.get_command_for_chat(command, chat_type_str)

        if not available_command:
            # Command not found - this is NOT a critical error, just an unrecognized command
            logger.info(f"ℹ️ Command {command} not found in registry - treating as unrecognized command")
            return await self._handle_unrecognized_command(command, chat_type, username)

    @user_registration_check_handler
    async def _check_user_registration_status(self, telegram_id: int) -> UserFlowType:
        """
        Check if a user is registered as a player or team member.

        Args:
            telegram_id: Telegram ID of the user

        Returns:
            UserFlowType indicating if user is registered or not

        Raises:
            RuntimeError: If critical services are unavailable
            ConnectionError: If database connection fails
        """
        # Validate telegram_id as positive integer
        if not isinstance(telegram_id, int) or telegram_id <= 0:
            logger.error(f"❌ Invalid telegram_id: {telegram_id}. Must be a positive integer.")
            return UserFlowType.UNREGISTERED_USER

        # Get services from dependency container with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                container = get_container()
                player_service = container.get_service("PlayerService")
                team_service = container.get_service("TeamService")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.critical(f"💥 Failed to get services after {max_retries} attempts: {e}")
                    raise RuntimeError(f"Service initialization failed: {e}")
                logger.warning(f"⚠️ Service retrieval attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff

        # Check if user exists as player or team member with timeout
        try:
            # Use asyncio.wait_for to add timeout protection
            player_task = asyncio.create_task(
                player_service.get_player_by_telegram_id(telegram_id, self.team_id)
            )
            team_member_task = asyncio.create_task(
                team_service.get_team_member_by_telegram_id(self.team_id, telegram_id)
            )

            # Wait for both with timeout
            is_player, is_team_member = await asyncio.wait_for(
                asyncio.gather(player_task, team_member_task, return_exceptions=True),
                timeout=10.0  # 10 second timeout
            )

            # Handle exceptions in results
            if isinstance(is_player, Exception):
                logger.warning(f"⚠️ Player lookup failed: {is_player}")
                is_player = None
            if isinstance(is_team_member, Exception):
                logger.warning(f"⚠️ Team member lookup failed: {is_team_member}")
                is_team_member = None

        except TimeoutError:
            logger.error(f"⏰ User registration check timed out for user {telegram_id}")
            # In case of timeout, assume unregistered to fail safe
            return UserFlowType.UNREGISTERED_USER
        except Exception as e:
            logger.error(f"❌ Error during user registration check: {e}")
            # In case of error, assume unregistered to fail safe
            return UserFlowType.UNREGISTERED_USER

        return UserFlowType.REGISTERED_USER if (is_player or is_team_member) else UserFlowType.UNREGISTERED_USER

    async def _handle_unrecognized_command(self, command_name: str, chat_type: ChatType, username: str) -> AgentResponse:
        """Handle unrecognized commands with helpful information."""
        try:
            logger.info(f"ℹ️ Handling unrecognized command: {command_name} in {chat_type.value} chat")

            # Get available commands for this chat type
            try:
                from kickai.core.command_registry_initializer import (
                    get_initialized_command_registry,
                )
                registry = get_initialized_command_registry()
                available_commands = registry.get_commands_for_chat_type(chat_type.value)

                # Format the response
                message_parts = [
                    f"❓ Unrecognized Command: {command_name}",
                    "",
                    f"🤖 I don't recognize the command `{command_name}`.",
                    "",
                    "📋 Available Commands in this chat:"
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
                    message_parts.append(f"\n{feature}:")
                    for cmd in commands:
                        message_parts.append(f"• `{cmd.name}` - {cmd.description}")

                message_parts.extend([
                    "",
                    "💡 Need Help?",
                    "• Use `/help` to see all available commands",
                    f"• Use `/help {command_name}` for detailed help on a specific command",
                    "• Contact team leadership for assistance",
                    "",
                    "🔍 Did you mean?",
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
                    message=f"❓ Unrecognized Command: {command_name}\n\n"
                           f"🤖 I don't recognize the command `{command_name}`.\n\n"
                           f"💡 Try these:\n"
                           f"• Use `/help` to see all available commands\n"
                           f"• Check for typos in the command name\n"
                           f"• Contact team leadership for assistance",
                    success=False,
                    error="Unrecognized command"
                )

        except Exception as e:
            logger.error(f"❌ Error in unrecognized command handler: {e}")
            return AgentResponse(
                message=f"❓ Unrecognized Command: {command_name}\n\n"
                       f"🤖 I don't recognize this command. Use `/help` to see available commands.",
                success=False,
                error="Unrecognized command"
            )

    @critical_system_error_handler("AgenticMessageRouter.route_contact_share")
    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """
        Route contact sharing messages for phone number linking.


            message: Telegram message with contact information


    :return: AgentResponse with the linking result
    :rtype: str  # TODO: Fix type
        """
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
            phone=message.contact_phone, telegram_id=message.telegram_id, username=message.username
        )

        if linked_player:
            return AgentResponse(
                success=True,
                message=f"✅ Successfully linked to your player record: {linked_player.name} ({linked_player.player_id})",
                error=None,
            )
        else:
            return AgentResponse(
                success=False,
                message="❌ No player record found with that phone number. Please contact team leadership.",
                error="No matching player record",
            )

    def _get_unregistered_user_message(self, chat_type: ChatType, username: str) -> str:
        """Get message for unregistered users based on chat type."""
        from kickai.core.constants import BOT_VERSION

        if chat_type == ChatType.LEADERSHIP:
            return f"""👋 Welcome to KICKAI Leadership for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🤔 You're not registered as a team member yet.

📞 Contact Team Administrator
You need to be added as a team member by the team administrator.

💡 What to do:
1. Contact the team administrator
2. Ask them to add you as a team member using the /addmember command
3. They'll send you an invite link to join the leadership chat
4. Once added, you can access leadership functions

❓ Got here by mistake?
If you're not part of the team leadership, please leave this chat.

Need help? Contact the team administrator."""
        else:
            return f"""👋 Welcome to KICKAI for {self.team_id}, {username}!

🤖 KICKAI v{BOT_VERSION} - Your AI-powered football team assistant

🤔 You're not registered as a player yet.

📞 Contact Team Leadership
You need to be added as a player by someone in the team's leadership.

💬 What to do:
1. Reach out to someone in the team's leadership chat
2. Ask them to add you as a player using the /addplayer command
3. They'll send you an invite link to join the main chat
4. Once added, you can register with your full details

❓ Got here by mistake?
If you're not interested in joining the team, you can leave this chat.

🤖 Need help?
Use /help to see available commands or ask me questions!"""

    async def _process_with_crewai_system(self, message: TelegramMessage) -> AgentResponse:
        """
        Route registered user messages to specialized agents.


            message: Telegram message to route


    :return: AgentResponse with the processed result
    :rtype: str  # TODO: Fix type
        """
        try:
            # Get detailed registration status from actual services
            try:
                container = get_container()
                player_service = container.get_service("PlayerService")
                team_service = container.get_service("TeamService")
            except Exception as e:
                logger.warning(f"⚠️ Could not get services for registration check: {e}")
                player_service = None
                team_service = None

            is_player = False
            is_team_member = False

            # Check actual registration status
            if player_service:
                try:
                    player = await player_service.get_player_by_telegram_id(
                        message.telegram_id, message.team_id
                    )
                    is_player = player is not None
                    logger.debug(f"🔍 Player check for {message.telegram_id}: {is_player}")
                except Exception as e:
                    logger.warning(f"⚠️ Player lookup failed: {e}")
                    pass

            if team_service:
                try:
                    team_member = await team_service.get_team_member_by_telegram_id(
                        message.team_id, message.telegram_id
                    )
                    is_team_member = team_member is not None
                    logger.debug(f"🔍 Team member check for {message.telegram_id}: {is_team_member}")
                except Exception as e:
                    logger.warning(f"⚠️ Team member lookup failed: {e}")
                    pass

            # Determine registration status based on actual data, not chat type
            is_registered = is_player or is_team_member

            # Log the actual registration status
            logger.info(
                f"🔄 AgenticMessageRouter: Actual registration status - is_player={is_player}, is_team_member={is_team_member}, is_registered={is_registered}"
            )

            # Create standardized context for CrewAI system
            standardized_context = create_context_from_telegram_message(
                telegram_id=message.telegram_id,
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

            # Store last identifiers for dynamic help fallback
            self._last_telegram_id = message.telegram_id
            self._last_username = message.username

            logger.info(
                f"🔄 AgenticMessageRouter: User registration status - is_registered={is_registered}, is_player={is_player}, is_team_member={is_team_member}"
            )

            # Always use crew lifecycle manager - no fallback needed
            logger.info("🔄 AgenticMessageRouter: Routing to crew lifecycle manager")
            result = await self.crew_lifecycle_manager.execute_task(
                team_id=self.team_id,
                task_description=message.text,
                execution_context=execution_context,
            )
            return AgentResponse(success=True, message=result)

        except Exception as e:
            logger.error(f"❌ Error routing to specialized agent: {e}")
            # Re-raise the exception instead of providing a fallback
            raise

    def convert_telegram_update_to_message(
        self, update: Any, command_name: str | None = None
    ) -> TelegramMessage:
        """
        Convert Telegram update to domain message.


            update: Telegram update object
            command_name: Optional command name for command messages


    :return: TelegramMessage domain object
    :rtype: str  # TODO: Fix type
        """
        try:
            telegram_id = update.effective_user.id  # Keep as integer - Telegram's native type
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
                    update.message.contact.user_id  # Keep as integer
                    if update.message.contact.user_id
                    else telegram_id
                )

            return TelegramMessage(
                telegram_id=telegram_id,
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

    async def shutdown(self) -> None:
        """
        Gracefully shutdown the router and clean up resources.

        This should be called when the application is shutting down
        to ensure proper cleanup of resources and connections.
        """
        logger.info(f"🔄 Shutting down AgenticMessageRouter for team {self.team_id}")

        try:
            # Force cleanup of all resources
            await self._cleanup_resources(force=True)

            # Clear state variables
            self._last_telegram_id = None
            self._last_username = None

            # Reset crew lifecycle manager to allow garbage collection
            self._crew_lifecycle_manager = None

            logger.info(f"✅ AgenticMessageRouter shutdown complete for team {self.team_id}")

        except Exception as e:
            logger.error(f"❌ Error during AgenticMessageRouter shutdown: {e}")
            raise

    def get_metrics(self) -> dict[str, Any]:
        """
        Get current metrics for monitoring and debugging.


    :return: Dictionary containing current metrics
    :rtype: str  # TODO: Fix type
        """
        return {
            "team_id": self.team_id,
            "active_requests": len(self._resource_manager.active_requests),
            "total_requests": self._resource_manager.request_count,
            "rate_limit_window": len(self._resource_manager.request_timestamps),
            "max_concurrent": self._resource_manager.max_concurrent_requests,
            "max_requests_per_minute": self._resource_manager.max_requests_per_minute,
            "last_cleanup": self._resource_manager.last_cleanup,
            "last_telegram_id": self._last_telegram_id,
            "last_username": self._last_username,
        }

    def _looks_like_phone_number(self, text: str) -> bool:
        """
        Check if text looks like a phone number with security considerations.


            text: Input text to check


    :return: True if text looks like a valid phone number, False otherwise
    :rtype: str  # TODO: Fix type
        """
        if not text or not isinstance(text, str):
            return False

        # Security: Limit input length to prevent DoS attacks
        if len(text.strip()) > 50 or len(text.strip()) < 10:
            return False

        # Security: Only allow known safe characters
        allowed_chars = set("0123456789+()-. ")
        if not all(c in allowed_chars for c in text):
            logger.warning("⚠️ Phone number validation: disallowed characters in input")
            return False

        # Remove common separators and check if it's mostly digits
        cleaned = "".join(c for c in text if c.isdigit() or c in "+()-")

        # Must have at least 10 digits but not more than 15 (international standard)
        digit_count = sum(1 for c in cleaned if c.isdigit())
        if digit_count < 10 or digit_count > 15:
            return False

        # Must start with + or be all digits (after removing separators)
        digits_only = "".join(c for c in cleaned if c.isdigit())
        if cleaned.startswith("+") or digits_only == cleaned.replace("+", "").replace("-", "").replace("(", "").replace(")", ""):
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
                phone=message.text.strip(), telegram_id=message.telegram_id, username=message.username
            )

            if linked_player:
                return AgentResponse(
                    success=True,
                    message=f"✅ Successfully linked to your player record: {linked_player.name} ({linked_player.player_id})\n\n🎉 Welcome to the team! You can now use all team features.",
                    error=None,
                )
            else:
                return AgentResponse(
                    success=False,
                    message="❌ No player record found with that phone number.\n\n💡 What to do:\n1. Make sure you were added by team leadership using /addplayer\n2. Check that the phone number matches what was used when you were added\n3. Contact team leadership if you need help",
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

    def _is_helper_command(self, command: str) -> bool:
        """
        Check if a command is a helper system command.


            command: The command to check


    :return: True if it's a helper command, False otherwise
    :rtype: str  # TODO: Fix type
        """
        # Helper system is now proactive - no command-driven interactions
        return False

    async def route_help_request(self, message: TelegramMessage) -> AgentResponse:
        """
        Route help requests to the Helper Agent using CrewAI tasks.


            message: The Telegram message containing the help request


    :return: AgentResponse with the helper's response
    :rtype: str  # TODO: Fix type
        """
        try:
            logger.info("🔄 AgenticMessageRouter: Routing help request to Helper Agent")

            # Extract the query from the message
            query = message.text
            if query.startswith("/"):
                # Remove the command and get the rest as the query
                parts = query.split(" ", 1)
                if len(parts) > 1:
                    query = parts[1]
                else:
                    query = "general help"

            # Create context for the helper agent
            context = {
                "telegram_id": message.telegram_id,
                "team_id": self.team_id,
                "chat_type": message.chat_type.value,
                "username": message.username,
                "query": query,
            }

            # Execute help task using the HELP_ASSISTANT agent through CrewAI system
            help_response = await self.crewai_system.execute_task(
                task_description=f"/help {query}",
                execution_context=context
            )

            return AgentResponse(success=True, message=help_response, error=None)

        except Exception as e:
            logger.error(f"❌ Error routing help request: {e}")
            return AgentResponse(
                success=False,
                message="❌ Sorry, I encountered an error while helping you. Please try again.",
                error=str(e),
            )

    async def send_proactive_suggestions(self, telegram_id: int, team_id: str) -> None:
        """
        Send proactive suggestions based on user behavior.


            telegram_id: The user's Telegram ID (as integer)
            team_id: The team's ID
        """
        try:
            # Get the reminder service using the new interface
            from kickai.core.dependency_container import get_container

            container = get_container()
            reminder_service = container.get_service("IReminderService")

            if reminder_service:
                # Schedule periodic reminders
                await reminder_service.schedule_periodic_reminders(telegram_id, team_id)

        except Exception as e:
            logger.error(f"Error sending proactive suggestions to user {telegram_id}: {e}")

    async def check_and_send_reminders(self, telegram_id: int, team_id: str) -> None:
        """
        Check and send pending reminders for a user.


            telegram_id: The user's Telegram ID (as integer)
            team_id: The team's ID
        """
        try:
            # Get the reminder service using the new interface
            from kickai.core.dependency_container import get_container

            container = get_container()
            reminder_service = container.get_service("IReminderService")

            if reminder_service:
                # Get pending reminders
                reminders = await reminder_service.get_pending_reminders(telegram_id, team_id)

                # Send reminders (in a full implementation, this would send via Telegram)
                for reminder in reminders:
                    logger.info(f"Sending reminder to user {telegram_id}: {reminder.title}")
                    # TODO: Implement actual Telegram message sending

        except Exception as e:
            logger.error(f"Error checking reminders for user {telegram_id}: {e}")

    def _get_unrecognized_command_message(self, command: str, chat_type: ChatType) -> str:
        """Return dynamic help from FINAL_HELP_RESPONSE tool instead of hardcoded lists."""
        try:
            from kickai.features.shared.domain.tools.help_tools import final_help_response
            # Use dynamic help tailored to chat context; preserve emojis and formatting
            # Convert telegram_id to string for the help tool (which expects string)
            telegram_id_str = str(self._last_telegram_id) if hasattr(self, "_last_telegram_id") and self._last_telegram_id else "0"
            return final_help_response(
                chat_type=chat_type.value,
                telegram_id=telegram_id_str,
                team_id=str(self.team_id),
                username=str(getattr(self, "_last_username", "user")),
            )
        except Exception:
            # Minimal safe fallback
            return (
                f"🤔 I don't recognize the command `{command}`.\n\n"
                f"💡 Try `/help` to see available commands for this chat."
            )

    def _is_new_chat_members_event(self, raw_update) -> bool:
        """
        Check if the raw update contains a new_chat_members event.


            raw_update: Raw update data from Telegram or mock service


    :return: True if this is a new_chat_members event, False otherwise
    :rtype: str  # TODO: Fix type
        """
        try:
            # Check for mock Telegram format
            if isinstance(raw_update, dict):
                # Mock telegram format
                if raw_update.get("type") == "new_chat_members":
                    return True
                # Check for new_chat_members field in message
                if "new_chat_members" in raw_update:
                    return True

            # Check for real Telegram format
            if hasattr(raw_update, 'message') and raw_update.message:
                if hasattr(raw_update.message, 'new_chat_members') and raw_update.message.new_chat_members:
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error checking for new_chat_members event: {e}")
            return False

    async def route_new_chat_members(self, message: TelegramMessage) -> AgentResponse:
        """
        Route new chat members events for invite link processing.


            message: Telegram message containing new_chat_members event


    :return: AgentResponse with the processing result
    :rtype: str  # TODO: Fix type
        """
        try:
            logger.info("🔗 Processing new_chat_members event for invite link validation")

            # Extract new members from the update
            new_members = self._extract_new_members(message.raw_update)
            if not new_members:
                logger.warning("⚠️ No new members found in new_chat_members event")
                return AgentResponse(
                    success=False,
                    message="No new members found in event",
                    error="No new members"
                )

            # Process each new member (usually just one for invite links)
            for member in new_members:
                telegram_id = member.get("id", 0)  # Keep as int
                username = member.get("username") or member.get("first_name", "Unknown")

                logger.info(f"🔗 Processing new member: {username} (ID: {telegram_id})")

                # Extract invite link information
                invite_link = self._extract_invite_link_from_event(message.raw_update)
                invite_id = self._extract_invite_id_from_event(message.raw_update)

                if invite_id:
                    logger.info(f"🔗 Found invite_id in event: {invite_id}")
                    # Process invite link validation
                    return await self._process_invite_link_validation(
                        invite_id=invite_id,
                        invite_link=invite_link,
                        telegram_id=telegram_id,
                        username=username,
                        chat_id=message.chat_id,
                        chat_type=message.chat_type
                    )
                else:
                    logger.info("🔗 No invite context found, treating as regular new member")
                    # Regular new member welcome (no invite link)
                    return await self._handle_regular_new_member(
                        telegram_id=telegram_id,
                        username=username,
                        chat_type=message.chat_type
                    )

            # Fallback response
            return AgentResponse(
                success=True,
                message="👋 Welcome to the team!",
                error=None
            )

        except Exception as e:
            logger.error(f"❌ Error processing new_chat_members event: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your join. Please contact team leadership.",
                error=str(e)
            )

    def _extract_new_members(self, raw_update) -> list:
        """Extract new members from the raw update."""
        try:
            # Mock Telegram format
            if isinstance(raw_update, dict):
                if "new_chat_members" in raw_update:
                    return raw_update["new_chat_members"]

            # Real Telegram format
            if hasattr(raw_update, 'message') and raw_update.message:
                if hasattr(raw_update.message, 'new_chat_members'):
                    members = raw_update.message.new_chat_members
                    # Convert Telegram User objects to dict format
                    if members:
                        return [
                            {
                                "id": member.id,
                                "username": member.username,
                                "first_name": member.first_name,
                                "last_name": member.last_name
                            }
                            for member in members
                        ]

            return []

        except Exception as e:
            logger.error(f"❌ Error extracting new members: {e}")
            return []

    def _extract_invite_link_from_event(self, raw_update) -> str | None:
        """Extract invite link from the event if available."""
        try:
            # Mock format may have invitation_context
            if isinstance(raw_update, dict):
                invitation_context = raw_update.get("invitation_context", {})
                if invitation_context:
                    return invitation_context.get("invite_link")

            # For real Telegram, we'd need to store the invite link differently
            # This is a limitation of the Telegram API - we can't get the specific invite link used
            return None

        except Exception as e:
            logger.error(f"❌ Error extracting invite link: {e}")
            return None

    def _extract_invite_id_from_event(self, raw_update) -> str | None:
        """Extract invite ID from the event."""
        try:
            # Mock format with invitation_context
            if isinstance(raw_update, dict):
                invitation_context = raw_update.get("invitation_context", {})
                if invitation_context:
                    invite_id = invitation_context.get("invite_id")
                    if invite_id:
                        logger.info(f"🔗 Found invitation context with invite_id: {invite_id}")
                        return invite_id

                # Fallback to check _invitation_data (backup field)
                if hasattr(raw_update, '_invitation_data'):
                    invitation_data = getattr(raw_update, '_invitation_data', {})
                    invite_id = invitation_data.get("invite_id")
                    if invite_id:
                        logger.info(f"🔗 Found backup invitation data with invite_id: {invite_id}")
                        return invite_id

            logger.warning("⚠️ No invitation context found, using default invite_id")
            return None

        except Exception as e:
            logger.error(f"❌ Error extracting invite ID: {e}")
            return None

    async def _process_invite_link_validation(
        self,
        invite_id: str,
        invite_link: str | None,
        telegram_id: int,
        username: str,
        chat_id: str,
        chat_type: ChatType
    ) -> AgentResponse:
        """Process invite link validation and player linking."""
        try:
            logger.info(f"🔗 Processing invitation link - invite_id: {invite_id}, telegram_id: {telegram_id}, chat_type: {chat_type.value}")

            # Get invite link service
            from kickai.core.dependency_container import get_container
            from kickai.features.communication.domain.services.invite_link_service import (
                InviteLinkService,
            )

            container = get_container()
            database = container.get_database()

            invite_service = InviteLinkService(database=database)

            # Validate and use the invite link (pass invite_id as invite_link for direct lookup)
            # Convert telegram_id to string as the service expects
            invite_data = await invite_service.validate_and_use_invite_link(
                invite_link=invite_id,  # Pass invite_id directly
                user_id=str(telegram_id),  # Convert to string for the service
                username=username,
                secure_data=None
            )

            if not invite_data:
                logger.warning(f"❌ Invalid or expired invite link: {invite_id}")
                return AgentResponse(
                    success=False,
                    message="❌ Invalid or expired invite link. Please contact team leadership for a new invitation.",
                    error="Invalid invite link"
                )

            # Extract player information from invite
            player_phone = invite_data.get("player_phone")
            player_name = invite_data.get("player_name")
            member_phone = invite_data.get("member_phone")
            member_name = invite_data.get("member_name")

            # Determine if this is a player or team member invite
            if player_phone and player_name:
                return await self._process_player_invite_link(
                    player_phone=player_phone,
                    player_name=player_name,
                    telegram_id=telegram_id,
                    username=username,
                    invite_data=invite_data
                )
            elif member_phone and member_name:
                return await self._process_team_member_invite_link(
                    member_phone=member_phone,
                    member_name=member_name,
                    telegram_id=telegram_id,
                    username=username,
                    invite_data=invite_data
                )
            else:
                logger.warning(f"⚠️ Invite data missing required fields: {invite_data}")
                return AgentResponse(
                    success=False,
                    message="❌ Invalid invite data. Please contact team leadership.",
                    error="Missing invite data fields"
                )

        except Exception as e:
            logger.error(f"❌ Error processing invite link validation: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your invitation. Please contact team leadership.",
                error=str(e)
            )

    async def _process_player_invite_link(
        self,
        player_phone: str,
        player_name: str,
        telegram_id: int,
        username: str,
        invite_data: dict
    ) -> AgentResponse:
        """Process player invite link and link the user."""
        try:
            # Use PlayerLinkingService to link the user
            from kickai.features.player_registration.domain.services.player_linking_service import (
                PlayerLinkingService,
            )

            linking_service = PlayerLinkingService(self.team_id)

            # Link the user by phone number
            linked_player = await linking_service.link_telegram_user_by_phone(
                phone=player_phone,
                telegram_id=telegram_id,
                username=username
            )

            if linked_player:
                logger.info(f"✅ Successfully linked player {player_name} to user {telegram_id}")
                return AgentResponse(
                    success=True,
                    message=f"🎉 Welcome to the team, {player_name}!\n\n✅ Your Telegram account has been successfully linked to your player record.\n\n⚽ You can now use all team features. Try /help to see what you can do!",
                    error=None
                )
            else:
                logger.warning(f"❌ Failed to link player {player_name} to user {telegram_id}")
                return AgentResponse(
                    success=False,
                    message=f"❌ Unable to link your account to the player record for {player_name}.\n\n📞 Please contact team leadership for assistance.",
                    error="Player linking failed"
                )

        except Exception as e:
            logger.error(f"❌ Error processing player invite: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error linking your player account. Please contact team leadership.",
                error=str(e)
            )

    async def _process_team_member_invite_link(
        self,
        member_phone: str,
        member_name: str,
        telegram_id: int,
        username: str,
        invite_data: dict
    ) -> AgentResponse:
        """Process team member invite link and link the user."""
        try:
            # TODO: Implement team member linking service
            # For now, provide a basic welcome message
            logger.info(f"🔗 Processing team member invite for {member_name}")

            return AgentResponse(
                success=True,
                message=f"👋 Welcome to the leadership team, {member_name}!\n\n✅ You have joined the leadership chat.\n\n📋 You can now manage team operations. Try /help to see available commands.",
                error=None
            )

        except Exception as e:
            logger.error(f"❌ Error processing team member invite: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing your team member invitation. Please contact the team administrator.",
                error=str(e)
            )

    async def _handle_regular_new_member(
        self,
        telegram_id: int,
        username: str,
        chat_type: ChatType
    ) -> AgentResponse:
        """Handle new members who joined without an invite link."""
        try:
            if chat_type == ChatType.MAIN:
                return AgentResponse(
                    success=True,
                    message=f"👋 Welcome to the team, {username}!\n\n🤔 I notice you joined without an invite link. Please contact team leadership to get properly registered as a player.",
                    error=None
                )
            elif chat_type == ChatType.LEADERSHIP:
                return AgentResponse(
                    success=True,
                    message=f"👋 Welcome to the leadership chat, {username}!\n\n🤔 I notice you joined without an invite link. Please contact the team administrator to get properly registered as a team member.",
                    error=None
                )
            else:
                return AgentResponse(
                    success=True,
                    message=f"👋 Welcome, {username}!",
                    error=None
                )

        except Exception as e:
            logger.error(f"❌ Error handling regular new member: {e}")
            return AgentResponse(
                success=True,
                message=f"👋 Welcome, {username}!",
                error=None
            )
