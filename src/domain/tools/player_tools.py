#!/usr/bin/env python3
"""
Player Tools for KICKAI

This module provides tools for player-related operations that can be used by agents.
All tools are designed to work with the context manager for proper user identification.
"""

import logging
from typing import Dict, Any, Optional
from crewai.tools import BaseTool

from database.models_improved import Player
from domain.adapters.player_operations_adapter import PlayerOperationsAdapter
from domain.interfaces.player_operations import IPlayerOperations
from core.context_manager import get_context_manager, UserContext

logger = logging.getLogger(__name__)


class GetPlayerStatusTool(BaseTool):
    """Tool to get player status by player ID."""
    
    name: str = "get_player_status"
    description: str = "Get player status by player ID."
    team_id: str = None
    player_id: str = None
    player_operations: PlayerOperationsAdapter = None
    
    def __init__(self, team_id: str = None, player_id: str = None, player_operations: IPlayerOperations = None):
        super().__init__()
        self.team_id = team_id
        self.player_id = player_id
        if player_operations:
            self.player_operations = PlayerOperationsAdapter(player_operations)
        else:
            # Fallback to legacy pattern for backward compatibility
            from services.player_service import get_player_service
            self.player_operations = PlayerOperationsAdapter(get_player_service(team_id=team_id))
    
    def _run(self, player_id: str) -> str:
        """Get player status by player ID."""
        try:
            # Validate context
            if not self.team_id or not player_id:
                return "❌ Missing team or player ID."
            
            # Get player status
            player = self.player_operations.get_player_by_id(player_id, self.team_id)
            if not player:
                return f"❌ Player {player_id} not found in team {self.team_id}."
            
            # Format player status
            status_info = f"""
👤 **Player Status: {player.name}**
📱 Phone: {player.phone}
🏃 Position: {player.position}
📊 Status: {player.onboarding_status.value}
📅 Registration Date: {player.registration_date}
"""
            return status_info.strip()
            
        except Exception as e:
            logger.error(f"Error in GetPlayerStatusTool: {e}")
            return f"❌ Error retrieving player status: {str(e)}"


class GetMyStatusTool(BaseTool):
    """Tool to get the current user's own status."""
    
    name: str = "get_my_status"
    description: str = "Get the current user's own player status."
    team_id: str = None
    user_id: str = None
    player_operations: PlayerOperationsAdapter = None
    
    def __init__(self, team_id: str = None, user_id: str = None, player_operations: IPlayerOperations = None):
        super().__init__()
        self.team_id = team_id
        self.user_id = user_id
        if player_operations:
            self.player_operations = PlayerOperationsAdapter(player_operations)
        else:
            # Fallback to legacy pattern for backward compatibility
            from services.player_service import get_player_service
            self.player_operations = PlayerOperationsAdapter(get_player_service(team_id=team_id))
    
    def _run(self) -> str:
        """Get the current user's own status."""
        try:
            # Validate context
            if not self.team_id or not self.user_id:
                return "❌ Missing team or user ID."
            
            # Get player by telegram ID
            player = self.player_operations.get_player_by_telegram_id(self.user_id, self.team_id)
            if not player:
                return "❌ You are not registered as a player in this team."
            
            # Format player status
            status_info = f"""
👤 **Your Status: {player.name}**
📱 Phone: {player.phone}
🏃 Position: {player.position}
📊 Status: {player.onboarding_status.value}
📅 Registration Date: {player.registration_date}
"""
            return status_info.strip()
            
        except Exception as e:
            logger.error(f"Error in GetMyStatusTool: {e}")
            return f"❌ Error retrieving your status: {str(e)}"


class GetAllPlayersTool(BaseTool):
    """Tool to get all players in the team."""
    
    name: str = "get_all_players"
    description: str = "Get all players in the team."
    team_id: str = None
    is_leadership_chat: bool = False
    player_operations: PlayerOperationsAdapter = None
    
    def __init__(self, team_id: str = None, is_leadership_chat: bool = False, player_operations: IPlayerOperations = None):
        super().__init__()
        self.team_id = team_id
        self.is_leadership_chat = is_leadership_chat
        if player_operations:
            self.player_operations = PlayerOperationsAdapter(player_operations)
        else:
            # Fallback to legacy pattern for backward compatibility
            from services.player_service import get_player_service
            self.player_operations = PlayerOperationsAdapter(get_player_service(team_id=team_id))
    
    def _run(self) -> str:
        """Get all players in the team."""
        try:
            # Validate context
            if not self.team_id:
                return "❌ Missing team ID."
            
            # Get all players
            players = self.player_operations.get_all_players(self.team_id, self.is_leadership_chat)
            if not players:
                return "❌ No players found in this team."
            
            # Format player list
            player_list = "👥 **Team Players:**\n\n"
            for player in players:
                status_emoji = "✅" if player.onboarding_status.value == "ACTIVE" else "⏸️"
                player_list += f"{status_emoji} **{player.name}** ({player.player_id})\n"
                player_list += f"   📱 {player.phone} | 🏃 {player.position}\n"
                player_list += f"   📊 {player.onboarding_status.value}\n\n"
            
            return player_list.strip()
            
        except Exception as e:
            logger.error(f"Error in GetAllPlayersTool: {e}")
            return f"❌ Error retrieving player list: {str(e)}"


