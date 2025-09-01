"""Squad Selection and Availability Tools - Clean Architecture Compliant

This module contains CrewAI tools for squad selection and availability management.
These tools follow the clean naming convention: [action]_[entity]_[modifier].
"""

from crewai.tools import tool
from kickai.core.dependency_container import get_container
from typing import Any
from datetime import datetime, timedelta


@tool("select_squad_optimal")
async def select_squad_optimal(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    match_id: str,
    squad_size: int = 16
) -> str:
    """Select optimal squad for a match based on availability and performance.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        match_id: Match to select squad for
        squad_size: Number of players to select (default 16)
    
    Returns:
        Formatted optimal squad selection
    """
    try:
        container = get_container()
        
        # Get services
        try:
            from kickai.features.match_management.domain.interfaces.availability_service_interface import IAvailabilityService
            from kickai.features.match_management.domain.interfaces.match_service_interface import IMatchService
            availability_service = container.get_service(IAvailabilityService)
            match_service = container.get_service(IMatchService)
        except Exception:
            return "❌ Squad or Availability service is not available"
        
        # Permission check
        if chat_type not in ["leadership", "private"]:
            return "❌ Squad selection requires leadership permissions"
        
        # Get match details first
        try:
            match_details = await match_service.get_match_details(match_id, team_id)
            if not match_details:
                return f"❌ Match {match_id} not found"
        except Exception:
            return f"❌ Could not retrieve match {match_id} details"
        
        # Get available players for the match
        try:
            available_players = await availability_service.get_available_players_for_match(
                match_id, team_id
            )
        except Exception:
            available_players = []
        
        if not available_players:
            return f"📋 No players available for squad selection for match vs {getattr(match_details, 'opponent', 'TBD')}"
        
        # Select optimal squad (limited by squad_size or available players)
        max_selection = min(squad_size, len(available_players))
        
        # Simple selection logic - prioritize by availability status and registration date
        try:
            available_players.sort(key=lambda p: (
                p.availability_status == "available",  # Available first
                -getattr(p, 'priority_score', 0),  # Higher priority first
                getattr(p, 'registration_date', datetime.min)  # Earlier registration first
            ), reverse=True)
        except:
            # Fallback sorting if attributes missing
            available_players.sort(key=lambda p: p.name)
        
        selected_squad = available_players[:max_selection]
        waiting_list = available_players[max_selection:max_selection+5]  # Top 5 on waiting list
        
        # Format squad selection results as plain text
        opponent = getattr(match_details, 'opponent', 'TBD')
        match_date = getattr(match_details, 'match_date', 'TBD')
        location = getattr(match_details, 'location', 'TBD')
        
        result_text = f"⚽ **Optimal Squad Selected**\n\n"
        result_text += f"🆚 Match: vs {opponent}\n"
        result_text += f"📅 Date: {match_date}\n"
        result_text += f"📍 Location: {location}\n\n"
        
        result_text += f"👥 **Selected Squad ({len(selected_squad)}/{squad_size})**\n"
        for i, player in enumerate(selected_squad, 1):
            result_text += f"{i}. {player.name} ({player.availability_status})\n"
            result_text += f"   ⚽ {getattr(player, 'position', 'Player')}\n"
        
        if waiting_list:
            result_text += f"\n🔄 **Waiting List ({len(waiting_list)})**\n"
            for i, player in enumerate(waiting_list, 1):
                result_text += f"{i}. {player.name} ({player.availability_status})\n"
        
        result_text += f"\n📊 Total Available: {len(available_players)} players"
        
        return result_text
        
    except Exception as e:
        return f"❌ Failed to select optimal squad: {str(e)}"


