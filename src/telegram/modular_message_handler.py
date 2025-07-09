#!/usr/bin/env python3
"""
Modular Message Handler for KICKAI Bot

This module provides a clean, maintainable message handling system that replaces
the massive player_registration_handler.py with a modular architecture using:
- Command parser for clean command parsing
- Base handlers for common functionality
- Specialized handlers for different command types
- Clean separation of concerns
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from telegram import Update
from telegram.ext import ContextTypes

from src.telegram.improved_command_parser import parse_command_improved, ParsedCommand, CommandType
from src.telegram.handlers.base_handler import HandlerContext, HandlerResult
from src.telegram.handlers.player_registration_handler import handle_player_registration_command
from src.services.access_control_service import AccessControlService
from src.core.enhanced_logging import (
    log_command_error, log_error, ErrorCategory, ErrorSeverity,
    create_error_context
)
from src.telegram.handlers.match_handler import MatchHandler
from src.telegram.handlers.payment_handler import PaymentHandler
from src.telegram.handlers.onboarding_handler import OnboardingHandler
from src.telegram.handlers.team_management_handler import TeamManagementHandler
from src.telegram.handlers.admin_handler import AdminHandler
from src.core.improved_configuration_manager import ImprovedConfigurationManager

logger = logging.getLogger(__name__)


@dataclass
class MessageContext:
    """Context for message processing."""
    update: Update
    context: ContextTypes.DEFAULT_TYPE
    user_id: str
    chat_id: str
    message_text: str
    username: Optional[str] = None
    team_id: Optional[str] = None
    chat_type: str = "main"  # main, leadership, private


class ModularMessageHandler:
    """Main message handler using modular architecture."""
    
    def __init__(self):
        self.config_manager = ImprovedConfigurationManager()
        self.access_control_service = AccessControlService()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.match_handler = MatchHandler()
        self.payment_handler = PaymentHandler()
        self.onboarding_handler = OnboardingHandler()
        self.team_management_handler = TeamManagementHandler()
        self.admin_handler = AdminHandler()
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handle incoming messages using modular architecture."""
        try:
            # Extract message context
            message_context = await self._extract_message_context(update, context)
            
            # Parse command
            parsed_command = parse_command_improved(message_context.message_text)
            
            # Route to appropriate handler
            result = await self._route_command(parsed_command, message_context)
            
            return result.message if result.success else result.error
            
        except Exception as e:
            error_context = create_error_context(
                user_id=str(update.effective_user.id) if update.effective_user else "unknown",
                chat_id=str(update.effective_chat.id) if update.effective_chat else "unknown",
                command="message_handling"
            )
            
            log_command_error(
                error=e,
                context=error_context,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.MESSAGE_HANDLING
            )
            
            self.logger.error(f"Error handling message: {str(e)}", exc_info=True)
            return f"❌ **Error**\n\nAn error occurred while processing your message. Please try again or contact support."
    
    async def _extract_message_context(self, update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> MessageContext:
        """Extract context from Telegram update."""
        user = update.effective_user
        chat = update.effective_chat
        message = update.message
        
        if not user or not chat or not message:
            raise ValueError("Invalid update: missing user, chat, or message")
        
        # Resolve team ID from chat
        team_id = self.config_manager.resolve_team_id(str(chat.id))
        
        # Determine chat type
        chat_type = self._determine_chat_type(chat.id, team_id)
        
        return MessageContext(
            update=update,
            context=context,
            user_id=str(user.id),
            chat_id=str(chat.id),
            message_text=message.text or "",
            username=user.username,
            team_id=team_id,
            chat_type=chat_type
        )
    
    def _determine_chat_type(self, chat_id: int, team_id: Optional[str]) -> str:
        """Determine the type of chat."""
        if not team_id:
            return "private"
        
        # This would need to be implemented based on your chat configuration
        # For now, we'll use a simple heuristic
        chat_id_str = str(chat_id)
        
        # You might want to check against leadership chat IDs from config
        # For now, we'll assume main chat
        return "main"
    
    async def _route_command(self, parsed_command: ParsedCommand, 
                            message_context: MessageContext) -> HandlerResult:
        """Route command to appropriate handler."""
        command_type = parsed_command.command_type
        
        # Create handler context
        handler_context = HandlerContext(
            user_id=message_context.user_id,
            chat_id=message_context.chat_id,
            team_id=message_context.team_id or "unknown",
            username=message_context.username,
            raw_update=message_context.update,
            additional_data={
                "chat_type": message_context.chat_type,
                "parsed_command": parsed_command
            }
        )
        
        # Player registration commands
        if command_type in [
            CommandType.ADD_PLAYER,
            CommandType.REGISTER,
            CommandType.REMOVE_PLAYER,
            CommandType.APPROVE,
            CommandType.REJECT,
            CommandType.INVITE,
            CommandType.STATUS,
            CommandType.LIST,
            CommandType.PENDING,
            CommandType.HELP,
            CommandType.START
        ]:
            return await handle_player_registration_command(
                message_context.message_text, 
                handler_context
            )
        # Match commands
        elif command_type in [
            CommandType.CREATE_MATCH,
            CommandType.ATTEND_MATCH,
            CommandType.UNATTEND_MATCH,
            CommandType.LIST_MATCHES,
            CommandType.RECORD_RESULT
        ]:
            return await self.match_handler.handle(handler_context, parsed_command=parsed_command)
        # Payment commands
        elif command_type in [
            CommandType.CREATE_PAYMENT,
            CommandType.PAYMENT_STATUS,
            CommandType.PENDING_PAYMENTS,
            CommandType.PAYMENT_HISTORY,
            CommandType.FINANCIAL_DASHBOARD
        ]:
            return await self.payment_handler.handle(handler_context, parsed_command=parsed_command)
        
        # Onboarding commands
        elif command_type in [
            CommandType.START_ONBOARDING,
            CommandType.PROCESS_ONBOARDING_RESPONSE,
            CommandType.ONBOARDING_STATUS
        ]:
            return await self.onboarding_handler.handle(handler_context, parsed_command=parsed_command)
        
        # Team management commands
        elif command_type in [
            CommandType.ADD_TEAM,
            CommandType.REMOVE_TEAM,
            CommandType.LIST_TEAMS,
            CommandType.UPDATE_TEAM_INFO
        ]:
            return await self.team_management_handler.handle(handler_context, parsed_command=parsed_command)
        
        # Admin commands
        elif command_type in [
            CommandType.BROADCAST,
            CommandType.PROMOTE_USER,
            CommandType.DEMOTE_USER,
            CommandType.SYSTEM_STATUS
        ]:
            return await self.admin_handler.handle(handler_context, parsed_command=parsed_command)
        
        # Default: unknown command
        return HandlerResult.error_result(
            f"Unknown command: {command_type.value}. Use /help for available commands."
        )
    
    async def handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handle /start command specifically."""
        try:
            message_context = await self._extract_message_context(update, context)
            
            # Create handler context
            handler_context = HandlerContext(
                user_id=message_context.user_id,
                chat_id=message_context.chat_id,
                team_id=message_context.team_id or "unknown",
                username=message_context.username,
                raw_update=message_context.update
            )
            
            # Parse start command
            parsed_command = parse_command_improved("/start")
            
            # Handle using player registration handler
            result = await handle_player_registration_command("/start", handler_context)
            
            return result.message if result.success else result.error
            
        except Exception as e:
            self.logger.error(f"Error handling start command: {str(e)}", exc_info=True)
            return "❌ **Error**\n\nFailed to start the bot. Please try again."
    
    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handle /help command specifically."""
        try:
            message_context = await self._extract_message_context(update, context)
            
            # Create handler context
            handler_context = HandlerContext(
                user_id=message_context.user_id,
                chat_id=message_context.chat_id,
                team_id=message_context.team_id or "unknown",
                username=message_context.username,
                raw_update=message_context.update
            )
            
            # Parse help command
            parsed_command = parse_command_improved("/help")
            
            # Handle using player registration handler
            result = await handle_player_registration_command("/help", handler_context)
            
            return result.message if result.success else result.error
            
        except Exception as e:
            self.logger.error(f"Error handling help command: {str(e)}", exc_info=True)
            return "❌ **Error**\n\nFailed to show help. Please try again."


# Global handler instance
_modular_message_handler = None

def get_modular_message_handler() -> ModularMessageHandler:
    """Get the global modular message handler instance."""
    global _modular_message_handler
    if _modular_message_handler is None:
        _modular_message_handler = ModularMessageHandler()
    return _modular_message_handler


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle a message using the global modular message handler."""
    handler = get_modular_message_handler()
    return await handler.handle_message(update, context)


async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle /start command using the global modular message handler."""
    handler = get_modular_message_handler()
    return await handler.handle_start_command(update, context)


async def handle_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle /help command using the global modular message handler."""
    handler = get_modular_message_handler()
    return await handler.handle_help_command(update, context) 