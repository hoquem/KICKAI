"""
LangChain tools for logging operations.

These tools provide logging capabilities for agents.
"""

import logging
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LogCommandInput(BaseModel):
    """Input for logging a command."""
    user_id: str = Field(description="The user ID")
    command: str = Field(description="The command executed")
    team_id: str = Field(description="The team ID")
    success: bool = Field(description="Whether the command was successful")


class LogEventInput(BaseModel):
    """Input for logging an event."""
    event_type: str = Field(description="The type of event")
    details: Dict[str, Any] = Field(description="Event details")
    team_id: str = Field(description="The team ID")


class LogCommandTool(BaseTool):
    """Tool to log command execution."""
    
    name = "log_command"
    description = "Log a command execution"
    args_schema = LogCommandInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    
    def __init__(self, team_id: str):
        super().__init__()
        self.team_id = team_id
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        LogCommandTool.logger = self.logger
        LogCommandTool.team_id = team_id
    
    def _run(self, user_id: str, command: str, team_id: str, success: bool) -> str:
        """Log a command synchronously."""
        try:
            status = "SUCCESS" if success else "FAILED"
            self.logger.info(f"Command logged - User: {user_id}, Command: {command}, Team: {team_id}, Status: {status}")
            return f"Command logged: {command} by {user_id} - {status}"
        except Exception as e:
            self.logger.error(f"Error logging command: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, user_id: str, command: str, team_id: str, success: bool) -> str:
        """Log a command asynchronously."""
        return self._run(user_id, command, team_id, success)


class LogEventTool(BaseTool):
    """Tool to log an event."""
    
    name = "log_event"
    description = "Log an event"
    args_schema = LogEventInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    
    def __init__(self, team_id: str):
        super().__init__()
        self.team_id = team_id
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        LogEventTool.logger = self.logger
        LogEventTool.team_id = team_id
    
    def _run(self, event_type: str, details: Dict[str, Any], team_id: str) -> str:
        """Log an event synchronously."""
        try:
            self.logger.info(f"Event logged - Type: {event_type}, Team: {team_id}, Details: {details}")
            return f"Event logged: {event_type} for team {team_id}"
        except Exception as e:
            self.logger.error(f"Error logging event: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, event_type: str, details: Dict[str, Any], team_id: str) -> str:
        """Log an event asynchronously."""
        return self._run(event_type, details, team_id) 