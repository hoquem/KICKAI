"""
LangChain tools for player operations.

These tools implement the domain interfaces and provide LangChain-compatible
tools for agent use.
"""

import logging
from typing import List, Optional, Any
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


class GetPlayerStatusInput(PlayerToolsInput):
    """Input for getting player status."""
    player_id: str = Field(description="The player ID")


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
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        GetAllPlayersTool.logger = self.logger
        GetAllPlayersTool.team_id = team_id
        GetAllPlayersTool.command_operations = command_operations
    
    def _run(self, team_id: str) -> str:
        """Get all players synchronously."""
        try:
            # Use the command operations to get player list
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                return "Async operation not supported in sync context"
            else:
                result = loop.run_until_complete(self.command_operations.list_players(team_id))
                return result
        except Exception as e:
            self.logger.error(f"Error getting all players: {e}")
            return f"Error: {str(e)}"
    
    async def _arun(self, team_id: str) -> str:
        """Get all players asynchronously."""
        try:
            # Use the command operations to get player list
            result = await self.command_operations.list_players(team_id)
            return result
        except Exception as e:
            self.logger.error(f"Error getting all players: {e}")
            return f"Error: {str(e)}"


class GetPlayerByIdTool(BaseTool):
    """Tool to get a player by ID."""
    
    name = "get_player_by_id"
    description = "Get a player by their ID"
    args_schema = GetPlayerByIdInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        GetPlayerByIdTool.logger = self.logger
        GetPlayerByIdTool.team_id = team_id
        GetPlayerByIdTool.command_operations = command_operations
    
    def _run(self, player_id: str, team_id: str) -> str:
        """Get a player by ID synchronously."""
        try:
            # Use the command operations to get player info
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                self.logger.info(f"Getting player by ID: {player_id} for team {team_id}")
                return f"Player info for {player_id} would be retrieved here"
            else:
                # Run in the event loop
                result = loop.run_until_complete(
                    self.command_operations.get_player_info(player_id, team_id)
                )
                return result
        except Exception as e:
            self.logger.error(f"Error getting player by ID: {e}")
            return f"Error getting player info: {str(e)}"
    
    async def _arun(self, player_id: str, team_id: str) -> str:
        """Get player by ID asynchronously."""
        try:
            # Use the command operations to get player info
            success, result = await self.command_operations.get_player_info(player_id, team_id)
            if success:
                return result
            else:
                return f"Failed to get player: {result}"
        except Exception as e:
            self.logger.error(f"Error getting player by ID: {e}")
            return f"Error: {str(e)}"


class GetPendingApprovalsTool(BaseTool):
    """Tool to get pending player approvals."""
    
    name = "get_pending_approvals"
    description = "Get list of players pending approval"
    args_schema = GetPendingApprovalsInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        GetPendingApprovalsTool.logger = self.logger
        GetPendingApprovalsTool.team_id = team_id
        GetPendingApprovalsTool.command_operations = command_operations
    
    def _run(self, team_id: str) -> str:
        """Get pending approvals synchronously."""
        try:
            # Use the command operations to get pending approvals
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                self.logger.info(f"Getting pending approvals for team {team_id}")
                return f"Pending approvals for team {team_id} would be retrieved here"
            else:
                # Run in the event loop
                result = loop.run_until_complete(
                    self.command_operations.get_pending_approvals(team_id)
                )
                return result
        except Exception as e:
            self.logger.error(f"Error getting pending approvals: {e}")
            return f"Error getting pending approvals: {str(e)}"
    
    async def _arun(self, team_id: str) -> str:
        """Get pending approvals asynchronously."""
        try:
            # Use the command operations to get pending approvals
            result = await self.command_operations.get_pending_approvals(team_id)
            return result
        except Exception as e:
            self.logger.error(f"Error getting pending approvals: {e}")
            return f"Error: {str(e)}"


class GetPlayerStatusTool(BaseTool):
    """Tool to get player status."""
    
    name = "get_player_status"
    description = "Get the status of a player"
    args_schema = GetPlayerStatusInput
    
    # Class-level attributes required by agent system
    logger: Optional[logging.Logger] = Field(default=None, description="Logger instance")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")
    
    def __init__(self, team_id: str, command_operations: ICommandOperations):
        super().__init__()
        self.team_id = team_id
        self.command_operations = command_operations
        self.logger = logging.getLogger(__name__)
        # Set class-level attributes for agent system compatibility
        GetPlayerStatusTool.logger = self.logger
        GetPlayerStatusTool.team_id = team_id
        GetPlayerStatusTool.command_operations = command_operations
    
    def _run(self, player_id: str, team_id: str) -> str:
        """Get player status synchronously."""
        try:
            # Use the command operations to get player status
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                self.logger.info(f"Getting player status for {player_id} in team {team_id}")
                return f"Player status for {player_id} would be retrieved here"
            else:
                # Run in the event loop
                result = loop.run_until_complete(
                    self.command_operations.get_player_info(player_id, team_id)
                )
                return result
        except Exception as e:
            self.logger.error(f"Error getting player status: {e}")
            return f"Error getting player status: {str(e)}"
    
    async def _arun(self, player_id: str, team_id: str) -> str:
        """Get player status asynchronously."""
        try:
            # Use the command operations to get player info
            success, result = await self.command_operations.get_player_info(player_id, team_id)
            if success:
                return result
            else:
                return f"Failed to get player status: {result}"
        except Exception as e:
            self.logger.error(f"Error getting player status: {e}")
            return f"Error: {str(e)}" 