#!/usr/bin/env python3
"""
Squad Selection and Availability Tools - Clean Architecture Application Layer

This module provides CrewAI tools for squad selection and availability management.
These tools serve as the application boundary and delegate to pure domain services.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.utils.tool_validation import create_tool_response


def _get_availability_service():
    """Get availability service from container with proper error handling."""
    try:
        from kickai.features.match_management.domain.interfaces.availability_service_interface import (
            IAvailabilityService,
        )

        container = get_container()
        service = container.get_service(IAvailabilityService)
        return service
    except Exception as e:
        logger.warning(f"Availability service not available: {e}")
        return None


def _get_match_service():
    """Get match service from container with proper error handling."""
    try:
        from kickai.features.match_management.domain.interfaces.match_service_interface import (
            IMatchService,
        )

        container = get_container()
        service = container.get_service(IMatchService)
        return service
    except Exception as e:
        logger.warning(f"Match service not available: {e}")
        return None


def _get_player_service():
    """Get player service from container with proper error handling."""
    try:
        from kickai.features.player_registration.domain.interfaces.player_service_interface import (
            IPlayerService,
        )

        container = get_container()
        service = container.get_service(IPlayerService)
        return service
    except Exception as e:
        logger.warning(f"Player service not available: {e}")
        return None


def _format_availability_status(status: str) -> str:
    """Format availability status with consistent emoji."""
    status_emoji = {
        "available": "✅",
        "unavailable": "❌",
        "maybe": "❓",
        "uncertain": "❓",
        "unknown": "❓",
    }
    if not status or not isinstance(status, str):
        return "❓"
    return status_emoji.get(status.lower().strip(), "❓")


def _validate_common_inputs(
    telegram_id: str, team_id: str, match_id: str | None = None
) -> tuple[int | None, str]:
    """Common input validation for tools to reduce duplication.

    Returns: (telegram_id_int or None, error_message)
    """
    if not telegram_id or not str(telegram_id).strip():
        return None, "User identification is required"

    if not team_id or not team_id.strip():
        return None, "Team ID is required"

    if match_id is not None and (not match_id or not match_id.strip()):
        return None, "Match ID is required"

    # Convert telegram_id to int with validation
    try:
        telegram_id_int = int(telegram_id)
        if telegram_id_int <= 0:
            return None, "Invalid user ID format"
        return telegram_id_int, ""
    except (ValueError, TypeError):
        return None, "Invalid user ID format"


@tool("select_squad_optimal")
async def select_squad_optimal(
    telegram_id: str, team_id: str, match_id: str, squad_size: int = 16
) -> str:
    """
    Analyze player availability and select optimal squad composition for a match.

    Business operation to evaluate available players and create balanced team lineup
    based on availability status, positions, and team formation requirements.

    Use when: Leadership needs to finalize squad selection for upcoming matches
    Required: Leadership privileges, match must exist, sufficient available players

    Returns: Optimal squad selection with chosen players, waiting list, and match details
    """
    try:
        # Enhanced input validation using common helper
        telegram_id_int, error_msg = _validate_common_inputs(telegram_id, team_id, match_id)
        if error_msg:
            return create_tool_response(False, error_msg)

        # Validate squad_size parameter for performance and business rules
        if squad_size < 11 or squad_size > 25:
            squad_size = 16  # Reset to default for football squads
            logger.info(f"Squad size adjusted to default: {squad_size}")

        logger.info(f"⚽ Squad selection request for {match_id} from player {telegram_id_int}")

        # Get required services
        availability_service = _get_availability_service()
        match_service = _get_match_service()

        if not availability_service or not match_service:
            return create_tool_response(False, "Required services are not available")

        # Get match details first
        try:
            match_details = await match_service.get_match_details(match_id, team_id)
            if not match_details:
                return create_tool_response(False, f"Match {match_id} not found")
        except Exception as e:
            return create_tool_response(False, f"Could not retrieve match details: {e}")

        # Get available players for the match
        try:
            available_players = await availability_service.get_available_players_for_match(
                match_id, team_id
            )
        except Exception:
            available_players = []

        if not available_players:
            opponent = getattr(match_details, "opponent", "TBD")
            return create_tool_response(
                True,
                "Operation completed successfully",
                data=f"📋 No players available for squad selection for match vs {opponent}",
            )

        # Select optimal squad (limited by squad_size or available players)
        max_selection = min(squad_size, len(available_players))

        # Sort players by priority with safe attribute access
        try:

            def safe_sort_key(player):
                """Safe sorting key function with fallback values."""
                try:
                    availability_priority = (
                        getattr(player, "availability_status", "") == "available"
                    )
                    priority_score = -getattr(player, "priority_score", 0)
                    registration_date = getattr(player, "registration_date", None) or "9999-12-31"
                    return (availability_priority, priority_score, registration_date)
                except Exception:
                    return (False, 0, "9999-12-31")  # Safe fallback

            available_players.sort(key=safe_sort_key, reverse=True)
        except Exception as e:
            logger.warning(f"Player sorting failed, using name fallback: {e}")
            # Safe fallback sorting
            try:
                available_players.sort(key=lambda p: getattr(p, "name", str(p)))
            except Exception:
                pass  # Keep original order if all sorting fails

        selected_squad = available_players[:max_selection]
        waiting_list = available_players[max_selection : max_selection + 5]  # Top 5 on waiting list

        # Format squad selection results
        opponent = getattr(match_details, "opponent", "TBD")
        match_date = getattr(match_details, "match_date", "TBD")
        location = getattr(match_details, "location", "TBD")

        result_lines = [
            "⚽ OPTIMAL SQUAD SELECTED",
            "",
            f"🆚 Match: vs {opponent}",
            f"📅 Date: {match_date}",
            f"📍 Location: {location}",
            "",
            f"👥 Selected Squad ({len(selected_squad)}/{squad_size})",
        ]

        for i, player in enumerate(selected_squad, 1):
            result_lines.extend(
                [
                    f"{i}. {getattr(player, 'name', 'Unknown')} ({player.availability_status})",
                    f"   ⚽ {getattr(player, 'position', 'Player')}",
                ]
            )

        if waiting_list:
            result_lines.extend(["", f"🔄 Waiting List ({len(waiting_list)})"])
            for i, player in enumerate(waiting_list, 1):
                result_lines.append(
                    f"{i}. {getattr(player, 'name', 'Unknown')} ({player.availability_status})"
                )

        result_lines.append(f"\n📊 Total Available: {len(available_players)} players")

        logger.info(
            f"✅ Squad selection completed for {match_id}: {len(selected_squad)} players selected"
        )
        return create_tool_response(True, "Squad selection completed", data="\n".join(result_lines))

    except Exception as e:
        logger.error(f"❌ Error selecting squad for {match_id}: {e}")
        return create_tool_response(False, f"Failed to select optimal squad: {e}")


@tool("list_players_available")
async def list_players_available(
    telegram_id: str, team_id: str, match_id: str | None = None, status_filter: str = "available"
) -> str:
    """
    Display players with availability status for squad planning and preparation.

    Business operation to show team players with their current availability status,
    positions, and submission details for match planning and squad selection.

    Use when: Planning squad composition for upcoming matches
    Required: Team must exist, user must have team access

    Returns: Player list with availability status, positions, and submission timestamps
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"👥 Available players request from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        # Get required services
        availability_service = _get_availability_service()
        player_service = _get_player_service()

        if not availability_service or not player_service:
            return create_tool_response(False, "Required services are not available")

        available_players = []

        if match_id:
            # Get availability for specific match
            try:
                players_with_availability = (
                    await availability_service.get_players_availability_for_match(match_id, team_id)
                )

                for player_availability in players_with_availability:
                    if (
                        status_filter == "all"
                        or player_availability.availability_status == status_filter
                    ):
                        available_players.append(
                            {
                                "name": getattr(
                                    player_availability,
                                    "player_name",
                                    player_availability.player_id,
                                ),
                                "availability_status": player_availability.availability_status,
                                "match_id": match_id,
                                "submitted_at": getattr(player_availability, "submitted_at", "N/A"),
                                "position": getattr(player_availability, "position", "Player"),
                            }
                        )
            except Exception as e:
                return create_tool_response(
                    False, f"Could not retrieve availability for match {match_id}: {e}"
                )
        else:
            # Get general player availability (all active players)
            try:
                all_players = await player_service.get_all_players(team_id)

                for player in all_players:
                    try:
                        latest_availability = (
                            await availability_service.get_player_latest_availability(
                                player.player_id, team_id
                            )
                        )

                        if latest_availability:
                            player_status = latest_availability.get("status", "unknown")
                            if status_filter == "all" or player_status == status_filter:
                                available_players.append(
                                    {
                                        "name": player.name,
                                        "availability_status": player_status,
                                        "match_id": "latest",
                                        "submitted_at": latest_availability.get("date", "N/A"),
                                        "position": getattr(player, "position", "Player"),
                                    }
                                )
                        else:
                            # No availability recorded
                            if status_filter == "all" or status_filter == "unknown":
                                available_players.append(
                                    {
                                        "name": player.name,
                                        "availability_status": "unknown",
                                        "match_id": "none",
                                        "submitted_at": "N/A",
                                        "position": getattr(player, "position", "Player"),
                                    }
                                )
                    except Exception:
                        # Handle individual player errors gracefully
                        continue
            except Exception as e:
                return create_tool_response(False, f"Could not retrieve player list: {e}")

        if not available_players:
            match_context = f" for match {match_id}" if match_id else ""
            return create_tool_response(
                True,
                "Operation completed successfully",
                data=f"📋 No players found with status '{status_filter}'{match_context}",
            )

        # Sort by name for consistent display
        available_players.sort(key=lambda x: x["name"].lower())

        # Format response
        match_context = f" for Match {match_id}" if match_id else " (Latest Status)"
        result_lines = [
            f"👥 Players Available{match_context} ({len(available_players)} total)",
            f"Filter: {status_filter}",
            "",
        ]

        for i, player in enumerate(available_players, 1):
            status_emoji = _format_availability_status(player["availability_status"])
            result_lines.extend(
                [
                    f"{i}. {status_emoji} {player['name']}",
                    f"   ⚽ {player['position']}",
                    f"   📊 Status: {player['availability_status']}",
                ]
            )
            if player["submitted_at"] != "N/A":
                result_lines.append(f"   📅 Submitted: {player['submitted_at']}")
            result_lines.append("")

        logger.info(f"✅ Listed {len(available_players)} available players")
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result_lines).strip()
        )

    except Exception as e:
        logger.error(f"❌ Error listing available players: {e}")
        return create_tool_response(False, f"Failed to list available players: {e}")


