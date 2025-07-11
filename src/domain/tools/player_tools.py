"""
Player tools for the KICKAI system.

This module provides LangChain tools for player-related operations.
"""

import logging
from typing import Any, Optional, List, Dict, Type
from pydantic import BaseModel, Field

from crewai.tools import BaseTool
from domain.interfaces.command_operations import ICommandOperations

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


class GetMyStatusInput(PlayerToolsInput):
    """Input for getting current user's status by Telegram user ID."""
    user_id: str = Field(description="The Telegram user ID")


class PlayerTools(BaseTool):
    """LangChain tool for player operations."""
    
    name: str = Field(default="player_tools", description="Tool name")
    description: str = Field(default="Tools for managing player information and operations", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=PlayerToolsInput, description="Input schema")
    
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
    """Tool to get all players for a team (async-only)."""
    
    name: str = Field(default="get_all_players", description="Tool name")
    description: str = Field(default="Get all players for a team", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=GetAllPlayersInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
    
    def _run(self, team_id: str) -> str:
        raise NotImplementedError("GetAllPlayersTool is async-only. Use 'await _arun(...)' instead.")
    
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
    """Tool to get a player by ID (async-only)."""
    
    name: str = Field(default="get_player_by_id", description="Tool name")
    description: str = Field(default="Get a player by their ID", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=GetPlayerByIdInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
    
    def _run(self, player_id: str) -> str:
        raise NotImplementedError("GetPlayerByIdTool is async-only. Use 'await _arun(...)' instead.")
    
    async def _arun(self, player_id: str, team_id: str) -> str:
        """Get player by ID asynchronously."""
        try:
            success, result = await self.command_operations.get_player_info(player_id, team_id)
            if success:
                return result
            else:
                return f"Failed to get player: {result}"
        except Exception as e:
            self.logger.error(f"Error getting player by ID: {e}")
            return f"Error: {str(e)}"


class GetPendingApprovalsTool(BaseTool):
    """Tool to get pending player approvals (async-only)."""
    
    name: str = Field(default="get_pending_approvals", description="Tool name")
    description: str = Field(default="Get list of players pending approval", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=GetPendingApprovalsInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
    
    def _run(self, team_id: str) -> str:
        raise NotImplementedError("GetPendingApprovalsTool is async-only. Use 'await _arun(...)' instead.")
    
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
    """Tool to get player status by player ID (async-only)."""
    
    name: str = Field(default="get_player_status", description="Tool name")
    description: str = Field(default="Get player status by player ID", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=GetPlayerStatusInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
    
    def _run(self, player_id: str) -> str:
        raise NotImplementedError("GetPlayerStatusTool is async-only. Use 'await _arun(...)' instead.")
    
    async def _arun(self, player_id: str, team_id: str) -> str:
        """Get player status asynchronously."""
        try:
            success, result = await self.command_operations.get_player_info(player_id, team_id)
            if success:
                return result
            else:
                return f"Failed to get player status: {result}"
        except Exception as e:
            self.logger.error(f"Error getting player status: {e}")
            return f"Error: {str(e)}"


class GetMyStatusTool(BaseTool):
    """Tool to get current user's status by Telegram user ID (async-only)."""
    
    name: str = Field(default="get_my_status", description="Tool name")
    description: str = Field(default="Get current user's status by Telegram user ID", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=GetMyStatusInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
        print(f"🔍 [DEBUG] GetMyStatusTool.__init__ called with team_id='{team_id}', kwargs={kwargs}")
        logger.info(f"[TOOL INIT] GetMyStatusTool initialized with team_id='{team_id}'")
        logger.info(f"[TOOL INIT] GetMyStatusTool kwargs: {kwargs}")
        
        # Extract command_operations from kwargs
        if 'command_operations' in kwargs:
            self.command_operations = kwargs['command_operations']
            logger.info(f"[TOOL INIT] GetMyStatusTool command_operations set: {type(self.command_operations).__name__}")
        else:
            logger.warning(f"[TOOL INIT] GetMyStatusTool command_operations not provided in kwargs")
            self.command_operations = None
    
    def _run(self, user_id: str) -> str:
        raise NotImplementedError("GetMyStatusTool is async-only. Use 'await _arun(...)' instead.")
    
    async def _arun(self, user_id: str, team_id: str) -> str:
        """Get current user's status asynchronously."""
        print(f"🔍 [DEBUG] GetMyStatusTool._arun called with user_id='{user_id}', team_id='{team_id}'")
        logger.info(f"[TOOL EXECUTE] GetMyStatusTool._arun called")
        logger.info(f"[TOOL EXECUTE] Parameters: user_id='{user_id}', team_id='{team_id}'")
        logger.info(f"[TOOL EXECUTE] Self.team_id: '{self.team_id}'")
        logger.info(f"[TOOL EXECUTE] Command operations available: {self.command_operations is not None}")
        
        if self.command_operations is None:
            error_msg = "Command operations interface not available"
            logger.error(f"[TOOL EXECUTE] ❌ {error_msg}")
            return f"Error: {error_msg}"
        
        try:
            logger.info(f"[TOOL EXECUTE] Calling command_operations.get_player_info with user_id='{user_id}', team_id='{team_id}'")
            
            # Call the command operations interface
            success, result = await self.command_operations.get_player_info(user_id, team_id)
            
            logger.info(f"[TOOL EXECUTE] Command operations result: success={success}")
            logger.info(f"[TOOL EXECUTE] Command operations result: result={result}")
            
            if success:
                logger.info(f"[TOOL EXECUTE] ✅ GetMyStatusTool completed successfully")
                return result
            else:
                logger.warning(f"[TOOL EXECUTE] ⚠️ GetMyStatusTool failed: {result}")
                return f"Failed to get player status: {result}"
                
        except Exception as e:
            error_msg = f"Error getting player status: {e}"
            logger.error(f"[TOOL EXECUTE] ❌ {error_msg}", exc_info=True)
            return f"Error: {error_msg}"


class ApprovePlayerInput(PlayerToolsInput):
    """Input for approving a player."""
    player_id: str = Field(description="The player ID to approve")


class ApprovePlayerTool(BaseTool):
    """Tool to approve a player (async-only)."""
    
    name: str = Field(default="approve_player", description="Tool name")
    description: str = Field(default="Approve a player for match squad selection", description="Tool description")
    args_schema: Type[BaseModel] = Field(default=ApprovePlayerInput, description="Input schema")
    team_id: Optional[str] = Field(default=None, description="Team ID")
    logger: Optional[logging.Logger] = Field(default_factory=lambda: logging.getLogger(__name__), description="Logger instance")
    command_operations: Optional[Any] = Field(default=None, description="Command operations interface")

    def __init__(self, team_id: str, **kwargs):
        super().__init__(team_id=team_id, **kwargs)
    
    def _run(self, player_id: str) -> str:
        raise NotImplementedError("ApprovePlayerTool is async-only. Use 'await _arun(...)' instead.")
    
    async def _arun(self, player_id: str, team_id: str) -> str:
        """Approve player asynchronously."""
        try:
            success, result = await self.command_operations.approve_player(player_id, team_id)
            if success:
                return result
            else:
                return f"Failed to approve player: {result}"
        except Exception as e:
            self.logger.error(f"Error approving player: {e}")
            return f"Error: {str(e)}" 