@tool("list_players_available")
async def list_players_available(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    match_id: str = None,
    status_filter: str = "available"
) -> str:
    """List players available for selection based on availability status.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        match_id: Specific match to check availability for (optional)
        status_filter: Filter by availability status (available/unavailable/all)
    
    Returns:
        Formatted list of available players
    """
    try:
        container = get_container()
        
        # Get services
        try:
            from kickai.features.match_management.domain.interfaces.availability_service_interface import IAvailabilityService
            from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
            availability_service = container.get_service(IAvailabilityService)
            player_service = container.get_service(IPlayerService)
        except Exception:
            return "❌ Availability or Player service is not available"
        
        available_players = []
        
        if match_id:
            # Get availability for specific match
            try:
                players_with_availability = await availability_service.get_players_availability_for_match(
                    match_id, team_id
                )
                
                for player_availability in players_with_availability:
                    if status_filter == "all" or player_availability.availability_status == status_filter:
                        available_players.append({
                            "name": getattr(player_availability, 'player_name', player_availability.player_id),
                            "availability_status": player_availability.availability_status,
                            "match_id": match_id,
                            "submitted_at": getattr(player_availability, 'submitted_at', 'N/A'),
                            "position": getattr(player_availability, 'position', 'Player')
                        })
            except Exception:
                return f"❌ Could not retrieve availability for match {match_id}"
        else:
            # Get general player availability (all active players)
            try:
                all_players = await player_service.get_all_players(team_id)
                
                for player in all_players:
                    # Get latest availability status
                    try:
                        latest_availability = await availability_service.get_player_latest_availability(
                            player.player_id, team_id
                        )
                        
                        if latest_availability:
                            player_status = latest_availability.get('status', 'unknown')
                            if status_filter == "all" or player_status == status_filter:
                                available_players.append({
                                    "name": player.name,
                                    "availability_status": player_status,
                                    "match_id": "latest",
                                    "submitted_at": latest_availability.get('date', 'N/A'),
                                    "position": getattr(player, 'position', 'Player')
                                })
                        else:
                            # No availability recorded
                            if status_filter == "all" or status_filter == "unknown":
                                available_players.append({
                                    "name": player.name,
                                    "availability_status": "unknown",
                                    "match_id": "none",
                                    "submitted_at": "N/A",
                                    "position": getattr(player, 'position', 'Player')
                                })
                    except:
                        # Handle individual player errors
                        continue
            except Exception:
                return "❌ Could not retrieve player list"
        
        if not available_players:
            match_context = f" for match {match_id}" if match_id else ""
            return f"📋 No players found with status '{status_filter}'{match_context}"
        
        # Sort by name
        available_players.sort(key=lambda x: x["name"].lower())
        
        # Format as clean text
        match_context = f" for Match {match_id}" if match_id else " (Latest Status)"
        result_text = f"👥 **Players Available{match_context}** ({len(available_players)} total)\n"
        result_text += f"Filter: {status_filter}\n\n"
        
        for i, player in enumerate(available_players, 1):
            status_emoji = "✅" if player["availability_status"] == "available" else "❌" if player["availability_status"] == "unavailable" else "❓"
            result_text += f"{i}. {status_emoji} {player['name']}\n"
            result_text += f"   ⚽ {player['position']}\n"
            result_text += f"   📊 Status: {player['availability_status']}\n"
            if player['submitted_at'] != 'N/A':
                result_text += f"   📅 Submitted: {player['submitted_at']}\n"
            result_text += "\n"
        
        return result_text.strip()
        
    except Exception as e:
        return f"❌ Failed to list available players: {str(e)}"


