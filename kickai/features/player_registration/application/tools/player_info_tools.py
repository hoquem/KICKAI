"""Player Information Tools - Clean Architecture Compliant

This module contains CrewAI tools for player information retrieval.
These tools follow the clean naming convention: [action]_[entity]_[modifier].
"""

from crewai.tools import tool
from kickai.core.dependency_container import get_container
from kickai.utils.player_search_utils import (
    find_player_by_identifier, 
    validate_player_identifier,
    format_search_suggestions,
    get_search_method_display
)
from typing import Any, Optional, Union, Dict
from loguru import logger


@tool("get_player_info")
async def get_player_info(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    player_identifier: str
) -> str:
    """
    Get detailed information about a specific player by ID, name, or phone number.
    
    Uses a comprehensive search strategy that tries multiple methods to find the player:
    1. Exact Player ID match
    2. Exact phone number match  
    3. Exact name match (case-insensitive)
    4. Partial name match (case-insensitive)
    
    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: Requesting user's Telegram ID (string)
        team_id: Team ID (required)
        username: Username for logging
        chat_type: Chat type context
        player_identifier: Player ID, name, or phone number to search for
        
    Returns:
        Formatted player information or error message
    """
    try:
        # Simple type conversion
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format provided"

        # Validate input parameters
        is_valid, error_msg = validate_player_identifier(player_identifier)
        if not is_valid:
            return f"❌ {error_msg}"
            
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
        
        logger.info(f"🔍 Getting player info for '{player_identifier}' in team {team_id} (user: {telegram_id_int})")
        
        # Get player service
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
        player_service = container.get_service(IPlayerService)
        
        # Use shared search utility
        search_result = await find_player_by_identifier(
            player_service, 
            player_identifier, 
            team_id
        )
        
        if not search_result:
            return f"❌ {format_search_suggestions(player_identifier, team_id)}"
        
        player = search_result.player
        
        # Build comprehensive player information
        player_data: Dict[str, Any] = {
            "player_id": player.player_id,
            "name": player.name,
            "phone": player.phone_number,
            "position": getattr(player, 'position', 'TBD'),
            "status": player.status.value if hasattr(player.status, 'value') else str(player.status),
            "team_id": player.team_id,
            "search_method": get_search_method_display(search_result.search_method),
            "created_at": str(getattr(player, 'created_at', 'N/A')),
            "last_updated": str(getattr(player, 'updated_at', 'N/A'))
        }
        
        # Format player info as clean text
        info_text = f"📋 **{player.name}** - Player Information\n\n"
        info_text += f"🆔 ID: {player_data['player_id']}\n"
        info_text += f"📞 Phone: {player_data['phone']}\n"
        info_text += f"⚽ Position: {player_data['position']}\n"
        info_text += f"📊 Status: {player_data['status']}\n"
        info_text += f"🔍 Found by: {player_data['search_method']}\n"
        info_text += f"📅 Created: {player_data['created_at']}\n"
        info_text += f"🔄 Updated: {player_data['last_updated']}"
        return info_text
        
    except Exception as e:
        logger.error(f"❌ Error getting player info for '{player_identifier}': {e}")
        return f"❌ Failed to retrieve player information: {str(e)}"


@tool("get_player_current_match")
async def get_player_current_match(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_id: str = None
) -> str:
    """Get player's current or upcoming match information.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        player_id: Specific player ID (optional, uses telegram_id if not provided)
    
    Returns:
        Formatted match information for the player
    """
    try:
        container = get_container()
        
        # Get match service
        try:
            match_service = container.get_service("MatchService")
        except Exception:
            return "❌ Match service is not available"
        
        # Use telegram_id if player_id not provided
        if not player_id:
            player_id = str(telegram_id)
        
        # Get player's current/upcoming matches
        matches = await match_service.get_matches_for_player(player_id, team_id)
        
        if not matches:
            return f"📅 No current or upcoming matches found for {username}"
        
        # Find current or next match
        current_match = None
        for match in matches:
            if match.status in ["upcoming", "in_progress"]:
                current_match = match
                break
        
        if current_match:
            match_text = f"⚽ **Current Match for {username}**\n\n"
            match_text += f"🆚 Opponent: {current_match.opponent}\n"
            match_text += f"📅 Date: {current_match.match_date.isoformat()}\n"
            match_text += f"📍 Location: {current_match.location}\n"
            match_text += f"📊 Status: {current_match.status}\n"
            if hasattr(current_match, 'player_availability'):
                match_text += f"✅ Your Availability: {current_match.player_availability}"
            return match_text
        else:
            return f"📅 No current or upcoming matches scheduled for {username}"
            
    except Exception as e:
        return f"❌ Failed to get player match information: {str(e)}"


