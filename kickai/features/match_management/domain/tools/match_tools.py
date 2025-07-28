#!/usr/bin/env python3
"""
Match Management Tools

This module provides tools for match creation, management, and squad selection.
These tools integrate with the existing match management services.
"""

import logging
from datetime import datetime

from kickai.utils.crewai_tool_decorator import tool

from kickai.core.dependency_container import get_container
from typing import Any, Dict, List, Optional
from kickai.features.match_management.domain.services.match_service import MatchService
from kickai.features.player_registration.domain.services.player_service import PlayerService
from kickai.features.match_management.domain.entities.match import Match, MatchStatus

logger = logging.getLogger(__name__)


@tool("create_match")
def create_match(
    team_id: str,
    opponent: str,
    date: str,
    time: str,
    venue: str = "Home",
    competition: str = "Friendly"
) -> str:
    """
    Create a new match for the team.
    
    Args:
        team_id: The team ID
        opponent: Opponent team name
        date: Match date (YYYY-MM-DD format)
        time: Match time (HH:MM format)
        venue: Match venue (Home/Away)
        competition: Competition type (Friendly, League, Cup, etc.)
    
    Returns:
        Confirmation message with match details
    """
    try:
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            logger.error("❌ MatchService not available")
            return "❌ Match service not available. Please try again later."
        
        # Parse date and time
        try:
            date_time_str = f"{date} {time}"
            match_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        except ValueError as e:
            logger.error(f"❌ Invalid date/time format: {e}")
            return "❌ Invalid date or time format. Please use YYYY-MM-DD HH:MM format."
        
        # Create match
        match = match_service.create_match(
            team_id=team_id,
            opponent=opponent,
            date=match_datetime,
            location=venue,
            status=MatchStatus.SCHEDULED,
            home_away=venue.lower(),
            competition=competition
        )
        
        logger.info(f"✅ Match created: {match.id} - {team_id} vs {opponent}")
        
        # Initialize attendance tracking for the match
        attendance_initialized = False
        try:
            from kickai.features.attendance_management.domain.services.attendance_service import AttendanceService
            attendance_service = container.get_service(AttendanceService)
            if attendance_service:
                attendance_records = attendance_service.initialize_match_attendance(match.id, team_id)
                attendance_initialized = len(attendance_records) > 0
                logger.info(f"✅ Attendance initialized for {len(attendance_records)} players")
        except Exception as e:
            logger.warning(f"Failed to initialize attendance: {e}")
        
        success_msg = f"""
🎉 **MATCH CREATED!**

⚽ **Match Details:**
• **Match ID:** {match.id}
• **Teams:** {team_id} vs {opponent}
• **Date:** {match_datetime.strftime('%A, %d %B %Y')}
• **Time:** {match_datetime.strftime('%H:%M')}
• **Venue:** {venue}
• **Competition:** {competition}

📋 **Next Steps:**
• Use `/selectsquad {match.id}` to select the match squad
• Use `/announce` to notify players about the match
• Use `/attendance {match.id}` to track attendance

🏆 **Match Status:** Scheduled"""

        if attendance_initialized:
            success_msg += f"""
✅ **Attendance:** Automatically initialized for all active players
💡 **Tip:** Players can now use `/markattendance` to mark their availability"""
        else:
            success_msg += f"""
⚠️ **Attendance:** Manual initialization may be required
💡 **Tip:** Use `/initialize_match_attendance {match.id}` if needed"""
        
        return success_msg.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to create match: {e}")
        return f"❌ Failed to create match: {e!s}"


