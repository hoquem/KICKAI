"""
Simplified Message Handler - Modular Architecture

This module provides the main message handler that orchestrates all components
following the single responsibility principle.
"""

import logging
from typing import Optional
from dataclasses import dataclass

from telegram import Update
from telegram.ext import ContextTypes

from core.context_manager import get_context_manager, UserContext
from .validation import MessageValidator, PermissionChecker
from .processing import CommandProcessor, NaturalLanguageProcessor
from .logging import MessageLogger, ErrorHandler

logger = logging.getLogger(__name__)


@dataclass
class MessageContext:
    """Context for message processing."""
    user_id: str
    chat_id: str
    team_id: str
    username: str
    message_text: str
    is_leadership_chat: bool
    is_registered_player: bool
    user_role: str
    timestamp: str


class SimplifiedMessageHandler:
    """
    Simplified message handler using modular components.
    
    This class orchestrates the message processing pipeline using separate
    components for validation, processing, and logging.
    """
    
    def __init__(self):
        self.context_manager = get_context_manager()
        self.validator = MessageValidator()
        self.permission_checker = PermissionChecker()
        self.command_processor = CommandProcessor()
        self.message_logger = MessageLogger()
        self.error_handler = ErrorHandler()
        logger.info("SimplifiedMessageHandler initialized with modular components")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """
        Handle incoming messages using the modular pipeline.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            Response message or None
        """
        try:
            # Step 1: Validate message
            is_valid, validation_message = self.validator.validate_message(update)
            if not is_valid:
                return self.error_handler.handle_validation_error(validation_message)
            
            # Step 2: Get user context
            user_id = str(update.effective_user.id)
            user_context = await self.context_manager.get_user_context(user_id)
            if not user_context:
                return "❌ Unable to determine your team context. Please try again."
            
            # Step 3: Log message received
            self.message_logger.log_message_received(update, user_context)
            
            # Step 4: Check permissions
            permission_valid, permission_message = self.permission_checker.check_chat_permissions(user_context)
            if not permission_valid:
                return self.error_handler.handle_permission_error(permission_message, user_context)
            
            # Step 5: Process message
            message_text = update.effective_message.text.strip()
            result = await self._process_message(message_text, user_context, update)
            
            # Step 6: Log message processed
            success = not result.startswith("❌") if result else False
            self.message_logger.log_message_processed(user_context, result, success)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in message handler: {e}", exc_info=True)
            return self.error_handler.handle_unknown_error(str(e), user_context if 'user_context' in locals() else None)
    
    async def _process_message(self, message_text: str, user_context: UserContext, update: Update) -> str:
        """Process a message using appropriate processor."""
        try:
            # Check if it's a command
            if self.command_processor.is_command(message_text):
                return await self._process_command(message_text, user_context, update)
            else:
                return await self._process_natural_language(message_text, user_context)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self.error_handler.handle_processing_error(str(e), user_context)
    
    async def _process_command(self, message_text: str, user_context: UserContext, update: Update) -> str:
        """Process a command."""
        try:
            command_name = self.command_processor.extract_command_name(message_text)
            
            # Check command permissions
            permission_valid, permission_message = self.permission_checker.check_command_permissions(command_name, user_context)
            if not permission_valid:
                return self.error_handler.handle_permission_error(permission_message, user_context)
            
            # Process command
            success, result = await self.command_processor.process_slash_command(message_text, user_context, update)
            
            # Log command execution
            self.message_logger.log_command_execution(user_context, command_name, success, result)
            
            if success:
                return result
            else:
                return self.error_handler.handle_command_error(result, user_context, command_name)
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return self.error_handler.handle_command_error(str(e), user_context, message_text)
    
    async def _process_natural_language(self, message_text: str, user_context: UserContext) -> str:
        """Process natural language."""
        try:
            # Check if it's a help request
            if self.command_processor.is_help_request(message_text):
                return await self._process_help_request(message_text, user_context)
            
            # Process with NLP
            result = await self.command_processor.process_natural_language(message_text, user_context)
            
            # Log NLP processing
            success = not result.startswith("❌") if result else False
            self.message_logger.log_nlp_processing(user_context, message_text, success, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing natural language: {e}")
            return self.error_handler.handle_nlp_error(str(e), user_context, message_text)
    
    async def _process_help_request(self, message_text: str, user_context: UserContext) -> str:
        """Process a help request."""
        try:
            # Help is now handled by the permission service in the Telegram bot service
            return "💡 Use /help to see available commands for this chat."
            
        except Exception as e:
            logger.error(f"Error processing help request: {e}")
            return "❌ Error providing help. Please use /help for assistance."
    
    def get_help_text(self, command_name: str, user_id: str) -> Optional[str]:
        """Get help text for a specific command."""
        # Help is now handled by the permission service
        return None
    
    def get_feature_help(self, feature: str, user_id: str) -> Optional[str]:
        """Get help text for a specific feature."""
        # Help is now handled by the permission service
        return None


# Global handler instance
_handler_instance: Optional[SimplifiedMessageHandler] = None


def get_simplified_message_handler(team_id: str = None) -> SimplifiedMessageHandler:
    """Get the global message handler instance."""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = SimplifiedMessageHandler()
    return _handler_instance


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Handle a message using the simplified handler."""
    handler = get_simplified_message_handler()
    return await handler.handle_message(update, context)


def register_simplified_handler(app):
    """Register the simplified message handler with the Telegram app."""
    from telegram.ext import MessageHandler, filters
    
    handler = get_simplified_message_handler()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Simplified message handler registered successfully")
    logger.info("   Architecture: Separated concerns, focused components")
    logger.info("   Benefits: Better maintainability, easier testing") 