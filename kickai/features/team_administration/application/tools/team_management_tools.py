#!/usr/bin/env python3
"""
Team Management Tools - Clean Architecture Application Layer

This module provides CrewAI tools for general team management functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
from kickai.utils.tool_helpers import create_json_response


@tool("list_team_members_and_players", result_as_answer=True)
async def list_team_members_and_players(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    Get comprehensive list of all team members and players.

    This tool serves as the application boundary for complete team listing functionality.
    It handles framework concerns and delegates business logic to the domain services.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context

    Returns:
        JSON formatted combined list of team members and players
    """
    try:
        logger.info(f"📋 Complete team list request from {username} ({telegram_id}) in team {team_id}")

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(IPlayerService)
        team_member_service = container.get_service(ITeamMemberService)

        if not player_service or not team_member_service:
            return create_json_response(
                ResponseStatus.ERROR,
                message="Required services are not available"
            )

        # Execute domain operations
        players = await player_service.get_all_players(team_id)
        team_members = await team_member_service.get_team_members(team_id)

        # Format combined list at application boundary
        formatted_players = []
        for player in players:
            player_data = {
                "type": "Player",
                "name": player.name or "Unknown",
                "identifier": player.player_id or "Not assigned",
                "status": player.status.title() if hasattr(player.status, 'title') else str(player.status),
                "position": player.position or "Not specified",
                "phone_number": getattr(player, 'phone_number', 'Not provided')
            }
            formatted_players.append(player_data)

        formatted_members = []
        for member in team_members:
            member_data = {
                "type": "Team Member",
                "name": member.name or "Unknown",
                "identifier": getattr(member, 'member_id', 'Not assigned'),
                "status": str(member.status) if hasattr(member, 'status') else 'Active',
                "role": getattr(member, 'role', 'Member'),
                "is_admin": getattr(member, 'is_admin', False),
                "phone_number": getattr(member, 'phone_number', 'Not provided')
            }
            formatted_members.append(member_data)

        # Create formatted message
        message_lines = ["🏆 **Complete Team Roster**", ""]

        if formatted_players:
            message_lines.extend(["🏃‍♂️ **Players:**", ""])
            for i, player in enumerate(formatted_players, 1):
                message_lines.append(f"{i}. **{player['name']}** ({player['position']})")
                message_lines.append(f"   🏷️ ID: {player['identifier']} | ✅ Status: {player['status']}")
                message_lines.append("")

        if formatted_members:
            message_lines.extend(["👥 **Team Members:**", ""])
            for i, member in enumerate(formatted_members, 1):
                admin_indicator = " 👑" if member['is_admin'] else ""
                message_lines.append(f"{i}. **{member['name']}**{admin_indicator}")
                message_lines.append(f"   🏷️ ID: {member['identifier']} | 👑 Role: {member['role']}")
                message_lines.append(f"   ✅ Status: {member['status']}")
                message_lines.append("")

        if not formatted_players and not formatted_members:
            message_lines.extend(["ℹ️ No players or team members found in the team."])

        formatted_message = "\n".join(message_lines)

        response_data = {
            "players": formatted_players,
            "team_members": formatted_members,
            "total_players": len(formatted_players),
            "total_members": len(formatted_members),
            "total_count": len(formatted_players) + len(formatted_members),
            "formatted_message": formatted_message
        }

        logger.info(f"✅ Retrieved complete team roster: {len(formatted_players)} players, {len(formatted_members)} members")
        return create_json_response(ResponseStatus.SUCCESS, data=response_data)

    except Exception as e:
        logger.error(f"❌ Error getting complete team roster: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get team roster: {e}")