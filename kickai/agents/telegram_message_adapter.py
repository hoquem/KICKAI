#!/usr/bin/env python3
"""
Telegram Message Adapter - Simplified Message Processing

This module provides telegram message adaptation and preprocessing before 
sending to CrewAI's native manager LLM routing system.

Responsibilities:
- Message format conversion (Telegram → KICKAI format)
- Rate limiting and resource management  
- Chat type determination
- Direct integration with TeamManagementSystem

No longer handles routing (done by CrewAI manager LLM).
"""

from typing import Any, Protocol

from loguru import logger

# Import configuration
from kickai.agents.config.message_router_config import (
    ERROR_MESSAGES,
    LOG_MESSAGES,
)

# Import utility classes
from kickai.agents.utils.resource_manager import ResourceManager
from kickai.agents.utils.user_registration_checker import UserRegistrationChecker
from kickai.core.context_types import create_context_from_telegram_message
from kickai.core.enums import ChatType
from kickai.core.types import (
    AgentResponse,
    TelegramMessage,
    UserFlowType,
)


class MessageAdapterProtocol(Protocol):
    """Protocol for message adaptation to enable better testing and extensibility."""

    async def process_message(self, message: TelegramMessage) -> AgentResponse:
        """Process a message through the system."""
        ...

    async def process_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """Handle contact sharing messages."""
        ...


