"""
Custom Exceptions for KICKAI

This module defines a comprehensive exception hierarchy for the KICKAI system,
providing proper error categorization and context for different types of failures.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """Context information for errors."""
    operation: str
    entity_id: Optional[str] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class KICKAIError(Exception):
    """Base exception for all KICKAI errors."""
    
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext("unknown")
    
    def __str__(self) -> str:
        context_str = f" [{self.context.operation}]" if self.context else ""
        return f"{self.__class__.__name__}: {self.message}{context_str}"


# Configuration Errors
class ConfigurationError(KICKAIError):
    """Configuration-related errors."""
    pass


class EnvironmentError(KICKAIError):
    """Environment-related errors."""
    pass


# Database Errors
class DatabaseError(KICKAIError):
    """Base exception for database-related errors."""
    pass


class ConnectionError(DatabaseError):
    """Database connection errors."""
    pass


class QueryError(DatabaseError):
    """Database query errors."""
    pass


class DatabaseValidationError(DatabaseError):
    """Database validation errors."""
    pass


class NotFoundError(DatabaseError):
    """Resource not found errors."""
    pass


class DuplicateError(DatabaseError):
    """Duplicate resource errors."""
    pass


# AI/LLM Errors
class AIError(KICKAIError):
    """Base exception for AI-related errors."""
    pass


class LLMError(AIError):
    """LLM-specific errors."""
    pass


class ModelError(AIError):
    """AI model errors."""
    pass


class TokenLimitError(AIError):
    """Token limit exceeded errors."""
    pass


class RateLimitError(AIError):
    """Rate limiting errors."""
    pass


# Agent Errors
class AgentError(KICKAIError):
    """Base exception for agent-related errors."""
    pass


class AgentInitializationError(AgentError):
    """Agent initialization errors."""
    pass


class AgentExecutionError(AgentError):
    """Agent execution errors."""
    pass


class AgentCommunicationError(AgentError):
    """Agent communication errors."""
    pass


class AgentCapabilityError(AgentError):
    """Agent capability errors."""
    pass


# Telegram Errors
class TelegramError(KICKAIError):
    """Base exception for Telegram-related errors."""
    pass


class BotError(TelegramError):
    """Telegram bot errors."""
    pass


class MessageError(TelegramError):
    """Message-related errors."""
    pass


class WebhookError(TelegramError):
    """Webhook-related errors."""
    pass


class TelegramAuthenticationError(TelegramError):
    """Telegram authentication errors."""
    pass


# Player Management Errors
class PlayerError(KICKAIError):
    """Base exception for player-related errors."""
    pass


class PlayerNotFoundError(PlayerError, NotFoundError):
    """Player not found errors."""
    pass


class PlayerValidationError(PlayerError, DatabaseValidationError):
    """Player validation errors."""
    pass


class PlayerDuplicateError(PlayerError, DuplicateError):
    """Duplicate player errors."""
    pass


class OnboardingError(PlayerError):
    """Player onboarding errors."""
    pass


# Team Management Errors
class TeamError(KICKAIError):
    """Base exception for team-related errors."""
    pass


class TeamNotFoundError(TeamError, NotFoundError):
    """Team not found errors."""
    pass


class TeamValidationError(TeamError, DatabaseValidationError):
    """Team validation errors."""
    pass


class TeamPermissionError(TeamError):
    """Team permission errors."""
    pass


# Service Errors
class ServiceError(KICKAIError):
    """Base exception for service-related errors."""
    pass


class ServiceUnavailableError(ServiceError):
    """Service unavailable errors."""
    pass


class ServiceTimeoutError(ServiceError):
    """Service timeout errors."""
    pass


class ServiceAuthenticationError(ServiceError):
    """Service authentication errors."""
    pass


# Validation Errors
class GeneralValidationError(KICKAIError):
    """General validation errors."""
    pass


# Alias for backward compatibility
ValidationError = GeneralValidationError


class InputValidationError(GeneralValidationError):
    """Input validation errors."""
    pass


class DataValidationError(GeneralValidationError):
    """Data validation errors."""
    pass


# Security Errors
class SecurityError(KICKAIError):
    """Base exception for security-related errors."""
    pass


class AuthenticationError(SecurityError):
    """Authentication errors."""
    pass


class AuthorizationError(SecurityError):
    """Authorization errors."""
    pass


class AccessDeniedError(AuthorizationError):
    """Access denied errors."""
    pass


class TokenError(SecurityError):
    """Token-related errors."""
    pass


# Performance Errors
class PerformanceError(KICKAIError):
    """Base exception for performance-related errors."""
    pass


class TimeoutError(PerformanceError):
    """Timeout errors."""
    pass


class ResourceExhaustedError(PerformanceError):
    """Resource exhaustion errors."""
    pass


class RateLimitExceededError(PerformanceError):
    """Rate limit exceeded errors."""
    pass


# Utility Functions
def create_error_context(operation: str, **kwargs) -> ErrorContext:
    """Create an error context with the given parameters."""
    return ErrorContext(
        operation=operation,
        entity_id=kwargs.get('entity_id'),
        user_id=kwargs.get('user_id'),
        team_id=kwargs.get('team_id'),
        additional_info=kwargs.get('additional_info')
    )


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable."""
    retryable_errors = (
        ConnectionError,
        ServiceUnavailableError,
        ServiceTimeoutError,
        RateLimitError,
        TimeoutError,
        ResourceExhaustedError
    )
    return isinstance(error, retryable_errors)


def is_critical_error(error: Exception) -> bool:
    """Check if an error is critical and should stop processing."""
    critical_errors = (
        ConfigurationError,
        AuthenticationError,
        AuthorizationError,
        SecurityError
    )
    return isinstance(error, critical_errors)


def get_error_category(error: Exception) -> str:
    """Get the category of an error."""
    if isinstance(error, ConfigurationError):
        return "configuration"
    elif isinstance(error, DatabaseError):
        return "database"
    elif isinstance(error, AIError):
        return "ai"
    elif isinstance(error, AgentError):
        return "agent"
    elif isinstance(error, TelegramError):
        return "telegram"
    elif isinstance(error, PlayerError):
        return "player"
    elif isinstance(error, TeamError):
        return "team"
    elif isinstance(error, ServiceError):
        return "service"
    elif isinstance(error, GeneralValidationError):
        return "validation"
    elif isinstance(error, SecurityError):
        return "security"
    elif isinstance(error, PerformanceError):
        return "performance"
    else:
        return "unknown"


def format_error_message(error: Exception, include_context: bool = True) -> str:
    """Format an error message with optional context."""
    if isinstance(error, KICKAIError) and include_context and error.context:
        context = error.context
        parts = [f"{error.__class__.__name__}: {error.message}"]
        
        if context.operation != "unknown":
            parts.append(f"Operation: {context.operation}")
        
        if context.entity_id:
            parts.append(f"Entity: {context.entity_id}")
        
        if context.user_id:
            parts.append(f"User: {context.user_id}")
        
        if context.team_id:
            parts.append(f"Team: {context.team_id}")
        
        if context.additional_info:
            for key, value in context.additional_info.items():
                parts.append(f"{key}: {value}")
        
        return " | ".join(parts)
    else:
        return str(error) 