#!/usr/bin/env python3
"""
Agentic Message Router

This module provides centralized agentic message routing following CrewAI best practices.
ALL messages go through agents - no direct processing bypasses the agentic system.
"""

from typing import Any, Optional

from loguru import logger

from kickai.agents.context.context_builder import ContextBuilder
from kickai.agents.handlers.message_router_factory import MessageRouterFactory
from kickai.agents.user_flow_agent import AgentResponse, TelegramMessage, UserFlowAgent, UserFlowDecision
from kickai.core.enums import ChatType


class AgenticMessageRouter:
    """
    Centralized agentic message routing following CrewAI best practices.

    This router ensures that ALL messages go through the agentic system.
    No direct processing bypasses agents.
    """

    def __init__(self, team_id: str, crewai_system=None):
        self.team_id = team_id
        self.crewai_system = crewai_system
        
        # Initialize components
        self.user_flow_agent = UserFlowAgent(team_id=team_id)
        self.context_builder = ContextBuilder(team_id=team_id)
        self.router_factory = MessageRouterFactory(team_id=team_id, crewai_system=crewai_system)
        
        # Chat configuration
        self.main_chat_id = None
        self.leadership_chat_id = None
        
        logger.info(f"🤖 AgenticMessageRouter initialized for team {team_id}")

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

            # Determine user flow
            user_flow_result = await self.user_flow_agent.determine_user_flow(
                user_id=message.user_id, 
                chat_type=message.chat_type, 
                command=message.text.split()[0] if message.text.startswith("/") else None
            )

            # Get appropriate handler
            handler = self.router_factory.get_handler_for_message(message, user_flow_result.value)

            # Handle the message
            return await handler.handle(message)

        except Exception as e:
            logger.error(f"❌ AgenticMessageRouter failed: {e}")
            return AgentResponse(
                success=False, 
                message="❌ System error. Please try again.", 
                error=str(e)
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
            logger.info(f"📱 AgenticMessageRouter: Processing contact share from {message.username}")

            # Use the contact share handler
            handler = self.router_factory.get_handler_for_message(message, "registered_user")
            return await handler.handle(message)

        except Exception as e:
            logger.error(f"❌ Error in contact share routing: {e}")
            return AgentResponse(
                success=False,
                message="I encountered an error processing your contact information. Please try again.",
            )

    async def route_new_member_welcome(self, message: TelegramMessage) -> AgentResponse:
        """
        Route new member welcome messages through the agentic system.
        
        Args:
            message: Telegram message with new member context
            
        Returns:
            AgentResponse with welcome message
        """
        try:
            logger.info(f"👋 AgenticMessageRouter: Processing new member welcome for {message.username}")

            # Use the new member welcome handler
            handler = self.router_factory.get_handler_for_message(message, "unregistered_user")
            return await handler.handle(message)

        except Exception as e:
            logger.error(f"❌ Critical error in new member welcome routing: {e}")
            return AgentResponse(
                success=False,
                message="❌ Error processing welcome message. Please try again.",
                error=str(e)
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
            logger.info(f"🔄 AgenticMessageRouter: Routing command {command_name} in {message.chat_type.value}")

            # Use the command handler
            handler = self.router_factory.get_handler_for_message(message, "registered_user")
            return await handler.handle(message)

        except Exception as e:
            logger.error(f"❌ Error routing command: {e}")
            return AgentResponse(
                message="I encountered an error processing your command. Please try again.",
                success=False,
                error=str(e),
            )

    def convert_telegram_update_to_message(
        self, update: Any, command_name: str = None, is_new_member: bool = False
    ) -> TelegramMessage:
        """
        Convert Telegram update to domain message.

        Args:
            update: Telegram update object (can be None for new member messages)
            command_name: Optional command name for command messages
            is_new_member: Whether this is for a new member welcome

        Returns:
            TelegramMessage domain object
        """
        try:
            # Handle new member case where update might be None
            if is_new_member and update is None:
                # Create a minimal message for new member processing
                return TelegramMessage(
                    user_id="",  # Will be set by caller
                    chat_id="",  # Will be set by caller
                    chat_type=ChatType.MAIN,  # Will be set by caller
                    username="",  # Will be set by caller
                    team_id=self.team_id,
                    text="",  # Not needed for new member messages
                    raw_update=None,
                    contact_phone=None,
                    contact_user_id=None,
                    is_new_member=True,
                )

            # Standard update processing
            if not update:
                raise ValueError("Update object is required for non-new-member messages")

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
                is_new_member=is_new_member,
            )

        except Exception as e:
            logger.error(f"❌ Error converting Telegram update to message: {e}")
            # Return a minimal valid message for error cases
            return TelegramMessage(
                user_id="",
                chat_id="",
                chat_type=ChatType.MAIN,
                username="",
                team_id=self.team_id,
                text="",
                raw_update=None,
                contact_phone=None,
                contact_user_id=None,
                is_new_member=is_new_member,
            )

    def _determine_chat_type(self, chat_id: str) -> ChatType:
        """Determine the chat type based on chat ID."""
        # Use configured chat IDs if available
        if self.main_chat_id and self.leadership_chat_id:
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

    def _determine_chat_type_with_ids(self, chat_id: str) -> ChatType:
        """Determine chat type using configured chat IDs."""
        if chat_id == self.main_chat_id:
            return ChatType.MAIN
        elif chat_id == self.leadership_chat_id:
            return ChatType.LEADERSHIP
        else:
            return ChatType.PRIVATE
