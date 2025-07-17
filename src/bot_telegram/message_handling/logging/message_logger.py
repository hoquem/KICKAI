"""
Message Logger

This module provides message logging functionality.
"""

import logging
from telegram import Update
from core.context_manager import UserContext
from core.logging_config import log_user_event, LogContext

logger = logging.getLogger(__name__)


class MessageLogger:
    """Handles message logging."""
    
    @staticmethod
    def log_message_received(update: Update, user_context: UserContext):
        """Log that a message was received."""
        try:
            context = LogContext(
                user_id=user_context.user_id,
                chat_id=user_context.chat_id,
                team_id=user_context.team_id,
                metadata={
                    "message_length": len(user_context.message_text),
                    "is_leadership_chat": user_context.is_leadership_chat,
                    "is_registered": user_context.is_registered_player
                }
            )
            log_user_event("message_received", user_context.user_id, context)
            logger.info(f"Message received from {user_context.username} ({user_context.user_id}) in {user_context.chat_id}")
        except Exception as e:
            logger.error(f"Error logging message received: {e}")
    
    @staticmethod
    def log_message_processed(user_context: UserContext, result: str, success: bool):
        """Log that a message was processed."""
        try:
            context = LogContext(
                user_id=user_context.user_id,
                chat_id=user_context.chat_id,
                team_id=user_context.team_id,
                metadata={
                    "success": success,
                    "result_length": len(result) if result else 0
                }
            )
            logger.info(f"Message processed for {user_context.username}: success={success}")
        except Exception as e:
            logger.error(f"Error logging message processed: {e}")
    
    @staticmethod
    def log_command_execution(user_context: UserContext, command: str, success: bool, result: str = None):
        """Log command execution."""
        try:
            context = LogContext(
                user_id=user_context.user_id,
                chat_id=user_context.chat_id,
                team_id=user_context.team_id,
                metadata={
                    "command": command,
                    "success": success,
                    "result_length": len(result) if result else 0
                }
            )
            log_user_event("command_executed", user_context.user_id, context)
            logger.info(f"Command '{command}' executed for {user_context.username}: success={success}")
        except Exception as e:
            logger.error(f"Error logging command execution: {e}")
    
    @staticmethod
    def log_nlp_processing(user_context: UserContext, query: str, success: bool, result: str = None):
        """Log natural language processing."""
        try:
            context = LogContext(
                user_id=user_context.user_id,
                chat_id=user_context.chat_id,
                team_id=user_context.team_id,
                metadata={
                    "query": query,
                    "success": success,
                    "result_length": len(result) if result else 0
                }
            )
            log_user_event("nlp_processed", user_context.user_id, context)
            logger.info(f"NLP query processed for {user_context.username}: success={success}")
        except Exception as e:
            logger.error(f"Error logging NLP processing: {e}")
    
    @staticmethod
    def log_permission_check(user_context: UserContext, resource: str, granted: bool):
        """Log permission checks."""
        try:
            context = LogContext(
                user_id=user_context.user_id,
                chat_id=user_context.chat_id,
                team_id=user_context.team_id,
                metadata={
                    "resource": resource,
                    "granted": granted
                }
            )
            log_user_event("permission_checked", user_context.user_id, context)
            logger.info(f"Permission check for {resource} by {user_context.username}: granted={granted}")
        except Exception as e:
            logger.error(f"Error logging permission check: {e}")
    
    @staticmethod
    def log_validation_result(user_context: UserContext, validation_type: str, passed: bool, details: str = None):
        """Log validation results."""
        try:
            context = LogContext(
                user_id=user_context.user_id,
                chat_id=user_context.chat_id,
                team_id=user_context.team_id,
                metadata={
                    "validation_type": validation_type,
                    "passed": passed,
                    "details": details
                }
            )
            log_user_event("validation_result", user_context.user_id, context)
            logger.info(f"Validation {validation_type} for {user_context.username}: passed={passed}")
        except Exception as e:
            logger.error(f"Error logging validation result: {e}") 