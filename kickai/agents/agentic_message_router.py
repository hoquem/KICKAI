#!/usr/bin/env python3
"""
Agentic Message Router - Refactored

This module provides centralized agentic message routing following CrewAI best practices.
ALL messages go through agents - no direct processing bypasses the agentic system.

Refactored to follow clean architecture principles with separated concerns.
"""

import asyncio
from typing import Any, Protocol
from loguru import logger

from kickai.core.context_types import create_context_from_telegram_message
from kickai.core.enums import ChatType
from kickai.core.types import (
    AgentResponse,
    TelegramMessage,
    UserFlowType,
)

# Import utility classes
from kickai.agents.utils.phone_validator import PhoneValidator
from kickai.agents.utils.command_analyzer import CommandAnalyzer
from kickai.agents.utils.welcome_message_builder import WelcomeMessageBuilder
from kickai.agents.utils.invite_processor import InviteProcessor
from kickai.agents.utils.user_registration_checker import UserRegistrationChecker
from kickai.agents.utils.resource_manager import ResourceManager

# Import configuration
from kickai.agents.config.message_router_config import (
    ERROR_MESSAGES,
    WARNING_MESSAGES,
    LOG_MESSAGES,
    SUCCESS_MESSAGES,
)


class MessageRouterProtocol(Protocol):
    """Protocol for message routing to enable better testing and extensibility."""

    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """Route a message through the system."""
        ...

    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """Handle contact sharing messages."""
        ...


