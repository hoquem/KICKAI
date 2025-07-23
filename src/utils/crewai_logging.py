#!/usr/bin/env python3
"""
CrewAI Logging Integration

This module provides utilities to redirect CrewAI logs to our loguru logging system.
"""

import logging
import sys
from typing import Any

from loguru import logger


class CrewAILogHandler(logging.Handler):
    """Custom log handler to redirect CrewAI logs to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to loguru."""
        try:
            # Convert logging level to loguru level
            level = self._get_loguru_level(record.levelno)

            # Format the message
            message = self.format(record)

            # Add CrewAI prefix to identify the source
            crewai_message = f"[CREWAI] {message}"

            # Log to loguru
            logger.bind(name=record.name).log(level, crewai_message)

        except Exception:
            # Fallback to stderr if loguru fails
            sys.stderr.write(f"[CREWAI LOG ERROR] {record.getMessage()}\n")

    def _get_loguru_level(self, levelno: int) -> str:
        """Convert Python logging level to loguru level."""
        if levelno >= logging.CRITICAL:
            return "CRITICAL"
        elif levelno >= logging.ERROR:
            return "ERROR"
        elif levelno >= logging.WARNING:
            return "WARNING"
        elif levelno >= logging.INFO:
            return "INFO"
        else:
            return "DEBUG"


def setup_crewai_logging(level: str = "INFO") -> None:
    """
    Set up CrewAI logging to redirect to loguru.
    
    Args:
        level: Logging level for CrewAI logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    try:
        # Get the CrewAI logger
        crewai_logger = logging.getLogger("crewai")

        # Remove existing handlers
        for handler in crewai_logger.handlers[:]:
            crewai_logger.removeHandler(handler)

        # Add our custom handler
        handler = CrewAILogHandler()
        handler.setLevel(getattr(logging, level.upper()))

        # Set formatter
        formatter = logging.Formatter(
            "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add handler to CrewAI logger
        crewai_logger.addHandler(handler)
        crewai_logger.setLevel(getattr(logging, level.upper()))

        # Also set up logging for related libraries
        related_loggers = [
            "langchain",
            "openai",
            "anthropic",
            "google.generativeai",
            "firebase_admin",
            "google.cloud.firestore"
        ]

        for logger_name in related_loggers:
            lib_logger = logging.getLogger(logger_name)
            lib_logger.handlers = []  # Clear existing handlers
            lib_logger.addHandler(handler)
            lib_logger.setLevel(getattr(logging, level.upper()))
            lib_logger.propagate = False  # Prevent duplicate logs

        logger.info(f"✅ CrewAI logging redirected to loguru (level: {level})")

    except Exception as e:
        logger.warning(f"⚠️ Failed to setup CrewAI logging: {e}")


def enable_crewai_debug_logging() -> None:
    """Enable debug logging for CrewAI and related libraries."""
    setup_crewai_logging("DEBUG")


def enable_crewai_info_logging() -> None:
    """Enable info logging for CrewAI and related libraries."""
    setup_crewai_logging("INFO")


def enable_crewai_warning_logging() -> None:
    """Enable warning logging for CrewAI and related libraries."""
    setup_crewai_logging("WARNING")


def get_crewai_log_level() -> str:
    """Get the current CrewAI log level."""
    try:
        crewai_logger = logging.getLogger("crewai")
        level_name = logging.getLevelName(crewai_logger.level)
        return level_name if level_name != "NOTSET" else "INFO"
    except Exception:
        return "INFO"


def log_crewai_agent_activity(agent_name: str, action: str, details: dict[str, Any] | None = None) -> None:
    """
    Log CrewAI agent activity with structured information.
    
    Args:
        agent_name: Name of the agent
        action: Action being performed
        details: Optional details about the action
    """
    message = f"🤖 Agent '{agent_name}' {action}"
    if details:
        message += f" | Details: {details}"

    logger.info(f"[CREWAI AGENT] {message}")


def log_crewai_tool_usage(tool_name: str, agent_name: str, result: str | None = None) -> None:
    """
    Log CrewAI tool usage.
    
    Args:
        tool_name: Name of the tool being used
        agent_name: Name of the agent using the tool
        result: Optional result of the tool usage
    """
    message = f"🔧 Tool '{tool_name}' used by agent '{agent_name}'"
    if result:
        # Truncate long results
        if len(result) > 200:
            result = result[:200] + "..."
        message += f" | Result: {result}"

    logger.info(f"[CREWAI TOOL] {message}")


def log_crewai_task_execution(task_description: str, agent_name: str, status: str) -> None:
    """
    Log CrewAI task execution.
    
    Args:
        task_description: Description of the task
        agent_name: Name of the agent executing the task
        status: Status of the task execution
    """
    # Truncate long task descriptions
    if len(task_description) > 100:
        task_description = task_description[:100] + "..."

    message = f"📋 Task: '{task_description}' | Agent: '{agent_name}' | Status: {status}"
    logger.info(f"[CREWAI TASK] {message}")
