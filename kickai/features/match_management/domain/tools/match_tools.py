#!/usr/bin/env python3
"""
Match Tools

This module provides tools for match management operations.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.features.match_management.domain.services.match_service import MatchService
from kickai.utils.json_helper import json_error, json_response
from kickai.utils.tool_helpers import (
    validate_required_input,
)
from kickai.utils.validation_utils import (
    validate_team_id,
)


@tool("list_matches")
def list_matches(team_id: str, status: str | None = None, limit: int = 10) -> str:
    """
    List matches for a team.


        team_id: Team ID (required) - available from context
        status: Optional status filter (e.g., "upcoming", "completed", "cancelled")
        limit: Maximum number of matches to return (default: 10)


    :return: JSON response with list of matches
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'team_id': team_id, 'status': status, 'limit': limit}


        # Get service
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return json_error(message="MatchService is not available", error_type="Service unavailable")

        # Get matches
        matches = match_service.get_matches_sync(team_id, status=status, limit=limit)

        if matches:
            matches_data = []
            ui_format = f"📅 **Matches for Team {team_id}**\n\n"

            for match in matches:
                status_emoji = "🟢" if match.status == "upcoming" else "🔴" if match.status == "completed" else "🟡"
                ui_format += f"{status_emoji} **{match.opponent}** - {match.date.strftime('%Y-%m-%d %H:%M') if match.date else 'TBD'}\n"
                ui_format += f"   📍 {match.location}\n"
                ui_format += f"   📊 Status: {match.status.title()}\n\n"

                matches_data.append({
                    'match_id': match.match_id,
                    'opponent': match.opponent,
                    'date': match.date.isoformat() if match.date else None,
                    'location': match.location,
                    'status': match.status
                })

            data = {
                'team_id': team_id,
                'status_filter': status,
                'matches': matches_data,
                'total_count': len(matches)
            }

            return json_response(data=data, ui_format=ui_format)
        else:
            data = {
                'team_id': team_id,
                'status_filter': status,
                'matches': [],
                'total_count': 0
            }
            return json_response(data=data, ui_format="📅 No matches found for this team.")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_matches: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to list matches: {e}")
        return json_error(message=f"Failed to list matches: {e}", error_type="Operation failed")

@tool("create_match")
def create_match(team_id: str, opponent: str, date: str, location: str) -> str:
    """
    Create a new match.


        team_id: Team ID (required) - available from context
        opponent: Opponent team name
        date: Match date (YYYY-MM-DD HH:MM format)
        location: Match location


    :return: JSON response with match creation status
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)
        opponent = validate_required_input(opponent, "Opponent")
        date = validate_required_input(date, "Date")
        location = validate_required_input(location, "Location")

        # Log tool execution start
        inputs = {'team_id': team_id, 'opponent': opponent, 'date': date, 'location': location}


        # Get service
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return json_error(message="MatchService is not available", error_type="Service unavailable")

        # Create match
        match = match_service.create_match_sync(team_id, opponent, date, location)

        if match:
            data = {
                'match_id': match.match_id,
                'team_id': team_id,
                'opponent': match.opponent,
                'date': match.date.isoformat() if match.date else None,
                'location': match.location,
                'status': match.status
            }

            ui_format = f"✅ **Match Created Successfully!**\n\n🏆 **Match ID**: {match.match_id}\n👥 **Opponent**: {match.opponent}\n📅 **Date**: {match.date.strftime('%Y-%m-%d %H:%M') if match.date else 'TBD'}\n📍 **Location**: {match.location}\n📊 **Status**: {match.status.title()}"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message="Failed to create match", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in create_match: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to create match: {e}")
        return json_error(message=f"Failed to create match: {e}", error_type="Operation failed")

@tool("list_matches_sync")
def list_matches_sync(team_id: str, status: str | None = None, limit: int = 10) -> str:
    """
    List matches synchronously for a team.


        team_id: Team ID (required) - available from context
        status: Optional status filter (e.g., "upcoming", "completed", "cancelled")
        limit: Maximum number of matches to return (default: 10)


    :return: JSON response with list of matches
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'team_id': team_id, 'status': status, 'limit': limit}


        # Get service
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return json_error(message="MatchService is not available", error_type="Service unavailable")

        # Get matches synchronously
        matches = match_service.get_matches_sync(team_id, status=status, limit=limit)

        if matches:
            matches_data = []
            ui_format = f"📅 **Matches for Team {team_id}**\n\n"

            for match in matches:
                status_emoji = "🟢" if match.status == "upcoming" else "🔴" if match.status == "completed" else "🟡"
                ui_format += f"{status_emoji} **{match.opponent}** - {match.date.strftime('%Y-%m-%d %H:%M') if match.date else 'TBD'}\n"
                ui_format += f"   📍 {match.location}\n"
                ui_format += f"   📊 Status: {match.status.title()}\n\n"

                matches_data.append({
                    'match_id': match.match_id,
                    'opponent': match.opponent,
                    'date': match.date.isoformat() if match.date else None,
                    'location': match.location,
                    'status': match.status
                })

            data = {
                'team_id': team_id,
                'status_filter': status,
                'matches': matches_data,
                'total_count': len(matches)
            }

            return json_response(data=data, ui_format=ui_format)
        else:
            data = {
                'team_id': team_id,
                'status_filter': status,
                'matches': [],
                'total_count': 0
            }
            return json_response(data=data, ui_format="📅 No matches found for this team.")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in list_matches_sync: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to list matches: {e}")
        return json_error(message=f"Failed to list matches: {e}", error_type="Operation failed")

