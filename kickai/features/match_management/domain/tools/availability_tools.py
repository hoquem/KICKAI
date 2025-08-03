#!/usr/bin/env python3
"""
Availability Management Tools

This module provides tools for managing player availability for matches.
"""

from loguru import logger
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.core.exceptions import ServiceNotAvailableError
from kickai.utils.crewai_tool_decorator import tool
from kickai.utils.tool_helpers import (
    format_tool_error,
    sanitize_input,
    validate_required_input,
)


class ListMatchesInput(BaseModel):
    """Input model for list_matches tool."""

    team_id: str
    user_id: str
    period: str | None = None


@tool("list_matches")
def list_matches(team_id: str, user_id: str, period: str | None = None) -> str:
    """
    List matches for availability management.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        period: Time period (optional) - "upcoming", "past", "all", or None for upcoming

    Returns:
        List of matches or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        if period:
            period = sanitize_input(period, max_length=20)

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return format_tool_error("Match service not available")

        # List matches
        success, message = match_service.list_matches_sync(
            team_id=team_id, period=period
        )

        if success:
            period_text = f" ({period})" if period else " (upcoming)"
            return f"""📅 Matches{period_text}

{message}

💡 Use /matches [period] to view matches for specific periods"""
        else:
            return format_tool_error(f"Failed to list matches: {message}")

    except Exception as e:
        logger.error(f"Failed to list matches: {e}", exc_info=True)
        return format_tool_error(f"Failed to list matches: {e}") 