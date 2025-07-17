#!/usr/bin/env python3
"""
Enhanced Logging and Error Handling for KICKAI

This module provides comprehensive error handling, structured logging,
and standardized error messages to improve debugging and observability.

Features:
- Structured error context with team_id, user_id, operation details
- Standardized error message templates
- Full stack trace capture and formatting
- Error categorization and severity levels
- Performance monitoring integration
- Debug information collection
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import json
import inspect
import os

from core.logging_config import LogContext, KICKAILogger, get_logger


class ErrorSeverity(Enum):
    """Error severity levels for prioritization."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "VALIDATION"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    SYSTEM = "SYSTEM"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    CONFIGURATION = "CONFIGURATION"
    UNKNOWN = "UNKNOWN"


@dataclass
class ErrorContext:
    """Comprehensive error context information."""
    # Core identifiers
    team_id: Optional[str] = None
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    request_id: Optional[str] = None
    
    # Operation details
    operation: Optional[str] = None
    component: Optional[str] = None
    function_name: Optional[str] = None
    module_name: Optional[str] = None
    
    # Error classification
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    
    # Input data (sanitized)
    input_parameters: Optional[Dict[str, Any]] = None
    input_data_summary: Optional[str] = None
    
    # System context
    timestamp: Optional[datetime] = None
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    
    # Additional context
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.tags is None:
            self.tags = []


@dataclass
class StructuredError:
    """Structured error information for logging and debugging."""
    # Required fields first
    error_type: str
    error_message: str
    context: ErrorContext
    
    # Optional fields with defaults
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    full_traceback: Optional[str] = None
    suggestions: Optional[List[str]] = None
    related_errors: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'error_type': self.error_type,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'context': asdict(self.context),
            'stack_trace': self.stack_trace,
            'full_traceback': self.full_traceback,
            'suggestions': self.suggestions,
            'related_errors': self.related_errors,
            'timestamp': self.context.timestamp.isoformat() if self.context.timestamp else None
        }


