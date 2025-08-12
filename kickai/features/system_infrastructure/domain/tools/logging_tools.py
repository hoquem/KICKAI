"""
Logging tools for KICKAI system.

This module provides tools for logging commands and errors.
"""

import logging

from crewai.tools import tool
from pydantic import BaseModel

from kickai.utils.json_helper import json_error, json_response

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


        command: The command that was executed
        user_id: Optional user ID who executed the command
        team_id: Optional team ID for context


    :return: JSON response with logging confirmation
    :rtype: str  # TODO: Fix type
    """
    try:
        context_info = []
        if user_id:
            context_info.append(f"user_id={user_id}")
        if team_id:
            context_info.append(f"team_id={team_id}")

        context_str = f" [{', '.join(context_info)}]" if context_info else ""

        logger.info(f"📝 Command executed: {command}{context_str}")

        data = {
            'command': command,
            'user_id': user_id,
            'team_id': team_id,
            'context_info': context_info,
            'status': 'logged'
        }
        ui_format = f"✅ Command logged: {command}"
        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"❌ Failed to log command: {e}")
        return json_error(f"Failed to log command: {e!s}", "Operation failed")

@tool("log_error")
def log_error(
    error_message: str, error_context: str | None = None, team_id: str | None = None
) -> str:
    """
    Log an error message. Requires: error_message


        error_message: The error message to log
        error_context: Optional context information
        team_id: Optional team ID for context


    :return: JSON response with error logging confirmation
    :rtype: str  # TODO: Fix type
    """
    try:
        context_info = []
        if error_context:
            context_info.append(f"context={error_context}")
        if team_id:
            context_info.append(f"team_id={team_id}")

        context_str = f" [{', '.join(context_info)}]" if context_info else ""

        logger.error(f"❌ Error: {error_message}{context_str}")

        data = {
            'error_message': error_message,
            'error_context': error_context,
            'team_id': team_id,
            'context_info': context_info,
            'status': 'logged'
        }
        ui_format = f"✅ Error logged: {error_message}"
        return json_response(data, ui_format=ui_format)

    except Exception as e:
        logger.error(f"❌ Failed to log error: {e}")
        return json_error(f"Failed to log error: {e!s}", "Operation failed")
