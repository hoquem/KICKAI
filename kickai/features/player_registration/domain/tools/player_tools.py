"""
Player management tools for KICKAI system.

This module provides tools for player management, approval, and information retrieval.
"""

import asyncio
import logging

from crewai.tools import tool
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.interfaces.team_service_interface import ITeamService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService

logger = logging.getLogger(__name__)


class ApprovePlayerInput(BaseModel):
    """Input model for approve_player tool."""
    player_id: str
    team_id: str | None = None


class GetPlayerStatusInput(BaseModel):
    """Input model for get_player_status tool."""
    player_id: str
    team_id: str | None = None


class AddPlayerInput(BaseModel):
    """Input model for add_player tool."""
    name: str
    phone: str
    position: str
    team_id: str | None = None


class GetMatchInput(BaseModel):
    """Input model for get_match tool."""
    match_id: str


@tool("add_player")
def add_player(name: str, phone: str, position: str, team_id: str | None = None) -> str:
    """
    Add a new player to the team with invite link. Requires: name, phone, position

    Args:
        name: The name of the player to add
        phone: The player's phone number
        position: The player's position
        team_id: Optional team ID for context

    Returns:
        Player information and invite link, or existing player info if already exists
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            logger.error("❌ PlayerService not available")
            return "❌ Player service not available"

        # Normalize phone number
        from kickai.utils.phone_utils import normalize_phone
        normalized_phone = normalize_phone(phone)

        # Check if player already exists
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        existing_player = loop.run_until_complete(
            player_service.get_player_by_phone(phone=normalized_phone, team_id=team_id or "KAI")
        )

        if existing_player:
            # Player exists - return existing info + new invite link
            logger.info(f"ℹ️ Player already exists: {name} ({position})")

            # Generate new invite link for existing player
            from kickai.core.settings import get_settings
            from kickai.features.communication.domain.services.invite_link_service import (
                InviteLinkService,
            )

            invite_service = container.get_service(InviteLinkService)
            
            # Get team to access bot configuration
            team_service = container.get_service(ITeamService)
            team = loop.run_until_complete(team_service.get_team(team_id or "KAI"))
            if not team or not team.main_chat_id:
                return "❌ Team not found or no main chat configured"

            invite_result = loop.run_until_complete(
                invite_service.create_player_invite_link(
                    team_id=team_id or "KAI",
                    player_name=existing_player.name,
                    player_phone=existing_player.phone,
                    player_position=existing_player.position,
                    main_chat_id=team.main_chat_id
                )
            )

            return f"""ℹ️ Player Already Exists

👤 Existing Player Details:
• Name: {existing_player.name}
• Phone: {existing_player.phone}
• Position: {existing_player.position}
• Player ID: {existing_player.player_id or 'Not assigned'}
• Status: {existing_player.status.title()}

🔗 New Invite Link for Main Chat:
{invite_result['invite_link']}

💡 Note: This invite link is unique, expires in 7 days, and can only be used once."""

        # Add new player
        success, result = loop.run_until_complete(
            player_service.add_player(
                name=name,
                phone=normalized_phone,
                position=position,
                team_id=team_id or "KAI"
            )
        )

        if success:
            logger.info(f"✅ Player added: {name} ({position})")

            # Extract player ID from the result message
            player_id = None
            if "ID:" in result:
                player_id = result.split("ID:")[1].strip()

            # Generate invite link for new player
            from kickai.core.settings import get_settings
            from kickai.features.communication.domain.services.invite_link_service import (
                InviteLinkService,
            )

            invite_service = container.get_service(InviteLinkService)
            
            # Get team to access bot configuration
            team_service = container.get_service(ITeamService)
            team = loop.run_until_complete(team_service.get_team(team_id or "KAI"))
            if not team or not team.main_chat_id:
                return "❌ Team not found or no main chat configured"

            invite_result = loop.run_until_complete(
                invite_service.create_player_invite_link(
                    team_id=team_id or "KAI",
                    player_name=name,
                    player_phone=normalized_phone,
                    player_position=position,
                    main_chat_id=team.main_chat_id,
                    player_id=player_id  # Pass the extracted player ID
                )
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

    except Exception as e:
        logger.error(f"❌ Failed to add player: {e}")
        return f"❌ Failed to add player: {e!s}"


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
def list_team_members_and_players(team_id: str) -> str:
    """
    Comprehensive list tool for /list command. Shows team members and players for a specific team.

    Args:
        team_id: The team ID to list members and players for

    Returns:
        Comprehensive list of team members and players for the specified team
    """
    try:
        logger.info(f"🔍 Listing team members and players for team: {team_id}")

        if not team_id or team_id == 'unknown':
            logger.error("❌ Invalid team_id provided. Cannot proceed without valid team_id.")
            return "❌ Error: Invalid team ID provided. Please try again or contact support."

        # Lazy-load services only when needed
        try:
            container = get_container()
            player_service = container.get_service(PlayerService)
            team_member_service = container.get_service(TeamMemberService) # Assuming TeamMemberService is still needed
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