@tool("list_team_combined")
async def list_team_combined(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    status: str = "all"
) -> str:
    """List both team members and players in a combined view.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        status: Filter by status ('all', 'active', 'pending')
    
    Returns:
        Formatted combined list of team members and players
    """
    try:
        container = get_container()
        
        # Get services
        try:
            team_service = container.get_service("TeamMemberService")
            from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
            player_service = container.get_service(IPlayerService)
        except Exception:
            return "❌ Team or Player service is not available"
        
        combined_list = []
        
        # Get team members
        try:
            team_members = await team_service.get_team_members_by_team(team_id)
            for member in team_members:
                if status == "all" or member.status == status:
                    combined_list.append({
                        "type": "team_member",
                        "name": member.name,
                        "role": member.role,
                        "status": member.status,
                        "phone": getattr(member, 'phone', '')
                    })
        except Exception:
            pass
        
        # Get players
        try:
            players = await player_service.get_all_players(team_id)
            for player in players:
                if status == "all" or player.status == status:
                    combined_list.append({
                        "type": "player",
                        "name": player.name,
                        "role": "Player",
                        "status": player.status,
                        "phone": getattr(player, 'phone', '')
                    })
        except Exception:
            pass
        
        # Sort by name
        combined_list.sort(key=lambda x: x["name"].lower())
        
        if not combined_list:
            return f"📋 No team members or players found (filter: {status})"
        
        # Format as clean text
        list_text = f"👥 **Combined Team List** ({len(combined_list)} total)\n"
        list_text += f"Filter: {status}\n\n"
        
        for i, member in enumerate(combined_list, 1):
            emoji = "👤" if member["type"] == "team_member" else "⚽"
            list_text += f"{i}. {emoji} {member['name']}\n"
            list_text += f"   📋 Role: {member['role']}\n"
            list_text += f"   📊 Status: {member['status']}\n"
            if member['phone']:
                list_text += f"   📞 Phone: {member['phone']}\n"
            list_text += "\n"
        
        return list_text.strip()
        
    except Exception as e:
        return f"❌ Failed to get combined team list: {str(e)}"


@tool("get_availability_player_history")
async def get_availability_player_history(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_id: str = None,
    limit: int = 10
) -> str:
    """Get player's availability history for past matches.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        player_id: Specific player ID (optional, uses telegram_id if not provided)
        limit: Number of records to return (default 10)
    
    Returns:
        Formatted availability history for the player
    """
    try:
        container = get_container()
        
        # Get availability service
        try:
            availability_service = container.get_service("AvailabilityService")
        except Exception:
            return "❌ Availability service is not available"
        
        # Use telegram_id if player_id not provided
        if not player_id:
            player_id = str(telegram_id)
        
        # Get player availability history
        history = await availability_service.get_player_availability_history(
            player_id, team_id, limit=limit
        )
        
        if not history:
            return f"📊 No availability history found for {username}"
        
        # Format history as clean text
        history_text = f"📊 **Availability History for {username}** ({len(history)} records)\n\n"
        
        for i, record in enumerate(history, 1):
            history_text += f"{i}. 📅 {record.match_date.isoformat() if hasattr(record, 'match_date') else 'N/A'}\n"
            history_text += f"   🆚 {getattr(record, 'opponent', 'Unknown')}\n"
            history_text += f"   📍 {getattr(record, 'location', 'TBD')}\n"
            history_text += f"   ✅ Status: {record.availability_status}\n"
            if hasattr(record, 'created_at'):
                history_text += f"   📤 Submitted: {record.created_at.isoformat()}\n"
            history_text += "\n"
        
        return history_text.strip()
        
    except Exception as e:
        return f"❌ Failed to get availability history: {str(e)}"


