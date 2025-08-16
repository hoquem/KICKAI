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
from kickai.core.types import (
    AgentResponse,
    TelegramMessage,
    UserFlowType,
)
from kickai.utils.dependency_utils import (
    get_player_service,
    get_team_service,
    validate_required_services,
)
from kickai.utils.error_handling import (
    command_registry_error_handler,
    critical_system_error_handler,
    user_registration_check_handler,
)

# CONSTANTS
DEFAULT_MAX_CONCURRENT = 10
DEFAULT_MAX_REQUESTS_PER_MINUTE = 60
DEFAULT_CLEANUP_INTERVAL = 300  # 5 minutes
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 0.1
DEFAULT_EXPONENTIAL_BACKOFF_FACTOR = 2

# RATE LIMITING
RATE_LIMIT_WINDOW_SECONDS = 60
PHONE_NUMBER_MAX_LENGTH = 50
PHONE_NUMBER_MIN_LENGTH = 10
PHONE_NUMBER_MAX_DIGITS = 15
PHONE_NUMBER_MIN_DIGITS = 10

# COMMAND PATTERNS
SLASH_COMMAND_PREFIX = "/"
CLEAR_COMMAND_NAMES = {"/help", "/ping", "/version", "/list", "help", "ping", "version", "list"}

# FOLLOWUP INDICATORS
FOLLOWUP_INDICATORS = [
    "yes",
    "no",
    "thanks",
    "ok",
    "sure",
    "please",
    "what about",
    "and",
    "also",
    "too",
    "again",
    "it",
    "that",
    "this",
    "them",
    "those",
]

# AMBIGUOUS REFERENCES
AMBIGUOUS_REFS = [
    "it",
    "that",
    "this",
    "them",
    "those",
    "he",
    "she",
    "they",
    "last",
    "previous",
    "next",
    "current",
    "recent",
]

# PHONE NUMBER VALIDATION
PHONE_ALLOWED_CHARS = set("0123456789+()-. ")

# ERROR MESSAGES
ERROR_MESSAGES = {
    "INVALID_TEAM_ID": "team_id must be a non-empty string, got: {type_name}",
    "INVALID_MESSAGE_TYPE": "Expected TelegramMessage, got {type_name}",
    "INVALID_MESSAGE_TEXT": "Invalid message: missing or empty text",
    "INVALID_USER_ID": "Invalid user ID format",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded for team {team_id}, user {telegram_id}",
    "CONCURRENT_LIMIT_EXCEEDED": "Concurrent request limit exceeded for team {team_id}",
    "SERVICE_INITIALIZATION_FAILED": "Service initialization failed: {error}",
    "USER_REGISTRATION_TIMEOUT": "User registration check timed out for user {telegram_id}",
    "USER_REGISTRATION_ERROR": "Error during user registration check: {error}",
    "PLAYER_LOOKUP_FAILED": "Player lookup failed: {error}",
    "TEAM_MEMBER_LOOKUP_FAILED": "Team member lookup failed: {error}",
    "NLP_PROCESSING_ERROR": "Error in NLP-enhanced processing: {error}",
    "COMMAND_ANALYSIS_ERROR": "Error in _is_clear_command: {error}",
    "COMMAND_CLARITY_ERROR": "Error in _classify_command_clarity: {error}",
    "COMMAND_EXTRACTION_ERROR": "Error extracting command from text: {error}",
    "COMMAND_REGISTRY_ERROR": "Error finding command in registry: {error}",
    "FOLLOWUP_CHECK_ERROR": "Error checking conversational follow-up: {error}",
    "AMBIGUOUS_REF_CHECK_ERROR": "Error checking ambiguous references: {error}",
    "PHONE_VALIDATION_ERROR": "Phone number validation: disallowed characters in input",
    "NEW_MEMBERS_EXTRACTION_ERROR": "Error extracting new members: {error}",
    "INVITE_LINK_EXTRACTION_ERROR": "Error extracting invite link: {error}",
    "INVITE_ID_EXTRACTION_ERROR": "Error extracting invite ID: {error}",
    "INVITE_CONTEXT_EXTRACTION_ERROR": "Error extracting invite context: {error}",
    "WELCOME_MESSAGE_ERROR": "Error creating enhanced welcome message: {error}",
    "CLEANUP_ERROR": "Error cleaning up request tracker: {error}",
}

# WARNING MESSAGES
WARNING_MESSAGES = {
    "TELEGRAM_ID_TYPE": "telegram_id should be int, got {type_name}",
    "CHAT_TYPE_STRING": "chat_type passed as string '{chat_type}', converting to enum",
    "CHAT_TYPE_NORMALIZATION_FAILED": "Failed to normalize chat_type '{chat_type}': {error}",
    "SERVICE_RETRIEVAL_FAILED": "Service retrieval attempt {attempt} failed: {error}",
    "PLAYER_LOOKUP_FAILED": "Player lookup failed: {error}",
    "TEAM_MEMBER_LOOKUP_FAILED": "Team member lookup failed: {error}",
    "SERVICE_UNAVAILABLE": "Could not get services for registration check: {error}",
    "COMMAND_REGISTRY_UNAVAILABLE": "Command registry not available",
    "INVALID_COMMAND_INPUT": "Invalid input for command analysis: {error}",
    "NO_INVITATION_CONTEXT": "No invitation context found, using default invite_id",
    "NO_INVITE_CONTEXT": "No invite context found in event",
}

# LOG MESSAGES
LOG_MESSAGES = {
    "ROUTER_INITIALIZED": "AgenticMessageRouter initialized for team {team_id}",
    "MESSAGE_ROUTING": "AgenticMessageRouter: Routing message from {username} in {chat_type}",
    "NEW_CHAT_MEMBERS_DETECTED": "AgenticMessageRouter: Detected new_chat_members event",
    "COMMAND_DETECTED": "AgenticMessageRouter: Detected command: {command}",
    "HELPER_COMMAND_ROUTING": "AgenticMessageRouter: Routing to Helper Agent: {command}",
    "UNREGISTERED_USER_FLOW": "AgenticMessageRouter: Unregistered user flow detected",
    "PHONE_NUMBER_DETECTED": "AgenticMessageRouter: Detected phone number in message from unregistered user",
    "REGISTERED_USER_FLOW": "AgenticMessageRouter: Registered user flow detected",
    "NLP_PROCESSING": "AgenticMessageRouter: Processing with NLP enhancement",
    "DIRECT_ROUTING": "AgenticMessageRouter: Direct routing for clear command",
    "USER_REGISTRATION_STATUS": "AgenticMessageRouter: User registration status - is_registered={is_registered}, is_player={is_player}, is_team_member={is_team_member}",
    "ACTUAL_REGISTRATION_STATUS": "AgenticMessageRouter: Actual registration status - is_player={is_player}, is_team_member={is_team_member}, is_registered={is_registered}",
    "SKIP_NLP_CLEAR_COMMAND": "Skipping NLP for clear command: {text}",
    "NLP_CONVERSATIONAL_FOLLOWUP": "NLP needed for conversational follow-up: {text}",
    "NLP_AMBIGUOUS_REFERENCES": "NLP needed for ambiguous references: {text}",
    "NLP_NATURAL_LANGUAGE": "NLP needed for natural language: {text}",
    "NLP_STARTING": "Starting NLP-enhanced message processing",
    "CONTACT_SHARE_PROCESSING": "AgenticMessageRouter: Processing contact share from {username}",
    "NEW_CHAT_MEMBERS_PROCESSING": "Processing new_chat_members event for auto-activation",
    "NEW_MEMBER_PROCESSING": "Processing new member for auto-activation: {username} (ID: {telegram_id})",
    "AUTO_ACTIVATION_SUCCESS": "Auto-activation successful for {username}: {player_name}",
    "AUTO_ACTIVATION_FAILED": "Auto-activation failed for {username}: {error}",
    "PLAYER_LINKING_SUCCESS": "Successfully linked player {player_name} to user {telegram_id}",
    "PLAYER_LINKING_FAILED": "Failed to link player {player_name} to user {telegram_id}",
    "TEAM_MEMBER_INVITE_PROCESSING": "Processing team member invite for {member_name}",
    "INVITATION_CONTEXT_FOUND": "Found invitation context with invite_id: {invite_id}",
    "BACKUP_INVITATION_DATA_FOUND": "Found backup invitation data with invite_id: {invite_id}",
    "INVITE_CONTEXT_EXTRACTED": "Extracted invite context: {keys}",
    "BACKUP_INVITE_CONTEXT_EXTRACTED": "Extracted backup invite context: {keys}",
    "FORCE_CLEANUP": "Force cleaned up resources for team {team_id}",
    "REGULAR_CLEANUP": "Cleaned up resources for team {team_id}",
    "ROUTER_SHUTDOWN": "Shutting down AgenticMessageRouter for team {team_id}",
    "ROUTER_SHUTDOWN_COMPLETE": "AgenticMessageRouter shutdown complete for team {team_id}",
    "ROUTER_SHUTDOWN_ERROR": "Error during AgenticMessageRouter shutdown: {error}",
}

