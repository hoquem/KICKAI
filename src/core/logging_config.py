#!/usr/bin/env python3
"""
Centralized Logging Configuration for KICKAI

This module provides standardized logging configuration, message formats,
and error handling patterns for consistent debugging across the entire system.

Features:
- Standardized log levels and message formats
- Structured logging with context information
- Error handling patterns with consistent formatting
- Performance monitoring and metrics
- Configurable log output destinations
"""

import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import json


class LogLevel(Enum):
    """Standardized log levels with consistent meanings."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Categories for organizing log messages."""
    SYSTEM = "SYSTEM"
    USER = "USER"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    BUSINESS = "BUSINESS"
    DEBUG = "DEBUG"


@dataclass
class LogContext:
    """Context information for structured logging."""
    team_id: Optional[str] = None
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    request_id: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with context."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        # Extract context from record if available
        context = getattr(record, 'context', None)
        
        # Base log entry
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add context if available
        if context and self.include_context:
            if isinstance(context, LogContext):
                log_entry['context'] = {
                    'team_id': context.team_id,
                    'user_id': context.user_id,
                    'chat_id': context.chat_id,
                    'operation': context.operation,
                    'component': context.component,
                    'request_id': context.request_id,
                    'duration_ms': context.duration_ms,
                    'metadata': context.metadata
                }
            else:
                log_entry['context'] = context
        
        # Add exception info if available
        if record.exc_info:
            # Handle both tuple and exception object formats
            if isinstance(record.exc_info, tuple) and len(record.exc_info) == 3:
                exc_type, exc_value, exc_traceback = record.exc_info
                log_entry['exception'] = {
                    'type': exc_type.__name__ if exc_type else None,
                    'message': str(exc_value) if exc_value else None,
                    'traceback': traceback.format_exception(*record.exc_info)
                }
            else:
                # Handle single exception object
                exc_obj = record.exc_info
                log_entry['exception'] = {
                    'type': exc_obj.__class__.__name__,
                    'message': str(exc_obj),
                    'traceback': traceback.format_exception(type(exc_obj), exc_obj, exc_obj.__traceback__)
                }
        
        # Format based on environment
        if os.getenv('KICKAI_LOG_FORMAT', 'text').lower() == 'json':
            return json.dumps(log_entry, default=str)
        else:
            return self._format_text(log_entry)
    
    def _format_text(self, log_entry: Dict[str, Any]) -> str:
        """Format log entry as human-readable text."""
        timestamp = log_entry['timestamp']
        level = log_entry['level']
        logger_name = log_entry['logger']
        message = log_entry['message']
        
        # Base format
        formatted = f"{timestamp} [{level}] {logger_name}: {message}"
        
        # Add context if available
        if 'context' in log_entry:
            context = log_entry['context']
            context_parts = []
            for key, value in context.items():
                if value is not None and key != 'metadata':
                    context_parts.append(f"{key}={value}")
            if context_parts:
                formatted += f" | Context: {' '.join(context_parts)}"
        
        # Add exception if available
        if 'exception' in log_entry:
            exc = log_entry['exception']
            formatted += f" | Exception: {exc['type']}: {exc['message']}"
        
        return formatted


