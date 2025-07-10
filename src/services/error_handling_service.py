"""
Enhanced Error Handling Service for KICKAI

This service provides centralized error handling, logging, and admin notification
for robust user feedback and system monitoring.
"""

import asyncio
import traceback
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime
import os

from core.logging_config import get_logger, LogContext
from core.exceptions import (
    KICKAIError, UserFacingError, SystemError, create_error_context,
    get_error_category, format_error_message, get_user_friendly_message,
    should_notify_admin, is_retryable_error, is_critical_error
)
from core.improved_config_system import get_improved_config
from services.telegram_service import get_telegram_service

logger = get_logger(__name__)


@dataclass
class ErrorReport:
    """Structured error report for logging and notification."""
    timestamp: datetime
    error: Exception
    user_id: Optional[str]
    chat_id: Optional[str]
    team_id: Optional[str]
    operation: str
    message_text: Optional[str]
    error_category: str
    is_retryable: bool
    requires_admin_attention: bool
    stack_trace: str
    context: Dict[str, Any]


class ErrorHandlingService:
    """
    Centralized error handling service for robust user feedback and system monitoring.
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        config = get_improved_config()
        team_config = config.get_team_config(team_id)
        self.admin_chat_id = team_config.leadership_chat_id if team_config else None
        self.error_reports: List[ErrorReport] = []
        self.max_reports = 100  # Keep last 100 error reports in memory
        
    async def handle_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        message_text: Optional[str] = None,
        operation: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Handle an error and return a user-friendly message.
        
        Args:
            error: The exception that occurred
            user_id: ID of the user who triggered the error
            chat_id: ID of the chat where the error occurred
            message_text: Original message text that caused the error
            operation: Operation being performed when error occurred
            context: Additional context information
            
        Returns:
            User-friendly error message to display
        """
        try:
            # Create error report
            error_report = self._create_error_report(
                error, user_id, chat_id, message_text, operation, context
            )
            
            # Log the error
            await self._log_error(error_report)
            
            # Send admin notification if needed
            if should_notify_admin(error):
                await self._notify_admin(error_report)
            
            # Store error report
            self._store_error_report(error_report)
            
            # Return user-friendly message
            return get_user_friendly_message(error)
            
        except Exception as logging_error:
            # If error handling itself fails, log it and return generic message
            logger.error(f"Error in error handling: {logging_error}", exc_info=True)
            return "❌ Sorry, I encountered an error processing your request. Please try again."
    
    def _create_error_report(
        self,
        error: Exception,
        user_id: Optional[str],
        chat_id: Optional[str],
        message_text: Optional[str],
        operation: str,
        context: Optional[Dict[str, Any]]
    ) -> ErrorReport:
        """Create a structured error report."""
        return ErrorReport(
            timestamp=datetime.now(),
            error=error,
            user_id=user_id,
            chat_id=chat_id,
            team_id=self.team_id,
            operation=operation,
            message_text=message_text,
            error_category=get_error_category(error),
            is_retryable=is_retryable_error(error),
            requires_admin_attention=should_notify_admin(error),
            stack_trace=traceback.format_exc(),
            context=context or {}
        )
    
    async def _log_error(self, error_report: ErrorReport) -> None:
        """Log the error with appropriate level and context."""
        log_context = LogContext(
            team_id=error_report.team_id,
            user_id=error_report.user_id,
            chat_id=error_report.chat_id,
            operation=error_report.operation,
            component="error_handling"
        )
        
        # Format error message
        error_msg = format_error_message(error_report.error, include_context=True)
        
        # Log with appropriate level based on error category
        if error_report.requires_admin_attention:
            logger.error(
                f"🚨 CRITICAL ERROR: {error_msg} | "
                f"Category: {error_report.error_category} | "
                f"Retryable: {error_report.is_retryable} | "
                f"Message: {error_report.message_text}",
                context=log_context,
                exc_info=error_report.error
            )
        elif error_report.error_category in ["system", "infrastructure"]:
            logger.error(
                f"🔴 SYSTEM ERROR: {error_msg} | "
                f"Category: {error_report.error_category} | "
                f"Message: {error_report.message_text}",
                context=log_context,
                exc_info=error_report.error
            )
        elif error_report.error_category in ["domain", "validation"]:
            logger.warning(
                f"🟡 DOMAIN ERROR: {error_msg} | "
                f"Category: {error_report.error_category} | "
                f"Message: {error_report.message_text}",
                context=log_context
            )
        else:
            logger.info(
                f"ℹ️ USER ERROR: {error_msg} | "
                f"Category: {error_report.error_category} | "
                f"Message: {error_report.message_text}",
                context=log_context
            )
    
    async def _notify_admin(self, error_report: ErrorReport) -> None:
        """Send admin notification for critical errors."""
        if not self.admin_chat_id:
            logger.warning("No admin chat ID configured for error notifications")
            return
        
        try:
            # Import here to avoid circular imports
            from services.telegram_service import get_telegram_service
            
            telegram_service = get_telegram_service()
            
            # Create admin notification message
            notification = self._format_admin_notification(error_report)
            
            # Send notification
            await telegram_service.send_message(
                chat_id=self.admin_chat_id,
                message=notification,
                parse_mode='HTML'
            )
            
            logger.info(f"Admin notification sent for error: {error_report.error.__class__.__name__}")
            
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}", exc_info=True)
    
    def _format_admin_notification(self, error_report: ErrorReport) -> str:
        """Format error notification for admin chat."""
        error = error_report.error
        category_emoji = {
            "system": "🚨",
            "infrastructure": "🔴", 
            "domain": "🟡",
            "validation": "🟡",
            "ai": "🤖",
            "external": "🌐",
            "performance": "⚡",
            "payment": "💰",
            "unknown": "❓"
        }
        
        emoji = category_emoji.get(error_report.error_category, "❓")
        
        notification = f"""
{emoji} <b>CRITICAL ERROR ALERT</b>

<b>Error:</b> {error.__class__.__name__}
<b>Category:</b> {error_report.error_category}
<b>Team:</b> {error_report.team_id}
<b>Operation:</b> {error_report.operation}

<b>User Info:</b>
• User ID: {error_report.user_id or 'Unknown'}
• Chat ID: {error_report.chat_id or 'Unknown'}
• Message: {error_report.message_text or 'Unknown'}

<b>Error Details:</b>
{str(error)[:200]}{'...' if len(str(error)) > 200 else ''}

<b>Timestamp:</b> {error_report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
<b>Retryable:</b> {'Yes' if error_report.is_retryable else 'No'}
        """.strip()
        
        return notification
    
    def _store_error_report(self, error_report: ErrorReport) -> None:
        """Store error report in memory (for debugging and analytics)."""
        self.error_reports.append(error_report)
        
        # Keep only the last max_reports
        if len(self.error_reports) > self.max_reports:
            self.error_reports = self.error_reports[-self.max_reports:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        if not self.error_reports:
            return {
                "total_errors": 0,
                "error_categories": {},
                "critical_errors": 0,
                "retryable_errors": 0
            }
        
        categories = {}
        critical_count = 0
        retryable_count = 0
        
        for report in self.error_reports:
            # Count by category
            category = report.error_category
            categories[category] = categories.get(category, 0) + 1
            
            # Count critical errors
            if report.requires_admin_attention:
                critical_count += 1
            
            # Count retryable errors
            if report.is_retryable:
                retryable_count += 1
        
        return {
            "total_errors": len(self.error_reports),
            "error_categories": categories,
            "critical_errors": critical_count,
            "retryable_errors": retryable_count,
            "last_error_time": self.error_reports[-1].timestamp.isoformat() if self.error_reports else None
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorReport]:
        """Get recent error reports for debugging."""
        return self.error_reports[-limit:] if self.error_reports else []
    
    def clear_error_reports(self) -> None:
        """Clear stored error reports."""
        self.error_reports.clear()
        logger.info("Error reports cleared")


# Global error handling service instance
_error_handling_service: Optional[ErrorHandlingService] = None


def get_error_handling_service(team_id: str) -> ErrorHandlingService:
    """Get the global error handling service instance."""
    global _error_handling_service
    if _error_handling_service is None or _error_handling_service.team_id != team_id:
        _error_handling_service = ErrorHandlingService(team_id)
    return _error_handling_service


async def handle_error_async(
    error: Exception,
    team_id: str,
    user_id: Optional[str] = None,
    chat_id: Optional[str] = None,
    message_text: Optional[str] = None,
    operation: str = "unknown",
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to handle errors asynchronously.
    
    Args:
        error: The exception that occurred
        team_id: Team ID for context
        user_id: ID of the user who triggered the error
        chat_id: ID of the chat where the error occurred
        message_text: Original message text that caused the error
        operation: Operation being performed when error occurred
        context: Additional context information
        
    Returns:
        User-friendly error message to display
    """
    service = get_error_handling_service(team_id)
    return await service.handle_error(
        error, user_id, chat_id, message_text, operation, context
    )


def handle_error_sync(
    error: Exception,
    team_id: str,
    user_id: Optional[str] = None,
    chat_id: Optional[str] = None,
    message_text: Optional[str] = None,
    operation: str = "unknown",
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Synchronous version of error handling for non-async contexts.
    
    Args:
        error: The exception that occurred
        team_id: Team ID for context
        user_id: ID of the user who triggered the error
        chat_id: ID of the chat where the error occurred
        message_text: Original message text that caused the error
        operation: Operation being performed when error occurred
        context: Additional context information
        
    Returns:
        User-friendly error message to display
    """
    # For sync contexts, we just return the user-friendly message
    # Logging will be handled by the calling code
    return get_user_friendly_message(error)


# Error handling decorators for easy integration
def handle_errors(operation: str = "unknown"):
    """
    Decorator to automatically handle errors in async functions.
    
    Usage:
        @handle_errors("player_registration")
        async def register_player(user_id: str, name: str):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Extract context from function arguments
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                # Try to extract team_id from arguments or use default
                team_id = kwargs.get('team_id', 'KAI')
                
                # Handle the error
                error_message = await handle_error_async(
                    e, team_id, operation=operation, context=context
                )
                
                # Return error message instead of raising
                return error_message
        
        return wrapper
    return decorator


def handle_errors_sync(operation: str = "unknown"):
    """
    Decorator to automatically handle errors in sync functions.
    
    Usage:
        @handle_errors_sync("data_validation")
        def validate_player_data(data: dict):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Extract context from function arguments
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                # Try to extract team_id from arguments or use default
                team_id = kwargs.get('team_id', 'KAI')
                
                # Handle the error
                error_message = handle_error_sync(
                    e, team_id, operation=operation, context=context
                )
                
                # Return error message instead of raising
                return error_message
        
        return wrapper
    return decorator 