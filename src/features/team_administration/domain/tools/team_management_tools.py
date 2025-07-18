"""
Team management tools for KICKAI (placeholder, not used in production).
"""

from typing import Optional, Type
from loguru import logger
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

TOOL_REGISTRY = {}

def register_tool_instance(tool_instance):
    TOOL_REGISTRY[tool_instance.name] = tool_instance
    return tool_instance

class CreateTeamInput(BaseModel):
    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description (optional)")

class CreateTeamTool(BaseTool):
    name: str = "create_team"
    description: str = "Create a new team (example tool)."
    args_schema: Type[BaseModel] = CreateTeamInput

    def _run(self, name: str, description: Optional[str] = None) -> dict:
        logger.info(f"[TOOL] Creating team: {name} | Description: {description}")
        return {"id": "team-123", "name": name, "description": description}

register_tool_instance(CreateTeamTool())

__all__ = ["TOOL_REGISTRY"] 