# SUCCESS MESSAGES
SUCCESS_MESSAGES = {
    "WELCOME_LEADERSHIP": """👋 Welcome to KICKAI Leadership for {team_id}, {username}!

🤖 KICKAI v{version} - Your AI-powered football team assistant

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

Need help? Contact the team administrator.""",
    "WELCOME_MAIN": """👋 Welcome to KICKAI for {team_id}, {username}!

🤖 KICKAI v{version} - Your AI-powered football team assistant

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
Use /help to see available commands or ask me questions!""",
    "RATE_LIMIT_MESSAGE": "⏰ Too many requests. Please wait a moment and try again.",
    "CONCURRENT_LIMIT_MESSAGE": "🚦 System busy. Please try again in a moment.",
    "CONTACT_LINKING_SUCCESS": "✅ Successfully linked to your player record: {player_name} ({player_id})",
    "CONTACT_LINKING_FAILED": "❌ No player record found with that phone number. Please contact team leadership.",
    "PHONE_LINKING_SUCCESS": "✅ Successfully linked to your player record: {player_name} ({player_id})\n\n🎉 Welcome to the team! You can now use all team features.",
    "PHONE_LINKING_FAILED": "❌ No player record found with that phone number.\n\n💡 What to do:\n1. Make sure you were added by team leadership using /addplayer\n2. Check that the phone number matches what was used when you were added\n3. Contact team leadership if you need help",
    "PHONE_PROCESSING_ERROR": "❌ Error processing your phone number. Please try again or contact team leadership.",
    "TEAM_MEMBER_WELCOME": "👋 Welcome to the leadership team, {member_name}!\n\n✅ You have joined the leadership chat.\n\n📋 You can now manage team operations. Try /help to see available commands.",
    "REGULAR_MEMBER_WELCOME_MAIN": "👋 Welcome to the team, {username}!\n\n🤔 I notice you joined without an invite link. Please contact team leadership to get properly registered as a player.",
    "REGULAR_MEMBER_WELCOME_LEADERSHIP": "👋 Welcome to the leadership chat, {username}!\n\n🤔 I notice you joined without an invite link. Please contact the team administrator to get properly registered as a team member.",
    "REGULAR_MEMBER_WELCOME_DEFAULT": "👋 Welcome, {username}!",
    "HELP_RESPONSE": "Help for: {query}\n\nThis is a simplified help response. In production, this would be handled by the CrewAI system.",
    "HELP_ERROR": "❌ Sorry, I encountered an error while helping you. Please try again.",
    "INVALID_INVITE_LINK": "❌ Invalid or expired invite link. Please contact team leadership for a new invitation.",
    "INVALID_INVITE_DATA": "❌ Invalid invite data. Please contact team leadership.",
    "INVITE_PROCESSING_ERROR": "❌ Error processing your invitation. Please contact team leadership.",
    "TEAM_MEMBER_INVITE_ERROR": "❌ Error processing your team member invitation. Please contact the team administrator.",
    "NEW_CHAT_MEMBERS_ERROR": "❌ Error processing your join. Please contact team leadership.",
    "UNRECOGNIZED_COMMAND": "❓ **Unrecognized Command: {command}**\n\n🤖 I don't recognize the command `{command}`.\n\n💡 **Try these:**\n• Use `/help` to see all available commands\n• Check for typos in the command name\n• Contact team leadership for assistance",
    "UNRECOGNIZED_COMMAND_FALLBACK": "❓ **Unrecognized Command: {command}**\n\n🤖 I don't recognize this command. Use `/help` to see available commands.",
    "NO_CONTACT_INFO": "❌ No contact information found in message.",
    "NO_MATCHING_PLAYER": "No matching player record",
    "NO_NEW_MEMBERS": "No new members found in new_chat_members event",
    "NO_NEW_MEMBERS_ERROR": "No new members",
    "WELCOME_TEAM": "👋 Welcome to the team!",
    "WELCOME_BACK": "👋 Welcome back, {player_name}!\n\n✅ **ACCOUNT LINKED SUCCESSFULLY!**\nYour Telegram account is now connected to your player record.\n\n⚽ **YOU'RE ALL SET!**\n• Your status: **ACTIVE** \n• Team features: **AVAILABLE**\n• Ready for team activities!",
    "AUTO_ACTIVATION_WELCOME": "🎉 **WELCOME TO THE TEAM, {player_name_upper}!**\n\n✅ **AUTO-ACTIVATION SUCCESSFUL!**\nYour account has been automatically activated! No manual approval needed.\n\n⚽ **YOU'RE READY TO PARTICIPATE!**\n• Your status: **ACTIVE** \n• Team features: **UNLOCKED**\n• Match selection: **AVAILABLE**",
    "MAIN_CHAT_GUIDANCE": "\n\n📱 **MAIN CHAT FEATURES:**\n• `/myinfo` - Check your player status\n• `/list` - See active players for matches\n• `/help` - View all available commands\n• Share availability for upcoming matches\n\n🎯 **GET STARTED:**\n• Use `/myinfo` to verify your player details\n• Check `/help` for all available commands\n• Stay tuned for match announcements!",
    "LEADERSHIP_CHAT_GUIDANCE": "\n\n👥 **LEADERSHIP CHAT ACCESS:**\n• `/listmembers` - View full team roster\n• `/addplayer` - Add new players to the team\n• `/announce` - Send team-wide messages\n• Administrative tools and team management\n\n🎯 **LEADERSHIP RESPONSIBILITIES:**\n• Player management and approvals\n• Team communication coordination\n• Match organization and planning",
    "PRIVATE_CHAT_GUIDANCE": "\n\n💬 **PRIVATE CHAT FEATURES:**\n• Personal player information\n• Direct communication with team system\n• Private status updates and notifications\n\n🎯 **PRIVATE FEATURES:**\n• Use `/myinfo` for personal status\n• Private help and support\n• Confidential team communications",
    "KICKAI_FOOTER": "\n\n🤖 **KICKAI POWERED TEAM MANAGEMENT**\nWelcome to the future of football team organization! \n\nNeed help? Type `/help` anytime! ⚽💪",
    "WELCOME_FALLBACK": "🎉 Welcome to the team, {player_name}!\n\n✅ Your account has been successfully activated! \n\n⚽ You're now ready to participate in all team activities. Type `/help` to see what you can do!",
}


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

    def __init__(
        self,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        max_requests_per_minute: int = DEFAULT_MAX_REQUESTS_PER_MINUTE,
    ):
        self.active_requests: WeakSet = WeakSet()
        self.request_timestamps: list[float] = []
        self.max_concurrent_requests = max_concurrent
        self.max_requests_per_minute = max_requests_per_minute
        self.cleanup_interval = DEFAULT_CLEANUP_INTERVAL
        self.last_cleanup = time.time()
        self.request_count = 0

    def add_request(self) -> object:
        """Add a new request and return a tracker."""
        tracker = type(
            "RequestTracker", (), {}
        )()  # Create a proper object that can be weak referenced
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
            ts for ts in self.request_timestamps if current_time - ts < RATE_LIMIT_WINDOW_SECONDS
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
            ts for ts in self.request_timestamps if current_time - ts < RATE_LIMIT_WINDOW_SECONDS
        ]

        self.last_cleanup = current_time


