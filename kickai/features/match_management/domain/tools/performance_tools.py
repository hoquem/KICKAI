#!/usr/bin/env python3
"""
Performance Analysis Tools

This module provides tools for performance analysis and statistics.
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


class GetMatchStatisticsInput(BaseModel):
    """Input model for get_match_statistics tool."""

    team_id: str
    user_id: str
    match_id: str | None = None


class GetPlayerPerformanceInput(BaseModel):
    """Input model for get_player_performance tool."""

    team_id: str
    user_id: str
    player_id: str


class GetTeamPerformanceInput(BaseModel):
    """Input model for get_team_performance tool."""

    team_id: str
    user_id: str
    period: str | None = None


class AnalyzePerformanceTrendsInput(BaseModel):
    """Input model for analyze_performance_trends tool."""

    team_id: str
    user_id: str
    metric: str
    period: str


@tool("get_match_statistics")
def get_match_statistics(team_id: str, user_id: str, match_id: str | None = None) -> str:
    """
    Get match statistics for a specific match or recent matches.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        match_id: Match ID (optional) - if provided, shows only that match

    Returns:
        Match statistics summary or error
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
        if match_id:
            match_id = sanitize_input(match_id, max_length=50)

        # Get match service
        container = get_container()
        match_service = container.get_service("MatchService")

        if not match_service:
            return format_tool_error("Match service not available")

        # Get match statistics
        success, message = match_service.get_match_statistics_sync(
            team_id=team_id, match_id=match_id
        )

        if success:
            return f"""📊 Match Statistics

{message}

💡 Use /stats [match_id] to view specific match statistics"""
        else:
            return format_tool_error(f"Failed to get match statistics: {message}")

    except Exception as e:
        logger.error(f"Failed to get match statistics: {e}", exc_info=True)
        return format_tool_error(f"Failed to get match statistics: {e}")


@tool("get_player_performance")
def get_player_performance(team_id: str, user_id: str, player_id: str) -> str:
    """
    Get performance statistics for a specific player.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        player_id: Player ID to analyze

    Returns:
        Player performance summary or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(player_id, "Player ID")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        player_id = sanitize_input(player_id, max_length=50)

        # Get player service
        container = get_container()
        player_service = container.get_service("PlayerService")

        if not player_service:
            return format_tool_error("Player service not available")

        # Get player performance
        success, message = player_service.get_player_performance_sync(
            team_id=team_id, player_id=player_id
        )

        if success:
            return f"""🏃‍♂️ Player Performance Analysis

{message}

💡 Use /performance [player_id] to view detailed player statistics"""
        else:
            return format_tool_error(f"Failed to get player performance: {message}")

    except Exception as e:
        logger.error(f"Failed to get player performance: {e}", exc_info=True)
        return format_tool_error(f"Failed to get player performance: {e}")


@tool("get_team_performance")
def get_team_performance(team_id: str, user_id: str, period: str | None = None) -> str:
    """
    Get overall team performance statistics.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        period: Time period (optional) - "week", "month", "season", or None for all time

    Returns:
        Team performance summary or error
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

        # Get team service
        container = get_container()
        team_service = container.get_service("TeamService")

        if not team_service:
            return format_tool_error("Team service not available")

        # Get team performance
        success, message = team_service.get_team_performance_sync(
            team_id=team_id, period=period
        )

        if success:
            period_text = f" ({period})" if period else ""
            return f"""🏆 Team Performance Analysis{period_text}

{message}

💡 Use /teamstats [period] to view team performance for specific periods"""
        else:
            return format_tool_error(f"Failed to get team performance: {message}")

    except Exception as e:
        logger.error(f"Failed to get team performance: {e}", exc_info=True)
        return format_tool_error(f"Failed to get team performance: {e}")


@tool("analyze_performance_trends")
def analyze_performance_trends(team_id: str, user_id: str, metric: str, period: str) -> str:
    """
    Analyze performance trends for a specific metric over time.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        metric: Metric to analyze (goals, assists, wins, etc.)
        period: Time period for analysis (week, month, season)

    Returns:
        Performance trend analysis or error
    """
    try:
        # Validate inputs
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(metric, "Metric")
        if validation_error:
            return validation_error

        validation_error = validate_required_input(period, "Period")
        if validation_error:
            return validation_error

        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=50)
        user_id = sanitize_input(user_id, max_length=50)
        metric = sanitize_input(metric, max_length=50)
        period = sanitize_input(period, max_length=20)

        # Get analytics service
        container = get_container()
        analytics_service = container.get_service("AnalyticsService")

        if not analytics_service:
            return format_tool_error("Analytics service not available")

        # Analyze performance trends
        success, message = analytics_service.analyze_performance_trends_sync(
            team_id=team_id, metric=metric, period=period
        )

        if success:
            return f"""📈 Performance Trend Analysis

📊 Metric: {metric}
⏰ Period: {period}

{message}

💡 Use /trends [metric] [period] to analyze different performance metrics"""
        else:
            return format_tool_error(f"Failed to analyze performance trends: {message}")

    except Exception as e:
        logger.error(f"Failed to analyze performance trends: {e}", exc_info=True)
        return format_tool_error(f"Failed to analyze performance trends: {e}") 