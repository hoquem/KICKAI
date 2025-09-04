#!/usr/bin/env python3
"""
Team Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for general team management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Any

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container


def _get_status_string(obj: Any, attr: str = "status") -> str:
    """
    Extract status string from object with various possible formats.

    :param obj: Object to extract status from
    :param attr: Attribute name to extract (default: 'status')
    :return: Normalized status string
    """
    value = getattr(obj, attr, "unknown")
    if hasattr(value, "value"):
        return str(value.value).lower()
    elif hasattr(value, "lower"):
        return value.lower()
    else:
        return str(value).lower()


def _format_player_data(player: Any) -> dict[str, Any]:
    """
    Format player object into standardized dictionary.

    :param player: Player domain object
    :return: Formatted player data dictionary
    """
    return {
        "type": "Player",
        "name": player.name or "Unknown",
        "identifier": player.player_id or "Not assigned",
        "status": _get_status_string(player).title(),
        "position": player.position or "Not specified",
        "phone_number": getattr(player, "phone_number", "Not provided"),
    }


def _format_member_data(member: Any) -> dict[str, Any]:
    """
    Format team member object into standardized dictionary.

    :param member: Team member domain object
    :return: Formatted member data dictionary
    """
    return {
        "type": "Team Member",
        "name": member.name or "Unknown",
        "identifier": getattr(member, "member_id", "Not assigned"),
        "status": _get_status_string(member),
        "role": getattr(member, "role", "Member"),
        "is_admin": getattr(member, "is_admin", False),
        "phone_number": getattr(member, "phone_number", "Not provided"),
    }


def _group_by_status(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Group items by status for organized display.

    :param items: List of formatted items to group
    :return: Dictionary with status groups
    """
    groups = {"active": [], "pending": [], "inactive": []}

    for item in items:
        status = item["status"].lower()
        if status == "active":
            groups["active"].append(item)
        elif status == "pending":
            groups["pending"].append(item)
        else:
            groups["inactive"].append(item)

    return groups


def _format_main_chat_response(players: list[dict[str, Any]]) -> list[str]:
    """
    Format response for main chat (simple view).

    :param players: List of formatted player data
    :return: Formatted message lines
    """
    message_lines = ["🏆 Team Players", ""]

    if players:
        for i, player in enumerate(players, 1):
            status_emoji = "✅" if player["status"].lower() == "active" else "🔶"
            message_lines.append(f"{i}. {player['name']} ({player['position']})")
            message_lines.append(
                f"🏷️ ID: {player['identifier']} | {status_emoji} Status: {player['status']}"
            )
            message_lines.append("")
    else:
        message_lines.append("ℹ️ No active players found in the team.")

    return message_lines


def _format_status_group(
    items: list[dict[str, Any]], status_name: str, item_type: str
) -> list[str]:
    """
    Format a status group for display.

    :param items: Items in this status group
    :param status_name: Name of the status (e.g., "Active")
    :param item_type: Type of items ("player" or "member")
    :return: Formatted message lines
    """
    lines = []
    if items:
        lines.append(f"{status_name} ({len(items)}):")
        for i, item in enumerate(items, 1):
            if item_type == "member":
                admin_indicator = " 👑" if item["is_admin"] else ""
                lines.append(
                    f"{i}. {item['name']}{admin_indicator} ({item['role']}) - ID: {item['identifier']}"
                )
            else:  # player
                lines.append(f"{i}. {item['name']} ({item['position']}) - ID: {item['identifier']}")
        lines.append("")
    return lines


def _format_leadership_chat_response(
    members: list[dict[str, Any]], players: list[dict[str, Any]]
) -> list[str]:
    """
    Format response for leadership chat (detailed view).

    :param members: List of formatted member data
    :param players: List of formatted player data
    :return: Formatted message lines
    """
    message_lines = ["🏆 Complete Team Roster", ""]

    # Format members section
    if members:
        message_lines.extend([f"👥 TEAM MEMBERS ({len(members)}):", ""])
        member_groups = _group_by_status(members)

        message_lines.extend(_format_status_group(member_groups["active"], "Active", "member"))
        message_lines.extend(_format_status_group(member_groups["pending"], "Pending", "member"))
        message_lines.extend(_format_status_group(member_groups["inactive"], "Inactive", "member"))
    else:
        message_lines.extend(["👥 TEAM MEMBERS (0):", "No team members found.", ""])

    # Format players section
    if players:
        message_lines.extend([f"⚽ PLAYERS ({len(players)}):", ""])
        player_groups = _group_by_status(players)

        message_lines.extend(_format_status_group(player_groups["active"], "Active", "player"))
        message_lines.extend(_format_status_group(player_groups["pending"], "Pending", "player"))
        message_lines.extend(_format_status_group(player_groups["inactive"], "Inactive", "player"))
    else:
        message_lines.extend(["⚽ PLAYERS (0):", "No players found.", ""])

    if not members and not players:
        message_lines.append("ℹ️ No players or team members found in the team.")

    return message_lines


@tool("list_team_members_and_players")
async def list_team_members_and_players(
    telegram_id: str, team_id: str, username: str, chat_type: str
) -> str:
    """
    Retrieve complete organizational roster with all participants.

    Provides comprehensive overview of entire team structure including
    administrative members and game participants with unified status display.

    Use when: Complete team overview is required
    Required: Team access privileges
    Context: Organizational review workflow

    Returns: Complete team structure summary
    """
    if not telegram_id or not team_id:
        return "❌ Missing required parameters: telegram_id and team_id are required"

    try:
        telegram_id_int = int(telegram_id)
    except (ValueError, TypeError):
        return "❌ Invalid telegram_id format - must be numeric"

    try:
        logger.info(
            f"📋 Complete team list request from {username} ({telegram_id_int}) in team {team_id}"
        )

        # Get services
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import (
            IPlayerService,
        )
        from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
            ITeamMemberService,
        )

        player_service = container.get_service(IPlayerService)
        team_member_service = container.get_service(ITeamMemberService)

        if not player_service or not team_member_service:
            return "❌ System services unavailable - please contact support"

        # Fetch data
        players = await player_service.get_all_players(team_id)
        team_members = await team_member_service.get_team_members(team_id)

        # Determine filtering based on chat type
        is_main_chat = chat_type and chat_type.lower() == "main"

        # Format and filter data
        formatted_players = []
        for player in players or []:
            player_status = _get_status_string(player)

            # Filter by chat type - main chat shows only active
            if is_main_chat and player_status != "active":
                continue

            formatted_players.append(_format_player_data(player))

        formatted_members = []
        for member in team_members or []:
            member_status = _get_status_string(member)

            # Filter by chat type - main chat shows only active
            if is_main_chat and member_status != "active":
                continue

            formatted_members.append(_format_member_data(member))

        # Generate appropriate response format
        if is_main_chat:
            message_lines = _format_main_chat_response(formatted_players)
        else:
            message_lines = _format_leadership_chat_response(formatted_members, formatted_players)

        formatted_message = "\n".join(message_lines)

        logger.info(
            f"✅ Retrieved team roster: {len(formatted_players)} players, {len(formatted_members)} members"
        )
        return formatted_message

    except Exception as e:
        logger.error(f"❌ Error retrieving team roster: {e}")
        return "❌ System error occurred while retrieving team roster"