class AgenticMessageRouter:
    """
    Centralized agentic message routing following CrewAI best practices.

    This router ensures that ALL messages go through the agentic system.
    No direct processing bypasses agents.
    """

    def __init__(
        self, team_id: str, crewai_system=None, resource_manager: ResourceManager | None = None
    ) -> None:
        # Input validation
        if not team_id or not isinstance(team_id, str):
            raise ValueError(
                ERROR_MESSAGES["INVALID_TEAM_ID"].format(type_name=type(team_id).__name__)
            )

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

    def _setup_router(self) -> None:
        """Set up the router configuration."""
        logger.info(LOG_MESSAGES["ROUTER_INITIALIZED"].format(team_id=self.team_id))

    async def _check_rate_limits(self, telegram_id: int) -> bool:
        """
        Check if request is within rate limits.

        Args:
            telegram_id: User's Telegram ID

        Returns:
            True if request is allowed, False if rate limited
        """
        if not self._resource_manager.check_rate_limit():
            logger.warning(
                ERROR_MESSAGES["RATE_LIMIT_EXCEEDED"].format(
                    team_id=self.team_id, telegram_id=telegram_id
                )
            )
            return False
        return True

    async def _check_concurrent_requests(self) -> bool:
        """
        Check if we're within concurrent request limits.

        Returns:
            True if request can be processed, False if limit exceeded
        """
        if not self._resource_manager.check_concurrent_limit():
            logger.warning(ERROR_MESSAGES["CONCURRENT_LIMIT_EXCEEDED"].format(team_id=self.team_id))
            return False
        return True

    async def _cleanup_resources(self, force: bool = False) -> None:
        """
        Clean up resources periodically.

        Args:
            force: Force cleanup regardless of time
        """
        await self._resource_manager.cleanup(force)
        if force:
            logger.debug(LOG_MESSAGES["FORCE_CLEANUP"].format(team_id=self.team_id))
        else:
            logger.debug(LOG_MESSAGES["REGULAR_CLEANUP"].format(team_id=self.team_id))

    @critical_system_error_handler("AgenticMessageRouter.route_message")
    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """
        Route ALL messages through the agentic system.
        No direct processing bypasses agents.

        Args:
            message: Telegram message to route

        Returns:
            AgentResponse with the processed result
        """
        # Validate input message
        if not isinstance(message, TelegramMessage):
            raise TypeError(
                ERROR_MESSAGES["INVALID_MESSAGE_TYPE"].format(type_name=type(message).__name__)
            )

        # Skip text validation for new_chat_members events (they have empty text)
        if not self._is_new_chat_members_event(message.raw_update):
            if not message.text or not isinstance(message.text, str):
                return AgentResponse(
                    success=False,
                    message=ERROR_MESSAGES["INVALID_MESSAGE_TEXT"],
                    error="Invalid message format",
                )

        # Ensure telegram_id is properly typed
        if not isinstance(message.telegram_id, int):
            logger.warning(
                WARNING_MESSAGES["TELEGRAM_ID_TYPE"].format(
                    type_name=type(message.telegram_id).__name__
                )
            )
            try:
                message.telegram_id = int(message.telegram_id)
            except (ValueError, TypeError):
                return AgentResponse(
                    success=False,
                    message=ERROR_MESSAGES["INVALID_USER_ID"],
                    error="Invalid telegram_id",
                )

        logger.info(
            LOG_MESSAGES["MESSAGE_ROUTING"].format(
                username=message.username, chat_type=message.chat_type.value
            )
        )

        # Check rate limits
        if not await self._check_rate_limits(message.telegram_id):
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["RATE_LIMIT_MESSAGE"],
                error="Rate limit exceeded",
            )

        # Check concurrent request limits
        if not await self._check_concurrent_requests():
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["CONCURRENT_LIMIT_MESSAGE"],
                error="Concurrent limit exceeded",
            )

        # Track this request
        request_tracker = self._resource_manager.add_request()

        try:
            # Periodic cleanup
            await self._cleanup_resources()

            # Check for new chat members event (invite link processing)
            if hasattr(message, "raw_update") and message.raw_update:
                if self._is_new_chat_members_event(message.raw_update):
                    logger.info(LOG_MESSAGES["NEW_CHAT_MEMBERS_DETECTED"])
                    return await self.route_new_chat_members(message)

            # Extract command from message text if it's a slash command
            command = None
            if message.text.startswith("/"):
                command = message.text.split()[0]  # Get the first word (the command)
                logger.info(LOG_MESSAGES["COMMAND_DETECTED"].format(command=command))

            # Check if this is a helper system command
            if self._is_helper_command(command):
                logger.info(LOG_MESSAGES["HELPER_COMMAND_ROUTING"].format(command=command))
                return await self.route_help_request(message)

            # Check if command is available for this chat type (for registered users)
            if command and not self._is_helper_command(command):
                await self._check_command_availability(command, message.chat_type, message.username)

            # Determine user flow - check if user is registered
            user_flow_result = await self._check_user_registration_status(message.telegram_id)

            # Handle unregistered users
            if user_flow_result == UserFlowType.UNREGISTERED_USER:
                logger.info(LOG_MESSAGES["UNREGISTERED_USER_FLOW"])

                # Check if the message looks like a phone number
                if self._looks_like_phone_number(message.text):
                    logger.info(LOG_MESSAGES["PHONE_NUMBER_DETECTED"])
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
            logger.info(LOG_MESSAGES["REGISTERED_USER_FLOW"])
            return await self._process_with_crewai_system(message)

        finally:
            # Always clean up request tracking
            try:
                self._resource_manager.remove_request(request_tracker)
            except Exception as cleanup_error:
                logger.warning(ERROR_MESSAGES["CLEANUP_ERROR"].format(error=cleanup_error))

    @command_registry_error_handler
    async def _check_command_availability(
        self, command: str, chat_type: ChatType, username: str
    ) -> None:
        """
        Check if a command is available for the given chat type.

        Args:
            command: Command to check
            chat_type: Type of chat
            username: Username for context

        Returns:
            None if command is available, raises exception if not found
        """
        from kickai.core.command_registry_initializer import get_initialized_command_registry

        registry = get_initialized_command_registry()

        # Handle case where chat_type might be a string instead of enum
        if isinstance(chat_type, str):
            logger.warning(WARNING_MESSAGES["CHAT_TYPE_STRING"].format(chat_type=chat_type))
            try:
                from kickai.core.constants.system_constants import SystemConstants

                chat_type = SystemConstants.normalize_chat_type(chat_type)
            except Exception as e:
                logger.error(
                    WARNING_MESSAGES["CHAT_TYPE_NORMALIZATION_FAILED"].format(
                        chat_type=chat_type, error=e
                    )
                )
                # Default to main chat type
                chat_type = ChatType.MAIN

        chat_type_str = chat_type.value
        available_command = registry.get_command_for_chat(command, chat_type_str)

        if not available_command:
            # Command not found - this is NOT a critical error, just an unrecognized command
            logger.info(
                f"Command {command} not found in registry - treating as unrecognized command"
            )
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
        # Normalize telegram_id to int
        if isinstance(telegram_id, str):
            try:
                telegram_id = int(telegram_id)
            except ValueError:
                logger.error(ERROR_MESSAGES["INVALID_USER_ID"])
                return UserFlowType.UNREGISTERED_USER

        # Validate that required services are available
        try:
            validate_required_services("PlayerService", "TeamService")
        except RuntimeError as e:
            logger.critical(ERROR_MESSAGES["SERVICE_UNAVAILABLE"].format(error=e))
            raise

        # Get services from dependency container with retries
        max_retries = DEFAULT_RETRY_ATTEMPTS
        for attempt in range(max_retries):
            try:
                player_service = get_player_service()
                team_service = get_team_service()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.critical(
                        ERROR_MESSAGES["SERVICE_RETRIEVAL_FAILED"].format(
                            attempt=attempt + 1, error=e
                        )
                    )
                    raise RuntimeError(
                        ERROR_MESSAGES["SERVICE_INITIALIZATION_FAILED"].format(error=e)
                    ) from None
                logger.warning(
                    WARNING_MESSAGES["SERVICE_RETRIEVAL_FAILED"].format(
                        attempt=attempt + 1, error=e
                    )
                )
                await asyncio.sleep(
                    DEFAULT_RETRY_DELAY * (DEFAULT_EXPONENTIAL_BACKOFF_FACTOR**attempt)
                )  # Exponential backoff

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
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )

            # Handle exceptions in results
            if isinstance(is_player, Exception):
                logger.warning(WARNING_MESSAGES["PLAYER_LOOKUP_FAILED"].format(error=is_player))
                is_player = None
            if isinstance(is_team_member, Exception):
                logger.warning(
                    WARNING_MESSAGES["TEAM_MEMBER_LOOKUP_FAILED"].format(error=is_team_member)
                )
                is_team_member = None

        except TimeoutError:
            logger.error(
                ERROR_MESSAGES["USER_REGISTRATION_TIMEOUT"].format(telegram_id=telegram_id)
            )
            # In case of timeout, assume unregistered to fail safe
            return UserFlowType.UNREGISTERED_USER
        except Exception as e:
            logger.error(ERROR_MESSAGES["USER_REGISTRATION_ERROR"].format(error=e))
            # In case of error, assume unregistered to fail safe
            return UserFlowType.UNREGISTERED_USER

        return (
            UserFlowType.REGISTERED_USER
            if (is_player or is_team_member)
            else UserFlowType.UNREGISTERED_USER
        )

    async def _handle_unrecognized_command(
        self, command_name: str, chat_type: ChatType, username: str
    ) -> AgentResponse:
        """Handle unrecognized commands with helpful information."""
        try:
            # Handle case where chat_type might be a string instead of enum
            if isinstance(chat_type, str):
                logger.warning(WARNING_MESSAGES["CHAT_TYPE_STRING"].format(chat_type=chat_type))
                try:
                    from kickai.core.constants.system_constants import SystemConstants

                    chat_type = SystemConstants.normalize_chat_type(chat_type)
                except Exception as e:
                    logger.error(
                        WARNING_MESSAGES["CHAT_TYPE_NORMALIZATION_FAILED"].format(
                            chat_type=chat_type, error=e
                        )
                    )
                    # Default to main chat type
                    chat_type = ChatType.MAIN

            logger.info(f"Handling unrecognized command: {command_name} in {chat_type.value} chat")

            # Get available commands for this chat type
            try:
                from kickai.core.command_registry_initializer import (
                    get_initialized_command_registry,
                )

                registry = get_initialized_command_registry()
                available_commands = registry.get_commands_by_chat_type(chat_type.value)

                # Format the response
                message_parts = [
                    f"❓ **Unrecognized Command: {command_name}**",
                    "",
                    f"🤖 I don't recognize the command `{command_name}`.",
                    "",
                    "📋 **Available Commands in this chat:**",
                ]

                # Group commands by feature
                commands_by_feature = {}
                for cmd in available_commands:
                    feature = cmd.feature.replace("_", " ").title()
                    if feature not in commands_by_feature:
                        commands_by_feature[feature] = []
                    commands_by_feature[feature].append(cmd)

                # Add commands by feature
                for feature, commands in commands_by_feature.items():
                    message_parts.append(f"\n**{feature}:**")
                    for cmd in commands:
                        message_parts.append(f"• `{cmd.name}` - {cmd.description}")

                message_parts.extend(
                    [
                        "",
                        "💡 **Need Help?**",
                        "• Use `/help` to see all available commands",
                        f"• Use `/help {command_name}` for detailed help on a specific command",
                        "• Contact team leadership for assistance",
                        "",
                        "🔍 **Did you mean?**",
                        "• Check for typos in the command name",
                        "• Some commands are only available in specific chat types",
                        "• Leadership commands are only available in leadership chat",
                    ]
                )

                return AgentResponse(
                    message="\n".join(message_parts), success=False, error="Unrecognized command"
                )

            except Exception as e:
                logger.error(ERROR_MESSAGES["COMMAND_REGISTRY_ERROR"].format(error=e))
                # Fallback response
                return AgentResponse(
                    message=ERROR_MESSAGES["UNRECOGNIZED_COMMAND"].format(command=command_name),
                    success=False,
                    error="Unrecognized command",
                )

        except Exception as e:
            logger.error(ERROR_MESSAGES["COMMAND_ANALYSIS_ERROR"].format(error=e))
            return AgentResponse(
                message=ERROR_MESSAGES["UNRECOGNIZED_COMMAND_FALLBACK"].format(
                    command=command_name
                ),
                success=False,
                error="Unrecognized command",
            )

    @critical_system_error_handler("AgenticMessageRouter.route_contact_share")
    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """
        Route contact sharing messages for phone number linking.

        Args:
            message: Telegram message with contact information

        Returns:
            AgentResponse with the linking result
        """
        logger.info(LOG_MESSAGES["CONTACT_SHARE_PROCESSING"].format(username=message.username))

        # Check if message has contact information
        if not hasattr(message, "contact_phone") or not message.contact_phone:
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["NO_CONTACT_INFO"],
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
                message=SUCCESS_MESSAGES["CONTACT_LINKING_SUCCESS"].format(
                    player_name=linked_player.name, player_id=linked_player.player_id
                ),
                error=None,
            )
        else:
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["CONTACT_LINKING_FAILED"],
                error="No matching player record",
            )

    def _get_unregistered_user_message(self, chat_type: ChatType, username: str) -> str:
        """Get message for unregistered users based on chat type."""
        from kickai.core.constants import BOT_VERSION

        if chat_type == ChatType.LEADERSHIP:
            return SUCCESS_MESSAGES["WELCOME_LEADERSHIP"].format(
                team_id=self.team_id, username=username, version=BOT_VERSION
            )
        else:
            return SUCCESS_MESSAGES["WELCOME_MAIN"].format(
                team_id=self.team_id, username=username, version=BOT_VERSION
            )

    async def _process_with_crewai_system(self, message: TelegramMessage) -> AgentResponse:
        """
        Route registered user messages to specialized agents.

        Args:
            message: Telegram message to route

        Returns:
            AgentResponse with the processed result
        """
        try:
            # Get detailed registration status from actual services
            try:
                from kickai.utils.dependency_utils import get_player_service, get_team_service

                player_service = get_player_service()
                team_service = get_team_service()
            except Exception as e:
                logger.warning(WARNING_MESSAGES["SERVICE_UNAVAILABLE"].format(error=e))
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
                    logger.warning(WARNING_MESSAGES["PLAYER_LOOKUP_FAILED"].format(error=e))
                    pass

            if team_service:
                try:
                    team_member = await team_service.get_team_member_by_telegram_id(
                        message.team_id, message.telegram_id
                    )
                    is_team_member = team_member is not None
                    logger.debug(
                        f"🔍 Team member check for {message.telegram_id}: {is_team_member}"
                    )
                except Exception as e:
                    logger.warning(WARNING_MESSAGES["TEAM_MEMBER_LOOKUP_FAILED"].format(error=e))
                    pass

            # Determine registration status based on actual data, not chat type
            is_registered = is_player or is_team_member

            # Log the actual registration status
            logger.info(
                LOG_MESSAGES["ACTUAL_REGISTRATION_STATUS"].format(
                    is_player=is_player, is_team_member=is_team_member, is_registered=is_registered
                )
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
                LOG_MESSAGES["USER_REGISTRATION_STATUS"].format(
                    is_registered=is_registered, is_player=is_player, is_team_member=is_team_member
                )
            )

            # Determine if NLP processing is needed
            if self._requires_nlp_processing(message):
                logger.info(LOG_MESSAGES["NLP_PROCESSING"])
                return await self._process_with_nlp_enhancement(message, execution_context)
            else:
                logger.info(LOG_MESSAGES["DIRECT_ROUTING"])
                # Direct routing for clear commands
                result = await self.crew_lifecycle_manager.execute_task(
                    team_id=self.team_id,
                    task_description=message.text,
                    execution_context=execution_context,
                )
                return AgentResponse(success=True, message=result)

        except Exception as e:
            logger.error(ERROR_MESSAGES["NLP_PROCESSING_ERROR"].format(error=e))
            # Re-raise the exception instead of providing a fallback
            raise

    def convert_telegram_update_to_message(
        self, update: Any, command_name: str | None = None
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
            logger.error(ERROR_MESSAGES["COMMAND_EXTRACTION_ERROR"].format(error=e))
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
        logger.info(LOG_MESSAGES["ROUTER_SHUTDOWN"].format(team_id=self.team_id))

        try:
            # Force cleanup of all resources
            await self._cleanup_resources(force=True)

            # Clear state variables
            self._last_telegram_id = None
            self._last_username = None

            # Reset crew lifecycle manager to allow garbage collection
            self._crew_lifecycle_manager = None

            logger.info(LOG_MESSAGES["ROUTER_SHUTDOWN_COMPLETE"].format(team_id=self.team_id))

        except Exception as e:
            logger.error(ERROR_MESSAGES["ROUTER_SHUTDOWN_ERROR"].format(error=e))
            raise

    def get_metrics(self) -> dict[str, Any]:
        """
        Get current metrics for monitoring and debugging.

        Returns:
            Dictionary containing current metrics
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

    def _requires_nlp_processing(self, message: TelegramMessage) -> bool:
        """
        Enhanced NLP requirement detection using command registry integration.

        Determines if a message requires natural language processing based on
        registry-based command classification and content analysis.

        Args:
            message: TelegramMessage to analyze

        Returns:
            True if message needs NLP processing, False for clear commands

        Raises:
            ValidationError: When message analysis fails

        Example:
            >>> router._requires_nlp_processing(help_message)
            False
            >>> router._requires_nlp_processing(natural_language_message)
            True
        """
        try:
            # Use the improved clear command detection
            if self._is_clear_command(message.text, message.chat_type.value):
                logger.info(LOG_MESSAGES["SKIP_NLP_CLEAR_COMMAND"].format(text=message.text))
                return False

            # Check if it's a conversational follow-up
            if self._is_conversational_followup(message):
                logger.info(LOG_MESSAGES["NLP_CONVERSATIONAL_FOLLOWUP"].format(text=message.text))
                return True

            # Check if text contains ambiguous references
            if self._contains_ambiguous_references(message.text):
                logger.info(LOG_MESSAGES["NLP_AMBIGUOUS_REFERENCES"].format(text=message.text))
                return True

            # Default to NLP for natural language queries
            logger.info(LOG_MESSAGES["NLP_NATURAL_LANGUAGE"].format(text=message.text))
            return True

        except Exception as e:
            logger.error(ERROR_MESSAGES["AMBIGUOUS_REF_CHECK_ERROR"].format(error=e))
            # Fail safe - assume needs NLP if uncertain
            return True

    def _is_clear_command(self, text: str, chat_type: str | None = None) -> bool:
        """
        Registry-based clear command detection with slash-agnostic support.

        Determines if a command is unambiguous and doesn't require NLP processing
        by leveraging the command registry metadata and classification rules.

        Args:
            text: User input text to analyze
            chat_type: Optional chat context for classification

        Returns:
            True if command is clear and doesn't need NLP processing

        Raises:
            ValidationError: When command analysis fails

        Example:
            >>> router._is_clear_command("/help")
            True
            >>> router._is_clear_command("tell me about the team")
            False
        """
        try:
            # Input validation using utility functions
            from kickai.utils.tool_validation import ToolValidationError, validate_string_input

            try:
                validate_string_input(text, "Command text", allow_empty=False)
            except ToolValidationError as e:
                logger.warning(WARNING_MESSAGES["INVALID_COMMAND_INPUT"].format(error=str(e)))
                return False

            # Extract command from text
            command = self._extract_command_from_text(text)
            if not command:
                return False

            # Get command registry
            from kickai.core.command_registry_initializer import get_initialized_command_registry

            registry = get_initialized_command_registry()
            if not registry:
                logger.warning(WARNING_MESSAGES["COMMAND_REGISTRY_UNAVAILABLE"])
                return False

            # Query registry with multiple variants
            command_metadata = self._find_command_in_registry(registry, command)
            if not command_metadata:
                return False

            # Classify command clarity
            return self._classify_command_clarity(command_metadata, text, chat_type)

        except Exception as e:
            logger.error(ERROR_MESSAGES["COMMAND_ANALYSIS_ERROR"].format(error=e))
            # Fail safe - assume needs NLP if uncertain
            return False

    def _extract_command_from_text(self, text: str) -> str | None:
        """
        Extract the command portion from user text.

        Args:
            text: User input text

        Returns:
            Command string if found, None otherwise
        """
        try:
            if not text or not text.strip():
                return None

            # Get first word
            first_word = text.strip().split()[0]

            # Handle slash commands and natural references
            if first_word.startswith("/"):
                return first_word.lower()

            # For non-slash text, check if it looks like a command
            # (single word that could be a command)
            if len(text.strip().split()) == 1:
                return first_word.lower()

            return None

        except Exception as e:
            logger.warning(WARNING_MESSAGES["COMMAND_EXTRACTION_ERROR"].format(error=e))
            return None

    def _find_command_in_registry(self, registry, command: str):
        """
        Find command in registry with multiple variants.

        Args:
            registry: Command registry instance
            command: Command to find

        Returns:
            CommandMetadata if found, None otherwise
        """
        try:
            # Try both with and without slash for flexibility
            command_variants = [command, f"/{command.lstrip('/')}", command.lstrip("/")]

            for variant in command_variants:
                command_metadata = registry.get_command(variant)
                if command_metadata:
                    return command_metadata

            return None

        except Exception as e:
            logger.warning(WARNING_MESSAGES["COMMAND_REGISTRY_ERROR"].format(error=e))
            return None

    def _classify_command_clarity(
        self, command_metadata, original_text: str, chat_type: str | None = None
    ) -> bool:
        """
        Intelligent command clarity classification based on metadata.

        Analyzes command characteristics to determine if it's unambiguous
        enough to skip NLP processing.

        Args:
            command_metadata: Command metadata from registry
            original_text: Original user input text
            chat_type: Optional chat context

        Returns:
            True if command is considered clear/unambiguous

        Raises:
            ValidationError: When classification fails
        """
        try:
            # System commands are always clear
            if hasattr(command_metadata, "command_type") and command_metadata.command_type:
                if command_metadata.command_type.value in ["system", "utility"]:
                    return True

            # Commands marked as not requiring NLP
            if hasattr(command_metadata, "requires_nlp") and not command_metadata.requires_nlp:
                return True

            # Commands with no required parameters
            if not command_metadata.parameters or getattr(
                command_metadata, "parameter_optional", True
            ):
                return True

            # Self-referential commands without parameters
            if self._is_self_referential_command(command_metadata, original_text):
                return True

            # Specific clear commands (extensible via config)
            return self._check_specific_clear_commands(command_metadata.name)

        except Exception as e:
            logger.error(ERROR_MESSAGES["COMMAND_CLARITY_ERROR"].format(error=e))
            from kickai.core.exceptions import ValidationError

            raise ValidationError(ERROR_MESSAGES["COMMAND_CLARITY_ERROR"].format(error=e)) from None

    def _is_self_referential_command(self, command_metadata, original_text: str) -> bool:
        """Check if command is self-referential (e.g., /info without parameters)."""
        try:
            text_parts = original_text.strip().split()
            if len(text_parts) == 1 and command_metadata.name.lower() in [
                "info",
                "/info",
                "status",
                "/status",
            ]:
                return True  # Single word info/status commands are clear (self-reference)
            return False
        except Exception:
            return False

    def _check_specific_clear_commands(self, command_name: str) -> bool:
        """Check if command is in the list of specifically clear commands."""
        try:
            return command_name.lower() in CLEAR_COMMAND_NAMES
        except Exception:
            return False

    def _is_conversational_followup(self, message: TelegramMessage) -> bool:
        """
        Check if message is a conversational follow-up that needs context.

        Args:
            message: TelegramMessage to analyze

        Returns:
            True if message appears to be a conversational follow-up
        """
        try:
            text_lower = message.text.lower().strip()
            return any(indicator in text_lower for indicator in FOLLOWUP_INDICATORS)

        except Exception as e:
            logger.warning(WARNING_MESSAGES["FOLLOWUP_CHECK_ERROR"].format(error=e))
            return False

    def _contains_ambiguous_references(self, text: str) -> bool:
        """
        Check if text contains references that need context resolution.

        Args:
            text: Text to analyze

        Returns:
            True if text contains ambiguous references
        """
        try:
            text_lower = text.lower()
            return any(ref in text_lower.split() for ref in AMBIGUOUS_REFS)

        except Exception as e:
            logger.warning(WARNING_MESSAGES["AMBIGUOUS_REF_CHECK_ERROR"].format(error=e))
            return False

    async def _process_with_nlp_enhancement(
        self, message: TelegramMessage, execution_context: dict
    ) -> AgentResponse:
        """
        Process message with NLP enhancement for natural language understanding.

        Args:
            message: TelegramMessage to process
            execution_context: Execution context for processing

        Returns:
            AgentResponse with NLP-enhanced processing results

        Raises:
            ToolError: When NLP processing fails
        """
        try:
            logger.info(LOG_MESSAGES["NLP_STARTING"])

            # For now, route to crew lifecycle manager with enhanced context
            # TODO: Implement actual NLP agent when created in Phase 2
            enhanced_context = execution_context.copy()
            enhanced_context.update(
                {
                    "nlp_required": True,
                    "processing_type": "nlp_enhanced",
                    "original_message": message.text,
                }
            )

            result = await self.crew_lifecycle_manager.execute_task(
                team_id=self.team_id,
                task_description=message.text,
                execution_context=enhanced_context,
            )

            return AgentResponse(success=True, message=result)

        except Exception as e:
            logger.error(ERROR_MESSAGES["NLP_PROCESSING_ERROR"].format(error=e))
            from kickai.core.exceptions import ToolError

            raise ToolError(ERROR_MESSAGES["NLP_PROCESSING_ERROR"].format(error=e)) from None

    def _looks_like_phone_number(self, text: str) -> bool:
        """
        Check if text looks like a phone number with security considerations.

        Args:
            text: Input text to check

        Returns:
            True if text looks like a valid phone number, False otherwise
        """
        if not text or not isinstance(text, str):
            return False

        # Security: Limit input length to prevent DoS attacks
        if (
            len(text.strip()) > PHONE_NUMBER_MAX_LENGTH
            or len(text.strip()) < PHONE_NUMBER_MIN_LENGTH
        ):
            return False

        # Security: Only allow known safe characters
        if not all(c in PHONE_ALLOWED_CHARS for c in text):
            logger.warning(WARNING_MESSAGES["PHONE_VALIDATION_ERROR"])
            return False

        # Remove common separators and check if it's mostly digits
        cleaned = "".join(c for c in text if c.isdigit() or c in "+()-")

        # Must have at least 10 digits but not more than 15 (international standard)
        digit_count = sum(1 for c in cleaned if c.isdigit())
        if digit_count < PHONE_NUMBER_MIN_DIGITS or digit_count > PHONE_NUMBER_MAX_DIGITS:
            return False

        # Must start with + or be all digits (after removing separators)
        digits_only = "".join(c for c in cleaned if c.isdigit())
        if cleaned.startswith("+") or digits_only == cleaned.replace("+", "").replace(
            "-", ""
        ).replace("(", "").replace(")", ""):
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
                phone=message.text.strip(),
                telegram_id=message.telegram_id,
                username=message.username,
            )

            if linked_player:
                return AgentResponse(
                    success=True,
                    message=SUCCESS_MESSAGES["PHONE_LINKING_SUCCESS"].format(
                        player_name=linked_player.name, player_id=linked_player.player_id
                    ),
                    error=None,
                )
            else:
                return AgentResponse(
                    success=False,
                    message=SUCCESS_MESSAGES["PHONE_LINKING_FAILED"],
                    error="No matching player record",
                )

        except Exception as e:
            logger.error(f"❌ Error in _handle_phone_contact: {e}")
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["PHONE_PROCESSING_ERROR"],
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

        Args:
            command: The command to check

        Returns:
            True if it's a helper command, False otherwise
        """
        # Helper system is now proactive - no command-driven interactions
        return False

    async def route_help_request(self, message: TelegramMessage) -> AgentResponse:
        """
        Route help requests to the Helper Agent using CrewAI tasks.

        Args:
            message: The Telegram message containing the help request

        Returns:
            AgentResponse with the helper's response
        """
        try:
            logger.info("🔄 AgenticMessageRouter: Routing help request to Helper Agent")

            # Extract the query from the message
            query = message.text
            if query.startswith(SLASH_COMMAND_PREFIX):
                # Remove the command and get the rest as the query
                parts = query.split(" ", 1)
                if len(parts) > 1:
                    query = parts[1]
                else:
                    query = "general help"

            # Create context for the helper agent (unused for now)
            # context = {
            #     "telegram_id": message.telegram_id,
            #     "team_id": self.team_id,
            #     "chat_type": message.chat_type.value,
            #     "username": message.username,
            #     "query": query,
            # }

            # Execute help task using simplified approach
            # In production, you'd want to use the CrewAI system for help requests
            response = SUCCESS_MESSAGES["HELP_RESPONSE"].format(query=query)

            return AgentResponse(success=True, message=response, error=None)

        except Exception as e:
            logger.error(f"❌ Error in _get_help_response: {e}")
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["HELP_ERROR"],
                error=str(e),
            )

    async def send_proactive_suggestions(self, telegram_id: int, team_id: str) -> None:
        """
        Send proactive suggestions based on user behavior.

        Args:
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

        Args:
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
        """Return dynamic help from help_response tool instead of hardcoded lists."""
        try:
            from kickai.features.shared.domain.tools.help_tools import help_response

            # Use dynamic help tailored to chat context; preserve emojis and formatting
            # Convert telegram_id to string for the help tool (which expects string)
            telegram_id_str = (
                str(self._last_telegram_id)
                if hasattr(self, "_last_telegram_id") and self._last_telegram_id
                else "0"
            )
            return help_response(
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

        Args:
            raw_update: Raw update data from Telegram or mock service

        Returns:
            True if this is a new_chat_members event, False otherwise
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
            if hasattr(raw_update, "message") and raw_update.message:
                if (
                    hasattr(raw_update.message, "new_chat_members")
                    and raw_update.message.new_chat_members
                ):
                    return True

            return False

        except Exception as e:
            logger.error(ERROR_MESSAGES["NEW_MEMBERS_EXTRACTION_ERROR"].format(error=e))
            return False

    async def route_new_chat_members(self, message: TelegramMessage) -> AgentResponse:
        """
        Route new chat members events for auto-activation via invite link processing.

        This enhanced method now supports automatic player activation when users join
        with valid invite links, eliminating the need for manual /approve commands.

        Args:
            message: Telegram message containing new_chat_members event

        Returns:
            AgentResponse with the auto-activation processing result
        """
        try:
            logger.info(LOG_MESSAGES["NEW_CHAT_MEMBERS_PROCESSING"])

            # Extract new members from the update
            new_members = self._extract_new_members(message.raw_update)
            if not new_members:
                logger.warning(WARNING_MESSAGES["NO_NEW_MEMBERS"])
                return AgentResponse(
                    success=False,
                    message=ERROR_MESSAGES["NO_NEW_MEMBERS_ERROR"],
                    error="No new members",
                )

            # Process each new member (usually just one for invite links)
            for member in new_members:
                telegram_id = member.get("id", 0)  # Keep as int
                username = member.get("username") or member.get("first_name", "Unknown")

                logger.info(
                    LOG_MESSAGES["NEW_MEMBER_PROCESSING"].format(
                        username=username, telegram_id=telegram_id
                    )
                )

                # Extract invite context for auto-activation
                invite_context = self._extract_invite_context_for_activation(message.raw_update)

                # Use PlayerAutoActivationService for intelligent processing
                from kickai.core.dependency_container import get_container
                from kickai.features.player_registration.domain.services.player_auto_activation_service import (
                    PlayerAutoActivationService,
                )

                container = get_container()
                database = container.get_database()

                # Initialize auto-activation service
                activation_service = PlayerAutoActivationService(database, self.team_id)

                # Process new chat member with auto-activation
                activation_result = await activation_service.process_new_chat_member(
                    telegram_id=telegram_id,
                    username=username,
                    chat_type=message.chat_type.value,
                    invite_context=invite_context,
                )

                # Return appropriate response based on activation result
                if activation_result.success:
                    logger.info(
                        LOG_MESSAGES["AUTO_ACTIVATION_SUCCESS"].format(
                            username=username, player_name=activation_result.player_name
                        )
                    )

                    # Enhanced welcome message for activated players
                    welcome_message = await self._create_enhanced_welcome_message(
                        activation_result, message.chat_type
                    )

                    return AgentResponse(success=True, message=welcome_message, error=None)
                else:
                    logger.warning(
                        LOG_MESSAGES["AUTO_ACTIVATION_FAILED"].format(
                            username=username, error=activation_result.error
                        )
                    )

                    # Handle uninvited users or activation failures
                    return AgentResponse(
                        success=False,
                        message=activation_result.message,
                        error=activation_result.error,
                    )

            # Fallback response (should not reach here normally)
            return AgentResponse(success=True, message=SUCCESS_MESSAGES["WELCOME_TEAM"], error=None)

        except Exception as e:
            logger.error(f"❌ Error in route_new_chat_members: {e}")
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["NEW_CHAT_MEMBERS_ERROR"],
                error=str(e),
            )

    def _extract_new_members(self, raw_update) -> list:
        """Extract new members from the raw update."""
        try:
            # Mock Telegram format
            if isinstance(raw_update, dict):
                if "new_chat_members" in raw_update:
                    return raw_update["new_chat_members"]

            # Real Telegram format
            if hasattr(raw_update, "message") and raw_update.message:
                if hasattr(raw_update.message, "new_chat_members"):
                    members = raw_update.message.new_chat_members
                    # Convert Telegram User objects to dict format
                    if members:
                        return [
                            {
                                "id": member.id,
                                "username": member.username,
                                "first_name": member.first_name,
                                "last_name": member.last_name,
                            }
                            for member in members
                        ]

            return []

        except Exception as e:
            logger.error(ERROR_MESSAGES["NEW_MEMBERS_EXTRACTION_ERROR"].format(error=e))
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
            logger.error(ERROR_MESSAGES["INVITE_LINK_EXTRACTION_ERROR"].format(error=e))
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
                        logger.info(
                            LOG_MESSAGES["INVITATION_CONTEXT_FOUND"].format(invite_id=invite_id)
                        )
                        return invite_id

                # Fallback to check _invitation_data (backup field)
                if hasattr(raw_update, "_invitation_data"):
                    invitation_data = getattr(raw_update, "_invitation_data", {})
                    invite_id = invitation_data.get("invite_id")
                    if invite_id:
                        logger.info(
                            LOG_MESSAGES["BACKUP_INVITATION_DATA_FOUND"].format(invite_id=invite_id)
                        )
                        return invite_id

            logger.warning(WARNING_MESSAGES["NO_INVITATION_CONTEXT"])
            return None

        except Exception as e:
            logger.error(ERROR_MESSAGES["INVITE_ID_EXTRACTION_ERROR"].format(error=e))
            return None

    async def _process_invite_link_validation(
        self,
        invite_id: str,
        invite_link: str | None,
        telegram_id: int,
        username: str,
        chat_id: str,
        chat_type: ChatType,
    ) -> AgentResponse:
        """Process invite link validation and player linking."""
        try:
            logger.info(
                f"🔗 Processing invitation link - invite_id: {invite_id}, telegram_id: {telegram_id}, chat_type: {chat_type.value}"
            )

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
                secure_data=None,
            )

            if not invite_data:
                logger.warning(f"❌ Invalid or expired invite link: {invite_id}")
                return AgentResponse(
                    success=False,
                    message=ERROR_MESSAGES["INVALID_INVITE_LINK"],
                    error="Invalid invite link",
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
                    invite_data=invite_data,
                )
            elif member_phone and member_name:
                return await self._process_team_member_invite_link(
                    member_phone=member_phone,
                    member_name=member_name,
                    telegram_id=telegram_id,
                    username=username,
                    invite_data=invite_data,
                )
            else:
                logger.warning(f"⚠️ Invite data missing required fields: {invite_data}")
                return AgentResponse(
                    success=False,
                    message=ERROR_MESSAGES["INVALID_INVITE_DATA"],
                    error="Missing invite data fields",
                )

        except Exception as e:
            logger.error(f"❌ Error in _process_invite_link_validation: {e}")
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["INVITE_PROCESSING_ERROR"],
                error=str(e),
            )

    async def _process_player_invite_link(
        self,
        player_phone: str,
        player_name: str,
        telegram_id: int,
        username: str,
        invite_data: dict,
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
                phone=player_phone, telegram_id=telegram_id, username=username
            )

            if linked_player:
                logger.info(
                    LOG_MESSAGES["PLAYER_LINKING_SUCCESS"].format(
                        player_name=player_name, telegram_id=telegram_id
                    )
                )
                return AgentResponse(
                    success=True,
                    message=SUCCESS_MESSAGES["WELCOME_BACK"].format(player_name=player_name),
                    error=None,
                )
            else:
                logger.warning(
                    WARNING_MESSAGES["PLAYER_LINKING_FAILED"].format(
                        player_name=player_name, telegram_id=telegram_id
                    )
                )
                return AgentResponse(
                    success=False,
                    message=ERROR_MESSAGES["PHONE_LINKING_FAILED"],
                    error="Player linking failed",
                )

        except Exception as e:
            logger.error(f"❌ Error in _process_player_invite_link: {e}")
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["PHONE_PROCESSING_ERROR"],
                error=str(e),
            )

    async def _process_team_member_invite_link(
        self,
        member_phone: str,
        member_name: str,
        telegram_id: int,
        username: str,
        invite_data: dict,
    ) -> AgentResponse:
        """Process team member invite link and link the user."""
        try:
            # TODO: Implement team member linking service
            # For now, provide a basic welcome message
            logger.info(
                LOG_MESSAGES["TEAM_MEMBER_INVITE_PROCESSING"].format(member_name=member_name)
            )

            return AgentResponse(
                success=True,
                message=SUCCESS_MESSAGES["TEAM_MEMBER_WELCOME"].format(member_name=member_name),
                error=None,
            )

        except Exception as e:
            logger.error(f"❌ Error in _process_team_member_invite_link: {e}")
            return AgentResponse(
                success=False,
                message=ERROR_MESSAGES["TEAM_MEMBER_INVITE_ERROR"],
                error=str(e),
            )

    async def _handle_regular_new_member(
        self, telegram_id: int, username: str, chat_type: ChatType
    ) -> AgentResponse:
        """Handle new members who joined without an invite link."""
        try:
            if chat_type == ChatType.MAIN:
                return AgentResponse(
                    success=True,
                    message=SUCCESS_MESSAGES["REGULAR_MEMBER_WELCOME_MAIN"].format(
                        username=username
                    ),
                    error=None,
                )
            elif chat_type == ChatType.LEADERSHIP:
                return AgentResponse(
                    success=True,
                    message=SUCCESS_MESSAGES["REGULAR_MEMBER_WELCOME_LEADERSHIP"].format(
                        username=username
                    ),
                    error=None,
                )
            else:
                return AgentResponse(
                    success=True,
                    message=SUCCESS_MESSAGES["REGULAR_MEMBER_WELCOME_DEFAULT"].format(
                        username=username
                    ),
                    error=None,
                )

        except Exception as e:
            logger.error(f"❌ Error handling regular new member: {e}")
            return AgentResponse(
                success=True,
                message=SUCCESS_MESSAGES["REGULAR_MEMBER_WELCOME_DEFAULT"].format(
                    username=username
                ),
                error=None,
            )

    def _extract_invite_context_for_activation(self, raw_update) -> dict[str, Any] | None:
        """
        Extract invite context in format expected by PlayerAutoActivationService.

        Args:
            raw_update: Raw update data from Telegram or mock service

        Returns:
            Dictionary with invite context or None if no context found
        """
        try:
            invite_context = {}

            # Extract from mock Telegram format
            if isinstance(raw_update, dict):
                invitation_context = raw_update.get("invitation_context", {})
                if invitation_context:
                    invite_context.update(
                        {
                            "invite_link": invitation_context.get("invite_link"),
                            "invite_id": invitation_context.get("invite_id"),
                            "secure_data": invitation_context.get("secure_data"),
                            "invite_type": invitation_context.get("invite_type", "player"),
                        }
                    )
                    logger.info(
                        LOG_MESSAGES["INVITE_CONTEXT_EXTRACTED"].format(
                            keys=list(invite_context.keys())
                        )
                    )
                    return invite_context

                # Fallback to check backup invitation data
                if hasattr(raw_update, "_invitation_data"):
                    invitation_data = getattr(raw_update, "_invitation_data", {})
                    if invitation_data:
                        invite_context.update(
                            {
                                "invite_link": invitation_data.get("invite_link"),
                                "invite_id": invitation_data.get("invite_id"),
                                "secure_data": invitation_data.get("secure_data"),
                                "invite_type": invitation_data.get("invite_type", "player"),
                            }
                        )
                        logger.info(
                            LOG_MESSAGES["BACKUP_INVITE_CONTEXT_EXTRACTED"].format(
                                keys=list(invite_context.keys())
                            )
                        )
                        return invite_context

            # For real Telegram API, invite context would need to be handled differently
            # as Telegram doesn't provide the specific invite link used in the join event
            logger.debug("🔍 No invite context found in event")
            return None

        except Exception as e:
            logger.error(ERROR_MESSAGES["INVITE_CONTEXT_EXTRACTION_ERROR"].format(error=e))
            return None

    async def _create_enhanced_welcome_message(self, activation_result, chat_type: ChatType) -> str:
        """
        Create enhanced welcome message for successfully activated players.

        Args:
            activation_result: ActivationResult from PlayerAutoActivationService
            chat_type: Type of chat the user joined

        Returns:
            Enhanced welcome message string
        """
        # FAIL FAST - Validate player_name is proper string, don't hide issues
        if not isinstance(activation_result.player_name, str):
            raise ValueError(f"Invalid player_name type: {type(activation_result.player_name)} - expected str")
        
        if not activation_result.player_name.strip():
            raise ValueError("Empty player_name provided to welcome message")
        
        player_name = activation_result.player_name.strip()
        was_activated = activation_result.was_activated

        # Get welcome message context for additional information (unused for now)
        # welcome_context = {
        #     "player_name": player_name,
        #     "player_id": activation_result.player_id,
        #     "was_activated": was_activated,
        #     "chat_type": chat_type.value,
        #     "team_id": self.team_id
        # }

        # Base welcome message with activation status
        if was_activated:
            # Player was just activated from pending -> active
            base_message = SUCCESS_MESSAGES["AUTO_ACTIVATION_WELCOME"].format(
                player_name_upper=player_name.upper()
            )
        else:
            # Player was already active
            base_message = SUCCESS_MESSAGES["WELCOME_BACK"].format(player_name=player_name)

        # Add chat-specific guidance
        if chat_type == ChatType.MAIN:
            chat_guidance = SUCCESS_MESSAGES["MAIN_CHAT_GUIDANCE"]
        elif chat_type == ChatType.LEADERSHIP:
            chat_guidance = SUCCESS_MESSAGES["LEADERSHIP_CHAT_GUIDANCE"]
        else:
            chat_guidance = SUCCESS_MESSAGES["PRIVATE_CHAT_GUIDANCE"]

        # Combine messages
        full_message = base_message + chat_guidance + SUCCESS_MESSAGES["KICKAI_FOOTER"]

        return full_message
