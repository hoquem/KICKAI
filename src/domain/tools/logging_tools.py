"""
Logging tools for the KICKAI system.

This module provides LangChain tools for logging operations.
"""

import logging
from typing import Any, Optional, Dict, Type
from pydantic import BaseModel, Field

from crewai.tools import BaseTool
from domain.interfaces.command_operations import ICommandOperations

logger = logging.getLogger(__name__)


class LogCommandInput(BaseModel):
    """Input for logging a command."""
    user_id: str = Field(description="The user ID")
    command: str = Field(description="The command executed")
    team_id: str = Field(description="The team ID")
    success: bool = Field(description="Whether the command was successful")
    chat_id: str = Field(description="The chat ID where the command was executed")
    details: Optional[str] = Field(default=None, description="Additional details about the command")


class LogEventInput(BaseModel):
    """Input for logging an event."""
    event_type: str = Field(description="The type of event")
    details: Any = Field(description="Event details")
    team_id: str = Field(description="The team ID")
    user_id: str = Field(description="The user ID associated with the event")


class LogCommandTool(BaseTool):
    """Tool to log command execution."""
    
    name: str = Field(default="log_command", description="Tool name")
    description: str = Field(default="Log a command execution", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=LogCommandInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
    
    def _run(self, command: str, user_id: str, chat_id: str, success: bool, details: Optional[str] = None) -> str:
        """Log a command synchronously."""
        try:
            status = "SUCCESS" if success else "FAILED"
            self.logger.info(f"Command logged - User: {user_id}, Command: {command}, Team: {self.team_id}, Status: {status}")
            return f"Command logged: {command} by {user_id} - {status}"
        except Exception as e:
            self.logger.error(f"Error logging command: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, user_id: str, command: str, team_id: str, success: bool) -> str:
        """Log a command asynchronously."""
        return self._run(user_id, command, team_id, success)


class LogEventTool(BaseTool):
    """Tool to log an event."""
    
    name: str = Field(default="log_event", description="Tool name")
    description: str = Field(default="Log an event", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=LogEventInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
    
    def _run(self, event_type: str, user_id: str, details: Optional[str] = None) -> str:
        """Log an event synchronously."""
        try:
            self.logger.info(f"Event logged - Type: {event_type}, Team: {self.team_id}, Details: {details}")
            return f"Event logged: {event_type} for team {self.team_id}"
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, event_type: str, details: Any, team_id: str) -> str:
        """Log an event asynchronously."""
        return self._run(event_type, details, team_id) 