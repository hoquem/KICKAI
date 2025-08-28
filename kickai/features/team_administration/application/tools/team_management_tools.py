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
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
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
        telegram_id: Requester's Telegram ID or dictionary with all parameters
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context

    Returns:
        JSON formatted combined list of team members and players
    """
    try:
        # Handle CrewAI parameter dictionary passing (Pattern A - CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
        
        logger.info(f"📋 Complete team list request from {username} ({telegram_id}) in team {team_id}")

        # Get required services from container (application boundary)
        container = get_container()
        player_service = container.get_service(PlayerService)
        team_member_service = container.get_service(TeamMemberService)

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
                "status": member.status.value if hasattr(member.status, 'value') else str(member.status),
                "role": getattr(member, 'role', 'Member'),
                "is_admin": getattr(member, 'is_admin', False),
                "phone_number": getattr(member, 'phone_number', 'Not provided')
            }
            formatted_members.append(member_data)

        # Create formatted message (clean, no markdown)
        message_lines = ["🏆 Complete Team Roster", ""]
        
        # Group and organize data by type and status
        if formatted_members:
            message_lines.extend([f"👥 TEAM MEMBERS ({len(formatted_members)}):", ""])
            
            # Group members by status
            active_members = [m for m in formatted_members if m['status'].lower() == 'active']
            pending_members = [m for m in formatted_members if m['status'].lower() == 'pending']
            inactive_members = [m for m in formatted_members if m['status'].lower() not in ['active', 'pending']]
            
            if active_members:
                message_lines.append(f"Active ({len(active_members)}):")
                for i, member in enumerate(active_members, 1):
                    admin_indicator = " 👑" if member['is_admin'] else ""
                    message_lines.append(f"{i}. {member['name']}{admin_indicator} ({member['role']}) - ID: {member['identifier']}")
                message_lines.append("")
                
            if pending_members:
                message_lines.append(f"Pending ({len(pending_members)}):")
                for i, member in enumerate(pending_members, 1):
                    admin_indicator = " 👑" if member['is_admin'] else ""
                    message_lines.append(f"{i}. {member['name']}{admin_indicator} ({member['role']}) - ID: {member['identifier']}")
                message_lines.append("")
                
            if inactive_members:
                message_lines.append(f"Inactive ({len(inactive_members)}):")
                for i, member in enumerate(inactive_members, 1):
                    admin_indicator = " 👑" if member['is_admin'] else ""
                    message_lines.append(f"{i}. {member['name']}{admin_indicator} ({member['role']}) - ID: {member['identifier']}")
                message_lines.append("")
        else:
            message_lines.extend(["👥 TEAM MEMBERS (0):", "No team members found.", ""])

        if formatted_players:
            message_lines.extend([f"⚽ PLAYERS ({len(formatted_players)}):", ""])
            
            # Group players by status
            active_players = [p for p in formatted_players if p['status'].lower() == 'active']
            pending_players = [p for p in formatted_players if p['status'].lower() == 'pending']
            inactive_players = [p for p in formatted_players if p['status'].lower() not in ['active', 'pending']]
            
            if active_players:
                message_lines.append(f"Active ({len(active_players)}):")
                for i, player in enumerate(active_players, 1):
                    message_lines.append(f"{i}. {player['name']} ({player['position']}) - ID: {player['identifier']}")
                message_lines.append("")
                
            if pending_players:
                message_lines.append(f"Pending ({len(pending_players)}):")
                for i, player in enumerate(pending_players, 1):
                    message_lines.append(f"{i}. {player['name']} ({player['position']}) - ID: {player['identifier']}")
                message_lines.append("")
                
            if inactive_players:
                message_lines.append(f"Inactive ({len(inactive_players)}):")
                for i, player in enumerate(inactive_players, 1):
                    message_lines.append(f"{i}. {player['name']} ({player['position']}) - ID: {player['identifier']}")
                message_lines.append("")
        else:
            message_lines.extend(["⚽ PLAYERS (0):", "No players found.", ""])

        if not formatted_players and not formatted_members:
            message_lines.extend(["ℹ️ No players or team members found in the team."])

        formatted_message = "\n".join(message_lines)

        response_data = {
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