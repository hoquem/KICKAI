#!/usr/bin/env python3
"""
Custom Exceptions for KICKAI

This module defines custom exceptions used throughout the KICKAI system.
"""

from typing import Any, Optional, Dict, List
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization."""
    VALIDATION = "validation"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    DATA = "data"


class KickAIError(Exception):
    """Base exception for all KICKAI errors."""

    def __init__(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.error_code = error_code or self.__class__.__name__
        self.severity = severity
        self.category = category
        self.user_message = user_message or self._generate_user_message()
        self.timestamp = datetime.utcnow().isoformat()
        
    def _generate_user_message(self) -> str:
        """Generate a user-friendly error message."""
        return "An error occurred while processing your request. Please try again."
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging and debugging."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "timestamp": self.timestamp,
            "class": self.__class__.__name__
        }


class PlayerError(KickAIError):
    """Base exception for player-related errors."""

    pass


class PlayerAlreadyExistsError(PlayerError):
    """Raised when trying to create a player that already exists."""

    def __init__(self, phone: str, team_id: str):
        message = f"Player with phone {phone} already exists in team {team_id}"
        super().__init__(
            message, 
            {"phone": phone, "team_id": team_id},
            error_code="PLAYER_ALREADY_EXISTS",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            user_message="A player with this phone number is already registered."
        )


class PlayerNotFoundError(PlayerError):
    """Raised when a player is not found."""

    def __init__(self, player_id: str, team_id: str):
        message = f"Player {player_id} not found in team {team_id}"
        super().__init__(
            message, 
            {"player_id": player_id, "team_id": team_id},
            error_code="PLAYER_NOT_FOUND",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.DATA,
            user_message="Player not found. Please check the player ID and try again."
        )


class PlayerValidationError(PlayerError):
    """Raised when player data validation fails."""

    def __init__(self, errors: List[str]):
        message = f"Player validation failed: {'; '.join(errors)}"
        super().__init__(
            message, 
            {"validation_errors": errors},
            error_code="PLAYER_VALIDATION_FAILED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            user_message=f"Please correct the following: {'; '.join(errors)}"
        )


class TeamError(KickAIError):
    """Base exception for team-related errors."""

    pass


class TeamNotFoundError(TeamError):
    """Raised when a team is not found."""

    def __init__(self, team_id: str):
        message = f"Team {team_id} not found"
        super().__init__(message, {"team_id": team_id})


class TeamNotConfiguredError(TeamError):
    """Raised when a team is not properly configured."""

    def __init__(self, team_id: str, missing_config: str):
        message = f"Team {team_id} not configured: {missing_config}"
        super().__init__(message, {"team_id": team_id, "missing_config": missing_config})


class InviteLinkError(KickAIError):
    """Base exception for invite link-related errors."""

    pass


class InviteLinkNotFoundError(InviteLinkError):
    """Raised when an invite link is not found."""

    def __init__(self, invite_id: str):
        message = f"Invite link {invite_id} not found"
        super().__init__(message, {"invite_id": invite_id})


class InviteLinkExpiredError(InviteLinkError):
    """Raised when an invite link has expired."""

    def __init__(self, invite_id: str):
        message = f"Invite link {invite_id} has expired"
        super().__init__(message, {"invite_id": invite_id})


class InviteLinkAlreadyUsedError(InviteLinkError):
    """Raised when an invite link has already been used."""

    def __init__(self, invite_id: str):
        message = f"Invite link {invite_id} has already been used"
        super().__init__(message, {"invite_id": invite_id})


class InviteLinkInvalidError(InviteLinkError):
    """Raised when an invite link is invalid."""

    def __init__(self, invite_link: str, reason: str):
        message = f"Invalid invite link: {reason}"
        super().__init__(message, {"invite_link": invite_link, "reason": reason})


class ServiceError(KickAIError):
    """Base exception for service-related errors."""

    pass


class ServiceNotAvailableError(ServiceError):
    """Raised when a required service is not available."""

    def __init__(self, service_name: str):
        message = f"Service {service_name} is not available"
        super().__init__(
            message, 
            {"service_name": service_name},
            error_code="SERVICE_UNAVAILABLE",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            user_message="Service temporarily unavailable. Please try again later."
        )


class ConfigurationError(KickAIError):
    """Base exception for configuration-related errors."""

    pass


class AgentError(KickAIError):
    """Base exception for agent-related errors."""

    pass


class AgentInitializationError(AgentError):
    """Raised when agent initialization fails."""

    def __init__(self, agent_name: str, error: str):
        message = f"Failed to initialize agent {agent_name}: {error}"
        super().__init__(message, {"agent_name": agent_name, "error": error})


class AgentConfigurationError(AgentError):
    """Raised when agent configuration is invalid."""

    def __init__(self, agent_name: str, config_error: str):
        message = f"Invalid configuration for agent {agent_name}: {config_error}"
        super().__init__(message, {"agent_name": agent_name, "config_error": config_error})


class AgentExecutionError(AgentError):
    """Raised when agent execution fails."""

    def __init__(self, agent_name: str, task: str, error: str):
        message = f"Agent {agent_name} failed to execute task '{task}': {error}"
        super().__init__(
            message, 
            {"agent_name": agent_name, "task": task, "error": error},
            error_code="AGENT_EXECUTION_FAILED",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            user_message="Unable to process your request at the moment. Please try again."
        )


class AuthorizationError(KickAIError):
    """Raised when authorization fails."""

    def __init__(self, user_id: str, action: str, reason: str = "Insufficient permissions"):
        message = f"Authorization failed for user {user_id} to perform {action}: {reason}"
        super().__init__(message, {"user_id": user_id, "action": action, "reason": reason})


class InputValidationError(KickAIError):
    """Raised when input validation fails."""

    def __init__(self, field: str, value: str, reason: str):
        message = f"Input validation failed for field '{field}' with value '{value}': {reason}"
        super().__init__(message, {"field": field, "value": value, "reason": reason})


class PaymentError(KickAIError):
    """Base exception for payment-related errors."""

    pass


class PaymentNotFoundError(PaymentError):
    """Raised when a payment is not found."""

    def __init__(self, payment_id: str):
        message = f"Payment {payment_id} not found"
        super().__init__(message, {"payment_id": payment_id})


class PaymentProcessingError(PaymentError):
    """Raised when payment processing fails."""

    def __init__(self, payment_id: str, error: str):
        message = f"Payment processing failed for {payment_id}: {error}"
        super().__init__(message, {"payment_id": payment_id, "error": error})


class PaymentValidationError(PaymentError):
    """Raised when payment validation fails."""

    def __init__(self, field: str, value: str, reason: str):
        message = f"Payment validation failed for field '{field}' with value '{value}': {reason}"
        super().__init__(message, {"field": field, "value": value, "reason": reason})


class MatchError(KickAIError):
    """Base exception for match-related errors."""

    pass


class MatchNotFoundError(MatchError):
    """Raised when a match is not found."""

    def __init__(self, match_id: str, context: Optional[Dict[str, Any]] = None):
        message = f"Match {match_id} not found"
        super().__init__(message, {"match_id": match_id, **(context or {})})


class MatchValidationError(MatchError):
    """Raised when match validation fails."""

    def __init__(self, field: str, value: str, reason: str):
        message = f"Match validation failed for field '{field}' with value '{value}': {reason}"
        super().__init__(message, {"field": field, "value": value, "reason": reason})


class AttendanceError(KickAIError):
    """Base exception for attendance-related errors."""

    pass


class AttendanceNotFoundError(AttendanceError):
    """Raised when an attendance record is not found."""

    def __init__(self, attendance_id: str, context: Optional[Dict[str, Any]] = None):
        message = f"Attendance record {attendance_id} not found"
        super().__init__(message, {"attendance_id": attendance_id, **(context or {})})


class AttendanceValidationError(AttendanceError):
    """Raised when attendance validation fails."""

    def __init__(self, field: str, value: str, reason: str):
        message = f"Attendance validation failed for field '{field}' with value '{value}': {reason}"
        super().__init__(message, {"field": field, "value": value, "reason": reason})


class TrainingError(KickAIError):
    """Base exception for training-related errors."""

    pass


class TrainingNotFoundError(TrainingError):
    """Raised when a training session is not found."""

    def __init__(self, training_id: str, context: Optional[Dict[str, Any]] = None):
        message = f"Training session {training_id} not found"
        super().__init__(message, {"training_id": training_id, **(context or {})})


class TrainingValidationError(TrainingError):
    """Raised when training validation fails."""

    def __init__(self, field: str, value: str, reason: str):
        message = f"Training validation failed for field '{field}' with value '{value}': {reason}"
        super().__init__(message, {"field": field, "value": value, "reason": reason})


class MissingEnvironmentVariableError(ConfigurationError):
    """Raised when a required environment variable is missing."""

    def __init__(self, variable_name: str):
        message = f"Required environment variable {variable_name} is not set"
        super().__init__(message, {"variable_name": variable_name})


class DatabaseError(KickAIError):
    """Base exception for database-related errors."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, database_name: str, error: str):
        message = f"Database connection failed for {database_name}: {error}"
        super().__init__(message, {"database_name": database_name, "error": error})


