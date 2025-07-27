#!/usr/bin/env python3
"""
Player Tools

This module provides tools for player management operations.
"""



from crewai.tools import tool
from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.constants import (
    DEFAULT_PLAYER_POSITION,
    ERROR_MESSAGES,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_POSITION_LENGTH,
    MAX_TEAM_ID_LENGTH,
    MAX_USER_ID_LENGTH,
)
from kickai.utils.tool_helpers import (
    extract_single_value,
    format_tool_error,
    sanitize_input,
    validate_required_input,
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
async def add_player(
    team_id: str, user_id: str, name: str, phone: str, position: str | None = None
) -> str:
    """
    Add a new player to the team with simplified ID generation.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        name: Player's full name
        phone: Player's phone number
        position: Player's position (optional, can be set later)

    Returns:
        Success message with invite link or error
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Simplified validation - only name and phone required
        if not name or not name.strip():
            return format_tool_error(ERROR_MESSAGES["NAME_REQUIRED"])

        if not phone or not phone.strip():
            return format_tool_error(ERROR_MESSAGES["PHONE_REQUIRED"])

        # Sanitize inputs
        name = sanitize_input(name, max_length=MAX_NAME_LENGTH)
        phone = sanitize_input(phone, max_length=MAX_PHONE_LENGTH)
        position = (
            sanitize_input(position, max_length=MAX_POSITION_LENGTH)
            if position
            else DEFAULT_PLAYER_POSITION
        )
        team_id = sanitize_input(team_id, max_length=MAX_TEAM_ID_LENGTH)
        user_id = sanitize_input(user_id, max_length=MAX_USER_ID_LENGTH)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError(
                ERROR_MESSAGES["SERVICE_UNAVAILABLE"].format(service="PlayerService")
            )

        # Add player with simplified ID generation
        success, message = await player_service.add_player(name, phone, position, team_id)

        if success:
            # Extract player ID from message
            import re

            player_id_match = re.search(r"ID: (\w+)", message)
            player_id = player_id_match.group(1) if player_id_match else "Unknown"

            # Create invite link
            invite_service = container.get_service(InviteLinkService)
            if invite_service:
                try:
                    # Get team configuration for main chat ID
                    team_service = container.get_service(TeamService)
                    team = await team_service.get_team(team_id=team_id)

                    if team and team.main_chat_id:
                        invite_result = await invite_service.create_player_invite_link(
                            team_id=team_id,
                            player_name=name,
                            player_phone=phone,
                            player_position=position,
                            main_chat_id=team.main_chat_id,
                            player_id=player_id,
                        )

                        return f"""✅ Player Added Successfully!

👤 Player Details:
• Name: {name}
• Phone: {phone}
• Position: {position}
• Player ID: {player_id}
• Status: Pending Approval

🔗 Invite Link for Main Chat:
{invite_result['invite_link']}

📋 Next Steps:
1. Share this invite link with {name}
2. They can join the main chat using the link
3. Once they join, they can register with /register
4. Use /approve to approve and activate their registration

🔒 Security:
• Link expires in 7 days
• One-time use only
• Automatically tracked in system

💡 Tip: The player will need to register with /register after joining the chat."""
                    else:
                        return f"""✅ Player Added Successfully!

👤 Player Details:
• Name: {name}
• Phone: {phone}
• Position: {position}
• Player ID: {player_id}
• Status: Pending Approval

⚠️ Note: Could not generate invite link - team configuration incomplete.
Please contact the system administrator."""
                except Exception as e:
                    logger.error(f"Error creating invite link: {e}")
                    return f"""✅ Player Added Successfully!

👤 Player Details:
• Name: {name}
• Phone: {phone}
• Position: {position}
• Player ID: {player_id}
• Status: Pending Approval

⚠️ Note: Could not generate invite link due to system error.
Please contact the system administrator."""
            else:
                return f"""✅ Player Added Successfully!

👤 Player Details:
• Name: {name}
• Phone: {phone}
• Position: {position}
• Player ID: {player_id}
• Status: Pending Approval

⚠️ Note: Could not generate invite link - invite service unavailable.
Please contact the system administrator."""
        else:
            return format_tool_error(f"Failed to add player: {message}")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in add_player: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to add player: {e}", exc_info=True)
        return format_tool_error(f"Failed to add player: {e}")


@tool("approve_player")
async def approve_player(team_id: str, user_id: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        player_id: The player ID to approve

    Returns:
        Success message or error
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(player_id, "Player ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        player_id = sanitize_input(player_id, max_length=20)
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Approve player
        result = await player_service.approve_player(player_id, team_id)

        # Check if result indicates success (starts with ✅)
        if result.startswith("✅"):
            # Extract player name from the result string
            # Expected format: "✅ Player {name} approved and activated successfully"
            try:
                player_name = result.split("Player ")[1].split(" approved")[0]
            except (IndexError, AttributeError):
                player_name = "Unknown"

            return f"""✅ Player Approved and Activated Successfully!

👤 Player Details:
• Name: {player_name}
• Player ID: {player_id}
• Status: Active

🎉 The player is now approved, activated, and can participate in team activities."""
        else:
            # Result contains error message
            return format_tool_error(f"Failed to approve player: {result}")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in approve_player: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to approve player: {e}", exc_info=True)
        return format_tool_error(f"Failed to approve player: {e}")


@tool("get_my_status")
async def get_my_status(team_id: str, user_id: str) -> str:
    """
    Get the current status of the requesting user.

    This tool requires team_id and user_id parameters which should be provided from the available context.

    Args:
        team_id: Team ID from the available context parameters
        user_id: User ID (telegram user ID) from the available context parameters

    Returns:
        User's current status or error message

    Example:
        If context provides "team_id: TEST, user_id: 12345",
        call this tool with team_id="TEST" and user_id="12345"
    """
    try:
        # Validate inputs - these should NOT be None, they must come from context
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return format_tool_error(
                "Team ID is required and must be provided from available context"
            )

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return format_tool_error(
                "User ID is required and must be provided from available context"
            )

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get player status
        player = await player_service.get_player_by_telegram_id(user_id, team_id)

        if not player:
            return format_tool_error(f"Player not found for user ID {user_id} in team {team_id}")

        # Format response
        status_emoji = "✅" if player.status.lower() == "active" else "⏳"
        status_text = player.status.title()

        result = f"""👤 Player Information

Name: {player.full_name}
Position: {player.position}
Status: {status_emoji} {status_text}
Player ID: {player.player_id or 'Not assigned'}
Phone: {player.phone_number or 'Not provided'}"""

        if player.status.lower() == "pending":
            result += "\n\n⏳ Note: Your registration is pending approval by team leadership."

        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_my_status: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get player status: {e}", exc_info=True)
        return format_tool_error(f"Failed to get player status: {e}")


@tool("get_player_status")
async def get_player_status(team_id: str, user_id: str, phone: str) -> str:
    """
    Get player status by phone number.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        phone: The player's phone number

    Returns:
        Player status or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(phone, "Phone")
        if validation_error:
            return validation_error

        # Sanitize inputs
        phone = sanitize_input(phone, max_length=20)
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get player status
        player = await player_service.get_player_by_phone(phone, team_id)

        if not player:
            return format_tool_error(f"Player not found for phone {phone} in team {team_id}")

        # Format response
        status_emoji = "✅" if player.status.lower() == "active" else "⏳"
        status_text = player.status.title()

        result = f"""👤 Player Status

Name: {player.full_name}
Position: {player.position}
Status: {status_emoji} {status_text}
Player ID: {player.player_id or 'Not assigned'}
Phone: {player.phone_number or 'Not provided'}"""

        if player.status.lower() == "pending":
            result += (
                "\n\n⏳ Note: This player's registration is pending approval by team leadership."
            )

        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_player_status: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get player status: {e}", exc_info=True)
        return format_tool_error(f"Failed to get player status: {e}")


@tool("get_all_players")
async def get_all_players(team_id: str, user_id: str) -> str:
    """
    Get all players in the team.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context

    Returns:
        List of all players or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get all players
        players = await player_service.get_all_players(team_id)

        if not players:
            return "📋 No players found in the team."

        # Format response
        result = "📋 All Players in Team\n\n"

        for player in players:
            status_emoji = "✅" if player.status.lower() == "active" else "⏳"
            result += f"{status_emoji} **{player.full_name}**\n"
            result += f"   • Position: {player.position}\n"
            result += f"   • Status: {player.status.title()}\n"
            result += f"   • Player ID: {player.player_id or 'Not assigned'}\n"
            result += f"   • Phone: {player.phone_number or 'Not provided'}\n\n"

        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_all_players: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get all players: {e}", exc_info=True)
        return format_tool_error(f"Failed to get all players: {e}")


@tool("get_active_players")
async def get_active_players(team_id: str, user_id: str) -> str:
    """
    Get all active players in the team.

    🚨 CRITICAL: This tool output MUST NEVER be modified by the agent.
    The agent MUST return this output exactly as received - NO additions, NO modifications.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context

    Returns:
        List of active players or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)

        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        # Get active players
        players = await player_service.get_active_players(team_id)

        if not players:
            return "📋 No active players found in the team."

        # Format response
        result = "✅ Active Players in Team\n\n"

        for player in players:
            result += f"👤 {player.full_name}\n"
            result += f"   • Position: {player.position}\n"
            result += f"   • Player ID: {player.player_id or 'Not assigned'}\n"
            result += f"   • Phone: {player.phone_number or 'Not provided'}\n\n"

        # 🚨 CRITICAL: This exact output must be returned by the agent without any modifications
        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_active_players: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get active players: {e}", exc_info=True)
        return format_tool_error(f"Failed to get active players: {e}")