class AgenticMessageRouter:
    """
    Centralized agentic message routing following CrewAI best practices.

    This router ensures that ALL messages go through the agentic system.
    No direct processing bypasses agents.

    Refactored to follow clean architecture principles with separated concerns.
    """

    def __init__(
        self, 
        team_id: str, 
        crewai_system=None, 
        resource_manager: ResourceManager | None = None
    ) -> None:
        """
        Initialize the agentic message router.

        Args:
            team_id: Team identifier
            crewai_system: Optional CrewAI system instance
            resource_manager: Optional resource manager for dependency injection
        """
        try:
            # Input validation using utility functions
            from kickai.utils.tool_validation import validate_string_input, ToolValidationError

            try:
                # validate_string_input returns the sanitized value, not an error message
                validated_team_id = validate_string_input(team_id, "Team ID", allow_empty=False)
                self.team_id = validated_team_id
            except ToolValidationError as e:
                raise ValueError(str(e))

            self.crewai_system = crewai_system
            
            # Lazy initialization to avoid circular dependencies
            self._crew_lifecycle_manager = None

            # Initialize state tracking for better error handling
            self._last_telegram_id: int | None = None
            self._last_username: str | None = None
            self.main_chat_id: str | None = None
            self.leadership_chat_id: str | None = None

            # Resource management (use dependency injection for testability)
            self._resource_manager = resource_manager or ResourceManager()

            self._setup_router()
            
        except Exception as e:
            logger.error(f"❌ Error in AgenticMessageRouter.__init__: {e}")
            raise

    @property
    def crew_lifecycle_manager(self):
        """Lazy load crew lifecycle manager to avoid circular imports."""
        try:
            if self._crew_lifecycle_manager is None:
                from kickai.agents.crew_lifecycle_manager import get_crew_lifecycle_manager
                self._crew_lifecycle_manager = get_crew_lifecycle_manager()
            return self._crew_lifecycle_manager
            
        except Exception as e:
            logger.error(f"❌ Error in crew_lifecycle_manager property: {e}")
            raise

    def _setup_router(self) -> None:
        """Set up the router configuration."""
        try:
            logger.info(LOG_MESSAGES["ROUTER_INITIALIZED"].format(team_id=self.team_id))
            
        except Exception as e:
            logger.error(f"❌ Error in _setup_router: {e}")
            raise

    async def route_message(self, message: TelegramMessage) -> AgentResponse:
        """
        Route a message through the agentic system.

        Args:
            message: Telegram message to route

        Returns:
            AgentResponse with routing result
        """
        try:
            # Input validation
            if not message or not isinstance(message, TelegramMessage):
                logger.error(ERROR_MESSAGES["INVALID_MESSAGE_TYPE"].format(
                    type_name=type(message).__name__
                ))
                return self._create_error_response("Invalid message format", "Invalid message type")

            # Resource management
            request_token = self._resource_manager.add_request()
            
            try:
                # Check rate limits
                if self._resource_manager.check_rate_limit(message.telegram_id):
                    return self._create_error_response(
                        ERROR_MESSAGES["RATE_LIMIT_MESSAGE"], 
                        "Rate limit exceeded"
                    )

                # Acquire semaphore for concurrent request limiting
                if not await self._resource_manager.acquire_semaphore():
                    return self._create_error_response(
                        ERROR_MESSAGES["CONCURRENT_LIMIT_MESSAGE"], 
                        "Concurrent limit exceeded"
                    )

                # Process the message
                return await self._process_message(message)
                
            finally:
                # Cleanup
                self._resource_manager.remove_request(request_token)
                self._resource_manager.release_semaphore()
                
        except Exception as e:
            logger.error(f"❌ Error in route_message: {e}")
            return self._create_error_response("Message processing failed", str(e))

    async def _process_message(self, message: TelegramMessage) -> AgentResponse:
        """
        Process a message through the agentic system.

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
                username=message.username,
                telegram_name=message.username,  # Use username as telegram_name for now
            )
            
            # Check if user is registered
            user_flow_type = await UserRegistrationChecker.check_user_registration_status(
                message.telegram_id, self.team_id
            )

            # Determine if message needs NLP processing
            requires_nlp = CommandAnalyzer.requires_nlp_processing(
                message.text, context.chat_type
            )

            # All message processing, whether NLP or command-based,
            # now goes through a unified crew task execution flow.
            return await self._execute_crew_task(context, user_flow_type)
                
        except Exception as e:
            logger.error(f"❌ Error in _process_message: {e}")
            return self._create_error_response("Message processing failed", str(e))

    async def _execute_crew_task(self, context: Any, user_flow_type: UserFlowType) -> AgentResponse:
        """
        Execute a task using the CrewAI system.

        This method centralizes the logic for creating a minimal context
        and executing a task via the crew_lifecycle_manager, handling both
        NLP and direct command scenarios.

        Args:
            context: Message context
            user_flow_type: User registration status

        Returns:
            AgentResponse from the crew's execution.
        """
        try:
            # Create minimal execution context following CrewAI best practices
            from kickai.agents.utils.context_optimizer import ContextOptimizer

            execution_context = ContextOptimizer.create_minimal_context(
                telegram_id=context.telegram_id,
                team_id=context.team_id,
                chat_id=context.chat_id,
                chat_type=context.chat_type,
                message_text=context.message_text,
                username=context.username, # user_flow_type is available if needed
                is_registered=getattr(context, 'is_registered', False),
                is_player=getattr(context, 'is_player', False),
                is_team_member=getattr(context, 'is_team_member', False),
            )

            result = await self.crew_lifecycle_manager.execute_task(
                team_id=self.team_id,
                task_description=context.message_text,
                execution_context=execution_context
            )

            return AgentResponse(success=True, message=result)

        except Exception as e:
            logger.error(f"❌ Error in _execute_crew_task: {e}")
            return self._create_error_response("Crew task execution failed", str(e))

    async def route_contact_share(self, message: TelegramMessage) -> AgentResponse:
        """
        Handle contact sharing messages.

        Args:
            message: Telegram message containing contact

        Returns:
            AgentResponse with contact processing result
        """
        try:
            # Validate contact data
            if not message.contact:
                return self._create_error_response(
                    ERROR_MESSAGES["NO_CONTACT_INFO"], 
                    "Missing contact data"
                )

            # Extract phone number
            phone = message.contact.phone_number
            if not phone:
                return self._create_error_response("No phone number in contact", "Missing phone number")

            # Validate phone number
            is_valid, normalized_phone = PhoneValidator.validate_phone_for_linking(phone)
            if not is_valid:
                return self._create_error_response("Invalid phone number format", "Phone validation failed")

            # Process contact through appropriate agent
            context = create_context_from_telegram_message(
                telegram_id=message.telegram_id,
                team_id=self.team_id,
                chat_id=message.chat_id,
                chat_type=message.chat_type,
                message_text=message.text,
                username=message.username,
                telegram_name=message.username,  # Use username as telegram_name for now
            )
            context.contact_phone = normalized_phone
            
            user_flow_type = await UserRegistrationChecker.check_user_registration_status(
                message.telegram_id, self.team_id
            )
            
            # Contact sharing goes through unified crew task execution
            return await self._execute_crew_task(context, user_flow_type)
            
        except Exception as e:
            logger.error(f"❌ Error in route_contact_share: {e}")
            return self._create_error_response("Contact processing failed", str(e))

    def convert_telegram_update_to_message(self, update: Any, command_name: str = None) -> TelegramMessage:
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
            username = update.effective_user.username or update.effective_user.first_name or "unknown"
            chat_id = str(update.effective_chat.id)
            
            # Determine chat type
            chat_type = self._determine_chat_type(chat_id)
            
            # Handle new chat members data
            new_chat_members = None
            if update.message and hasattr(update.message, 'new_chat_members') and update.message.new_chat_members:
                new_chat_members = [{
                    'id': member.id,
                    'username': member.username,
                    'first_name': member.first_name,
                    'last_name': member.last_name,
                    'is_bot': member.is_bot
                } for member in update.message.new_chat_members if not member.is_bot]
            
            return TelegramMessage(
                telegram_id=telegram_id,
                text=text,
                chat_id=chat_id,
                chat_type=chat_type,
                team_id=self.team_id,
                username=username,
                name=update.effective_user.first_name,
                raw_update=update,
                new_chat_members=new_chat_members
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
                raw_update=update
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
            # Input validation using utility functions
            from kickai.utils.tool_validation import validate_string_input, ToolValidationError

            try:
                validated_main_chat_id = validate_string_input(main_chat_id, "Main Chat ID", allow_empty=False)
                validated_leadership_chat_id = validate_string_input(leadership_chat_id, "Leadership Chat ID", allow_empty=False)
                
                self.main_chat_id = validated_main_chat_id
                self.leadership_chat_id = validated_leadership_chat_id
                
                logger.info(f"Chat IDs set - Main: {validated_main_chat_id}, Leadership: {validated_leadership_chat_id}")
                
            except ToolValidationError as e:
                raise ValueError(str(e))
                
        except Exception as e:
            logger.error(f"❌ Error in set_chat_ids: {e}")
            raise

    async def get_metrics(self) -> dict:
        """
        Get router metrics for monitoring.

        Returns:
            Dictionary with router metrics
        """
        try:
            resource_metrics = self._resource_manager.get_metrics()
            
            return {
                "router_type": "AgenticMessageRouter",
                "team_id": self.team_id,
                "resources": resource_metrics,
                "crew_manager_available": self._crew_lifecycle_manager is not None,
                "main_chat_id": self.main_chat_id,
                "leadership_chat_id": self.leadership_chat_id,
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_metrics: {e}")
            return {
                "error": "Failed to get metrics",
                "router_type": "AgenticMessageRouter",
                "team_id": self.team_id,
            }

    def _create_error_response(self, message: str, error: str) -> AgentResponse:
        """
        Create a standardized error response.

        Args:
            message: User-friendly error message
            error: Technical error description

        Returns:
            AgentResponse with error details
        """
        try:
            return AgentResponse(
                success=False,
                message=message,
                error=error
            )
            
        except Exception as e:
            logger.error(f"❌ Error in _create_error_response: {e}")
            # Fallback to basic error response
            return AgentResponse(
                success=False,
                message="System error occurred",
                error="Error response creation failed"
            )