class ErrorMessageTemplates:
    """Standardized error message templates with context."""
    
    # Player operations
    PLAYER_NOT_FOUND = "Player '{player_id}' not found in team '{team_id}'"
    PLAYER_ALREADY_EXISTS = "Player with phone '{phone}' already exists in team '{team_id}'"
    PLAYER_REGISTRATION_FAILED = "Failed to register player '{phone}' in team '{team_id}': {reason}"
    PLAYER_APPROVAL_FAILED = "Failed to approve player '{player_id}' in team '{team_id}': {reason}"
    PLAYER_REMOVAL_FAILED = "Failed to remove player '{player_id}' from team '{team_id}': {reason}"
    
    # Team operations
    TEAM_NOT_FOUND = "Team '{team_id}' not found"
    TEAM_CREATION_FAILED = "Failed to create team '{team_id}': {reason}"
    TEAM_DELETION_FAILED = "Failed to delete team '{team_id}': {reason}"
    
    # Match operations
    MATCH_NOT_FOUND = "Match '{match_id}' not found in team '{team_id}'"
    MATCH_CREATION_FAILED = "Failed to create match in team '{team_id}': {reason}"
    MATCH_UPDATE_FAILED = "Failed to update match '{match_id}' in team '{team_id}': {reason}"
    
    # Payment operations
    PAYMENT_RECORDING_FAILED = "Failed to record payment for player '{player_id}' in team '{team_id}': {reason}"
    PAYMENT_NOT_FOUND = "Payment '{payment_id}' not found in team '{team_id}'"
    PAYMENT_REFUND_FAILED = "Failed to refund payment '{payment_id}' in team '{team_id}': {reason}"
    
    # Database operations
    DATABASE_CONNECTION_FAILED = "Database connection failed: {reason}"
    DATABASE_QUERY_FAILED = "Database query failed for operation '{operation}' in team '{team_id}': {reason}"
    DATABASE_TRANSACTION_FAILED = "Database transaction failed for operation '{operation}' in team '{team_id}': {reason}"
    
    # Authentication/Authorization
    USER_NOT_AUTHORIZED = "User '{user_id}' not authorized for operation '{operation}' in team '{team_id}'"
    INVALID_PERMISSIONS = "Insufficient permissions for operation '{operation}' in team '{team_id}'"
    
    # Validation errors
    INVALID_INPUT = "Invalid input for operation '{operation}': {reason}"
    MISSING_REQUIRED_FIELD = "Missing required field '{field}' for operation '{operation}'"
    INVALID_FORMAT = "Invalid format for field '{field}' in operation '{operation}': {reason}"
    
    # System errors
    CONFIGURATION_ERROR = "Configuration error: {reason}"
    EXTERNAL_SERVICE_ERROR = "External service '{service}' error: {reason}"
    NETWORK_ERROR = "Network error for operation '{operation}': {reason}"
    
    # Generic with context
    GENERIC_ERROR = "Error in {operation} for team '{team_id}' (user: {user_id}): {reason}"
    
    @staticmethod
    def format(template: str, **kwargs) -> str:
        """Format error message template with provided values."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # Fallback if template has missing keys
            return f"Error message formatting failed: {template} (missing: {e})"


class ErrorHandler:
    """Centralized error handling with structured logging."""
    
    def __init__(self, logger: Optional[KICKAILogger] = None):
        self.logger = logger or get_logger(__name__)
    
    def capture_error(self, 
                     error: Exception,
                     context: ErrorContext,
                     include_stack_trace: bool = True,
                     include_suggestions: bool = True) -> StructuredError:
        """Capture comprehensive error information."""
        
        # Get stack trace
        stack_trace = None
        full_traceback = None
        if include_stack_trace:
            stack_trace = ''.join(traceback.format_tb(error.__traceback__))
            full_traceback = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        
        # Generate suggestions
        suggestions = None
        if include_suggestions:
            suggestions = self._generate_suggestions(error, context)
        
        # Create structured error
        structured_error = StructuredError(
            error_type=error.__class__.__name__,
            error_message=str(error),
            context=context,
            stack_trace=stack_trace,
            full_traceback=full_traceback,
            suggestions=suggestions
        )
        
        return structured_error
    
    def log_error(self, 
                  error: Exception,
                  context: ErrorContext,
                  user_message: Optional[str] = None,
                  include_stack_trace: bool = True) -> str:
        """Log error with structured information and return user-friendly message."""
        
        # Capture error details
        structured_error = self.capture_error(error, context, include_stack_trace)
        
        # Log with appropriate level based on severity
        log_level = self._get_log_level(context.severity)
        
        # Create log context
        log_context = LogContext(
            team_id=context.team_id,
            user_id=context.user_id,
            chat_id=context.chat_id,
            operation=context.operation,
            component=context.component,
            request_id=context.request_id,
            duration_ms=context.duration_ms,
            metadata={
                'error_type': structured_error.error_type,
                'error_category': context.category.value,
                'error_severity': context.severity.value,
                'input_summary': context.input_data_summary,
                'suggestions': structured_error.suggestions
            }
        )
        
        # Log the error
        if log_level == logging.ERROR:
            self.logger.error(
                f"Error in {context.operation}: {structured_error.error_message}",
                context=log_context,
                exc_info=error
            )
        elif log_level == logging.CRITICAL:
            self.logger.critical(
                f"Critical error in {context.operation}: {structured_error.error_message}",
                context=log_context,
                exc_info=error
            )
        else:
            self.logger.warning(
                f"Warning in {context.operation}: {structured_error.error_message}",
                context=log_context,
                exc_info=error
            )
        
        # Return user-friendly message
        return user_message or self._generate_user_message(structured_error)
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """Map error severity to log level."""
        mapping = {
            ErrorSeverity.LOW: logging.WARNING,
            ErrorSeverity.MEDIUM: logging.ERROR,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.ERROR)
    
    def _generate_suggestions(self, error: Exception, context: ErrorContext) -> List[str]:
        """Generate debugging suggestions based on error type and context."""
        suggestions = []
        
        # Common suggestions based on error type
        if isinstance(error, (KeyError, AttributeError)):
            suggestions.append("Check input parameters and data structure")
            suggestions.append("Verify field names and object properties")
        elif isinstance(error, ValueError):
            suggestions.append("Validate input data format and constraints")
        elif isinstance(error, PermissionError):
            suggestions.append("Check user permissions and authentication")
            suggestions.append("Verify team membership and role assignments")
        elif isinstance(error, ConnectionError):
            suggestions.append("Check network connectivity and service availability")
            suggestions.append("Verify external service configurations")
        
        # Context-specific suggestions
        if context.category == ErrorCategory.DATABASE:
            suggestions.append("Check database connection and query syntax")
            suggestions.append("Verify data integrity and constraints")
        elif context.category == ErrorCategory.VALIDATION:
            suggestions.append("Review input validation rules")
            suggestions.append("Check required fields and data formats")
        elif context.category == ErrorCategory.AUTHORIZATION:
            suggestions.append("Verify user roles and permissions")
            suggestions.append("Check team access controls")
        
        return suggestions
    
    def _generate_user_message(self, structured_error: StructuredError) -> str:
        """Generate user-friendly error message."""
        # Use template-based messages when possible
        if structured_error.context.operation:
            template = ErrorMessageTemplates.GENERIC_ERROR
            return ErrorMessageTemplates.format(
                template,
                operation=structured_error.context.operation,
                team_id=structured_error.context.team_id or "unknown",
                user_id=structured_error.context.user_id or "unknown",
                reason=structured_error.error_message
            )
        
        return f"❌ Error: {structured_error.error_message}"


def create_error_context(operation: str,
                        team_id: Optional[str] = None,
                        user_id: Optional[str] = None,
                        chat_id: Optional[str] = None,
                        category: ErrorCategory = ErrorCategory.UNKNOWN,
                        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                        input_parameters: Optional[Dict[str, Any]] = None,
                        **kwargs) -> ErrorContext:
    """Create error context with current function information."""
    
    # Get calling function information
    frame = inspect.currentframe().f_back
    function_name = frame.f_code.co_name if frame else None
    module_name = frame.f_globals.get('__name__', 'unknown') if frame else None
    
    # Sanitize input parameters
    sanitized_input = None
    input_summary = None
    if input_parameters:
        sanitized_input = _sanitize_input_data(input_parameters)
        input_summary = _create_input_summary(input_parameters)
    
    return ErrorContext(
        team_id=team_id,
        user_id=user_id,
        chat_id=chat_id,
        operation=operation,
        component=module_name,
        function_name=function_name,
        category=category,
        severity=severity,
        input_parameters=sanitized_input,
        input_data_summary=input_summary,
        metadata=kwargs
    )


def _sanitize_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data for logging (remove sensitive information)."""
    sensitive_fields = {'password', 'token', 'secret', 'key', 'auth', 'credential'}
    sanitized = {}
    
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_input_data(value)
        elif isinstance(value, list):
            sanitized[key] = [_sanitize_input_data(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


def _create_input_summary(data: Dict[str, Any]) -> str:
    """Create a summary of input data for logging."""
    if not data:
        return "No input data"
    
    summary_parts = []
    for key, value in data.items():
        if isinstance(value, str):
            summary_parts.append(f"{key}='{value[:50]}{'...' if len(value) > 50 else ''}'")
        elif isinstance(value, (int, float, bool)):
            summary_parts.append(f"{key}={value}")
        elif isinstance(value, (list, tuple)):
            summary_parts.append(f"{key}=[{len(value)} items]")
        elif isinstance(value, dict):
            summary_parts.append(f"{key}={{...}}")
        else:
            summary_parts.append(f"{key}=<{type(value).__name__}>")
    
    return f"Input: {' '.join(summary_parts)}"


def handle_errors(error_handler: Optional[ErrorHandler] = None,
                  category: ErrorCategory = ErrorCategory.UNKNOWN,
                  severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                  user_message_template: Optional[str] = None):
    """Decorator for automatic error handling and logging."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create error handler if not provided
            handler = error_handler or ErrorHandler()
            
            # Extract context from function signature
            context_kwargs = {}
            if 'team_id' in kwargs:
                context_kwargs['team_id'] = kwargs['team_id']
            if 'user_id' in kwargs:
                context_kwargs['user_id'] = kwargs['user_id']
            if 'chat_id' in kwargs:
                context_kwargs['chat_id'] = kwargs['chat_id']
            
            # Create error context
            context = create_error_context(
                operation=func.__name__,
                category=category,
                severity=severity,
                input_parameters=kwargs,
                **context_kwargs
            )
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Generate user message from template if provided
                user_message = None
                if user_message_template:
                    try:
                        user_message = ErrorMessageTemplates.format(user_message_template, **kwargs)
                    except:
                        pass  # Fall back to default message
                
                # Log and return error message
                error_msg = handler.log_error(e, context, user_message)
                return False, error_msg
        
        return wrapper
    return decorator


# Global error handler instance
_global_error_handler = ErrorHandler()


def log_error(error: Exception,
              operation: str,
              team_id: Optional[str] = None,
              user_id: Optional[str] = None,
              chat_id: Optional[str] = None,
              category: ErrorCategory = ErrorCategory.UNKNOWN,
              severity: ErrorSeverity = ErrorSeverity.MEDIUM,
              user_message: Optional[str] = None,
              **kwargs) -> str:
    """Convenience function for logging errors with context."""
    
    context = create_error_context(
        operation=operation,
        team_id=team_id,
        user_id=user_id,
        chat_id=chat_id,
        category=category,
        severity=severity,
        **kwargs
    )
    
    return _global_error_handler.log_error(error, context, user_message)


def log_command_error(error: Exception,
                     command: str,
                     team_id: str,
                     user_id: str,
                     chat_id: str,
                     user_message: Optional[str] = None) -> str:
    """Specialized function for logging command execution errors."""
    
    return log_error(
        error=error,
        operation=f"command_{command}",
        team_id=team_id,
        user_id=user_id,
        chat_id=chat_id,
        category=ErrorCategory.BUSINESS_LOGIC,
        severity=ErrorSeverity.MEDIUM,
        user_message=user_message
    )


def log_database_error(error: Exception,
                      operation: str,
                      team_id: Optional[str] = None,
                      user_id: Optional[str] = None,
                      user_message: Optional[str] = None) -> str:
    """Specialized function for logging database errors."""
    
    return log_error(
        error=error,
        operation=f"database_{operation}",
        team_id=team_id,
        user_id=user_id,
        category=ErrorCategory.DATABASE,
        severity=ErrorSeverity.HIGH,
        user_message=user_message
    )


def log_validation_error(error: Exception,
                        operation: str,
                        field: Optional[str] = None,
                        team_id: Optional[str] = None,
                        user_id: Optional[str] = None,
                        user_message: Optional[str] = None) -> str:
    """Specialized function for logging validation errors."""
    
    return log_error(
        error=error,
        operation=f"validation_{operation}",
        team_id=team_id,
        user_id=user_id,
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.LOW,
        user_message=user_message,
        field=field
    ) 