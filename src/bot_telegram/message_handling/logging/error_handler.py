"""
Error Handler

This module provides error handling functionality.
"""

import logging
from core.context_manager import UserContext
from core.logging_config import log_errors, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


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
        return f"❌ Processing error: {error}"
    
    @staticmethod
    def handle_command_error(error: str, user_context: UserContext, command: str) -> str:
        """Handle command execution errors."""
        log_errors(
            error_type=ErrorCategory.COMMAND,
            severity=ErrorSeverity.ERROR,
            message=f"Command execution failed: {error}",
            context={
                "user_id": user_context.user_id,
                "chat_id": user_context.chat_id,
                "command": command,
                "error": error
            }
        )
        return f"❌ Command '{command}' failed: {error}"
    
    @staticmethod
    def handle_nlp_error(error: str, user_context: UserContext, query: str) -> str:
        """Handle natural language processing errors."""
        log_errors(
            error_type=ErrorCategory.NLP,
            severity=ErrorSeverity.ERROR,
            message=f"NLP processing failed: {error}",
            context={
                "user_id": user_context.user_id,
                "chat_id": user_context.chat_id,
                "query": query,
                "error": error
            }
        )
        return f"❌ I couldn't understand your request: {error}"
    
    @staticmethod
    def handle_system_error(error: str, user_context: UserContext) -> str:
        """Handle system errors."""
        log_errors(
            error_type=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            message=f"System error: {error}",
            context={
                "user_id": user_context.user_id,
                "chat_id": user_context.chat_id,
                "error": error
            }
        )
        return f"❌ System error: {error}"
    
    @staticmethod
    def handle_unknown_error(error: str, user_context: UserContext) -> str:
        """Handle unknown errors."""
        log_errors(
            error_type=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.ERROR,
            message=f"Unknown error: {error}",
            context={
                "user_id": user_context.user_id,
                "chat_id": user_context.chat_id,
                "error": error
            }
        )
        return f"❌ An unexpected error occurred: {error}"
    
    @staticmethod
    def format_error_message(error: str, user_friendly: bool = True) -> str:
        """Format error message for user display."""
        if user_friendly:
            # Provide user-friendly error messages
            friendly_errors = {
                "timeout": "The request took too long to process. Please try again.",
                "network": "Network connection issue. Please check your connection and try again.",
                "permission": "You don't have permission to perform this action.",
                "validation": "The input provided is not valid. Please check and try again.",
                "not_found": "The requested resource was not found.",
                "server_error": "A server error occurred. Please try again later."
            }
            
            for error_type, friendly_msg in friendly_errors.items():
                if error_type.lower() in error.lower():
                    return f"❌ {friendly_msg}"
            
            # Default friendly message
            return "❌ An error occurred. Please try again or contact support if the problem persists."
        else:
            # Return technical error message
            return f"❌ Error: {error}"
    
    @staticmethod
    def should_retry(error: str) -> bool:
        """Determine if an operation should be retried based on the error."""
        retryable_errors = [
            "timeout",
            "network",
            "connection",
            "temporary",
            "rate limit",
            "service unavailable"
        ]
        
        error_lower = error.lower()
        return any(retryable in error_lower for retryable in retryable_errors)
    
    @staticmethod
    def get_error_category(error: str) -> ErrorCategory:
        """Categorize an error based on its content."""
        error_lower = error.lower()
        
        if any(keyword in error_lower for keyword in ["permission", "access", "unauthorized"]):
            return ErrorCategory.PERMISSION
        elif any(keyword in error_lower for keyword in ["validation", "invalid", "format"]):
            return ErrorCategory.VALIDATION
        elif any(keyword in error_lower for keyword in ["timeout", "network", "connection"]):
            return ErrorCategory.NETWORK
        elif any(keyword in error_lower for keyword in ["command", "execution"]):
            return ErrorCategory.COMMAND
        elif any(keyword in error_lower for keyword in ["nlp", "language", "understanding"]):
            return ErrorCategory.NLP
        elif any(keyword in error_lower for keyword in ["system", "internal", "server"]):
            return ErrorCategory.SYSTEM
        else:
            return ErrorCategory.UNKNOWN 