class KICKAILogger:
    """Enhanced logger with standardized methods and context support."""
    
    def __init__(self, name: str, context: Optional[LogContext] = None):
        self.logger = logging.getLogger(name)
        self.context = context or LogContext()
    
    def _log_with_context(self, level: int, message: str, context: Optional[LogContext] = None, 
                         exc_info: Optional[Exception] = None, **kwargs):
        """Log message with context information."""
        # Merge contexts
        merged_context = LogContext(
            team_id=context.team_id if context else self.context.team_id,
            user_id=context.user_id if context else self.context.user_id,
            chat_id=context.chat_id if context else self.context.chat_id,
            operation=context.operation if context else self.context.operation,
            component=context.component if context else self.context.component,
            request_id=context.request_id if context else self.context.request_id,
            duration_ms=context.duration_ms if context else self.context.duration_ms,
            metadata={**(self.context.metadata or {}), **(context.metadata or {})} if context else self.context.metadata
        )
        
        # Create log record with context
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), exc_info
        )
        record.context = merged_context
        
        # Add additional kwargs to record
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
    
    def debug(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, context, **kwargs)
    
    def info(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, context, **kwargs)
    
    def warning(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, context, **kwargs)
    
    def error(self, message: str, context: Optional[LogContext] = None, 
              exc_info: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception info."""
        self._log_with_context(logging.ERROR, message, context, exc_info, **kwargs)
    
    def critical(self, message: str, context: Optional[LogContext] = None, 
                 exc_info: Optional[Exception] = None, **kwargs):
        """Log critical message with optional exception info."""
        self._log_with_context(logging.CRITICAL, message, context, exc_info, **kwargs)
    
    def exception(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log exception with current exception info."""
        self._log_with_context(logging.ERROR, message, context, sys.exc_info(), **kwargs)
    
    def performance(self, operation: str, duration_ms: float, context: Optional[LogContext] = None, **kwargs):
        """Log performance metrics."""
        perf_context = context or LogContext()
        perf_context.operation = operation
        perf_context.duration_ms = duration_ms
        self._log_with_context(logging.INFO, f"Performance: {operation} took {duration_ms:.2f}ms", 
                              perf_context, **kwargs)
    
    def business_event(self, event: str, details: Dict[str, Any], context: Optional[LogContext] = None, **kwargs):
        """Log business events."""
        business_context = context or LogContext()
        business_context.metadata = {**(business_context.metadata or {}), 'event_details': details}
        self._log_with_context(logging.INFO, f"Business Event: {event}", business_context, **kwargs)
    
    def security_event(self, event: str, details: Dict[str, Any], context: Optional[LogContext] = None, **kwargs):
        """Log security events."""
        security_context = context or LogContext()
        security_context.metadata = {**(security_context.metadata or {}), 'security_details': details}
        self._log_with_context(logging.WARNING, f"Security Event: {event}", security_context, **kwargs)


class LoggingConfig:
    """Centralized logging configuration manager."""
    
    def __init__(self):
        self._configured = False
        self._loggers = {}
    
    def configure(self, 
                  log_level: str = "INFO",
                  log_format: str = "text",
                  log_file: Optional[str] = None,
                  max_file_size: int = 10 * 1024 * 1024,  # 10MB
                  backup_count: int = 5,
                  include_context: bool = True):
        """Configure logging system."""
        if self._configured:
            return
        
        # Set log level
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Create formatter
        formatter = StructuredFormatter(include_context=include_context)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_file_size, backupCount=backup_count
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Set environment variable for format preference
        os.environ['KICKAI_LOG_FORMAT'] = log_format
        
        self._configured = True
        
        # Log configuration success
        config_logger = self.get_logger(__name__)
        config_logger.info("Logging system configured successfully", 
                          context=LogContext(
                              component="logging",
                              metadata={
                                  'log_level': log_level,
                                  'log_format': log_format,
                                  'log_file': log_file,
                                  'include_context': include_context
                              }
                          ))
    
    def get_logger(self, name: str, context: Optional[LogContext] = None) -> KICKAILogger:
        """Get a logger instance with optional context."""
        if name not in self._loggers:
            self._loggers[name] = KICKAILogger(name, context)
        elif context:
            self._loggers[name].context = context
        return self._loggers[name]
    
    def set_context(self, name: str, context: LogContext):
        """Set context for a specific logger."""
        if name in self._loggers:
            self._loggers[name].context = context


# Global logging configuration instance
_logging_config = LoggingConfig()


def configure_logging(**kwargs):
    """Configure the global logging system."""
    _logging_config.configure(**kwargs)


def get_logger(name: str, context: Optional[LogContext] = None) -> KICKAILogger:
    """Get a logger instance."""
    return _logging_config.get_logger(name, context)


def log_errors(func: Callable) -> Callable:
    """Decorator for standardized error logging."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=e)
            raise
    return wrapper


def log_performance(operation: str):
    """Decorator for performance logging."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.performance(operation, duration)
        return wrapper
    return decorator


def log_business_event(event: str, details: Dict[str, Any]):
    """Decorator for business event logging."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            try:
                result = func(*args, **kwargs)
                logger.business_event(event, details)
                return result
            except Exception as e:
                logger.error(f"Business event failed: {event}", exc_info=e)
                raise
        return wrapper
    return decorator


# Standardized log message templates
class LogMessages:
    """Standardized log message templates."""
    
    # System messages
    SYSTEM_STARTUP = "System startup initiated"
    SYSTEM_SHUTDOWN = "System shutdown initiated"
    SYSTEM_HEALTHY = "System health check passed"
    SYSTEM_UNHEALTHY = "System health check failed"
    
    # User messages
    USER_LOGIN = "User login successful"
    USER_LOGOUT = "User logout successful"
    USER_ACTION = "User action completed"
    
    # Database messages
    DB_CONNECTION = "Database connection established"
    DB_QUERY = "Database query executed"
    DB_ERROR = "Database operation failed"
    
    # Network messages
    NETWORK_REQUEST = "Network request sent"
    NETWORK_RESPONSE = "Network response received"
    NETWORK_ERROR = "Network operation failed"
    
    # Security messages
    SECURITY_ACCESS = "Security access granted"
    SECURITY_DENIED = "Security access denied"
    SECURITY_VIOLATION = "Security violation detected"
    
    # Performance messages
    PERFORMANCE_SLOW = "Performance degradation detected"
    PERFORMANCE_OPTIMIZED = "Performance optimization applied"
    
    # Business messages
    BUSINESS_TRANSACTION = "Business transaction completed"
    BUSINESS_RULE_VIOLATION = "Business rule violation detected"
    
    @staticmethod
    def format_message(template: str, **kwargs) -> str:
        """Format a log message template with parameters."""
        return template.format(**kwargs)


# Convenience functions for common logging patterns
def log_system_event(event: str, context: Optional[LogContext] = None, **kwargs):
    """Log a system event."""
    logger = get_logger("system")
    logger.info(event, context, **kwargs)


def log_user_event(event: str, user_id: str, context: Optional[LogContext] = None, **kwargs):
    """Log a user event."""
    user_context = context or LogContext()
    user_context.user_id = user_id
    logger = get_logger("user")
    logger.info(event, user_context, **kwargs)


def log_database_event(event: str, operation: str, context: Optional[LogContext] = None, **kwargs):
    """Log a database event."""
    db_context = context or LogContext()
    db_context.operation = operation
    logger = get_logger("database")
    logger.info(event, db_context, **kwargs)


def log_security_event(event: str, details: Dict[str, Any], context: Optional[LogContext] = None, **kwargs):
    """Log a security event."""
    security_context = context or LogContext()
    logger = get_logger("security")
    logger.security_event(event, details, security_context, **kwargs)


def log_business_event(event: str, details: Dict[str, Any], context: Optional[LogContext] = None, **kwargs):
    """Log a business event."""
    business_context = context or LogContext()
    logger = get_logger("business")
    logger.business_event(event, details, business_context, **kwargs) 