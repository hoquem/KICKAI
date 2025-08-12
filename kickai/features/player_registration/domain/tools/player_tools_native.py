#!/usr/bin/env python3
"""
Player Tools - Native CrewAI Implementation

This module provides tools for player management operations using ONLY CrewAI native patterns.
"""


from crewai.tools import tool
from loguru import logger

from kickai.core.constants import normalize_chat_type
from kickai.core.dependency_container import get_container
from kickai.core.enums import ChatType
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_service import TeamService


@tool("approve_player")
def approve_player(telegram_id: int, team_id: str, chat_type: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        player_id (str): The player ID to approve (M001MH format)


    :return: Player approval status with updated player details and activation confirmation
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to approve player."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to approve player."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to approve player."

    if not player_id or player_id.strip() == "":
        return "❌ Player ID is required to approve player."

    try:
        # Get service using simple container access
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            return "❌ Player service is temporarily unavailable. Please try again later."

        # Approve player
        result = player_service.approve_player_sync(player_id, team_id)

        # Check if result indicates success (starts with ✅)
        if result.startswith("✅"):
            # Extract player name from the result string
            try:
                player_name = result.split("Player ")[1].split(" approved")[0]
            except (IndexError, AttributeError):
                player_name = "Unknown"

            # Format as simple string response
            return f"✅ Player Approved Successfully\n\n• Name: {player_name}\n• Player ID: {player_id}\n• Team: {team_id}\n• Status: Approved\n\nPlayer is now approved for squad selection."
        else:
            return f"❌ Failed to approve player: {result}"

    except Exception as e:
        logger.error(f"Failed to approve player: {e}")
        return f"❌ Failed to approve player: {e!s}"


@tool("get_my_status")
def get_my_status(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Get the current user's status (player or team member based on chat type).


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private) - determines lookup type


    :return: User status information including name, position, role, and registration details
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get status."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get status."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get status."

    try:
        # telegram_id is already int from standardized signature
        user_id = telegram_id

        # Get services from container
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service(TeamService)

        if not player_service or not team_service:
            return "❌ Required services are temporarily unavailable. Please try again later."

        # Normalize chat type
        chat_type_enum = normalize_chat_type(chat_type)

        # Determine whether to check player or team member status based on chat type
        if chat_type_enum == ChatType.MAIN:
            # Main chat - check player status
            player = player_service.get_player_by_telegram_id_sync(user_id, team_id)
            if player:
                return f"👤 Your Player Status\n\n• Name: {player.name}\n• Position: {player.position or 'Not set'}\n• Status: {player.status}\n• Player ID: {player.player_id}\n• Team: {team_id}"
            else:
                return "❌ You are not registered as a player in this team. Use /register to join as a player."

        elif chat_type_enum in [ChatType.LEADERSHIP, ChatType.PRIVATE]:
            # Leadership/private chat - check team member status
            team_member = team_service.get_team_member_by_telegram_id_sync(team_id, telegram_id)
            if team_member:
                roles = ", ".join(team_member.roles) if team_member.roles else "Member"
                return f"👔 Your Team Member Status\n\n• Name: {team_member.name}\n• Roles: {roles}\n• Status: {team_member.status}\n• Team: {team_id}"
            else:
                return "❌ You are not registered as a team member. Contact an administrator for access."

        else:
            return f"❌ Unsupported chat type: {chat_type}"

    except Exception as e:
        logger.error(f"Failed to get user status: {e}")
        return f"❌ Failed to get user status: {e!s}"


@tool("get_player_status")
def get_player_status(telegram_id: int, team_id: str, chat_type: str, player_id: str) -> str:
    """
    Get detailed information about a specific player.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)
        player_id (str): The ID of the player to get status for


    :return: Detailed player information including name, position, status, phone, and registration date
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get player status."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get player status."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get player status."

    if not player_id or player_id.strip() == "":
        return "❌ Player ID is required to get player status."

    try:
        # Get service using simple container access
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            return "❌ Player service is temporarily unavailable. Please try again later."

        # Get player information
        player = player_service.get_player_by_id_sync(player_id, team_id)

        if player:
            # Format as simple string response
            result = "👤 Player Information\n\n"
            result += f"• Name: {player.name}\n"
            result += f"• Position: {player.position or 'Not set'}\n"
            result += f"• Status: {player.status}\n"
            result += f"• Player ID: {player.player_id}\n"
            result += f"• Phone: {player.phone_number or 'Not provided'}\n"
            result += f"• Team: {team_id}"

            if hasattr(player, 'registered_date') and player.registered_date:
                result += f"\n• Registered: {player.registered_date}"

            return result
        else:
            return f"❌ Player with ID '{player_id}' not found in team '{team_id}'."

    except Exception as e:
        logger.error(f"Failed to get player status: {e}")
        return f"❌ Failed to get player status: {e!s}"


@tool("get_all_players")
def get_all_players(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Get a list of all players in the team.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)


    :return: Comprehensive list of all players with names, positions, and status information
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get all players."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get all players."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get all players."

    try:
        # Get service using simple container access
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            return "❌ Player service is temporarily unavailable. Please try again later."

        # Get all players
        players = player_service.get_all_players_sync(team_id)

        if not players:
            return f"📋 All Players (Team: {team_id})\n\nNo players found in this team."

        # Format as simple string response
        result = f"📋 All Players (Team: {team_id})\n\n"
        for player in players:
            status_emoji = "✅" if player.status == "active" else "⏸️"
            result += f"{status_emoji} {player.name} - {player.position or 'No position'} (ID: {player.player_id})\n"

        result += f"\nTotal Players: {len(players)}"
        return result

    except Exception as e:
        logger.error(f"Failed to get all players: {e}")
        return f"❌ Failed to get all players: {e!s}"


@tool("get_active_players")
def get_active_players(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Get a list of active players in the team.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)


    :return: List of active players available for squad selection with positions and details
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to get active players."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get active players."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to get active players."

    try:
        # Get service using simple container access
        container = get_container()
        player_service = container.get_service(PlayerService)

        if not player_service:
            return "❌ Player service is temporarily unavailable. Please try again later."

        # Get active players
        players = player_service.get_active_players_sync(team_id)

        if not players:
            return f"📋 Active Players (Team: {team_id})\n\nNo active players found in this team."

        # Format as simple string response
        result = f"📋 Active Players (Team: {team_id})\n\n"
        for player in players:
            result += f"✅ {player.name} - {player.position or 'No position'} (ID: {player.player_id})\n"

        result += f"\nTotal Active Players: {len(players)}"
        return result

    except Exception as e:
        logger.error(f"Failed to get active players: {e}")
        return f"❌ Failed to get active players: {e!s}"


@tool("list_team_members_and_players")
def list_team_members_and_players(telegram_id: int, team_id: str, chat_type: str) -> str:
    """
    Get a comprehensive list of team members and players.


        telegram_id (int): Telegram ID of the user making the request
        team_id (str): Team identifier for context and data isolation
        chat_type (str): Chat context (main, leadership, private)


    :return: Complete team overview with both management members and players including roles and statistics
    :rtype: str  # TODO: Fix type
    """
    # Native CrewAI pattern - simple parameter validation
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        return "❌ Valid Telegram ID is required to list team members and players."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to list team members and players."

    if not chat_type or chat_type.strip() == "":
        return "❌ Chat type is required to list team members and players."

    try:
        # Get services using simple container access
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_service = container.get_service(TeamService)

        if not player_service or not team_service:
            return "❌ Required services are temporarily unavailable. Please try again later."

        # Get team members and players
        team_members = team_service.get_team_members_sync(team_id)
        players = player_service.get_all_players_sync(team_id)

        # Format as simple string response
        result = f"📋 Team Overview (Team: {team_id})\n\n"

        # Team Members section
        if team_members:
            result += "👔 Team Members:\n"
            for member in team_members:
                roles = ", ".join(member.roles) if member.roles else "Member"
                result += f"• {member.name} - {roles}\n"
        else:
            result += "👔 Team Members: No team members found\n"

        result += "\n"

        # Players section
        if players:
            result += "👥 Players:\n"
            for player in players:
                status_emoji = "✅" if player.status == "active" else "⏸️"
                result += f"• {status_emoji} {player.name} - {player.position or 'No position'} (ID: {player.player_id})\n"
        else:
            result += "👥 Players: No players found\n"

        # Summary
        team_count = len(team_members) if team_members else 0
        player_count = len(players) if players else 0
        result += f"\n📊 Summary: {team_count} team members, {player_count} players"

        return result

    except Exception as e:
        logger.error(f"Failed to list team members and players: {e}")
        return f"❌ Failed to list team members and players: {e!s}"
