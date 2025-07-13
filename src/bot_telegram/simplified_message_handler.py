#!/usr/bin/env python3
"""
Simplified Message Handler

This module provides a simplified, maintainable message handler that separates
concerns into focused components for better maintainability.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from telegram import Update
from telegram.ext import ContextTypes

from core.context_manager import get_context_manager, UserContext
from core.enhanced_logging import log_user_event, log_errors, ErrorCategory, ErrorSeverity
from agents.simplified_orchestration import SimplifiedOrchestrationPipeline
from agents.crew_agents import TeamManagementSystem
from domain.interfaces.team_operations import ITeamOperations
from bot_telegram.unified_command_system import is_slash_command, extract_command_name, process_command

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


class MessageValidator:
    """Validates incoming messages."""
    
    @staticmethod
    def validate_message(update: Update) -> Tuple[bool, str]:
        """Validate that a message can be processed."""
        if not update.effective_message or not update.effective_message.text:
            return False, "No text message found"
        
        if not update.effective_user or not update.effective_chat:
            return False, "Missing user or chat information"
        
        text = update.effective_message.text.strip()
        if not text:
            return False, "Empty message"
        
        return True, "Valid message"


class PermissionChecker:
    """Handles permission checking for messages."""
    
    @staticmethod
    def check_user_registration(user_context: UserContext) -> Tuple[bool, str]:
        """Check if user is registered."""
        if not user_context.is_registered_player:
            return False, "User not registered"
        return True, "User registered"
    
    @staticmethod
    def check_chat_permissions(user_context: UserContext) -> Tuple[bool, str]:
        """Check chat-based permissions."""
        # Add any chat-specific permission logic here
        return True, "Chat permissions valid"
    
    @staticmethod
    def check_command_permissions(command_name: str, user_context: UserContext) -> Tuple[bool, str]:
        """Check command-specific permissions."""
        # Add command-specific permission logic here
        return True, "Command permissions valid"


class MessageLogger:
    """Handles message logging."""
    
    @staticmethod
    def log_message_received(update: Update, user_context: UserContext):
        """Log that a message was received."""
        log_user_event(
            user_id=user_context.user_id,
            event_type="message_received",
            details={
                "chat_id": user_context.chat_id,
                "team_id": user_context.team_id,
                "message_length": len(user_context.message_text),
                "is_leadership_chat": user_context.is_leadership_chat,
                "is_registered": user_context.is_registered_player
            }
        )
        logger.info(f"Message received from {user_context.username} ({user_context.user_id}) in {user_context.chat_id}")
    
    @staticmethod
    def log_message_processed(user_context: UserContext, result: str, success: bool):
        """Log that a message was processed."""
        log_user_event(
            user_id=user_context.user_id,
            event_type="message_processed",
            details={
                "chat_id": user_context.chat_id,
                "team_id": user_context.team_id,
                "success": success,
                "result_length": len(result) if result else 0
            }
        )
        logger.info(f"Message processed for {user_context.username}: success={success}")


class ErrorHandler:
    """Handles error processing."""
    
    @staticmethod
    def handle_validation_error(error: str) -> str:
        """Handle validation errors."""
        log_errors(
            error_type=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            message=f"Message validation failed: {error}",
            context={"error": error}
        )
        return f"❌ Message validation failed: {error}"
    
    @staticmethod
    def handle_permission_error(error: str, user_context: UserContext) -> str:
        """Handle permission errors."""
        log_errors(
            error_type=ErrorCategory.PERMISSION,
            severity=ErrorSeverity.WARNING,
            message=f"Permission denied: {error}",
            context={
                "user_id": user_context.user_id,
                "chat_id": user_context.chat_id,
                "error": error
            }
        )
        return f"❌ Permission denied: {error}"
    
    @staticmethod
    def handle_processing_error(error: str, user_context: UserContext) -> str:
        """Handle processing errors."""
        log_errors(
            error_type=ErrorCategory.PROCESSING,
            severity=ErrorSeverity.ERROR,
            message=f"Message processing failed: {error}",
            context={
                "user_id": user_context.user_id,
                "chat_id": user_context.chat_id,
                "error": error
            }
        )
        return f"❌ Sorry, I encountered an error processing your message. Please try again or contact support if the issue persists."


class CommandProcessor:
    """Handles command processing."""
    
    @staticmethod
    async def process_slash_command(message_text: str, user_context: UserContext, update: Update) -> Tuple[bool, str]:
        """Process a slash command."""
        try:
            command_name = extract_command_name(message_text)
            logger.info(f"Processing slash command: {command_name}")
            
            result = await process_command(
                command_name=command_name,
                user_id=user_context.user_id,
                chat_id=user_context.chat_id,
                team_id=user_context.team_id,
                message_text=message_text,
                username=user_context.username,
                raw_update=update
            )
            
            if result and result.success:
                logger.info(f"Command {command_name} executed successfully")
                return True, result.message
            else:
                error_msg = result.message if result else "Unknown command error"
                logger.warning(f"Command {command_name} failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return False, f"Command processing error: {str(e)}"


class NaturalLanguageProcessor:
    """Handles natural language processing."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.agent_system = self._initialize_agent_system()
    
    def _initialize_agent_system(self) -> TeamManagementSystem:
        """Initialize the agent system."""
        try:
            from core.config_adapter import TeamConfigObject
            from core.settings import Settings
            
            settings = Settings()
            team_config = TeamConfigObject(settings, self.team_id)
            
            return TeamManagementSystem(
                team_id=self.team_id,
                team_config=team_config
            )
        except Exception as e:
            logger.error(f"Error initializing agent system: {e}")
            raise
    
    async def process_natural_language(self, message_text: str, user_context: UserContext) -> str:
        """Process natural language queries."""
        try:
            logger.info(f"Processing natural language query: {message_text[:50]}...")
            
            # Build execution context
            execution_context = {
                'user_id': user_context.user_id,
                'chat_id': user_context.chat_id,
                'team_id': user_context.team_id,
                'player_id': user_context.player_id,
                'is_leadership_chat': user_context.is_leadership_chat,
                'is_registered': user_context.is_registered,
                'is_in_correct_team': user_context.is_in_correct_team,
                'username': user_context.username,
                'timestamp': user_context.timestamp.isoformat() if user_context.timestamp else None,
                'onboarding_message': user_context.onboarding_message
            }
            
            # Execute using agent system
            result = await self.agent_system.execute_task(message_text, execution_context)
            
            logger.info(f"Natural language processing completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in natural language processing: {e}")
            raise


