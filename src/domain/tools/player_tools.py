"""
LangChain tools for player operations.

These tools implement the domain interfaces and provide LangChain-compatible
tools for agent use.
"""

import logging
from typing import List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..interfaces.agent_tools import IPlayerTools, PlayerInfo
from ..interfaces.command_operations import ICommandOperations

logger = logging.getLogger(__name__)


class PlayerToolsInput(BaseModel):
    """Input schema for player tools."""
    team_id: str = Field(description="The team ID")


class GetAllPlayersInput(PlayerToolsInput):
    """Input for getting all players."""
    pass


class GetPlayerByIdInput(PlayerToolsInput):
    """Input for getting player by ID."""
    player_id: str = Field(description="The player ID")


class GetPlayerByPhoneInput(PlayerToolsInput):
    """Input for getting player by phone."""
    phone: str = Field(description="The player's phone number")


class GetPendingApprovalsInput(PlayerToolsInput):
    """Input for getting pending approvals."""
    pass


class PlayerTools(BaseTool):
    """LangChain tool for player operations."""
    
    name = "player_tools"
    description = "Tools for managing player information and operations"
    args_schema = PlayerToolsInput
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
    
    def _run(self, **kwargs) -> str:
        """Run the tool synchronously."""
        try:
            # This is a placeholder - in a real implementation, you'd call the async methods
            # For now, we'll return a message indicating the tool is available
            return f"Player tools available for team {self.team_id}. Use specific player tool methods."
        except Exception as e:
            self.logger.error(f"Error in player tools: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, **kwargs) -> str:
        """Run the tool asynchronously."""
        try:
            # This is a placeholder - in a real implementation, you'd call the async methods
            return f"Player tools available for team {self.team_id}. Use specific player tool methods."
        except Exception as e:
            self.logger.error(f"Error in player tools: {e}")
            return f"Error: {str(e)}"


class GetAllPlayersTool(BaseTool):
    """Tool to get all players for a team."""
    
    name = "get_all_players"
    description = "Get all players for a team"
    args_schema = GetAllPlayersInput
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
    
    def _run(self, team_id: str) -> str:
        """Get all players synchronously."""
        try:
            # Use the command operations to get player list
            success, result = self.command_operations.get_team_players(team_id)
            if success:
                return result
            else:
                return f"Failed to get players: {result}"
        except Exception as e:
            self.logger.error(f"Error getting all players: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, team_id: str) -> str:
        """Get all players asynchronously."""
        return self._run(team_id)


class GetPlayerByIdTool(BaseTool):
    """Tool to get player by ID."""
    
    name = "get_player_by_id"
    description = "Get player information by player ID"
    args_schema = GetPlayerByIdInput
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
    
    def _run(self, player_id: str, team_id: str) -> str:
        """Get player by ID synchronously."""
        try:
            # Use the command operations to get player info
            success, result = self.command_operations.get_player_info(player_id, team_id)
            if success:
                return result
            else:
                return f"Failed to get player: {result}"
        except Exception as e:
            self.logger.error(f"Error getting player by ID: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, player_id: str, team_id: str) -> str:
        """Get player by ID asynchronously."""
        return self._run(player_id, team_id)


class GetPendingApprovalsTool(BaseTool):
    """Tool to get pending player approvals."""
    
    name = "get_pending_approvals"
    description = "Get list of players pending approval"
    args_schema = GetPendingApprovalsInput
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
    
    def _run(self, team_id: str) -> str:
        """Get pending approvals synchronously."""
        try:
            # Use the command operations to get pending approvals
            success, result = self.command_operations.get_pending_approvals(team_id)
            if success:
                return result
            else:
                return f"Failed to get pending approvals: {result}"
        except Exception as e:
            self.logger.error(f"Error getting pending approvals: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, team_id: str) -> str:
        """Get pending approvals asynchronously."""
        return self._run(team_id) 