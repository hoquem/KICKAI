#!/usr/bin/env python3
"""
Player Tools

This module provides tools for player management operations.
"""

import asyncio
from typing import Any

from crewai.tools import tool
from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import (
    PlayerAlreadyExistsError,
    PlayerValidationError,
    ServiceNotAvailableError,
    TeamNotFoundError,
    TeamNotConfiguredError,
)
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.interfaces.team_service_interface import ITeamService
from kickai.utils.validation_utils import (
    normalize_phone,
    sanitize_input,
    validate_player_input,
)


class AddPlayerInput(BaseModel):
    """Input model for add_player tool."""
    name: str
    phone: str
    position: str
    team_id: str


class ApprovePlayerInput(BaseModel):
    """Input model for approve_player tool."""
    player_id: str
    team_id: str


class GetPlayerStatusInput(BaseModel):
    """Input model for get_player_status tool."""
    player_id: str
    team_id: str


class GetMatchInput(BaseModel):
    """Input model for get_match tool."""
    match_id: str
    team_id: str


@tool("add_player")
async def add_player(name: str, phone: str, position: str, team_id: str) -> str:
    """
    Add a new player to the team with invite link. Requires: name, phone, position, team_id

    Args:
        name: The name of the player to add
        phone: The player's phone number
        position: The player's position
        team_id: Team ID (required)

    Returns:
        Player information and invite link, or existing player info if already exists
    """
    try:
        # Sanitize inputs to prevent injection attacks
        name = sanitize_input(name, max_length=100)
        phone = sanitize_input(phone, max_length=20)
        position = sanitize_input(position, max_length=50)
        team_id = sanitize_input(team_id, max_length=20)
        
        # Validate inputs
        validation_errors = validate_player_input(name, phone, position, team_id)
        if validation_errors:
            raise PlayerValidationError(validation_errors)
        
        # Normalize phone number
        normalized_phone = normalize_phone(phone)
        
        # Get services from container
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service(ITeamService)
        
        if not player_service:
            raise ServiceNotAvailableError("PlayerService")
        
        if not team_service:
            raise ServiceNotAvailableError("TeamService")
        
        # Check if player already exists
        existing_player = await player_service.get_player_by_phone(
            phone=normalized_phone, team_id=team_id
        )
        
        if existing_player:
            # Player exists - return existing info + new invite link
            logger.info(f"ℹ️ Player already exists: {name} ({position})")
            
            # Generate new invite link for existing player
            from kickai.features.communication.domain.services.invite_link_service import (
                InviteLinkService,
            )
            
            invite_service = container.get_service(InviteLinkService)
            if not invite_service:
                raise ServiceNotAvailableError("InviteLinkService")
            
            # Get team to access bot configuration
            team = await team_service.get_team(team_id=team_id)
            if not team:
                raise TeamNotFoundError(team_id)
            
            if not team.main_chat_id:
                raise TeamNotConfiguredError(team_id, "main_chat_id")
            
            invite_result = await invite_service.create_player_invite_link(
                team_id=team_id,
                player_name=existing_player.full_name,
                player_phone=existing_player.phone_number,
                player_position=existing_player.position,
                main_chat_id=team.main_chat_id
            )
            
            return f"""ℹ️ Player Already Exists

👤 Existing Player Details:
• Name: {existing_player.full_name}
• Phone: {existing_player.phone_number}
• Position: {existing_player.position}
• Player ID: {existing_player.player_id or 'Not assigned'}
• Status: {existing_player.status.title()}

🔗 New Invite Link for Main Chat:
{invite_result['invite_link']}

💡 Note: This invite link is unique, expires in 7 days, and can only be used once."""
        
        # Add new player
        success, result = await player_service.add_player(
            name=name,
            phone=normalized_phone,
            position=position,
            team_id=team_id
        )
        
        if success:
            logger.info(f"✅ Player added: {name} ({position})")
            
            # Extract player ID from the result message
            player_id = None
            if "ID:" in result:
                player_id = result.split("ID:")[1].strip()
            
            # Generate invite link for new player
            from kickai.features.communication.domain.services.invite_link_service import (
                InviteLinkService,
            )
            
            invite_service = container.get_service(InviteLinkService)
            if not invite_service:
                raise ServiceNotAvailableError("InviteLinkService")
            
            # Get team to access bot configuration
            team = await team_service.get_team(team_id=team_id)
            if not team:
                raise TeamNotFoundError(team_id)
            
            if not team.main_chat_id:
                raise TeamNotConfiguredError(team_id, "main_chat_id")
            
            invite_result = await invite_service.create_player_invite_link(
                team_id=team_id,
                player_name=name,
                player_phone=normalized_phone,
                player_position=position,
                main_chat_id=team.main_chat_id,
                player_id=player_id  # Pass the extracted player ID
            )
            
            return f"""✅ Player Added Successfully!

👤 Player Details:
• Name: {name}
• Phone: {normalized_phone}
• Position: {position}
• Status: Pending Approval

🔗 Unique Invite Link for Main Chat:
{invite_result['invite_link']}

📋 Next Steps:
1. Send the invite link to {name}
2. Ask them to join the main chat
3. They can then use /register to complete their profile
4. Use /approve [player_id] to approve them once registered

💡 Note: This invite link is unique, expires in 7 days, and can only be used once."""
        else:
            logger.error(f"❌ Failed to add player: {name}")
            return f"❌ Failed to add player: {name}\n\n{result}"
    
    except PlayerValidationError as e:
        logger.warning(f"Validation error in add_player: {e}")
        return f"❌ Invalid input: {e.message}"
    except PlayerAlreadyExistsError:
        # This should be handled above, but just in case
        return "ℹ️ Player already exists. Generating new invite link..."
    except TeamNotFoundError as e:
        logger.error(f"Team not found in add_player: {e}")
        return f"❌ Team not found: {e.message}"
    except TeamNotConfiguredError as e:
        logger.error(f"Team not configured in add_player: {e}")
        return f"❌ Team not configured: {e.message}"
    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in add_player: {e}")
        return f"❌ Service temporarily unavailable: {e.message}"
    except Exception as e:
        logger.error(f"Unexpected error in add_player: {e}", exc_info=True)
        return "❌ System error. Please try again later."