@tool("get_match")
def get_match(match_id: str, team_id: str) -> str:
    """
    Get detailed information about a specific match.
    
    Args:
        match_id: The match ID
        team_id: The team ID
    
    Returns:
        Detailed match information
    """
    try:
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            logger.error("❌ MatchService not available")
            return "❌ Match service not available. Please try again later."
        
        match = match_service.get_match(match_id)
        
        if not match:
            return f"❌ Match not found: {match_id}"
        
        # Format match details
        match_date = datetime.fromisoformat(match.date.replace('Z', '+00:00'))
        
        match_info = f"""
⚽ **MATCH DETAILS**

📋 **Match ID:** {match.id}
🏆 **Competition:** {match.competition or 'Friendly'}
🏟️ **Venue:** {match.home_away or 'TBD'}
📅 **Date:** {match_date.strftime('%A, %d %B %Y')}
🕐 **Time:** {match_date.strftime('%H:%M')}
📍 **Location:** {match.location or 'TBD'}
📊 **Status:** {match.status}
"""
        
        if match.score:
            match_info += f"🎯 **Score:** {match.score}\n"
        
        match_info += f"""
📝 **Created:** {match.created_at or 'Unknown'}
🔄 **Last Updated:** {match.updated_at or 'Unknown'}
        """
        
        return match_info.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to get match: {e}")
        return f"❌ Failed to get match details: {e!s}"


@tool("list_matches")
def list_matches(team_id: str, status: str = "all") -> str:
    """
    List all matches for the team with optional status filter.
    
    Args:
        team_id: The team ID
        status: Match status filter (all, scheduled, completed, cancelled)
    
    Returns:
        List of matches with details
    """
    try:
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            logger.error("❌ MatchService not available")
            return "❌ Match service not available. Please try again later."
        
        # Get matches
        if status.lower() == "all":
            matches = match_service.list_matches(team_id)
        else:
            try:
                match_status = MatchStatus(status.lower())
                matches = match_service.list_matches(team_id, match_status)
            except ValueError:
                return f"❌ Invalid status: {status}. Valid options: all, scheduled, completed, cancelled"
        
        if not matches:
            return f"📋 No matches found for team {team_id}"
        
        # Sort matches by date
        matches.sort(key=lambda m: datetime.fromisoformat(m.date.replace('Z', '+00:00')))
        
        match_list = f"📋 **MATCHES FOR {team_id.upper()}**\n\n"
        
        for i, match in enumerate(matches, 1):
            match_date = datetime.fromisoformat(match.date.replace('Z', '+00:00'))
            
            match_list += f"""
**{i}. {match.opponent}** ({match.competition or 'Friendly'})
• **ID:** {match.id}
• **Date:** {match_date.strftime('%d/%m/%Y')}
• **Time:** {match_date.strftime('%H:%M')}
• **Venue:** {match.home_away or 'TBD'}
• **Status:** {match.status}
"""
            
            if match.score:
                match_list += f"• **Score:** {match.score}\n"
        
        return match_list.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to list matches: {e}")
        return f"❌ Failed to list matches: {e!s}"


@tool("update_match")
def update_match(match_id: str, team_id: str, updates: Dict[str, Any]) -> str:
    """
    Update match details.
    
    Args:
        match_id: The match ID
        team_id: The team ID
        updates: Dictionary of fields to update
    
    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            logger.error("❌ MatchService not available")
            return "❌ Match service not available. Please try again later."
        
        # Validate updates
        valid_fields = ['opponent', 'date', 'location', 'status', 'score', 'competition']
        invalid_fields = [field for field in updates.keys() if field not in valid_fields]
        
        if invalid_fields:
            return f"❌ Invalid fields: {', '.join(invalid_fields)}. Valid fields: {', '.join(valid_fields)}"
        
        # Update match
        updated_match = match_service.update_match(match_id, **updates)
        
        logger.info(f"✅ Match updated: {match_id}")
        
        return f"""
✅ **MATCH UPDATED!**

📋 **Match ID:** {match_id}
🔄 **Updated Fields:** {', '.join(updates.keys())}

