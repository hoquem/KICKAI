#!/usr/bin/env python3
"""
Player Registration Tools - Clean Architecture Application Layer

This module provides CrewAI tools for player registration functionality.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Dict, List, Any
from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.team_administration.domain.services.team_member_service import TeamMemberService
from kickai.utils.tool_validation import create_tool_response


@tool("approve_player", result_as_answer=True)
async def approve_player(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.

    This tool serves as the application boundary for player approval functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Telegram ID of the approving user
        team_id: Team ID (required) - available from context
        username: Username of the approving user
        chat_type: Chat type context
        player_id: The player ID to approve (M001MH format)

    Returns:
        JSON formatted approval result or error message
    """
    try:
        logger.info(f"🎯 Player approval request for {player_id} from {username} ({telegram_id}) in team {team_id}")

        if not player_id:
            return create_tool_response(
                False, 
                "Player ID is required for approval"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation
        result = await player_service.approve_player(player_id, team_id)
        
        logger.info(f"✅ Player {player_id} approved successfully by {username}")
        
        return create_tool_response(True, "Player approved successfully", data=result)

    except Exception as e:
        logger.error(f"❌ Error approving player {player_id}: {e}")
        return create_tool_response(False, f"Failed to approve player: {e}")



@tool("get_all_players", result_as_answer=True)
async def get_all_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get players for the team (filtered by chat type).

    This tool serves as the application boundary for player listing functionality.
    It handles framework concerns and delegates business logic to the domain service.
    
    Chat Type Filtering:
    - Main chat: Shows only ACTIVE players
    - Leadership chat: Shows ALL players (including pending)

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context (determines filtering)

    Returns:
        JSON formatted list of players (filtered by chat type)
    """
    try:
        logger.info(f"📋 All players request from {username} ({telegram_id}) in team {team_id}")

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation
        players = await player_service.get_all_players(team_id)
        
        if not players:
            return "No players found in the team."

        # Apply status filtering based on chat type
        # Main chat: Show only active players
        # Leadership chat: Show all players (including pending)
        is_main_chat = chat_type.lower() == 'main'

        # Format player list at application boundary with filtering
        formatted_players = []
        for player in players:
            player_status = player.status.lower() if hasattr(player.status, 'lower') else str(player.status).lower()
            
            # Filter by chat type - skip non-active players in main chat
            if is_main_chat and player_status != 'active':
                continue  # Skip non-active players in main chat
                
            player_data = {
                "name": player.name or "Unknown",
                "position": player.position or "Not specified",
                "status": player.status.title() if hasattr(player.status, 'title') else str(player.status),
                "player_id": player.player_id or "Not assigned",
                "phone_number": getattr(player, 'phone_number', 'Not provided')
            }
            formatted_players.append(player_data)

        # Handle case where filtering resulted in no players
        if not formatted_players:
            return "No active players found in the team." if is_main_chat else "No players found in the team."

        # Create formatted message with chat type-aware title
        roster_title = "🏆 Team Players" if is_main_chat else "🏆 Complete Team Roster"
        message_lines = [roster_title, ""]
        for i, player in enumerate(formatted_players, 1):
            message_lines.append(f"{i}. {player['name']} ({player['position']})")
            message_lines.append(f"   🏷️ ID: {player['player_id']} | ✅ Status: {player['status']}")
            message_lines.append("")

        formatted_message = "\n".join(message_lines)
        
        logger.info(f"✅ Retrieved {len(formatted_players)} players for team {team_id}")
        
        # Return formatted string directly (like help tools do)
        return formatted_message

    except Exception as e:
        logger.error(f"❌ Error getting all players for team {team_id}: {e}")
        return f"❌ Failed to get players: {e}"


@tool("get_active_players", result_as_answer=True)
async def get_active_players(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """
    Get all active players for the team.

    This tool serves as the application boundary for active player listing functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context

    Returns:
        JSON formatted list of active players
    """
    try:
        logger.info(f"🟢 Active players request from {username} ({telegram_id}) in team {team_id}")

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation
        active_players = await player_service.get_active_players(team_id)
        
        if not active_players:
            return create_tool_response(True, "Operation completed successfully", data="No active players found in the team."
            )

        # Format active player list at application boundary
        formatted_players = []
        for player in active_players:
            player_data = {
                "name": player.name or "Unknown",
                "position": player.position or "Not specified",
                "status": "Active",
                "player_id": player.player_id or "Not assigned",
                "phone_number": getattr(player, 'phone_number', 'Not provided')
            }
            formatted_players.append(player_data)

        # Create formatted message
        message_lines = ["🟢 Active Players", ""]
        for i, player in enumerate(formatted_players, 1):
            message_lines.append(f"{i}. {player['name']} ({player['position']})")
            message_lines.append(f"   🏷️ ID: {player['player_id']} | 📱 Phone: {player['phone_number']}")
            message_lines.append("")

        formatted_message = "\n".join(message_lines)
        
        logger.info(f"✅ Retrieved {len(formatted_players)} active players for team {team_id}")
        
        # Since result_as_answer=True, return formatted message directly for user display
        return formatted_message

    except Exception as e:
        logger.error(f"❌ Error getting active players for team {team_id}: {e}")
        return create_tool_response(False, f"Failed to get active players: {e}")


@tool("get_player_match", result_as_answer=True)
async def get_player_match(telegram_id: int, team_id: str, username: str, chat_type: str, player_id: str) -> str:
    """
    Get match information for a specific player.

    This tool serves as the application boundary for player match information functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        telegram_id: Requester's Telegram ID
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        player_id: The player ID to get match info for

    Returns:
        JSON formatted match information for the player
    """
    try:
        logger.info(f"🏈 Match info request for player {player_id} from {username} ({telegram_id})")

        if not player_id:
            return create_tool_response(False, "Player ID is required to get match information"
            )

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Execute domain operation to get player
        player = await player_service.get_player_by_id(player_id, team_id)
        
        if not player:
            return create_tool_response(False, f"Player {player_id} not found"
            )

        # For now, return basic player match-related info
        # This could be expanded to include actual match scheduling data
        match_info = {
            "player_id": player.player_id,
            "name": player.name,
            "position": player.position,
            "status": player.status.title() if hasattr(player.status, 'title') else str(player.status),
            "is_available_for_selection": player.status.lower() == "active" if player.status else False,
            "formatted_message": f"""🏈 Match Information for {player.name}

🏷️ Player ID: {player.player_id}
⚽ Position: {player.position or 'Not specified'}
✅ Status: {player.status.title() if hasattr(player.status, 'title') else str(player.status)}
🟢 Available for Selection: {'Yes' if player.status and player.status.lower() == 'active' else 'No'}

💡 Contact team management for specific match assignments."""
        }

        logger.info(f"✅ Retrieved match info for player {player_id}")
        return create_tool_response(True, "Operation completed successfully", data=match_info)

    except Exception as e:
        logger.error(f"❌ Error getting match info for player {player_id}: {e}")
        return create_tool_response(False, f"Failed to get match information: {e}")


# NOTE: list_team_members_and_players tool has been moved to team_administration module
# to avoid duplication and maintain clean architecture separation