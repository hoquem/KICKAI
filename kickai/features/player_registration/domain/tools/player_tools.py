#!/usr/bin/env python3
"""
Player Registration Tools

This module provides tools for player registration and management.
All tools follow CrewAI best practices with proper error handling and JSON responses.
"""

import json
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from crewai.tools import tool

from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
from kickai.utils.tool_helpers import create_json_response, validate_required_input, sanitize_input
from kickai.utils.tool_validation import create_tool_response, validate_team_id, validate_telegram_id
from kickai.core.dependency_container import get_container


def _validate_standard_inputs(team_id: str, telegram_id: Union[str, int]) -> tuple[str, int]:
    """Validate standard tool inputs."""
    validated_team_id = validate_team_id(team_id)
    validated_telegram_id = validate_telegram_id(telegram_id)
    return validated_team_id, validated_telegram_id


def _log_tool_start(tool_name: str, inputs: Dict[str, Any]) -> None:
    """Log tool execution start."""
    logger.info(f"🔧 {tool_name} called with inputs: {inputs}")


def _get_service_from_container(service_class: type) -> Any:
    """Get service from container."""
    container = get_container()
    service = container.get_service(service_class)
    
    if not service:
        logger.warning(f"⚠️ {service_class.__name__} is not available")
        
    return service


def _create_player_data(player: Any, telegram_id: int, team_id: str) -> Dict[str, Any]:
    """Create structured player data for response."""
    return {
        "telegram_id": telegram_id,
        "team_id": team_id,
        "name": player.name or "Unknown",
        "username": player.username or "Unknown",
        "position": player.position or "Not specified",
        "phone_number": player.phone_number or "Not provided",
        "player_id": player.player_id or "Not assigned",
        "status": player.status.title() if player.status else "Unknown",
        "is_player": True,
        "is_team_member": False,
        "is_active": player.status.lower() == "active" if player.status else False,
        "is_pending": player.status.lower() == "pending" if player.status else False,
        "created_at": player.created_at.isoformat() if player.created_at else None,
        "updated_at": player.updated_at.isoformat() if player.updated_at else None,
    }


