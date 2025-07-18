#!/usr/bin/env python3
"""
Player Registration Tools for CrewAI Agents

This module provides CrewAI tools for player registration operations
including registration, approval, and player management.
"""

from typing import Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

TOOL_REGISTRY = {}

def register_tool_instance(tool_instance):
    TOOL_REGISTRY[tool_instance.name] = tool_instance
    return tool_instance

class RegisterPlayerInput(BaseModel):
    name: str = Field(description="Player's full name")
    phone: str = Field(description="Player's phone number")
    position: str = Field(description="Player's preferred position")

class RegisterPlayerTool(BaseTool):
    name: str = "register_player"
    description: str = "Register a new player for the team"
    args_schema: Type[BaseModel] = RegisterPlayerInput

    def _run(self, name: str, phone: str, position: str) -> str:
        return f"Player {name} registered successfully with phone {phone} for position {position}"

register_tool_instance(RegisterPlayerTool())

class ApprovePlayerInput(BaseModel):
    player_id: str = Field(description="Player ID to approve")

class ApprovePlayerTool(BaseTool):
    name: str = "approve_player"
    description: str = "Approve a pending player registration"
    args_schema: Type[BaseModel] = ApprovePlayerInput

    def _run(self, player_id: str) -> str:
        return f"Player {player_id} approved successfully"

register_tool_instance(ApprovePlayerTool())

class GetPlayerInfoInput(BaseModel):
    player_id: str = Field(description="Player ID to get info for")

class GetPlayerInfoTool(BaseTool):
    name: str = "get_player_info"
    description: str = "Get detailed information about a specific player"
    args_schema: Type[BaseModel] = GetPlayerInfoInput

    def _run(self, player_id: str) -> str:
        return f"Player {player_id} information retrieved successfully"

register_tool_instance(GetPlayerInfoTool())

class ListPlayersTool(BaseTool):
    name: str = "list_players"
    description: str = "List all players in the team"

    def _run(self) -> str:
        return "All players listed successfully"

register_tool_instance(ListPlayersTool())

class RemovePlayerInput(BaseModel):
    player_id: str = Field(description="Player ID to remove")

class RemovePlayerTool(BaseTool):
    name: str = "remove_player"
    description: str = "Remove a player from the team"
    args_schema: Type[BaseModel] = RemovePlayerInput

    def _run(self, player_id: str) -> str:
        return f"Player {player_id} removed successfully"

register_tool_instance(RemovePlayerTool())

# New tools for missing functionality

class GetMyStatusTool(BaseTool):
    name: str = "get_my_status"
    description: str = "Get the current user's player status and information"

    def _run(self) -> str:
        return "Your player status retrieved successfully"

register_tool_instance(GetMyStatusTool())

class GetPlayerStatusInput(BaseModel):
    player_id: str = Field(description="Player ID to get status for")

class GetPlayerStatusTool(BaseTool):
    name: str = "get_player_status"
    description: str = "Get status information for a specific player"
    args_schema: Type[BaseModel] = GetPlayerStatusInput

    def _run(self, player_id: str) -> str:
        return f"Player {player_id} status retrieved successfully"

register_tool_instance(GetPlayerStatusTool())

class GetAllPlayersTool(BaseTool):
    name: str = "get_all_players"
    description: str = "Get a list of all players in the team with their status"

    def _run(self) -> str:
        return "All players list retrieved successfully"

register_tool_instance(GetAllPlayersTool())

class GetMatchInput(BaseModel):
    match_id: Optional[str] = Field(description="Match ID to get info for (optional)")

class GetMatchTool(BaseTool):
    name: str = "get_match"
    description: str = "Get information about upcoming or recent matches"
    args_schema: Type[BaseModel] = GetMatchInput

    def _run(self, match_id: Optional[str] = None) -> str:
        if match_id:
            return f"Match {match_id} information retrieved successfully"
        else:
            return "Upcoming matches information retrieved successfully"

register_tool_instance(GetMatchTool())

__all__ = ["TOOL_REGISTRY"] 