@tool("get_match_details")
def get_match_details(match_id: str, team_id: str) -> str:
    """
    Get detailed information about a specific match.


        match_id: Match ID (required) - available from context
        team_id: Team ID (required) - available from context


    :return: JSON response with match details
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        match_id = validate_required_input(match_id, "Match ID")
        team_id = validate_team_id(team_id)

        # Log tool execution start
        inputs = {'match_id': match_id, 'team_id': team_id}


        # Get service
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return json_error(message="MatchService is not available", error_type="Service unavailable")

        # Get match details
        match = match_service.get_match_sync(match_id, team_id)

        if match:
            data = {
                'match_id': match.match_id,
                'team_id': team_id,
                'opponent': match.opponent,
                'date': match.date.isoformat() if match.date else None,
                'location': match.location,
                'status': match.status,
                'squad_size': match.squad_size if hasattr(match, 'squad_size') else None,
                'notes': match.notes if hasattr(match, 'notes') else None
            }

            ui_format = f"⚽ **Match Details**\n\n🏆 **Match ID**: {match.match_id}\n👥 **Opponent**: {match.opponent}\n📅 **Date**: {match.date.strftime('%Y-%m-%d %H:%M') if match.date else 'TBD'}\n📍 **Location**: {match.location}\n📊 **Status**: {match.status.title()}"

            if hasattr(match, 'squad_size') and match.squad_size:
                ui_format += f"\n👥 **Squad Size**: {match.squad_size}"

            if hasattr(match, 'notes') and match.notes:
                ui_format += f"\n📝 **Notes**: {match.notes}"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message=f"Match {match_id} not found", error_type="Match not found")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in get_match_details: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to get match details: {e}")
        return json_error(message=f"Failed to get match details: {e}", error_type="Operation failed")

@tool("select_squad_tool")
def select_squad_tool(match_id: str, team_id: str, player_ids: list) -> str:
    """
    Select squad for a match.


        match_id: Match ID (required) - available from context
        team_id: Team ID (required) - available from context
        player_ids: List of player IDs to include in squad


    :return: JSON response with squad selection status
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        match_id = validate_required_input(match_id, "Match ID")
        team_id = validate_team_id(team_id)

        if not player_ids or not isinstance(player_ids, list):
            return json_error(message="Player IDs list is required", error_type="Validation failed")

        # Log tool execution start
        inputs = {'match_id': match_id, 'team_id': team_id, 'player_ids': player_ids}


        # Get service
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return json_error(message="MatchService is not available", error_type="Service unavailable")

        # Select squad
        success = match_service.select_squad_sync(match_id, team_id, player_ids)

        if success:
            data = {
                'match_id': match_id,
                'team_id': team_id,
                'player_ids': player_ids,
                'squad_size': len(player_ids),
                'status': 'squad_selected'
            }

            ui_format = f"✅ **Squad Selected Successfully!**\n\n🏆 **Match ID**: {match_id}\n👥 **Squad Size**: {len(player_ids)} players\n📋 **Selected Players**: {', '.join(player_ids)}"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message="Failed to select squad", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in select_squad_tool: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to select squad: {e}")
        return json_error(message=f"Failed to select squad: {e}", error_type="Operation failed")

@tool("record_match_result")
def record_match_result(match_id: str, team_id: str, result: str, score: str | None = None) -> str:
    """
    Record the result of a match.


        match_id: Match ID (required) - available from context
        team_id: Team ID (required) - available from context
        result: Match result (win, loss, draw)
        score: Optional score (e.g., "2-1")


    :return: JSON response with match result recording status
    :rtype: str  # TODO: Fix type
    """
    try:
        # Validate inputs
        match_id = validate_required_input(match_id, "Match ID")
        team_id = validate_team_id(team_id)
        result = validate_required_input(result, "Result")

        # Log tool execution start
        inputs = {'match_id': match_id, 'team_id': team_id, 'result': result, 'score': score}


        # Get service
        container = get_container()
        match_service = container.get_service(MatchService)

        if not match_service:
            return json_error(message="MatchService is not available", error_type="Service unavailable")

        # Record match result
        success = match_service.record_result_sync(match_id, team_id, result, score)

        if success:
            data = {
                'match_id': match_id,
                'team_id': team_id,
                'result': result,
                'score': score,
                'status': 'result_recorded'
            }

            result_emoji = "🏆" if result == "win" else "😔" if result == "loss" else "🤝"
            ui_format = f"{result_emoji} **Match Result Recorded!**\n\n🏆 **Match ID**: {match_id}\n📊 **Result**: {result.title()}"

            if score:
                ui_format += f"\n⚽ **Score**: {score}"

            return json_response(data=data, ui_format=ui_format)
        else:
            return json_error(message="Failed to record match result", error_type="Operation failed")

    except ServiceNotAvailableError as e:
        logger.error(f"Service not available in record_match_result: {e}")
        return json_error(message=f"Service temporarily unavailable: {e.message}", error_type="Service unavailable")
    except Exception as e:
        logger.error(f"Failed to record match result: {e}")
        return json_error(message=f"Failed to record match result: {e}", error_type="Operation failed")
