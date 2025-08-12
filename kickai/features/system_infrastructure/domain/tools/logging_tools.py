"""
Logging tools for KICKAI system.

This module provides tools for logging commands and errors.
"""

import logging

from pydantic import BaseModel

from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import create_json_response
from typing import Optional

logger = logging.getLogger(__name__)


class LogCommandInput(BaseModel):
    """Input model for log_command tool."""

    command: str
    user_id: Optional[str] = None
    team_id: Optional[str] = None


class LogErrorInput(BaseModel):
    """Input model for log_error tool."""

    error_message: str
    context: Optional[str] = None
    team_id: Optional[str] = None


@tool("log_command", result_as_answer=True)
def log_command(command: str, user_id: Optional[str] = None, team_id: Optional[str] = None) -> str:
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
        return create_json_response("success", data=f"Command logged: {command}")

    except Exception as e:
        logger.error(f"❌ Failed to log command: {e}")
        return create_json_response("error", message=f"Failed to log command: {e!s}")


@tool("log_error", result_as_answer=True)
def log_error(
    error_message: str, error_context: Optional[str] = None, team_id: Optional[str] = None
) -> str:
    """
    Log an error message. Requires: error_message

    Args:
        error_message: The error message to log
        error_context: Optional context information
        team_id: Optional team ID for context

    Returns:
        Confirmation message indicating the error was logged
    """
    try:
        context_info = []
        if error_context:
            context_info.append(f"context={error_context}")
        if team_id:
            context_info.append(f"team_id={team_id}")

        context_str = f" [{', '.join(context_info)}]" if context_info else ""

        logger.error(f"❌ Error: {error_message}{context_str}")
        return create_json_response("success", data=f"Error logged: {error_message}")

    except Exception as e:
        logger.error(f"❌ Failed to log error: {e}")
        return create_json_response("error", message=f"Failed to log error: {e!s}")