@tool("approve_player")
async def approve_player(player_id: str, team_id: str) -> str:
    """
    Approve a player for team participation. Requires: player_id, team_id

    Args:
        player_id: The player ID to approve
        team_id: Team ID for context

    Returns:
        Approval status or error message
    """
    try:
        # Sanitize inputs
        player_id = sanitize_input(player_id, max_length=50)
        team_id = sanitize_input(team_id, max_length=20)
        
        # Validate team_id
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
        
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            raise ServiceNotAvailableError("PlayerService")
        
        result = await player_service.approve_player(player_id, team_id)
        logger.info(f"✅ Player approved: {player_id}")
        return result
    
    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in approve_player: {e}")
        return f"❌ Service temporarily unavailable: {e.message}"
    except Exception as e:
        logger.error(f"Failed to approve player: {e}", exc_info=True)
        return f"❌ Failed to approve player: {e}"


@tool("get_my_status")
async def get_my_status(team_id: str, user_id: str) -> str:
    """
    Get current user's player status and information. 
    This tool is for players in the main chat.
    For team members in leadership chat, use get_my_team_member_status.
    Uses context information from the task description.

    Returns:
        User's player status and information
    """
    try:
        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=50)
        
        # Validate inputs
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
        
        if not user_id or not user_id.strip():
            return "❌ User ID is required"
        
        # Get services from container
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            raise ServiceNotAvailableError("PlayerService")
        
        logger.info(f"🔧 get_my_status called with team_id: {team_id}, user_id: {user_id}")
        
        # Get player status
        player = await player_service.get_player_by_user_id(user_id, team_id)
        
        if not player:
            return f"""👋 Welcome to KICKAI! 

I don't see your registration in our system yet. No worries - let's get you set up to join the team! 

📞 Contact Team Leadership
You need to be added as a player by someone in the team's leadership.

💡 What to do:
1. Reach out to someone in the team's leadership chat
2. Ask them to add you as a player using the /addplayer command
3. They'll send you an invite link to join the main chat
4. Once added, you can register with your full details

🔗 Need Help?
Contact the team admin in the leadership chat."""
        
        # Format player status
        status_emoji = {
            "active": "✅",
            "pending": "⏳",
            "inactive": "❌",
            "suspended": "🚫"
        }.get(player.status.lower(), "❓")
        
        return f"""👤 Your Player Information

{status_emoji} Status: {player.status.title()}
📝 Name: {player.full_name}
📱 Phone: {player.phone_number}
⚽️ Position: {player.position}
🆔 Player ID: {player.player_id or 'Not assigned'}
🏢 Team: {player.team_id}

💬 Need Help?
Contact the team admin in the leadership chat."""
    
    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_my_status: {e}")
        return f"❌ Service temporarily unavailable: {e.message}"
    except Exception as e:
        logger.error(f"Error in get_my_status: {e}", exc_info=True)
        return "❌ System error. Please try again later."


@tool("get_player_status")
async def get_player_status(phone: str, team_id: str) -> str:
    """
    Get player status by phone number. Requires: phone, team_id

    Args:
        phone: The player's phone number
        team_id: Team ID for context

    Returns:
        Player status or error message
    """
    try:
        # Sanitize inputs
        phone = sanitize_input(phone, max_length=20)
        team_id = sanitize_input(team_id, max_length=20)
        
        # Validate inputs
        if not phone or not phone.strip():
            return "❌ Phone number is required"
        
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
        
        # Normalize phone number
        normalized_phone = normalize_phone(phone)
        
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            raise ServiceNotAvailableError("PlayerService")
        
        player = await player_service.get_player_by_phone(phone=normalized_phone, team_id=team_id)
        
        if not player:
            return f"❌ Player with phone {phone} not found in team {team_id}"
        
        # Format player status
        status_emoji = {
            "active": "✅",
            "pending": "⏳",
            "inactive": "❌",
            "suspended": "🚫"
        }.get(player.status.lower(), "❓")
        
        return f"""👤 Player Status

{status_emoji} Status: {player.status.title()}
📝 Name: {player.full_name}
📱 Phone: {player.phone_number}
⚽️ Position: {player.position}
🆔 Player ID: {player.player_id or 'Not assigned'}
🏢 Team: {player.team_id}"""
    
    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_player_status: {e}")
        return f"❌ Service temporarily unavailable: {e.message}"
    except Exception as e:
        logger.error(f"Failed to get player status: {e}", exc_info=True)
        return f"❌ Failed to get player status: {e}"


