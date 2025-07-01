"""
Logging Configuration for KICKAI

This module provides a comprehensive logging system with structured logging,
different handlers, and performance monitoring capabilities.
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import time
import traceback

from .config import get_config, LoggingConfig
from .exceptions import KICKAIError, create_error_context


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    logger: str
    message: str
    operation: Optional[str] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    entity_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            operation=getattr(record, 'operation', None),
            user_id=getattr(record, 'user_id', None),
            team_id=getattr(record, 'team_id', None),
            entity_id=getattr(record, 'entity_id', None),
            duration_ms=getattr(record, 'duration_ms', None),
            error_type=getattr(record, 'error_type', None),
            error_message=getattr(record, 'error_message', None),
            stack_trace=getattr(record, 'stack_trace', None),
            additional_data=getattr(record, 'additional_data', None)
        )
        
        return json.dumps(asdict(log_entry), default=str)


class PerformanceFormatter(logging.Formatter):
    """Performance-focused formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format performance log record."""
        duration = getattr(record, 'duration_ms', 0)
        operation = getattr(record, 'operation', 'unknown')
        
        if duration:
            return f"[PERF] {operation} took {duration:.2f}ms"
        else:
            return f"[PERF] {operation}"


class KICKAILogger:
    """Enhanced logger for KICKAI with structured logging and performance tracking."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._performance_timers: Dict[str, float] = {}
    
    def _add_context(self, record: logging.LogRecord, **kwargs):
        """Add context to log record."""
        for key, value in kwargs.items():
            setattr(record, key, value)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        record = self.logger.makeRecord(
            self.logger.name, logging.DEBUG, "", 0, message, (), None
        )
        self._add_context(record, **kwargs)
        self.logger.handle(record)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0, message, (), None
        )
        self._add_context(record, **kwargs)
        self.logger.handle(record)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        record = self.logger.makeRecord(
            self.logger.name, logging.WARNING, "", 0, message, (), None
        )
        self._add_context(record, **kwargs)
        self.logger.handle(record)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with context and error details."""
        record = self.logger.makeRecord(
            self.logger.name, logging.ERROR, "", 0, message, (), None
        )
        
        if error:
            self._add_context(
                record,
                error_type=error.__class__.__name__,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                **kwargs
            )
        else:
            self._add_context(record, **kwargs)
        
        self.logger.handle(record)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message with context and error details."""
        record = self.logger.makeRecord(
            self.logger.name, logging.CRITICAL, "", 0, message, (), None
        )
        
        if error:
            self._add_context(
                record,
                error_type=error.__class__.__name__,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                **kwargs
            )
        else:
            self._add_context(record, **kwargs)
        
        self.logger.handle(record)
    
    def performance(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics."""
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0, f"Performance: {operation}", (), None
        )
        self._add_context(record, operation=operation, duration_ms=duration_ms, **kwargs)
        self.logger.handle(record)
    
    @contextmanager
    def performance_timer(self, operation: str, **kwargs):
        """Context manager for performance timing."""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.performance(operation, duration_ms, **kwargs)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an exception with context."""
        if isinstance(error, KICKAIError):
            error_context = error.context
            self.error(
                str(error),
                error=error,
                operation=error_context.operation,
                user_id=error_context.user_id,
                team_id=error_context.team_id,
                entity_id=error_context.entity_id,
                additional_data=error_context.additional_info,
                **(context or {})
            )
        else:
            self.error(str(error), error=error, **(context or {}))


class LoggingManager:
    """Centralized logging management."""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self._loggers: Dict[str, KICKAILogger] = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(self.config.format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if configured)
        if self.config.file_path:
            file_handler = logging.handlers.RotatingFileHandler(
                self.config.file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count
            )
            file_handler.setLevel(logging.DEBUG)
            structured_formatter = StructuredFormatter()
            file_handler.setFormatter(structured_formatter)
            root_logger.addHandler(file_handler)
        
        # Performance logger
        perf_logger = logging.getLogger("performance")
        perf_handler = logging.StreamHandler(sys.stderr)
        perf_handler.setLevel(logging.INFO)
        perf_formatter = PerformanceFormatter()
        perf_handler.setFormatter(perf_formatter)
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> KICKAILogger:
        """Get or create a logger with the given name."""
        if name not in self._loggers:
            self._loggers[name] = KICKAILogger(name)
        return self._loggers[name]
    
    def log_system_startup(self):
        """Log system startup information."""
        logger = self.get_logger("system")
        logger.info("KICKAI system starting up", operation="system_startup")
    
    def log_system_shutdown(self):
        """Log system shutdown information."""
        logger = self.get_logger("system")
        logger.info("KICKAI system shutting down", operation="system_shutdown")
    
    def log_operation_start(self, operation: str, **kwargs):
        """Log the start of an operation."""
        logger = self.get_logger("operations")
        logger.info(f"Starting operation: {operation}", operation=operation, **kwargs)
    
    def log_operation_end(self, operation: str, success: bool = True, **kwargs):
        """Log the end of an operation."""
        logger = self.get_logger("operations")
        status = "completed" if success else "failed"
        logger.info(f"Operation {operation} {status}", operation=operation, **kwargs)


# Global logging manager
_logging_manager: Optional[LoggingManager] = None


def initialize_logging(config: Optional[LoggingConfig] = None) -> LoggingManager:
    """Initialize the global logging manager."""
    global _logging_manager
    if config is None:
        config = get_config().logging
    _logging_manager = LoggingManager(config)
    return _logging_manager


def get_logger(name: str) -> KICKAILogger:
    """Get a logger with the given name."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = initialize_logging()
    return _logging_manager.get_logger(name)


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log an error with context."""
    logger = get_logger("errors")
    logger.log_error(error, context)


def log_performance(operation: str, duration_ms: float, **kwargs):
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.performance(operation, duration_ms, **kwargs)


@contextmanager
def performance_timer(operation: str, **kwargs):
    """Context manager for performance timing."""
    logger = get_logger("performance")
    with logger.performance_timer(operation, **kwargs):
        yield 