Use `/matchdetails {match_id}` to view updated details.
        """.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to update match: {e}")
        return f"❌ Failed to update match: {e!s}"


@tool("delete_match")
def delete_match(match_id: str, team_id: str) -> str:
    """
    Delete a match.
    
    Args:
        match_id: The match ID
        team_id: The team ID
    
    Returns:
        Confirmation message
    """
    try:
        container = get_container()
        match_service = container.get_service(MatchService)
        
        if not match_service:
            logger.error("❌ MatchService not available")
            return "❌ Match service not available. Please try again later."
        
        # Delete match
        success = match_service.delete_match(match_id)
        
        if success:
            logger.info(f"✅ Match deleted: {match_id}")
            return f"✅ Match {match_id} has been deleted successfully."
        else:
            return f"❌ Failed to delete match {match_id}"
        
    except Exception as e:
        logger.error(f"❌ Failed to delete match: {e}")
        return f"❌ Failed to delete match: {e!s}"


@tool("get_available_players_for_match")
def get_available_players_for_match(match_id: str, team_id: str) -> str:
    """
    Get list of available players for a specific match.
    
    Args:
        match_id: The match ID
        team_id: The team ID
    
    Returns:
        List of available players with their details
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        match_service = container.get_service(MatchService)
        
        if not player_service or not match_service:
            logger.error("❌ Required services not available")
            return "❌ Player or match service not available. Please try again later."
        
        # Get match details
        match = match_service.get_match(match_id)
        if not match:
            return f"❌ Match not found: {match_id}"
        
        # Get all active players
        players = player_service.get_all_players(team_id)
        active_players = [p for p in players if p.status == "active"]
        
        if not active_players:
            return f"❌ No active players found for team {team_id}"
        
        # Format player list
        player_list = f"👥 **AVAILABLE PLAYERS FOR MATCH {match_id}**\n\n"
        player_list += f"📅 **Match:** {match.opponent} on {match.date}\n"
        player_list += f"👤 **Total Players:** {len(active_players)}\n\n"
        
        for i, player in enumerate(active_players, 1):
            player_list += f"""
**{i}. {player.full_name}**
• **ID:** {player.player_id}
• **Position:** {player.position}
• **Phone:** {player.phone_number}
• **Status:** {player.status}
"""
        
        player_list += f"""
📋 **Next Steps:**
• Use `/selectsquad {match_id}` to select the match squad
• Use `/attendance {match_id}` to track attendance
        """
        
        return player_list.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to get available players: {e}")
        return f"❌ Failed to get available players: {e!s}"


@tool("select_squad")
def select_squad(match_id: str, team_id: str, player_ids: List[str]) -> str:
    """
    Select squad for a match.
    
    Args:
        match_id: The match ID
        team_id: The team ID
        player_ids: List of player IDs to include in squad
    
    Returns:
        Confirmation message with squad details
    """
    try:
        container = get_container()
        player_service = container.get_service(PlayerService)
        match_service = container.get_service(MatchService)
        
        if not player_service or not match_service:
            logger.error("❌ Required services not available")
            return "❌ Player or match service not available. Please try again later."
        
        # Get match details
        match = match_service.get_match(match_id)
        if not match:
            return f"❌ Match not found: {match_id}"
        
        # Validate players
        all_players = player_service.get_all_players(team_id)
        valid_players = []
        invalid_players = []
        
        for player_id in player_ids:
            player = next((p for p in all_players if p.player_id == player_id), None)
            if player and player.status == "active":
                valid_players.append(player)
            else:
                invalid_players.append(player_id)
        
        if invalid_players:
            return f"❌ Invalid or inactive players: {', '.join(invalid_players)}"
        
        if not valid_players:
            return "❌ No valid players selected for squad"
        
        # Format squad details
        squad_info = f"""
🏆 **SQUAD SELECTED FOR MATCH {match_id}**

📅 **Match:** {match.opponent} on {match.date}
👥 **Squad Size:** {len(valid_players)} players

**Selected Players:**
"""
        
        for i, player in enumerate(valid_players, 1):
            squad_info += f"""
**{i}. {player.full_name}**
• **ID:** {player.player_id}
• **Position:** {player.position}
• **Phone:** {player.phone_number}
"""
        
        squad_info += f"""
📋 **Next Steps:**
• Use `/announce` to notify selected players
• Use `/attendance {match_id}` to track attendance
• Use `/remind` to send match reminders
        """
        
        logger.info(f"✅ Squad selected for match {match_id}: {len(valid_players)} players")
        
        return squad_info.strip()
        
    except Exception as e:
        logger.error(f"❌ Failed to select squad: {e}")
        return f"❌ Failed to select squad: {e!s}" 