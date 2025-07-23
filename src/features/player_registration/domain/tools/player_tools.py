"""
Player management tools for KICKAI system.

This module provides tools for player management, approval, and information retrieval.
"""

import asyncio
import logging
import re
from typing import Any

from crewai.tools import tool
from pydantic import BaseModel

from src.core.context_types import StandardizedContext
from src.core.dependency_container import get_container
from src.features.player_registration.domain.services.player_service import PlayerService
from src.features.team_administration.domain.services.team_member_service import TeamMemberService

logger = logging.getLogger(__name__)


class ApprovePlayerInput(BaseModel):
    """Input model for approve_player tool."""
    player_id: str
    team_id: str | None = None


class GetPlayerStatusInput(BaseModel):
    """Input model for get_player_status tool."""
    phone: str
    team_id: str | None = None


class GetMyStatusInput(BaseModel):
    """Input model for get_my_status tool."""
    user_id: str
    team_id: str | None = None


class GetAllPlayersInput(BaseModel):
    """Input model for get_all_players tool."""
    team_id: str | None = None


class GetMatchInput(BaseModel):
    """Input model for get_match tool."""
    match_id: str
    team_id: str | None = None


# Note: register_player tool is implemented in registration_tools.py to avoid duplication

@tool("approve_player")
def approve_player(player_id: str, team_id: str | None = None) -> str:
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
        player_service = container.get_service(PlayerService)
        result = player_service.approve_player(player_id, team_id)
        logger.info(f"✅ Player approved: {player_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Failed to approve player: {e}")
        return f"❌ Failed to approve player: {e!s}"


@tool("get_my_status")
def get_my_status(team_id: str, user_id: str) -> str:
    """
    Get current user's player status and information. 
    This tool is for players in the main chat.
    For team members in leadership chat, use get_my_team_member_status.
    Uses context information from the task description.
    
    Returns:
        User's player status and information
    """
    try:
        # For now, we'll use a simplified approach that works with the current system
        # In a future iteration, we can improve this to extract context from the task description
        
        # Lazy-load services only when needed
        try:
            container = get_container()
            player_service = container.get_service(PlayerService)
        except Exception as e:
            logger.error(f"❌ Failed to get services from container: {e}")
            return "❌ Service temporarily unavailable. Please try again in a moment."
        
        # Parameters are now passed explicitly - no context extraction needed
        logger.info(f"🔧 get_my_status called with team_id: {team_id}, user_id: {user_id}")
        
        # Try to get player status
        try:
            result = player_service.get_my_status(user_id, team_id)
            logger.info(f"✅ Player status retrieved for user: {user_id} in team: {team_id}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to get player status: {e}")
            return f"❌ Failed to get player status: {e!s}"

    except Exception as e:
        logger.error(f"❌ Failed to get status: {e}")
        return f"❌ Failed to get status: {e!s}"


@tool("get_player_status")
def get_player_status(phone: str, team_id: str | None = None) -> str:
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
        player_service = container.get_service(PlayerService)
        result = player_service.get_player_status(phone, team_id)
        logger.info(f"✅ Player status retrieved for phone: {phone}")
        return result

    except Exception as e:
        logger.error(f"❌ Failed to get player status: {e}")
        return f"❌ Failed to get player status: {e!s}"