# Aliases for backward compatibility
ConnectionError = DatabaseConnectionError
DuplicateError = DatabaseError  # Generic duplicate error
NotFoundError = DatabaseError  # Generic not found error
KICKAIError = KickAIError  # Alias for case-sensitive imports


class DatabaseOperationError(DatabaseError):
    """Raised when a database operation fails."""

    def __init__(self, operation: str, error: str):
        message = f"Database operation '{operation}' failed: {error}"
        super().__init__(message, {"operation": operation, "error": error})


class ToolExecutionError(KickAIError):
    """Raised when a CrewAI tool execution fails."""
    
    def __init__(self, tool_name: str, error: str, parameters: Optional[Dict[str, Any]] = None):
        message = f"Tool '{tool_name}' execution failed: {error}"
        super().__init__(
            message,
            {"tool_name": tool_name, "error": error, "parameters": parameters or {}},
            error_code="TOOL_EXECUTION_FAILED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.SYSTEM,
            user_message="Unable to complete the requested action. Please try again."
        )


class DataIntegrityError(KickAIError):
    """Raised when data integrity is compromised."""
    
    def __init__(self, entity_type: str, entity_id: str, integrity_issue: str):
        message = f"Data integrity issue for {entity_type} {entity_id}: {integrity_issue}"
        super().__init__(
            message,
            {"entity_type": entity_type, "entity_id": entity_id, "integrity_issue": integrity_issue},
            error_code="DATA_INTEGRITY_ERROR",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.DATA,
            user_message="Data consistency issue detected. Please contact support."
        )