class TelegramMessageAdapter:
    """
    Telegram message adapter for preprocessing before CrewAI execution.

    Handles message conversion, rate limiting, and direct integration with
    CrewAI's native manager LLM routing (no manual routing needed).

    Simplified from AgenticMessageRouter to focus on actual responsibilities.
    """

    def __init__(
        self, team_id: str, resource_manager: ResourceManager | None = None
    ) -> None:
        """
        Initialize the telegram message adapter.

        Args:
            team_id: Team identifier
            resource_manager: Optional resource manager for dependency injection
        """
        try:
            # Input validation
            from kickai.utils.tool_validation import ToolValidationError, validate_string_input

            try:
                validated_team_id = validate_string_input(team_id, "Team ID", allow_empty=False)
                self.team_id = validated_team_id
            except ToolValidationError as e:
                raise ValueError(str(e))

            # Initialize state tracking for better error handling
            self.main_chat_id: str | None = None
            self.leadership_chat_id: str | None = None

            # Resource management (use dependency injection for testability)
            self._resource_manager = resource_manager or ResourceManager()

            logger.info(LOG_MESSAGES["ROUTER_INITIALIZED"].format(team_id=self.team_id))

        except Exception as e:
            logger.error(f"❌ Error in TelegramMessageAdapter.__init__: {e}")
            raise

    async def process_message(self, message: TelegramMessage) -> AgentResponse:
        """
        Process a message through the system using CrewAI native routing.

        Args:
            message: Telegram message to process

        Returns:
            AgentResponse with processing result
        """
        try:
            # Input validation
            if not message or not isinstance(message, TelegramMessage):
                logger.error(
                    ERROR_MESSAGES["INVALID_MESSAGE_TYPE"].format(type_name=type(message).__name__)
                )
                return self._create_error_response("Invalid message format", "Invalid message type")

            # Resource management
            request_token = self._resource_manager.add_request()

            try:
                # Check rate limits
                if self._resource_manager.check_rate_limit(message.telegram_id):
                    return self._create_error_response(
                        ERROR_MESSAGES["RATE_LIMIT_MESSAGE"], "Rate limit exceeded"
                    )

                # Acquire semaphore for concurrent request limiting
                if not await self._resource_manager.acquire_semaphore():
                    return self._create_error_response(
                        ERROR_MESSAGES["CONCURRENT_LIMIT_MESSAGE"], "Concurrent limit exceeded"
                    )

                # Process the message directly with CrewAI
                return await self._process_message_direct(message)

            finally:
                # Cleanup
                self._resource_manager.remove_request(request_token)
                self._resource_manager.release_semaphore()

        except Exception as e:
            logger.error(f"❌ Error in process_message: {e}")
            return self._create_error_response("Message processing failed", str(e))

    async def _process_message_direct(self, message: TelegramMessage) -> AgentResponse:
        """
        Process a message directly with CrewAI system (no manual routing).

        Args:
            message: Telegram message to process

        Returns:
            AgentResponse with processing result
        """
        try:
            # Create context from message
            context = create_context_from_telegram_message(
                telegram_id=message.telegram_id,
                team_id=self.team_id,
                chat_id=message.chat_id,
                chat_type=message.chat_type,
                message_text=message.text,
                telegram_username=message.username,
            )

            # Check if user is registered
            user_flow_type = await UserRegistrationChecker.check_user_registration_status(
                message.telegram_id, self.team_id
            )

            # Get or create team system and execute directly
            # CrewAI manager LLM handles all routing decisions
            from kickai.core.team_system_manager import get_team_system
            
            team_system = await get_team_system(self.team_id)
            
            # Create execution context
            execution_context = {
                'telegram_id': context.telegram_id,
                'team_id': context.team_id,
                'chat_type': context.chat_type,
                'telegram_username': context.telegram_username,
                'is_registered': user_flow_type != UserFlowType.UNREGISTERED_USER,
                'user_flow_type': user_flow_type.value if hasattr(user_flow_type, 'value') else str(user_flow_type)
            }

            # Execute task with CrewAI native manager LLM routing
            result = await team_system.execute_task(
                task_description=context.message_text,
                execution_context=execution_context
            )

            return AgentResponse(success=True, message=result)

        except Exception as e:
            logger.error(f"❌ Error in _process_message_direct: {e}")
            return self._create_error_response("Direct message processing failed", str(e))

    async def process_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """
        Handle contact sharing messages.

        Args:
            message: Contact sharing message

        Returns:
            AgentResponse with contact handling result
        """
        try:
            logger.info(f"📞 Processing contact share from user {message.telegram_id}")

            # Extract phone number from contact
            contact = message.raw_update.message.contact
            phone_number = contact.phone_number

            # Validate phone number
            from kickai.agents.utils.phone_validator import PhoneValidator
            
            if not PhoneValidator.is_valid_phone(phone_number):
                return self._create_error_response(
                    "❌ Invalid phone number format. Please share a valid UK mobile number.",
                    "Invalid phone format"
                )

            # Create registration message with phone number
            registration_text = f"register_with_phone {phone_number}"
            
            # Create new message for registration
            registration_message = TelegramMessage(
                telegram_id=message.telegram_id,
                text=registration_text,
                chat_id=message.chat_id,
                chat_type=message.chat_type,
                team_id=self.team_id,
                username=message.username,
                name=message.name,
                raw_update=message.raw_update,
            )

            # Process registration through normal flow
            return await self.process_message(registration_message)

        except Exception as e:
            logger.error(f"❌ Error in process_contact_share: {e}")
            return self._create_error_response("Contact processing failed", str(e))

    def convert_telegram_update_to_message(
        self, update: Any, command_name: str = None
    ) -> TelegramMessage:
        """
        Convert Telegram update to TelegramMessage format.

        Args:
            update: Telegram update object
            command_name: Optional command name for command messages

        Returns:
            TelegramMessage object
        """
        try:
            # Extract basic message information
            text = update.message.text if update.message and update.message.text else ""
            telegram_id = update.effective_user.id
            username = (
                update.effective_user.username or update.effective_user.first_name or "unknown"
            )
            chat_id = str(update.effective_chat.id)

            # Determine chat type
            chat_type = self._determine_chat_type(chat_id)

            # Handle new chat members data
            new_chat_members = None
            if (
                update.message
                and hasattr(update.message, "new_chat_members")
                and update.message.new_chat_members
            ):
                new_chat_members = [
                    {
                        "id": member.id,
                        "username": member.username,
                        "first_name": member.first_name,
                        "last_name": member.last_name,
                        "is_bot": member.is_bot,
                    }
                    for member in update.message.new_chat_members
                    if not member.is_bot
                ]

            return TelegramMessage(
                telegram_id=telegram_id,
                text=text,
                chat_id=chat_id,
                chat_type=chat_type,
                team_id=self.team_id,
                username=username,
                name=update.effective_user.first_name,
                raw_update=update,
                new_chat_members=new_chat_members,
            )

        except Exception as e:
            logger.error(f"❌ Error converting Telegram update to message: {e}")
            # Return a basic message with error handling
            return TelegramMessage(
                telegram_id=update.effective_user.id if update.effective_user else 0,
                text=update.message.text if update.message and update.message.text else "",
                chat_id=str(update.effective_chat.id) if update.effective_chat else "",
                chat_type=ChatType.MAIN,  # Default to main chat
                team_id=self.team_id,
                username="unknown",
                name="Unknown",
                raw_update=update,
            )

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """
        Determine chat type based on chat ID.

        Args:
            chat_id: Chat ID to determine type for

        Returns:
            ChatType enum value
        """
        try:
            if chat_id == self.main_chat_id:
                return ChatType.MAIN
            elif chat_id == self.leadership_chat_id:
                return ChatType.LEADERSHIP
            else:
                return ChatType.MAIN  # Default to main chat

        except Exception as e:
            logger.error(f"❌ Error determining chat type: {e}")
            return ChatType.MAIN  # Default fallback

    def set_chat_ids(self, main_chat_id: str, leadership_chat_id: str) -> None:
        """
        Set the chat IDs for proper chat type determination.

        Args:
            main_chat_id: Main chat ID
            leadership_chat_id: Leadership chat ID
        """
        try:
            self.main_chat_id = main_chat_id
            self.leadership_chat_id = leadership_chat_id
            logger.info(f"Chat IDs set - Main: {main_chat_id}, Leadership: {leadership_chat_id}")

        except Exception as e:
            logger.error(f"❌ Error setting chat IDs: {e}")
            raise

    def _create_error_response(self, message: str, error_detail: str) -> AgentResponse:
        """
        Create a standardized error response.

        Args:
            message: User-friendly error message
            error_detail: Technical error detail

        Returns:
            AgentResponse with error information
        """
        return AgentResponse(
            success=False,
            message=message,
            error=error_detail,
        )


# Backward compatibility aliases
AgenticMessageRouter = TelegramMessageAdapter  # For existing code
MessageRouterProtocol = MessageAdapterProtocol  # For existing code