@tool("get_availability_summary")
async def get_availability_summary(telegram_id: str, team_id: str, match_id: str) -> str:
    """
    Provide detailed availability statistics and response summary for a match.

    Business operation to assess squad strength, response rates, and team participation
    patterns for comprehensive match planning and squad formation decisions.

    Use when: Assessing squad strength and response rates for match planning
    Required: Match must exist, user must have team access

    Returns: Detailed availability counts, response rates, and squad formation assessment
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"📊 Availability summary request for {match_id} from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        if not match_id.strip():
            return create_tool_response(False, "Match ID is required")

        # Get required services
        availability_service = _get_availability_service()
        match_service = _get_match_service()

        if not availability_service or not match_service:
            return create_tool_response(False, "Required services are not available")

        # Get match details
        try:
            match_details = await match_service.get_match_details(match_id, team_id)
            if not match_details:
                return create_tool_response(False, f"Match {match_id} not found")
        except Exception as e:
            return create_tool_response(False, f"Could not retrieve match details: {e}")

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

        # Format summary
        opponent = getattr(match_details, "opponent", "TBD")
        match_date = getattr(match_details, "match_date", "TBD")
        location = getattr(match_details, "location", "TBD")

        result_lines = [
            "📊 AVAILABILITY SUMMARY",
            "",
            f"🆚 Match: vs {opponent}",
            f"📅 Date: {match_date}",
            f"📍 Location: {location}",
            "",
            f"👥 Response Summary ({total_responses} responses)",
            f"✅ Available: {available_count} players",
            f"❌ Unavailable: {unavailable_count} players",
        ]

        if maybe_count > 0:
            result_lines.append(f"❓ Maybe: {maybe_count} players")

        # Calculate availability percentage
        if total_responses > 0:
            availability_percentage = (available_count / total_responses) * 100
            result_lines.append(f"\n📈 Availability Rate: {availability_percentage:.1f}%")

        # Squad formation capability assessment
        min_squad_size = 11  # Minimum for football
        if available_count >= min_squad_size:
            result_lines.append(
                f"\n⚽ Squad Formation: ✅ Sufficient players ({available_count} available)"
            )
        else:
            needed = min_squad_size - available_count
            result_lines.append(f"\n⚽ Squad Formation: ❌ Need {needed} more players")

        logger.info(f"✅ Availability summary generated for {match_id}")
        return create_tool_response(
            True, "Operation completed successfully", data="\n".join(result_lines)
        )

    except Exception as e:
        logger.error(f"❌ Error getting availability summary for {match_id}: {e}")
        return create_tool_response(False, f"Failed to get availability summary: {e}")


@tool("get_availability_player_self")
async def get_availability_player_self(
    telegram_id: str, team_id: str, match_id: str | None = None
) -> str:
    """
    Display current user's personal availability status for matches.

    Business operation to show player's own availability submissions and commitment
    status for specific matches or latest general availability status.

    Use when: Player wants to check their own availability submissions
    Required: User must be registered player in team

    Returns: Personal availability status with submission dates and notes
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"📊 Self availability check from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        # Get availability service
        availability_service = _get_availability_service()
        if not availability_service:
            return create_tool_response(False, "Availability service is not available")

        # Get player's availability
        player_id = str(telegram_id_int)

        try:
            if match_id:
                # Get availability for specific match
                availability = await availability_service.get_player_match_availability(
                    player_id, match_id, team_id
                )
                if not availability:
                    return create_tool_response(
                        True,
                        "Operation completed successfully",
                        data=f"❌ No availability recorded for match {match_id}",
                    )

                # Format specific match availability
                result_lines = [
                    "✅ Your Match Availability",
                    "",
                    f"⚙️ Match: {match_id}",
                    f"📊 Status: {availability.availability_status}",
                    f"📅 Submitted: {getattr(availability, 'submitted_at', 'N/A')}",
                ]
                if hasattr(availability, "notes") and availability.notes:
                    result_lines.append(f"📝 Notes: {availability.notes}")

                return create_tool_response(
                    True, "Operation completed successfully", data="\n".join(result_lines)
                )
            else:
                # Get latest availability
                latest_availability = await availability_service.get_player_latest_availability(
                    player_id, team_id
                )
                if not latest_availability:
                    return create_tool_response(
                        True,
                        "Operation completed successfully",
                        data="📊 No availability records found",
                    )

                # Format latest availability
                result_lines = [
                    "✅ Your Latest Availability",
                    "",
                    f"📊 Status: {latest_availability.get('status', 'unknown')}",
                    f"📅 Date: {latest_availability.get('date', 'N/A')}",
                    f"⚙️ Match: {latest_availability.get('match_id', 'N/A')}",
                ]
                if latest_availability.get("notes"):
                    result_lines.append(f"📝 Notes: {latest_availability.get('notes')}")

                return create_tool_response(
                    True, "Operation completed successfully", data="\n".join(result_lines)
                )

        except Exception as e:
            return create_tool_response(False, f"Could not retrieve your availability: {e}")

    except Exception as e:
        logger.error(f"❌ Error getting player availability: {e}")
        return create_tool_response(False, f"Failed to get player availability: {e}")