class RateLimitExceededError(KickAIError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, user_id: str, action: str, limit: int, window: str):
        message = f"Rate limit exceeded for user {user_id} on action '{action}': {limit} per {window}"
        super().__init__(
            message,
            {"user_id": user_id, "action": action, "limit": limit, "window": window},
            error_code="RATE_LIMIT_EXCEEDED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.AUTHORIZATION,
            user_message="Too many requests. Please wait before trying again."
        )


def create_error_context(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Create a standardized error context.

    Args:
        operation: The operation that failed
        **kwargs: Additional context information

    Returns:
        Dictionary containing error context
    """
    context = {
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs,
    }
    return context


def handle_error_gracefully(error: Exception, operation: str, **context) -> KickAIError:
    """
    Convert any exception to a KickAI error with proper context.
    
    Args:
        error: The original exception
        operation: The operation that failed
        **context: Additional context information
        
    Returns:
        KickAIError instance with proper context
    """
    if isinstance(error, KickAIError):
        return error
        
    # Convert common exceptions
    if isinstance(error, ValueError):
        return InputValidationError(
            field="unknown",
            value=str(context),
            reason=str(error)
        )
    elif isinstance(error, KeyError):
        return DataIntegrityError(
            entity_type="unknown",
            entity_id=str(context.get("entity_id", "unknown")),
            integrity_issue=f"Missing key: {error}"
        )
    elif isinstance(error, ConnectionError):
        return DatabaseConnectionError(
            database_name=context.get("database", "unknown"),
            error=str(error)
        )
    else:
        return KickAIError(
            message=f"Unexpected error in {operation}: {error}",
            context=create_error_context(operation, original_error=str(error), **context),
            error_code="UNEXPECTED_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM
        )
