"""
Player management tools for KICKAI system.

This module provides tools for player management, approval, and information retrieval.
"""

import logging
from typing import Optional
from pydantic import BaseModel

from crewai.tools import tool
from src.features.player_registration.domain.services.player_service import PlayerService
from src.core.dependency_container import get_container
from src.core.context_types import StandardizedContext

logger = logging.getLogger(__name__)


class ApprovePlayerInput(BaseModel):
    """Input model for approve_player tool."""
    player_id: str
    team_id: Optional[str] = None


class GetPlayerStatusInput(BaseModel):
    """Input model for get_player_status tool."""
    phone: str
    team_id: Optional[str] = None


class GetMyStatusInput(BaseModel):
    """Input model for get_my_status tool."""
    user_id: str
    team_id: Optional[str] = None


class GetAllPlayersInput(BaseModel):
    """Input model for get_all_players tool."""
    team_id: Optional[str] = None


class GetMatchInput(BaseModel):
    """Input model for get_match tool."""
    match_id: str
    team_id: Optional[str] = None


# Note: register_player tool is implemented in registration_tools.py to avoid duplication

@tool("approve_player")
def approve_player(player_id: str, team_id: Optional[str] = None) -> str:
    """
    Approve a player for team participation. Requires: player_id
    
    Args:
        player_id: The player ID to approve
        team_id: Optional team ID for context
    
    Returns:
        Approval status or error message
    """
    try:
        container = get_container()
        player_service = container.get(PlayerService)
        result = player_service.approve_player(player_id, team_id)
        logger.info(f"✅ Player approved: {player_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to approve player: {e}")
        return f"❌ Failed to approve player: {str(e)}"


@tool("get_my_status")
def get_my_status(context: dict) -> str:
    """
    Get current user's player status and information. Requires: context
    
    Args:
        context: Dictionary containing user information (will be converted to StandardizedContext)
    
    Returns:
        User's player status and information
    """
    try:
        # Convert dictionary to StandardizedContext
        if isinstance(context, dict):
            standardized_context = StandardizedContext.from_dict(context)
        else:
            standardized_context = context
        
        user_id = standardized_context.user_id
        team_id = standardized_context.team_id
        
        container = get_container()
        player_service = container.get(PlayerService)
        result = player_service.get_my_status(user_id, team_id)
        logger.info(f"✅ My status retrieved for user: {user_id} in team: {team_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get my status for {context.get('user_id', 'unknown')}: {e}")
        return f"❌ Failed to get my status: {str(e)}"


@tool("get_player_status")
def get_player_status(phone: str, team_id: Optional[str] = None) -> str:
    """
    Get player status by phone number. Requires: phone
    
    Args:
        phone: The phone number to check
        team_id: Optional team ID for context
    
    Returns:
        Player status or error message
    """
    try:
        container = get_container()
        player_service = container.get(PlayerService)
        result = player_service.get_player_status(phone, team_id)
        logger.info(f"✅ Player status retrieved for phone: {phone}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get player status: {e}")
        return f"❌ Failed to get player status: {str(e)}"


@tool("get_all_players")
def get_all_players(context: dict) -> str:
    """
    Get all players for the team. Requires: context
    
    Args:
        context: Dictionary containing team information (will be converted to StandardizedContext)
    
    Returns:
        List of all players or error message
    """
    try:
        # Convert dictionary to StandardizedContext
        if isinstance(context, dict):
            standardized_context = StandardizedContext.from_dict(context)
        else:
            standardized_context = context
        
        team_id = standardized_context.team_id
        
        container = get_container()
        player_service = container.get(PlayerService)
        result = player_service.get_all_players(team_id)
        logger.info(f"✅ All players retrieved for team: {team_id}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get all players for team {context.get('team_id', 'unknown')}: {e}")
        return f"❌ Failed to get all players: {str(e)}"


@tool("get_match")
def get_match(match_id: str, team_id: Optional[str] = None) -> str:
    """
    Get match information. Requires: match_id
    
    Args:
        match_id: The match ID to get information for
        team_id: Optional team ID for context
    
    Returns:
        Match information or error message
    """
    try:
        # This would integrate with match service
        logger.info(f"✅ Match info retrieved: {match_id}")
        return f"✅ Match info for {match_id}: Match details would be displayed here"
        
    except Exception as e:
        logger.error(f"❌ Failed to get match info: {e}")
        return f"❌ Failed to get match info: {str(e)}"

# Note: Removed unused tools: remove_player, get_player_info, list_players
# These tools are not assigned to any agents in the configuration 