def _create_team_member_data(team_member: Any, telegram_id: int, team_id: str) -> Dict[str, Any]:
    """Create structured team member data for response."""
    return {
        "telegram_id": telegram_id,
        "team_id": team_id,
        "name": team_member.name or "Unknown",
        "username": team_member.username or "Unknown",
        "role": team_member.role or "Team Member",
        "phone_number": team_member.phone_number or "Not provided",
        "member_id": team_member.member_id or "Not assigned",
        "status": team_member.status.value.title() if team_member.status else "Unknown",
        "is_player": False,
        "is_team_member": True,
        "is_admin": team_member.is_admin or False,
        "is_active": team_member.status.value.lower() == "active" if team_member.status else False,
        "created_at": team_member.created_at.isoformat() if team_member.created_at else None,
        "updated_at": team_member.updated_at.isoformat() if team_member.updated_at else None,
    }


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def approve_player(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.

    Args:
        telegram_id: Telegram ID of the approving user
        team_id: Team ID (required) - available from context
        username: Username of the approving user
        chat_type: Chat type context
        player_id: The player ID to approve (M001MH format)

    Returns:
        Success message or error
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)
        
        # Log tool execution start
        _log_tool_start("approve_player", {'team_id': team_id, 'telegram_id': telegram_id_int, 'player_id': player_id})
        
        # Get player service
        player_service = _get_service_from_container(IPlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")
        
        # Approve the player
        success = await player_service.approve_player(player_id, team_id)
        
        if success:
            return create_tool_response(
                success=True,
                message=f"Player {player_id} approved successfully",
                data={
                    "player_id": player_id,
                    "team_id": team_id,
                    "approved_by": telegram_id_int,
                    "status": "approved"
                }
            )
        else:
            return create_json_response(ResponseStatus.ERROR, message=f"Failed to approve player {player_id}")
            
    except Exception as e:
        logger.error(f"❌ Error in approve_player: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to approve player: {str(e)}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_my_status(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get the current user's status (player or team member based on chat type).

    Args:
        telegram_id: The Telegram ID of the user whose status is to be retrieved.
        team_id: The ID of the team the user belongs to.
        username: Username of the user
        chat_type: The chat type - determines whether to look up player or team member status.

    Returns:
        User status information (player or team member) or error message
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)
        
        # Log tool execution start
        _log_tool_start("get_my_status", {'team_id': team_id, 'telegram_id': telegram_id_int, 'chat_type': chat_type})
        
        # Route based on chat type
        if chat_type.lower() in ["leadership", "leadership_chat"]:
            # Get team member information for leadership chat
            team_member_service = _get_service_from_container(ITeamMemberService)
            
            if not team_member_service:
                return create_json_response(ResponseStatus.ERROR, message="TeamMemberService is not available")
            
            # Get team member by telegram ID
            team_member = await team_member_service.get_team_member_by_telegram_id(telegram_id_int, team_id)
            
            if team_member:
                # Create structured team member data
                team_member_data = _create_team_member_data(team_member, telegram_id_int, team_id)
            else:
                # Team member not found
                return create_tool_response(
                    success=False,
                    message="Team member not found",
                    data={
                        "telegram_id": telegram_id_int,
                        "team_id": team_id,
                        "is_team_member": False,
                        "is_player": False,
                        "status": "Not registered"
                    }
                )
            
            return create_tool_response(
                success=True,
                message="Team member status retrieved successfully",
                data=team_member_data
            )
        
        else:
            # Get player information for main chat
            player_service = _get_service_from_container(IPlayerService)
            if not player_service:
                return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

            player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)

            if player:
                # Create structured player data
                player_data = _create_player_data(player, telegram_id_int, team_id)
                
                # Add pending note if applicable
                if player_data["is_pending"]:
                    player_data["note"] = "Your registration is pending approval by team leadership."
                
                return create_tool_response(
                    success=True,
                    message="Player status retrieved successfully",
                    data=player_data
                )
            else:
                return create_json_response(ResponseStatus.ERROR, message=f"Player not found for telegram ID {telegram_id_int} in team {team_id}")

    except Exception as e:
        from kickai.features.player_registration.domain.exceptions import PlayerLookupError
        logger.error(f"❌ Error in get_my_status: {e}")
        lookup_error = PlayerLookupError(str(telegram_id_int), team_id, str(e))
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get user status: {lookup_error.message}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_all_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all players in the team.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context

    Returns:
        List of all players or error message
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ ", ""))

        # Sanitize and validate inputs
        team_id = sanitize_input(team_id, max_length=20)
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)

        # Get service
        player_service = _get_service_from_container(IPlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

        # Get all players
        players = await player_service.get_all_players(team_id)

        if not players:
            return create_tool_response(
                success=True,
                message="No players found in the team",
                data={"players": [], "count": 0, "team_id": team_id}
            )

        # Create structured player data
        players_data = []
        for player in players:
            player_info = {
                "name": player.name,
                "position": player.position,
                "status": player.status.title(),
                "player_id": player.player_id or "Not assigned",
                "phone_number": player.phone_number or "Not provided",
                "is_active": player.status.lower() == "active",
                "status_emoji": "✅" if player.status.lower() == "active" else "⏳"
            }
            players_data.append(player_info)

        return create_tool_response(
            success=True,
            message=f"Retrieved {len(players)} players from team",
            data={
                "players": players_data,
                "count": len(players_data),
                "team_id": team_id,
                "telegram_id": telegram_id_int
            }
        )

    except Exception as e:
        from kickai.features.player_registration.domain.exceptions import PlayerDataError
        logger.error(f"❌ Error in get_all_players: {e}")
        data_error = PlayerDataError(team_id, str(e))
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get all players: {data_error.message}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_active_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all active players in the team.

    🎯 CONTEXT USAGE GUIDANCE:
    - MAIN CHAT: Primary tool for /list commands (focused player view for match planning)
    - PRIVATE CHAT: Personal player information requests
    - LEADERSHIP CHAT: Use list_team_members_and_players instead (comprehensive team oversight needed)
    
    📋 USE WHEN:
    - Player needs to see who's available for matches
    - Simple player list requests in main chat
    - Personal context queries about active players
    
    ❌ AVOID WHEN:
    - Leadership needs full team administrative view (use list_team_members_and_players)
    - Need to see both team members and players together
    - Administrative decisions requiring complete team roster

    🚨 CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:
    - This tool queries the ACTUAL DATABASE for active players
    - If the database returns NO players, return JSON with empty players array - DO NOT INVENT PLAYERS
    - The agent MUST return this tool's output EXACTLY as received - NO additions, NO modifications
    - NEVER create imaginary player data if the database is empty

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context

    Returns:
        JSON response with EXACT database results - List of active players or empty array
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ ", ""))

        validation_error = validate_required_input(telegram_id, "Telegram ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error.replace("❌ ", ""))

        # Sanitize and validate inputs
        team_id = sanitize_input(team_id, max_length=20)
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)

        # Get service
        player_service = _get_service_from_container(IPlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")

        # Get active players
        active_players = await player_service.get_active_players(team_id)

        if not active_players:
            return create_tool_response(
                success=True,
                message="No active players found in the team",
                data={"players": [], "count": 0, "team_id": team_id}
            )

        # Create structured player data
        players_data = []
        for player in active_players:
            player_info = {
                "name": player.name,
                "position": player.position,
                "status": player.status.title(),
                "player_id": player.player_id or "Not assigned",
                "phone_number": player.phone_number or "Not provided",
                "is_active": True,
                "status_emoji": "✅"
            }
            players_data.append(player_info)

        return create_tool_response(
            success=True,
            message=f"Retrieved {len(active_players)} active players from team",
            data={
                "players": players_data,
                "count": len(players_data),
                "team_id": team_id,
                "telegram_id": telegram_id_int
            }
        )

    except Exception as e:
        from kickai.features.player_registration.domain.exceptions import PlayerDataError
        logger.error(f"❌ Error in get_active_players: {e}")
        data_error = PlayerDataError(team_id, str(e))
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get active players: {data_error.message}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def get_player_match(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: str) -> str:
    """
    Get match information for a specific player.

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context
        player_id: The player ID to get match info for

    Returns:
        Match information for the player or error message
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)
        
        # Log tool execution start
        _log_tool_start("get_player_match", {'team_id': team_id, 'telegram_id': telegram_id_int, 'player_id': player_id})
        
        # Get player service
        player_service = _get_service_from_container(IPlayerService)
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")
        
        # Get player match information
        match_info = await player_service.get_player_match_info(player_id, team_id)
        
        if match_info:
            return create_tool_response(
                success=True,
                message=f"Match information retrieved for player {player_id}",
                data=match_info
            )
        else:
            return create_json_response(ResponseStatus.ERROR, message=f"No match information found for player {player_id}")
            
    except Exception as e:
        logger.error(f"❌ Error in get_player_match: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get player match info: {str(e)}")


# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def list_team_members_and_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get comprehensive team overview including both team members and players.

    🎯 CONTEXT USAGE GUIDANCE:
    - LEADERSHIP CHAT: Primary tool for /list commands (comprehensive team oversight)
    - MAIN CHAT: Use get_active_players instead (focused player view for match planning)
    - PRIVATE CHAT: Use get_my_status for personal information
    
    📋 USE WHEN:
    - Leadership needs complete team roster overview
    - Administrative decisions requiring full team information
    - Need to see both team members and players together
    
    ❌ AVOID WHEN:
    - Simple player list requests in main chat (use get_active_players)
    - Personal status queries (use get_my_status)
    - Match planning focused queries (use get_active_players)

    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context

    Returns:
        Comprehensive team overview with both team members and players
    """
    try:
        # Validate inputs
        team_id, telegram_id_int = _validate_standard_inputs(team_id, telegram_id)
        
        # Log tool execution start
        _log_tool_start("list_team_members_and_players", {'team_id': team_id, 'telegram_id': telegram_id_int})
        
        # Get services
        player_service = _get_service_from_container(IPlayerService)
        team_member_service = _get_service_from_container(ITeamMemberService)
        
        if not player_service:
            return create_json_response(ResponseStatus.ERROR, message="PlayerService is not available")
        if not team_member_service:
            return create_json_response(ResponseStatus.ERROR, message="TeamMemberService is not available")
        
        # Get team members and players
        team_members = await team_member_service.get_team_members_by_team(team_id)
        players = await player_service.get_all_players(team_id)
        
        # Create structured data
        team_members_data = []
        if team_members:
            for member in team_members:
                member_info = {
                    "name": member.name,
                    "role": member.role,
                    "is_admin": member.is_admin,
                    "status": member.status.value.title() if member.status else "Unknown",
                    "member_id": member.member_id or "Not assigned"
                }
                team_members_data.append(member_info)
        
        players_data = []
        if players:
            for player in players:
                player_info = {
                    "name": player.name,
                    "position": player.position,
                    "status": player.status.title(),
                    "player_id": player.player_id or "Not assigned",
                    "is_active": player.status.lower() == "active"
                }
                players_data.append(player_info)
        
        return create_tool_response(
            success=True,
            message=f"Team overview retrieved for {team_id}",
            data={
                "team_id": team_id,
                "team_members": {
                    "count": len(team_members_data),
                    "members": team_members_data
                },
                "players": {
                    "count": len(players_data),
                    "players": players_data
                },
                "total_count": len(team_members_data) + len(players_data)
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Error in list_team_members_and_players: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to get team overview: {str(e)}")