@tool("get_availability_summary")
async def get_availability_summary(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    match_id: str
) -> str:
    """Get availability summary for a specific match.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        match_id: Match to get availability summary for
    
    Returns:
        Formatted availability summary for the match
    """
    try:
        container = get_container()
        
        # Get services
        try:
            from kickai.features.match_management.domain.interfaces.availability_service_interface import IAvailabilityService
            from kickai.features.match_management.domain.interfaces.match_service_interface import IMatchService
            availability_service = container.get_service(IAvailabilityService)
            match_service = container.get_service(IMatchService)
        except Exception:
            return "❌ Required services are not available"
        
        # Get match details
        try:
            match_details = await match_service.get_match_details(match_id, team_id)
            if not match_details:
                return f"❌ Match {match_id} not found"
        except Exception:
            return f"❌ Could not retrieve match {match_id} details"
        
        # Get all availability responses for the match
        try:
            availability_responses = await availability_service.get_players_availability_for_match(
                match_id, team_id
            )
        except Exception:
            availability_responses = []
        
        # Count by status
        available_count = 0
        unavailable_count = 0
        maybe_count = 0
        total_responses = len(availability_responses)
        
        for response in availability_responses:
            status = response.availability_status.lower()
            if status == "available":
                available_count += 1
            elif status == "unavailable":
                unavailable_count += 1
            elif status in ["maybe", "uncertain"]:
                maybe_count += 1
        
        # Format summary as clean text
        opponent = getattr(match_details, 'opponent', 'TBD')
        match_date = getattr(match_details, 'match_date', 'TBD')
        location = getattr(match_details, 'location', 'TBD')
        
        summary_text = f"📊 **Availability Summary**\n\n"
        summary_text += f"🆚 Match: vs {opponent}\n"
        summary_text += f"📅 Date: {match_date}\n"
        summary_text += f"📍 Location: {location}\n\n"
        
        summary_text += f"👥 **Response Summary ({total_responses} responses)**\n"
        summary_text += f"✅ Available: {available_count} players\n"
        summary_text += f"❌ Unavailable: {unavailable_count} players\n"
        if maybe_count > 0:
            summary_text += f"❓ Maybe: {maybe_count} players\n"
        
        # Calculate availability percentage
        if total_responses > 0:
            availability_percentage = (available_count / total_responses) * 100
            summary_text += f"\n📈 Availability Rate: {availability_percentage:.1f}%"
        
        # Squad formation capability
        min_squad_size = 11  # Minimum for football
        if available_count >= min_squad_size:
            summary_text += f"\n⚽ Squad Formation: ✅ Sufficient players ({available_count} available)"
        else:
            needed = min_squad_size - available_count
            summary_text += f"\n⚽ Squad Formation: ❌ Need {needed} more players"
        
        return summary_text
        
    except Exception as e:
        return f"❌ Failed to get availability summary: {str(e)}"


@tool("get_availability_player")
async def get_availability_player(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_identifier: str = None,
    match_id: str = None
) -> str:
    """Get availability status for a specific player.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        player_identifier: Player ID, name, or phone (optional, uses telegram_id if not provided)
        match_id: Specific match to check (optional, gets latest if not provided)
    
    Returns:
        Formatted player availability information
    """
    try:
        container = get_container()
        
        # Get services
        try:
            from kickai.features.match_management.domain.interfaces.availability_service_interface import IAvailabilityService
            from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
            availability_service = container.get_service(IAvailabilityService)
            player_service = container.get_service(IPlayerService)
        except Exception:
            return "❌ Availability or Player service is not available"
        
        # Determine player to check
        if not player_identifier:
            # Get availability for requesting user
            player_id = str(telegram_id)
            player_name = username
        else:
            # Find player by identifier
            try:
                from kickai.utils.player_search_utils import find_player_by_identifier
                search_result = await find_player_by_identifier(
                    player_service, player_identifier, team_id
                )
                if not search_result:
                    return f"❌ Player '{player_identifier}' not found in team {team_id}"
                
                player_id = search_result.player.player_id
                player_name = search_result.player.name
            except Exception:
                return f"❌ Could not find player '{player_identifier}'"
        
        # Get player availability
        try:
            if match_id:
                # Get availability for specific match
                availability = await availability_service.get_player_match_availability(
                    player_id, match_id, team_id
                )
                if not availability:
                    return f"❌ No availability recorded for {player_name} for match {match_id}"
                
                # Format specific match availability
                availability_text = f"✅ **{player_name}** - Match Availability\n\n"
                availability_text += f"⚙️ Match: {match_id}\n"
                availability_text += f"📊 Status: {availability.availability_status}\n"
                availability_text += f"📅 Submitted: {getattr(availability, 'submitted_at', 'N/A')}\n"
                if hasattr(availability, 'notes') and availability.notes:
                    availability_text += f"📝 Notes: {availability.notes}\n"
                
                return availability_text
            else:
                # Get latest availability
                latest_availability = await availability_service.get_player_latest_availability(
                    player_id, team_id
                )
                if not latest_availability:
                    return f"📊 No availability records found for {player_name}"
                
                # Format latest availability
                availability_text = f"✅ **{player_name}** - Latest Availability\n\n"
                availability_text += f"📊 Status: {latest_availability.get('status', 'unknown')}\n"
                availability_text += f"📅 Date: {latest_availability.get('date', 'N/A')}\n"
                availability_text += f"⚙️ Match: {latest_availability.get('match_id', 'N/A')}\n"
                if latest_availability.get('notes'):
                    availability_text += f"📝 Notes: {latest_availability.get('notes')}\n"
                
                return availability_text
                
        except Exception:
            return f"❌ Could not retrieve availability for {player_name}"
        
    except Exception as e:
        return f"❌ Failed to get player availability: {str(e)}"