def validate_tool_output_integrity(original_output: str, agent_response: str) -> bool:
    """
    Validate that the agent response matches the original tool output exactly.

    Args:
        original_output: The original tool output
        agent_response: The agent's response

    Returns:
        True if the outputs match exactly, False otherwise
    """
    # Remove any leading/trailing whitespace for comparison
    original_clean = original_output.strip()
    agent_clean = agent_response.strip()

    # Check for exact match
    if original_clean == agent_clean:
        return True

    # Log the difference for debugging
    logger.warning("Tool output integrity check failed:")
    logger.warning(f"Original: {original_clean!r}")
    logger.warning(f"Agent: {agent_clean!r}")

    return False


@tool("get_match")
async def get_match(match_id: str, team_id: str) -> str:
    """
    Get match details by match ID. Requires: match_id, team_id

    Args:
        match_id: The match ID to retrieve
        team_id: Team ID (required)

    Returns:
        Match details or error message
    """
    try:
        # Handle JSON string input using utility functions
        match_id = extract_single_value(match_id, "match_id")
        team_id = extract_single_value(team_id, "team_id")

        # Validate inputs using utility functions
        validation_error = validate_required_input(match_id, "Match ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        match_id = sanitize_input(match_id, max_length=20)
        team_id = sanitize_input(team_id, max_length=20)

        # Get services from container
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            raise ServiceNotAvailableError("MatchService")

        # Get match details
        match = await match_service.get_match(match_id, team_id)

        if not match:
            return format_tool_error(f"Match {match_id} not found in team {team_id}")

        # Format match details
        return f"""📋 Match Details

🏆 Match ID: {match.get('match_id', 'N/A')}
📅 Date: {match.get('date', 'N/A')}
⏰ Time: {match.get('time', 'N/A')}
📍 Location: {match.get('location', 'N/A')}
👥 Opponent: {match.get('opponent', 'N/A')}
📊 Status: {match.get('status', 'N/A')}"""

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_match: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to get match: {e}", exc_info=True)
        return format_tool_error(f"Failed to get match: {e}")


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
        # Handle JSON string input using utility functions
        team_id = extract_single_value(team_id, "team_id")

        # Validate input using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        # Sanitize input
        team_id = sanitize_input(team_id, max_length=20)

        # Get services from container
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service("TeamService")  # Assuming TeamService is available

        if not player_service:
            raise ServiceNotAvailableError("PlayerService")

        if not team_service:
            raise ServiceNotAvailableError("TeamService")

        # Get players and team members
        players = await player_service.get_all_players(team_id)
        team_members = await team_service.get_team_members(team_id)

        result = f"📋 Team Overview for {team_id}\n\n"

        # Add team members section
        if team_members:
            result += "👔 Team Members:\n"
            for member in team_members:
                result += f"• {member.full_name} - {member.role.title()}\n"
            result += "\n"
        else:
            result += "👔 No team members found\n\n"

        # Add players section
        if players:
            result += "👥 Players:\n"
            for player in players:
                status_emoji = "✅" if player.status.lower() == "active" else "⏳"
                player_id_display = f" (ID: {player.player_id})" if player.player_id else ""
                result += f"• {player.full_name} - {player.position} {status_emoji} {player.status.title()}{player_id_display}\n"
        else:
            result += "👥 No players found"

        return result

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_team_members_and_players: {e}")
        return format_tool_error(f"Service temporarily unavailable: {e.message}")
    except Exception as e:
        logger.error(f"Failed to list team members and players: {e}", exc_info=True)
        return format_tool_error(f"Failed to list team members and players: {e}")
