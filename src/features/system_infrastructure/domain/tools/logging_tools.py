"""
Logging tools for KICKAI system.

This module provides tools for logging commands and errors.
"""

import logging

from crewai.tools import tool
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LogCommandInput(BaseModel):
    """Input model for log_command tool."""
    command: str
    user_id: str | None = None
    team_id: str | None = None


class LogErrorInput(BaseModel):
    """Input model for log_error tool."""
    error_message: str
    context: str | None = None
    team_id: str | None = None


@tool("log_command")
def log_command(command: str, user_id: str | None = None, team_id: str | None = None) -> str:
    """
    Log a command execution. Requires: command
    
    Args:
        command: The command that was executed
        user_id: Optional user ID who executed the command
        team_id: Optional team ID for context
    
    Returns:
        Confirmation message indicating the command was logged
    """
    try:
        context_info = []
        if user_id:
            context_info.append(f"user_id={user_id}")
        if team_id:
            context_info.append(f"team_id={team_id}")

        context_str = f" [{', '.join(context_info)}]" if context_info else ""

        logger.info(f"📝 Command executed: {command}{context_str}")
        return f"✅ Command logged: {command}"

    except Exception as e:
        logger.error(f"❌ Failed to log command: {e}")
        return f"❌ Failed to log command: {e!s}"


@tool("log_error")
def log_error(error_message: str, context: str | None = None, team_id: str | None = None) -> str:
    """
    Log an error message. Requires: error_message
    
    Args:
        error_message: The error message to log
        context: Optional context information
        team_id: Optional team ID for context
    
    Returns:
        Confirmation message indicating the error was logged
    """
    try:
        context_info = []
        if context:
            context_info.append(f"context={context}")
        if team_id:
            context_info.append(f"team_id={team_id}")

        context_str = f" [{', '.join(context_info)}]" if context_info else ""

        logger.error(f"❌ Error: {error_message}{context_str}")
        return f"✅ Error logged: {error_message}"

    except Exception as e:
        logger.error(f"❌ Failed to log error: {e}")
        return f"❌ Failed to log error: {e!s}"