@tool("get_all_players")
def get_all_players(team_id: str) -> str:
    """
    Get players for the team. Uses context information from the task description.
    
    Returns:
        List of players or error message
    """
    try:
        # Lazy-load services only when needed
        try:
            container = get_container()
            player_service = container.get_service(PlayerService)
        except Exception as e:
            logger.error(f"❌ Failed to get PlayerService from container: {e}")
            return "❌ Service temporarily unavailable. Please try again in a moment."

        # Parameter is now passed explicitly - no context extraction needed
        logger.info(f"🔧 get_all_players called with team_id: {team_id}")
        
        # Get all players
        players = asyncio.run(player_service.get_all_players(team_id=team_id))
        if not players:
            return "📋 No players found in the team."
        
        # Group players by status
        active_players = [p for p in players if p.status == "active"]
        pending_players = [p for p in players if p.status == "pending"]
        inactive_players = [p for p in players if p.status == "inactive"]
        
        result = "📋 Team Players (All Statuses):\n\n"
        
        if active_players:
            result += "🟢 Active Players:\n"
            for player in sorted(active_players, key=lambda p: p.name or ""):
                result += f"• {player.player_id} - {player.name} ({player.position})\n"
            result += "\n"
        
        if pending_players:
            result += "🟡 Pending Players:\n"
            for player in sorted(pending_players, key=lambda p: p.name or ""):
                result += f"• {player.player_id} - {player.name} ({player.position})\n"
            result += "\n"
        
        if inactive_players:
            result += "🔴 Inactive Players:\n"
            for player in sorted(inactive_players, key=lambda p: p.name or ""):
                result += f"• {player.player_id} - {player.name} ({player.position})\n"
        
        return result

    except Exception as e:
        logger.error(f"❌ Failed to get players: {e}")
        return f"❌ Failed to get players: {e!s}"


@tool("get_match")
def get_match(match_id: str, team_id: str | None = None) -> str:
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
        return f"❌ Failed to get match info: {e!s}"


@tool("list_team_members_and_players")
def list_team_members_and_players(context: dict[str, Any] | None = None) -> str:
    """
    Comprehensive list tool for /list command. Shows team members and players based on chat context.
    Uses proper context parameter for team information.
    
    Args:
        context: Execution context containing team_id and other information
    
    Returns:
        Comprehensive list of team members and players based on chat context
    """
    try:
        # Extract team ID from context parameter
        team_id = None
        if context and isinstance(context, dict):
            team_id = context.get('team_id')
            logger.info(f"🔍 Extracted team_id from context: {team_id}")
        
        if not team_id or team_id == 'unknown':
            logger.error("❌ Team ID not found in context or is 'unknown'. Cannot proceed without valid team_id.")
            return "❌ Error: Team ID not available. Please try again or contact support."
        
        # Lazy-load services only when needed
        try:
            container = get_container()
            player_service = container.get_service(PlayerService)
            team_member_service = container.get_service(TeamMemberService)
        except Exception as e:
            logger.error(f"❌ Failed to get services from container: {e}")
            return "❌ Service temporarily unavailable. Please try again in a moment."
        
        # Get all players and team members
        players = asyncio.run(player_service.get_all_players(team_id=team_id))
        team_members = asyncio.run(team_member_service.get_team_members_by_team(team_id))
        
        result = f"📋 Team Overview for {team_id}:\n\n"
        
        # Team Members Section
        if team_members:
            result += "👥 Team Members:\n"
            for member in sorted(team_members, key=lambda m: m.full_name or m.first_name or ""):
                role_text = member.role if member.role else "No role"
                admin_status = "👑 Admin" if member.is_admin else "👤 Member"
                result += f"• {member.full_name or member.first_name or 'Unknown'} - {admin_status} ({role_text})\n"
            result += "\n"
        else:
            result += "👥 Team Members: None\n\n"
        
        # Players Section
        if players:
            # Group players by status
            active_players = [p for p in players if p.status == "active"]
            pending_players = [p for p in players if p.status == "pending"]
            inactive_players = [p for p in players if p.status == "inactive"]
            
            if active_players:
                result += "🟢 Active Players:\n"
                for player in sorted(active_players, key=lambda p: p.name or ""):
                    result += f"• {player.player_id} - {player.name} ({player.position})\n"
                result += "\n"
            
            if pending_players:
                result += "🟡 Pending Players:\n"
                for player in sorted(pending_players, key=lambda p: p.name or ""):
                    result += f"• {player.player_id} - {player.name} ({player.position})\n"
                result += "\n"
            
            if inactive_players:
                result += "🔴 Inactive Players:\n"
                for player in sorted(inactive_players, key=lambda p: p.name or ""):
                    result += f"• {player.player_id} - {player.name} ({player.position})\n"
        else:
            result += "📋 Players: None\n"
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to get comprehensive list: {e}")
        return f"❌ Failed to get comprehensive list: {e!s}"


# Note: Removed unused tools: remove_player, get_player_info, list_players
# These tools are not assigned to any agents in the configuration