class SimplifiedMessageHandler:
    """
    Simplified message handler with separated concerns.
    
    This class provides a clean, maintainable message processing pipeline
    with separate components for validation, permissions, logging, and processing.
    """
    
    def __init__(self, team_id: str = None):
        """Initialize the simplified message handler."""
        self.team_id = team_id or self._get_default_team_id()
        self.context_manager = get_context_manager()
        
        # Initialize components
        self.validator = MessageValidator()
        self.permission_checker = PermissionChecker()
        self.logger = MessageLogger()
        self.error_handler = ErrorHandler()
        self.command_processor = CommandProcessor()
        self.nlp_processor = NaturalLanguageProcessor(self.team_id)
        
        logger.info("✅ SimplifiedMessageHandler initialized successfully")
    
    def _get_default_team_id(self) -> str:
        """Get default team ID."""
        try:
            from core.settings import get_settings
            return get_settings().default_team_id
        except:
            return 'KAI'  # Fallback
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """Handle incoming messages using the simplified pipeline."""
        try:
            # Step 1: Validate message
            is_valid, validation_error = self.validator.validate_message(update)
            if not is_valid:
                return self.error_handler.handle_validation_error(validation_error)
            
            # Step 2: Build user context
            user_context = await self.context_manager.build_context(update, context, update.effective_message.text)
            
            # Step 3: Log message received
            self.logger.log_message_received(update, user_context)
            
            # Step 4: Check user registration
            is_registered, registration_error = self.permission_checker.check_user_registration(user_context)
            if not is_registered:
                welcome_message = self.context_manager.get_welcome_message_for_unregistered_user(user_context)
                self.logger.log_message_processed(user_context, welcome_message, True)
                return welcome_message
            
            # Step 5: Check chat permissions
            chat_permitted, chat_error = self.permission_checker.check_chat_permissions(user_context)
            if not chat_permitted:
                error_msg = self.error_handler.handle_permission_error(chat_error, user_context)
                self.logger.log_message_processed(user_context, error_msg, False)
                return error_msg
            
            # Step 6: Process message based on type
            message_text = update.effective_message.text.strip()
            result = None
            success = False
            
            if is_slash_command(message_text):
                # Process slash command
                success, result = await self.command_processor.process_slash_command(
                    message_text, user_context, update
                )
            else:
                # Process natural language
                try:
                    result = await self.nlp_processor.process_natural_language(message_text, user_context)
                    success = True
                except Exception as e:
                    result = self.error_handler.handle_processing_error(str(e), user_context)
                    success = False
            
            # Step 7: Log message processed
            self.logger.log_message_processed(user_context, result, success)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in simplified message handler: {e}", exc_info=True)
            return self.error_handler.handle_processing_error(str(e), user_context)


# Global instance and convenience functions
_simplified_handler: Optional[SimplifiedMessageHandler] = None


def get_simplified_message_handler(team_id: str = None) -> SimplifiedMessageHandler:
    """Get the global simplified message handler instance."""
    global _simplified_handler
    if _simplified_handler is None:
        _simplified_handler = SimplifiedMessageHandler(team_id=team_id)
    return _simplified_handler


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    """Global message handler function."""
    handler = get_simplified_message_handler()
    return await handler.handle_message(update, context)


def register_simplified_handler(app):
    """
    Register the simplified message handler with the telegram application.
    """
    try:
        from telegram.ext import MessageHandler, filters
        
        # Register handler for all text messages
        app.add_handler(MessageHandler(filters.TEXT, handle_message))
        
        logger.info("✅ Simplified message handler registered successfully")
        logger.info("   Architecture: Separated concerns, focused components")
        logger.info("   Benefits: Better maintainability, easier testing")
        
    except Exception as e:
        logger.error(f"❌ Failed to register simplified message handler: {e}")
        raise 