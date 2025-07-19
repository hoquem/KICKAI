"""
Player management tools for KICKAI system.

This module provides tools for player management, approval, and information retrieval.
"""

import logging
from typing import Optional, List
from pydantic import BaseModel

from crewai.tools import tool
from features.player_registration.domain.services.player_service import PlayerService
from core.dependency_container import get_container

logger = logging.getLogger(__name__)


class RegisterPlayerInput(BaseModel):
    """Input model for register_player tool."""
    player_name: str
    phone_number: str
    position: str
    team_id: Optional[str] = None


class ApprovePlayerInput(BaseModel):
    """Input model for approve_player tool."""
    player_id: str
    team_id: Optional[str] = None


class GetPlayerInfoInput(BaseModel):
    """Input model for get_player_info tool."""
    player_id: str
    team_id: Optional[str] = None


class ListPlayersInput(BaseModel):
    """Input model for list_players tool."""
    team_id: Optional[str] = None
    status: Optional[str] = None


class RemovePlayerInput(BaseModel):
    """Input model for remove_player tool."""
    player_id: str
    team_id: Optional[str] = None


class GetPlayerStatusInput(BaseModel):
    """Input model for get_player_status tool."""
    phone_number: str
    team_id: Optional[str] = None


class GetUserStatusInput(BaseModel):
    """Input model for get_user_status tool."""
    user_id: str
    team_id: Optional[str] = None


@tool("register_player")
def register_player(player_name: str, phone_number: str, position: str, team_id: Optional[str] = None) -> str:
    """
    Register a new player. Requires: player_name, phone_number, position
    
    Args:
        player_name: The name of the player to register
        phone_number: The player's phone number
        position: The player's position
        team_id: Optional team ID for context
    
    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Register the player
        player = player_service.register_player(player_name, phone_number, position, team_id)
        
        if player:
            logger.info(f"✅ Player registered: {player_name} ({position})")
            return f"✅ Player registered successfully: {player_name} ({position})"
        else:
            logger.error(f"❌ Failed to register player: {player_name}")
            return f"❌ Failed to register player: {player_name}"
        
    except Exception as e:
        logger.error(f"❌ Failed to register player: {e}")
        return f"❌ Failed to register player: {str(e)}"


@tool("approve_player")
def approve_player(player_id: str, team_id: Optional[str] = None) -> str:
    """
    Approve a player for match squad selection. Requires: player_id
    
    Args:
        player_id: The player ID to approve
        team_id: Optional team ID for context
    
    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Approve the player
        result = player_service.approve_player(player_id, team_id)
        
        if result:
            logger.info(f"✅ Player approved: {player_id}")
            return f"✅ Player {player_id} approved successfully"
        else:
            logger.error(f"❌ Failed to approve player: {player_id}")
            return f"❌ Failed to approve player: {player_id}"
        
    except Exception as e:
        logger.error(f"❌ Failed to approve player: {e}")
        return f"❌ Failed to approve player: {str(e)}"


@tool("get_player_info")
def get_player_info(player_id: str, team_id: Optional[str] = None) -> str:
    """
    Get information about a player. Requires: player_id
    
    Args:
        player_id: The player ID to get information for
        team_id: Optional team ID for context
    
    Returns:
        Player information or error message
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Get player info
        player_info = player_service.get_player_info(player_id, team_id)
        
        if player_info:
            logger.info(f"✅ Player info retrieved: {player_id}")
            return f"✅ Player info: {player_info}"
        else:
            logger.warning(f"⚠️ Player not found: {player_id}")
            return f"⚠️ Player {player_id} not found"
        
    except Exception as e:
        logger.error(f"❌ Failed to get player info: {e}")
        return f"❌ Failed to get player info: {str(e)}"


@tool("list_players")
def list_players(team_id: Optional[str] = None, status: Optional[str] = None) -> str:
    """
    List all players. Optional: team_id, status
    
    Args:
        team_id: Optional team ID to filter by
        status: Optional status to filter by (active, pending, etc.)
    
    Returns:
        List of players or error message
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # List players
        players = player_service.list_players(team_id, status)
        
        if players:
            logger.info(f"✅ Listed {len(players)} players")
            return f"✅ Players: {players}"
        else:
            logger.info("ℹ️ No players found")
            return "ℹ️ No players found"
        
    except Exception as e:
        logger.error(f"❌ Failed to list players: {e}")
        return f"❌ Failed to list players: {str(e)}"


