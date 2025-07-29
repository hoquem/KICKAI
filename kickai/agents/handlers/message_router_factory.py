#!/usr/bin/env python3
"""
Message Router Factory

Factory for creating and configuring message handlers following the Factory Pattern.
"""

from typing import List

from loguru import logger

from kickai.agents.handlers.message_handlers import (
    CommandHandler,
    ContactShareHandler,
    MessageHandler,
    NewMemberWelcomeHandler,
    RegisteredUserHandler,
    UnregisteredUserHandler,
)
from kickai.agents.user_flow_agent import TelegramMessage


class MessageRouterFactory:
    """Factory for creating message handlers."""

    def __init__(self, team_id: str, crewai_system=None):
        self.team_id = team_id
        self.crewai_system = crewai_system

    def create_handlers(self) -> List[MessageHandler]:
        """Create all message handlers in priority order."""
        handlers = [
            # High priority handlers (specific message types)
            NewMemberWelcomeHandler(self.team_id),
            ContactShareHandler(self.team_id),
            CommandHandler(self.team_id, self.crewai_system),
            
            # Lower priority handlers (general message types)
            # These will be used based on user flow determination
            UnregisteredUserHandler(self.team_id),
            RegisteredUserHandler(self.team_id, self.crewai_system),
        ]
        
        logger.info(f"🔧 MessageRouterFactory: Created {len(handlers)} handlers for team {self.team_id}")
        return handlers

    def get_handler_for_message(self, message: TelegramMessage, user_flow_decision: str) -> MessageHandler:
        """Get the appropriate handler for a message based on its type and user flow."""
        
        # First, check for specific message types
        for handler in self.create_handlers():
            if handler.can_handle(message):
                logger.info(f"🔧 MessageRouterFactory: Selected {handler.__class__.__name__} for message")
                return handler
        
        # If no specific handler found, use user flow to determine handler
        if user_flow_decision == "unregistered_user":
            handler = UnregisteredUserHandler(self.team_id)
            logger.info(f"🔧 MessageRouterFactory: Using UnregisteredUserHandler based on user flow")
            return handler
        else:
            handler = RegisteredUserHandler(self.team_id, self.crewai_system)
            logger.info(f"🔧 MessageRouterFactory: Using RegisteredUserHandler based on user flow")
            return handler