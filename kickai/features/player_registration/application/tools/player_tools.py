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
from kickai.utils.native_crewai_helpers import (
    convert_telegram_id, 
    validate_required_strings, 
    sanitize_list_response,
    format_safe_response
)
from kickai.utils.robust_parameter_handler import (
    extract_context_parameters,
    extract_tool_parameters,
    validate_required_context,
    create_error_response
)



@tool("approve_player")
async def approve_player(*args, **kwargs) -> str:
    """
    Approve a player for match squad selection.

    This tool serves as the application boundary for player approval functionality.
    It handles framework concerns and delegates business logic to the domain service.

    Args:
        *args: Positional arguments (may include context dict)
        **kwargs: Keyword arguments including telegram_id, team_id, username, chat_type, player_id
                 Handles multiple parameter formats for robustness

    Returns:
        JSON formatted approval result or error message
    """
    try:
        # Extract context and tool parameters
        context_params, tool_params = extract_tool_parameters(*args, **kwargs)
        
        # Get context values
        telegram_id = context_params.get('telegram_id')
        team_id = context_params.get('team_id', '')
        username = context_params.get('username', 'user')
        chat_type = context_params.get('chat_type', 'main')
        
        # Get tool-specific parameters
        player_id = tool_params.get('player_id', '')
        
        # Validate required parameters
        validation_error = validate_required_context(context_params, ['telegram_id', 'team_id'])
        if validation_error:
            return create_tool_response(False, validation_error)
            
        if not player_id:
            return create_tool_response(
                False, 
                "Player ID is required for approval"
            )
        
        logger.info(f"🎯 Player approval request for {player_id} from {username} ({telegram_id}) in team {team_id}")

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



@tool("list_players_all")
async def list_players_all(*args, **kwargs) -> str:
    """
    Get players for the team (filtered by chat type).

    This tool serves as the application boundary for player listing functionality.
    It handles framework concerns and delegates business logic to the domain service.
    
    Chat Type Filtering:
    - Main chat: Shows only ACTIVE players
    - Leadership chat: Shows ALL players (including pending)

    Args:
        *args: Positional arguments (may include context dict)
        **kwargs: Keyword arguments including telegram_id, team_id, username, chat_type
                 Handles multiple parameter formats for robustness

    Returns:
        JSON formatted list of players (filtered by chat type)
    """
    try:
        # Extract context parameters
        context_params = extract_context_parameters(*args, **kwargs)
        
        # Get context values
        telegram_id = context_params.get('telegram_id')
        team_id = context_params.get('team_id', '')
        username = context_params.get('username', 'user')
        chat_type = context_params.get('chat_type', 'main')
        
        # Validate required parameters
        validation_error = validate_required_context(context_params, ['telegram_id', 'team_id'])
        if validation_error:
            return create_tool_response(False, validation_error)
        
        logger.info(f"📋 All players request from {username} ({telegram_id}) in team {team_id}")

        # Get domain service from container and delegate to domain function
        container = get_container()
        player_service = container.get_service(PlayerService)
        
        # Convert telegram_id to int if needed for domain service
        try:
            telegram_id_int = int(telegram_id) if telegram_id else None
        except (ValueError, TypeError):
            telegram_id_int = None
        
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
        logger.error(f"❌ Error listing all players for team {team_id}: {e}")
        return f"❌ Failed to get players: {e}"


@tool("list_players_active")
async def list_players_active(telegram_id: str, team_id: str, username: str, chat_type: str) -> str:
    """
    List all active players in the team.
    
    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: User's Telegram ID (string)
        team_id: Team ID
        username: Username of the requesting user
        chat_type: Chat type context
    
    Returns:
        Formatted list of active players or error message
    """
    try:
        # Validate required parameters
        validation_error = validate_required_strings(
            telegram_id, team_id, username, chat_type,
            names=["telegram_id", "team_id", "username", "chat_type"]
        )
        if validation_error:
            return validation_error
        
        # Convert telegram_id
        telegram_id_int = convert_telegram_id(telegram_id)
        if not telegram_id_int:
            return "❌ Invalid telegram_id format"
        
        logger.info(f"📋 Listing active players for team {team_id} by {username} ({telegram_id_int})")
        
        # Get container and services
        container = get_container()
        if not container._initialized:
            logger.warning("⚠️ Container not initialized, attempting to initialize...")
            try:
                await container.initialize()
                logger.info("✅ Container initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize container: {e}")
                return "❌ System is currently initializing. Please try again in a moment."
        
        player_service = container.get_service(PlayerService)
        if not player_service:
            return "❌ Player service is not available"
        
        # Get REAL data from database (no hallucination possible)
        players = await player_service.get_active_players(team_id)
        
        # Sanitize the response to prevent overwhelming output
        players = sanitize_list_response(players, max_items=20)
        
        if not players:
            return "📋 No active players found in the team."
        
        # Format ONLY the real data we have
        formatted_players = []
        for player in players:
            # Validate each player's data
            if hasattr(player, 'name') and hasattr(player, 'player_id'):
                formatted_players.append(f"• {player.name} ({player.player_id})")
            else:
                logger.warning(f"Skipping player with missing data: {player}")
        
        # Create response with ONLY validated data
        response = f"📋 Active Players ({len(formatted_players)}):\n" + "\n".join(formatted_players)
        
        # Format safely to prevent overflow
        response = format_safe_response(response, max_length=1500)
        
        logger.info(f"✅ Retrieved {len(formatted_players)} active players for team {team_id}")
        
        # Return formatted message for agent coordination
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in list_players_active: {e}")
        return f"❌ Error retrieving active players: {str(e)}"



# NOTE: list_team_members_and_players tool has been moved to team_administration module
# to avoid duplication and maintain clean architecture separation