@tool("remove_player")
def remove_player(player_id: str, team_id: Optional[str] = None) -> str:
    """
    Remove a player from the team. Requires: player_id
    
    Args:
        player_id: The player ID to remove
        team_id: Optional team ID for context
    
    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Remove the player
        result = player_service.remove_player(player_id, team_id)
        
        if result:
            logger.info(f"✅ Player removed: {player_id}")
            return f"✅ Player {player_id} removed successfully"
        else:
            logger.error(f"❌ Failed to remove player: {player_id}")
            return f"❌ Failed to remove player: {player_id}"
        
    except Exception as e:
        logger.error(f"❌ Failed to remove player: {e}")
        return f"❌ Failed to remove player: {str(e)}"


@tool("get_my_status")
def get_my_status(user_id: str, team_id: Optional[str] = None) -> str:
    """
    Get the current user's status. Requires: user_id
    
    Args:
        user_id: The user ID to get status for
        team_id: Optional team ID for context
    
    Returns:
        User status information or error message
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Get user status
        status = player_service.get_user_status(user_id, team_id)
        
        if status:
            logger.info(f"✅ User status retrieved: {user_id}")
            return f"✅ Your status: {status}"
        else:
            logger.warning(f"⚠️ User not found: {user_id}")
            return f"⚠️ User {user_id} not found"
        
    except Exception as e:
        logger.error(f"❌ Failed to get user status: {e}")
        return f"❌ Failed to get user status: {str(e)}"


@tool("get_player_status")
def get_player_status(phone_number: str, team_id: Optional[str] = None) -> str:
    """
    Get player status by phone number. Requires: phone_number
    
    Args:
        phone_number: The phone number to look up
        team_id: Optional team ID for context
    
    Returns:
        Player status information or error message
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Get player status by phone
        status = player_service.get_player_status_by_phone(phone_number, team_id)
        
        if status:
            logger.info(f"✅ Player status retrieved for phone: {phone_number}")
            return f"✅ Player status: {status}"
        else:
            logger.warning(f"⚠️ Player not found for phone: {phone_number}")
            return f"⚠️ Player not found for phone: {phone_number}"
        
    except Exception as e:
        logger.error(f"❌ Failed to get player status: {e}")
        return f"❌ Failed to get player status: {str(e)}"


@tool("get_all_players")
def get_all_players(team_id: Optional[str] = None) -> str:
    """
    Get all players for a team. Optional: team_id
    
    Args:
        team_id: Optional team ID to filter by
    
    Returns:
        List of all players or error message
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Get all players
        players = player_service.get_all_players(team_id)
        
        if players:
            logger.info(f"✅ Retrieved {len(players)} players")
            return f"✅ All players: {players}"
        else:
            logger.info("ℹ️ No players found")
            return "ℹ️ No players found"
        
    except Exception as e:
        logger.error(f"❌ Failed to get all players: {e}")
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


@tool("get_user_status")
def get_user_status(user_id: str, team_id: Optional[str] = None) -> str:
    """
    Get user status information. Requires: user_id
    
    Args:
        user_id: The user ID to get status for
        team_id: Optional team ID for context
    
    Returns:
        User status information or error message
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"
        
        # Get user status
        status = player_service.get_user_status(user_id, team_id)
        
        if status:
            logger.info(f"✅ User status retrieved: {user_id}")
            return f"✅ User status: {status}"
        else:
            logger.warning(f"⚠️ User not found: {user_id}")
            return f"⚠️ User {user_id} not found"
        
    except Exception as e:
        logger.error(f"❌ Failed to get user status: {e}")
        return f"❌ Failed to get user status: {str(e)}"


@tool("get_available_commands")
def get_available_commands(user_id: str, team_id: Optional[str] = None) -> str:
    """
    Get available commands for the user. Requires: user_id
    
    Args:
        user_id: The user ID to get commands for
        team_id: Optional team ID for context
    
    Returns:
        List of available commands or error message
    """
    try:
        # This would check user permissions and return appropriate commands
        commands = [
            "/help - Get help information",
            "/myinfo - Get your player information",
            "/list - List all players",
            "/status [phone] - Check player status by phone number"
        ]
        
        logger.info(f"✅ Available commands retrieved for user: {user_id}")
        return f"✅ Available commands:\n" + "\n".join(commands)
        
    except Exception as e:
        logger.error(f"❌ Failed to get available commands: {e}")
        return f"❌ Failed to get available commands: {str(e)}"


@tool("format_help_message")
def format_help_message(command: Optional[str] = None, team_id: Optional[str] = None) -> str:
    """
    Format a help message. Optional: command
    
    Args:
        command: Optional specific command to get help for
        team_id: Optional team ID for context
    
    Returns:
        Formatted help message
    """
    try:
        if command:
            # Return specific command help
            help_text = f"📖 Help for /{command}:\n\n"
            if command == "help":
                help_text += "Get help information for available commands."
            elif command == "myinfo":
                help_text += "Get your player information and status."
            elif command == "list":
                help_text += "List all players in the team."
            elif command == "status":
                help_text += "Check player status by phone number. Usage: /status [phone]"
            else:
                help_text += f"Help information for /{command} not available."
        else:
            # Return general help
            help_text = (
                "🤖 *KICKAI Bot Help*\n\n"
                "📋 *Available Commands:*\n"
                "• /help - Get this help message\n"
                "• /myinfo - Get your player information\n"
                "• /list - List all players\n"
                "• /status [phone] - Check player status by phone number\n\n"
                "💡 *Need more help?* Contact the team leadership."
            )
        
        logger.info(f"✅ Help message formatted for command: {command}")
        return help_text
        
    except Exception as e:
        logger.error(f"❌ Failed to format help message: {e}")
        return f"❌ Failed to format help message: {str(e)}" 