@tool("get_all_players")
async def get_all_players(team_id: str) -> str:
    """
    Get all players for a team. Requires: team_id

    Args:
        team_id: Team ID

    Returns:
        List of all players or error message
    """
    try:
        # Sanitize input
        team_id = sanitize_input(team_id, max_length=20)
        
        # Validate input
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
        
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        if not player_service:
            raise ServiceNotAvailableError("PlayerService")
        
        players = await player_service.get_all_players(team_id)
        
        if not players:
            return f"📋 No players found in team {team_id}"
        
        # Group players by status
        active_players = [p for p in players if p.status.lower() == "active"]
        pending_players = [p for p in players if p.status.lower() == "pending"]
        other_players = [p for p in players if p.status.lower() not in ["active", "pending"]]
        
        result = f"📋 Players for {team_id}\n\n"
        
        if active_players:
            result += "✅ Active Players:\n"
            for player in active_players:
                result += f"• {player.full_name} - {player.position} ({player.player_id or 'No ID'})\n"
            result += "\n"
        
        if pending_players:
            result += "⏳ Pending Approval:\n"
            for player in pending_players:
                result += f"• {player.full_name} - {player.position} ({player.player_id or 'No ID'})\n"
            result += "\n"
        
        if other_players:
            result += "❓ Other Status:\n"
            for player in other_players:
                result += f"• {player.full_name} - {player.position} ({player.status.title()})\n"
        
        return result
    
    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_all_players: {e}")
        return f"❌ Service temporarily unavailable: {e.message}"
    except Exception as e:
        logger.error(f"Failed to get all players: {e}", exc_info=True)
        return f"❌ Failed to get players: {e}"


@tool("get_match")
async def get_match(match_id: str, team_id: str) -> str:
    """
    Get match details. Requires: match_id, team_id

    Args:
        match_id: The match ID
        team_id: Team ID for context

    Returns:
        Match details or error message
    """
    try:
        # Sanitize inputs
        match_id = sanitize_input(match_id, max_length=50)
        team_id = sanitize_input(team_id, max_length=20)
        
        # Validate inputs
        if not match_id or not match_id.strip():
            return "❌ Match ID is required"
        
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
        
        container = get_container()
        match_service = container.get_service("MatchService")
        
        if not match_service:
            raise ServiceNotAvailableError("MatchService")
        
        match = await match_service.get_match(match_id)
        
        if not match:
            return f"❌ Match {match_id} not found"
        
        return f"""⚽️ Match Details

🏆 Match ID: {match.id}
🏠 Home Team: {match.home_team}
✈️ Away Team: {match.away_team}
📅 Date: {match.date}
📍 Location: {match.location or 'TBD'}
📊 Status: {match.status.value.title()}
🏆 Competition: {match.competition or 'Friendly'}"""
    
    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_match: {e}")
        return f"❌ Service temporarily unavailable: {e.message}"
    except Exception as e:
        logger.error(f"Failed to get match: {e}", exc_info=True)
        return f"❌ Failed to get match: {e}"


@tool("list_team_members_and_players")
async def list_team_members_and_players(team_id: str) -> str:
    """
    List all team members and players for a team. Requires: team_id

    Args:
        team_id: Team ID

    Returns:
        List of team members and players or error message
    """
    try:
        # Sanitize input
        team_id = sanitize_input(team_id, max_length=20)
        
        # Validate input
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
        
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service(ITeamService)
        
        if not player_service:
            raise ServiceNotAvailableError("PlayerService")
        
        if not team_service:
            raise ServiceNotAvailableError("TeamService")
        
        # Get team members and players
        team_members = await team_service.get_team_members(team_id)
        players = await player_service.get_all_players(team_id)
        
        result = f"👥 Team Members for {team_id}\n\n"
        
        if team_members:
            for member in team_members:
                role_emoji = "👑" if member.role.lower() in ["admin", "administrator"] else "⚽️"
                result += f"• {member.full_name} - {role_emoji} {member.role}\n"
        else:
            result += "📋 No team members found.\n"
        
        result += "\n"
        
        if players:
            active_players = [p for p in players if p.status.lower() == "active"]
            if active_players:
                result += "✅ Active Players:\n"
                for player in active_players:
                    result += f"• {player.full_name} - {player.position}\n"
            else:
                result += "📋 No active players found in the team.\n"
        else:
            result += "📋 No players found in the team.\n"
        
        return result
    
    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_team_members_and_players: {e}")
        return f"❌ Service temporarily unavailable: {e.message}"
    except Exception as e:
        logger.error(f"Failed to list team members and players: {e}", exc_info=True)
        return f"❌ Failed to list team members and players: {e}"