@tool("list_matches_upcoming")
async def list_matches_upcoming(telegram_id: str, team_id: str, limit: int = 10) -> str:
    """
    Display upcoming matches with comprehensive scheduling details.

    Business operation to show team's upcoming fixture list including opponents,
    dates, locations, and current status for match preparation planning.

    Use when: Planning squad selection for upcoming matches
    Required: Team must exist, user must have team access

    Returns: Upcoming matches list with scheduling details and match IDs for reference
    """
    try:
        # Convert telegram_id to int for domain operations
        telegram_id_int = int(telegram_id)
        logger.info(f"📅 Upcoming matches request from player {telegram_id_int}")

        # Validate required parameters
        if not team_id.strip():
            return create_tool_response(False, "Team ID is required")

        # Get match service
        match_service = _get_match_service()
        if not match_service:
            return create_tool_response(False, "Match service is not available")

        # Get upcoming matches
        try:
            upcoming_matches = await match_service.get_upcoming_matches(team_id, limit=limit)

            if not upcoming_matches:
                return create_tool_response(
                    True,
                    "Operation completed successfully",
                    data="📅 No upcoming matches scheduled",
                )

            # Format upcoming matches
            result_lines = [f"⚽ UPCOMING MATCHES ({len(upcoming_matches)} matches)", ""]

            for i, match in enumerate(upcoming_matches, 1):
                result_lines.extend(
                    [
                        f"{i}. 🆚 vs {getattr(match, 'opponent', 'TBD')}",
                        f"   📅 {getattr(match, 'match_date', 'TBD')}",
                        f"   📍 {getattr(match, 'location', 'TBD')}",
                        f"   📊 Status: {getattr(match, 'status', 'scheduled')}",
                    ]
                )
                if hasattr(match, "match_id"):
                    result_lines.append(f"   🆔 ID: {match.match_id}")
                result_lines.append("")

            logger.info(f"✅ Listed {len(upcoming_matches)} upcoming matches")
            return create_tool_response(
                True, "Operation completed successfully", data="\n".join(result_lines).strip()
            )

        except Exception as e:
            return create_tool_response(False, f"Could not retrieve upcoming matches: {e}")

    except Exception as e:
        logger.error(f"❌ Error listing upcoming matches: {e}")
        return create_tool_response(False, f"Failed to list upcoming matches: {e}")