class GetPlayerByIdTool(BaseTool):
    """Tool to get player by ID."""
    
    name: str = "get_player_by_id"
    description: str = "Get player information by player ID."
    team_id: str = None
    player_operations: PlayerOperationsAdapter = None
    
    def __init__(self, team_id: str = None, player_operations: IPlayerOperations = None):
        super().__init__()
        self.team_id = team_id
        if player_operations:
            self.player_operations = PlayerOperationsAdapter(player_operations)
        else:
            # Fallback to legacy pattern for backward compatibility
            from services.player_service import get_player_service
            self.player_operations = PlayerOperationsAdapter(get_player_service(team_id=team_id))
    
    def _run(self, player_id: str) -> str:
        """Get player by ID."""
        try:
            # Validate context
            if not self.team_id or not player_id:
                return "❌ Missing team or player ID."
            
            # Get player
            player = self.player_operations.get_player_by_id(player_id, self.team_id)
            if not player:
                return f"❌ Player {player_id} not found in team {self.team_id}."
            
            # Format player information
            player_info = f"""
👤 **Player Information: {player.name}**
🆔 Player ID: {player.player_id}
📱 Phone: {player.phone}
🏃 Position: {player.position}
📊 Status: {player.onboarding_status.value}
📅 Registration Date: {player.registration_date}
"""
            return player_info.strip()
            
        except Exception as e:
            logger.error(f"Error in GetPlayerByIdTool: {e}")
            return f"❌ Error retrieving player information: {str(e)}"


class GetPendingApprovalsTool(BaseTool):
    """Tool to get pending player approvals."""
    
    name: str = "get_pending_approvals"
    description: str = "Get list of players pending approval."
    team_id: str = None
    player_operations: PlayerOperationsAdapter = None
    
    def __init__(self, team_id: str = None, player_operations: IPlayerOperations = None):
        super().__init__()
        self.team_id = team_id
        if player_operations:
            self.player_operations = PlayerOperationsAdapter(player_operations)
        else:
            # Fallback to legacy pattern for backward compatibility
            from services.player_service import get_player_service
            self.player_operations = PlayerOperationsAdapter(get_player_service(team_id=team_id))
    
    def _run(self) -> str:
        """Get pending player approvals."""
        try:
            # Validate context
            if not self.team_id:
                return "❌ Missing team ID."
            
            # Get pending approvals
            pending_players = self.player_operations.get_pending_approvals(self.team_id)
            if not pending_players:
                return "✅ No players pending approval."
            
            # Format pending approvals list
            pending_list = "⏳ **Players Pending Approval:**\n\n"
            for player in pending_players:
                pending_list += f"👤 **{player.name}** ({player.player_id})\n"
                pending_list += f"   📱 {player.phone} | 🏃 {player.position}\n"
                pending_list += f"   📅 Registration Date: {player.registration_date}\n\n"
            
            return pending_list.strip()
            
        except Exception as e:
            logger.error(f"Error in GetPendingApprovalsTool: {e}")
            return f"❌ Error retrieving pending approvals: {str(e)}"


class ApprovePlayerTool(BaseTool):
    """Tool to approve a player."""
    
    name: str = "approve_player"
    description: str = "Approve a player for the team."
    team_id: str = None
    player_operations: PlayerOperationsAdapter = None
    
    def __init__(self, team_id: str = None, player_operations: IPlayerOperations = None):
        super().__init__()
        self.team_id = team_id
        if player_operations:
            self.player_operations = PlayerOperationsAdapter(player_operations)
        else:
            # Fallback to legacy pattern for backward compatibility
            from services.player_service import get_player_service
            self.player_operations = PlayerOperationsAdapter(get_player_service(team_id=team_id))
    
    def _run(self, player_id: str) -> str:
        """Approve a player."""
        try:
            # Validate context
            if not self.team_id or not player_id:
                return "❌ Missing team or player ID."
            
            # Approve player
            success = self.player_operations.approve_player(player_id, self.team_id)
            if success:
                return f"✅ Player {player_id} has been approved successfully."
            else:
                return f"❌ Failed to approve player {player_id}."
            
        except Exception as e:
            logger.error(f"Error in ApprovePlayerTool: {e}")
            return f"❌ Error approving player: {str(e)}"


def configure_tool_with_context(tool: BaseTool, context: Dict[str, Any]) -> None:
    """
    Configure a tool with execution context.
    
    This function sets the appropriate attributes on tools based on the context.
    It also handles onboarding messages for unregistered users.
    
    Args:
        tool: The tool to configure
        context: Execution context dictionary
    """
    try:
        # Set team_id on tools that support it
        if hasattr(tool, 'team_id'):
            tool.team_id = context.get('team_id')
        
        # Set user_id on tools that support it
        if hasattr(tool, 'user_id'):
            tool.user_id = context.get('user_id')
        
        # Set is_leadership_chat on tools that support it
        if hasattr(tool, 'is_leadership_chat'):
            tool.is_leadership_chat = context.get('is_leadership_chat', False)
        
        # Check if user needs onboarding
        is_registered = context.get('is_registered', False)
        is_in_correct_team = context.get('is_in_correct_team', False)
        onboarding_message = context.get('onboarding_message')
        
        # If user needs onboarding, modify tool behavior
        if not is_registered or not is_in_correct_team:
            if onboarding_message:
                # Override the tool's _run method to return onboarding message
                original_run = tool._run
                def onboarding_run(*args, **kwargs):
                    return onboarding_message
                tool._run = onboarding_run
                logger.info(f"[TOOL CONFIG] Configured tool {tool.name} to show onboarding message")
        
        logger.debug(f"[TOOL CONFIG] Configured tool {getattr(tool, 'name', 'unknown')} with context")
        
    except Exception as e:
        logger.warning(f"[TOOL CONFIG] Error configuring tool {getattr(tool, 'name', 'unknown')}: {e}")
        # Don't raise - continue with other tools 