#!/usr/bin/env python3
"""
Player Registration Tools - Clean Architecture Application Layer

This module provides CrewAI tools for player registration functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.utils.native_crewai_helpers import (
    format_safe_response,
    sanitize_list_response,
    validate_required_strings,
)


@tool("approve_player")
async def approve_player(
    telegram_id: str, team_id: str, player_id: str, telegram_username: str, chat_type: str
) -> str:
    """Activate player for match participation.

    Grants player eligibility for squad selection and team activities,
    completing the registration and verification process.

    Use when: Player registration verification is complete
    Required: Leadership privileges and valid player record

    Returns: Player activation confirmation
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            team_id, player_id, names=["team_id", "player_id"]
        )
        if validation_error:
            return validation_error

        # Sanitize inputs
        player_id = player_id.strip()
        team_id = team_id.strip()
        username = telegram_username or "unknown user"

        logger.info(
            f"🎯 Player approval request for {player_id} "
            f"from {username} ({telegram_id}) in team {team_id}"
        )

        # Get domain service and execute operation
        container = get_container()
        player_service = container.get_service(PlayerService)

        result = await player_service.approve_player(player_id, team_id)

        if result:
            logger.info(f"✅ Player {player_id} approved successfully by {username}")
            return f"✅ Player {player_id} approved successfully"
        else:
            logger.warning(
                f"❌ Failed to approve player {player_id} - may not exist or already approved"
            )
            return f"❌ Failed to approve player {player_id}. Player may not exist or is already approved."

    except Exception as e:
        error_msg = f"Failed to approve player {player_id}: {e!s}"
        logger.error(f"❌ {error_msg}")
        return f"❌ {error_msg}"


@tool("list_players_all")
async def list_players_all(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str
) -> str:
    """Display comprehensive team player roster.

    Provides complete view of all registered players including pending
    approvals, with their positions and current status for roster management.

    Use when: Full team roster review is required
    Required: Team member access and appropriate permissions (leadership chat)

    Returns: Complete player roster with status details
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            team_id, chat_type, names=["team_id", "chat_type"]
        )
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = team_id.strip()
        chat_type = chat_type.strip().lower()
        username = telegram_username or "unknown user"

        logger.info(
            f"📋 All players request from {username} ({telegram_id}) "
            f"in team {team_id}, chat_type: {chat_type}"
        )

        # Get domain service and execute operation
        container = get_container()
        player_service = container.get_service(PlayerService)

        players = await player_service.get_all_players(team_id)

        if not players:
            return "No players found in the team."

        # Apply context-aware filtering
        is_main_chat = chat_type == "main"
        formatted_players = _format_player_list(players, is_main_chat)

        # Handle case where filtering resulted in no players
        if not formatted_players:
            return (
                "No active players found in the team."
                if is_main_chat
                else "No players found in the team."
            )

        # Create formatted message
        roster_title = "🏆 Team Players" if is_main_chat else "🏆 Complete Team Roster"
        message_lines = [roster_title, ""]

        for i, player in enumerate(formatted_players, 1):
            message_lines.extend(
                [
                    f"{i}. {player['name']} ({player['position']})",
                    f"   🏷️ ID: {player['player_id']} | ✅ Status: {player['status']}",
                    "",
                ]
            )

        formatted_message = "\n".join(message_lines)
        logger.info(f"✅ Retrieved {len(formatted_players)} players for team {team_id}")

        return formatted_message

    except Exception as e:
        error_msg = f"Failed to get players for team {team_id}: {e!s}"
        logger.error(f"❌ {error_msg}")
        return f"❌ {error_msg}"


@tool("list_players_active")
async def list_players_active(
    telegram_id: str, team_id: str, telegram_username: str, chat_type: str
) -> str:
    """Display active players available for selection.

    Shows current roster of approved and active players eligible
    for match squad selection and team activities.

    Use when: Squad selection or active roster review is needed
    Required: Team player access (main or private chat)

    Returns: Active player roster with positions
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(team_id, names=["team_id"])
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = team_id.strip()
        username = telegram_username or "unknown user"

        logger.info(
            f"📋 Listing active players for team {team_id} " f"by {username} ({telegram_id})"
        )

        # Get domain service
        container = get_container()
        player_service = container.get_service(PlayerService)
        if not player_service:
            return "❌ Player service is not available"

        # Get active players from database
        players = await player_service.get_active_players(team_id)
        players = sanitize_list_response(players, max_items=20)

        if not players:
            return "📋 No active players found in the team."

        # Format validated player data
        formatted_players = []
        for player in players:
            if hasattr(player, "name") and hasattr(player, "player_id"):
                name = str(player.name or "Unknown").strip()
                player_id = str(player.player_id or "N/A").strip()
                formatted_players.append(f"• {name} ({player_id})")
            else:
                logger.warning(f"Skipping player with missing data: {player}")

        # Create response
        response = f"📋 Active Players ({len(formatted_players)}):\n" + "\n".join(formatted_players)
        response = format_safe_response(response, max_length=1500)

        logger.info(f"✅ Retrieved {len(formatted_players)} active players for team {team_id}")
        return response

    except Exception as e:
        error_msg = f"Error retrieving active players for team {team_id}: {e!s}"
        logger.error(f"❌ {error_msg}")
        return f"❌ {error_msg}"


def _format_player_list(players: list, is_main_chat: bool) -> list[dict[str, str]]:
    """Format player list with context-aware filtering.

    Args:
        players: List of player entities
        is_main_chat: Whether this is for main chat (active only) or leadership chat (all)

    Returns:
        List of formatted player dictionaries
    """
    formatted_players = []
    for player in players:
        # Get player status safely
        status = getattr(player, "status", "unknown")
        player_status = status.lower() if hasattr(status, "lower") else str(status).lower()

        # Filter by chat type - skip non-active players in main chat
        if is_main_chat and player_status != "active":
            continue

        # Format player data safely
        player_data = {
            "name": str(getattr(player, "name", "Unknown")).strip() or "Unknown",
            "position": str(getattr(player, "position", "Not specified")).strip()
            or "Not specified",
            "status": status.title() if hasattr(status, "title") else str(status),
            "player_id": str(getattr(player, "player_id", "Not assigned")).strip()
            or "Not assigned",
            "phone_number": str(getattr(player, "phone_number", "Not provided")).strip()
            or "Not provided",
        }
        formatted_players.append(player_data)

    return formatted_players


# NOTE: list_team_members_and_players tool has been moved to team_administration module
# to avoid duplication and maintain clean architecture separation
