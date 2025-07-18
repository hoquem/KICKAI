from typing import Type
from loguru import logger
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

TOOL_REGISTRY = {}

def register_tool_instance(tool_instance):
    TOOL_REGISTRY[tool_instance.name] = tool_instance
    return tool_instance

class LogCommandInput(BaseModel):
    command: str = Field(..., description="Command executed")
    user_id: str = Field(..., description="User ID")
    team_id: str = Field(..., description="Team ID")

class LogCommandTool(BaseTool):
    name: str = "log_command"
    description: str = "Log a command execution."
    args_schema: Type[BaseModel] = LogCommandInput

    def _run(self, command: str, user_id: str, team_id: str) -> str:
        logger.info(f"[TOOL] Command executed: {command} by user {user_id} in team {team_id}")
        return f"Logged command: {command}"

register_tool_instance(LogCommandTool())

class LogErrorInput(BaseModel):
    error: str = Field(..., description="Error message")
    context: str = Field(..., description="Error context")
    team_id: str = Field(..., description="Team ID")

class LogErrorTool(BaseTool):
    name: str = "log_error"
    description: str = "Log an error event."
    args_schema: Type[BaseModel] = LogErrorInput

    def _run(self, error: str, context: str, team_id: str) -> str:
        logger.error(f"[TOOL] Error: {error} | Context: {context} | Team: {team_id}")
        return f"Logged error: {error}"

register_tool_instance(LogErrorTool())

__all__ = ["TOOL_REGISTRY"] 