@tool("get_attendance_player_history")
async def get_attendance_player_history(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_identifier: str = None,
    limit: int = 10
) -> str:
    """Get attendance history for a specific player.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        player_identifier: Player ID, name, or phone (optional, uses telegram_id if not provided)
        limit: Number of records to return (default 10)
    
    Returns:
        Formatted player attendance history
    """
    try:
        container = get_container()
        
        # Get services
        try:
            from kickai.features.match_management.domain.interfaces.attendance_service_interface import IAttendanceService
            from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
            attendance_service = container.get_service(IAttendanceService)
            player_service = container.get_service(IPlayerService)
        except Exception:
            return "❌ Attendance or Player service is not available"
        
        # Determine player to check
        if not player_identifier:
            # Get attendance for requesting user
            player_id = str(telegram_id)
            player_name = username
        else:
            # Find player by identifier
            try:
                from kickai.utils.player_search_utils import find_player_by_identifier
                search_result = await find_player_by_identifier(
                    player_service, player_identifier, team_id
                )
                if not search_result:
                    return f"❌ Player '{player_identifier}' not found in team {team_id}"
                
                player_id = search_result.player.player_id
                player_name = search_result.player.name
            except Exception:
                return f"❌ Could not find player '{player_identifier}'"
        
        # Get player attendance history
        try:
            attendance_history = await attendance_service.get_player_attendance_history(
                player_id, team_id, limit=limit
            )
            
            if not attendance_history:
                return f"📊 No attendance history found for {player_name}"
            
            # Format attendance history as clean text
            history_text = f"📊 **Attendance History for {player_name}** ({len(attendance_history)} records)\n\n"
            
            for i, record in enumerate(attendance_history, 1):
                history_text += f"{i}. 📅 {getattr(record, 'match_date', 'N/A')}\n"
                history_text += f"   🆚 {getattr(record, 'opponent', 'Unknown')}\n"
                history_text += f"   📍 {getattr(record, 'location', 'TBD')}\n"
                attendance_status = getattr(record, 'attendance_status', 'unknown')
                status_emoji = "✅" if attendance_status == "present" else "❌" if attendance_status == "absent" else "❓"
                history_text += f"   {status_emoji} Status: {attendance_status}\n"
                if hasattr(record, 'recorded_at'):
                    history_text += f"   📤 Recorded: {record.recorded_at}\n"
                history_text += "\n"
            
            return history_text.strip()
            
        except Exception:
            return f"❌ Could not retrieve attendance history for {player_name}"
        
    except Exception as e:
        return f"❌ Failed to get attendance history: {str(e)}"


@tool("list_matches_upcoming")
async def list_matches_upcoming(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    limit: int = 10
) -> str:
    """List upcoming matches for the team.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        limit: Number of matches to return (default 10)
    
    Returns:
        Formatted list of upcoming matches
    """
    try:
        container = get_container()
        
        # Get match service
        try:
            from kickai.features.match_management.domain.interfaces.match_service_interface import IMatchService
            match_service = container.get_service(IMatchService)
        except Exception:
            return "❌ Match service is not available"
        
        # Get upcoming matches
        try:
            upcoming_matches = await match_service.get_upcoming_matches(team_id, limit=limit)
            
            if not upcoming_matches:
                return "📅 No upcoming matches scheduled"
            
            # Format upcoming matches as clean text
            matches_text = f"⚽ **Upcoming Matches** ({len(upcoming_matches)} matches)\n\n"
            
            for i, match in enumerate(upcoming_matches, 1):
                matches_text += f"{i}. 🆚 vs {getattr(match, 'opponent', 'TBD')}\n"
                matches_text += f"   📅 {getattr(match, 'match_date', 'TBD')}\n"
                matches_text += f"   📍 {getattr(match, 'location', 'TBD')}\n"
                matches_text += f"   📊 Status: {getattr(match, 'status', 'scheduled')}\n"
                if hasattr(match, 'match_id'):
                    matches_text += f"   🆔 ID: {match.match_id}\n"
                matches_text += "\n"
            
            return matches_text.strip()
            
        except Exception:
            return "❌ Could not retrieve upcoming matches"
        
    except Exception as e:
        return f"❌ Failed to list upcoming matches: {str(e)}"