@tool("get_player_current_info")
async def get_player_current_info(telegram_id: str, team_id: str, username: str, chat_type: str) -> str:
    """
    Get current information for a player, including recent activity and status.
    
    If no player_identifier is provided, gets info for the requesting user.
    Uses the shared search utility for consistent player lookup behavior.
    
    Native CrewAI tool using simple string parameters.
    
    Args:
        telegram_id: Requesting user's Telegram ID (string)
        team_id: Team ID (required)  
        username: Username for logging
        chat_type: Chat type context
        
    Returns:
        Formatted current player information
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
        
        # No player_identifier provided, get info for requesting user
        player_identifier = None

        # Validate required parameters
        if not team_id or not team_id.strip():
            return "❌ Team ID is required"
            
        container = get_container()
        from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
        player_service = container.get_service(IPlayerService)
        player = None
        search_method = "telegram_id"
        
        # If no identifier provided, get info for requesting user
        if not player_identifier:
            try:
                player = await player_service.get_player_by_telegram_id(telegram_id_int, team_id)
                if not player:
                    return "❌ You are not registered as a player in this team"
            except Exception as e:
                logger.error(f"❌ Error getting player by telegram_id {telegram_id_int}: {e}")
                return f"❌ Failed to retrieve your player information: {str(e)}"
        else:
            # Validate the provided identifier
            is_valid, error_msg = validate_player_identifier(player_identifier)
            if not is_valid:
                return f"❌ {error_msg}"
            
            # Use shared search utility for other players
            search_result = await find_player_by_identifier(
                player_service, 
                player_identifier, 
                team_id
            )
            
            if not search_result:
                return f"❌ {format_search_suggestions(player_identifier, team_id)}"
            
            player = search_result.player
            search_method = get_search_method_display(search_result.search_method)
        
        logger.info(f"🔍 Getting current info for player {player.name} ({player.player_id})")
        
        # Format current info as clean text
        info_text = f"📋 **Current Information for {player.name}**\n\n"
        info_text += f"🆔 ID: {player.player_id}\n"
        info_text += f"📞 Phone: {player.phone_number}\n"
        info_text += f"⚽ Position: {getattr(player, 'position', 'TBD')}\n"
        status_value = player.status.value if hasattr(player.status, 'value') else str(player.status)
        info_text += f"📊 Status: {status_value}\n"
        is_active = status_value.lower() == 'active'
        info_text += f"✅ Active: {'Yes' if is_active else 'No'}\n"
        
        # Try to get recent availability (optional)
        try:
            availability_service = container.get_availability_service()
            recent_availability = await availability_service.get_player_latest_availability(
                player.player_id, team_id
            )
            if recent_availability:
                info_text += f"📅 Last Availability: {recent_availability.get('date', 'N/A')}\n"
                info_text += f"✅ Availability Status: {recent_availability.get('status', 'unknown')}\n"
        except:
            info_text += f"📅 Last Availability: N/A\n"
        
        # Try to get upcoming matches (optional)
        try:
            match_service = container.get_match_service()
            upcoming_matches = await match_service.get_upcoming_matches(team_id, limit=3)
            match_count = len(upcoming_matches) if upcoming_matches else 0
            info_text += f"⚽ Upcoming Matches: {match_count}"
        except:
            info_text += f"⚽ Upcoming Matches: 0"
        
        return info_text
        
    except Exception as e:
        logger.error(f"❌ Error getting current player info: {e}")
        return f"❌ Failed to retrieve current player information: {str(e)}"