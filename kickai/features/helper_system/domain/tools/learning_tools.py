#!/usr/bin/env python3
"""
Learning Agent Tools

This module provides tools for learning and system optimization.
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


class AnalyzeInteractionPatternsInput(BaseModel):
    """Input model for analyze_interaction_patterns tool."""

    team_id: str
    user_id: str
    period: str | None = None


class GetSystemPerformanceMetricsInput(BaseModel):
    """Input model for get_system_performance_metrics tool."""

    team_id: str
    user_id: str
    metric_type: str | None = None


class GenerateLearningInsightsInput(BaseModel):
    """Input model for generate_learning_insights tool."""

    team_id: str
    user_id: str
    insight_type: str | None = None


@tool("analyze_interaction_patterns")
def analyze_interaction_patterns(team_id: str, user_id: str, period: str | None = None) -> str:
    """
    Analyze user interaction patterns to identify trends and optimization opportunities.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        period: Time period (optional) - "day", "week", "month", or None for all time

    Returns:
        Interaction pattern analysis or error
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

        # Get learning service
        container = get_container()
        learning_service = container.get_service("LearningService")

        if not learning_service:
            return format_tool_error("Learning service not available")

        # Analyze interaction patterns
        success, message = learning_service.analyze_interaction_patterns_sync(
            team_id=team_id, period=period
        )

        if success:
            period_text = f" ({period})" if period else ""
            return f"""🧠 Interaction Pattern Analysis{period_text}

{message}

💡 Use /patterns [period] to analyze interaction patterns for specific periods"""
        else:
            return format_tool_error(f"Failed to analyze interaction patterns: {message}")

    except Exception as e:
        logger.error(f"Failed to analyze interaction patterns: {e}", exc_info=True)
        return format_tool_error(f"Failed to analyze interaction patterns: {e}")


@tool("get_system_performance_metrics")
def get_system_performance_metrics(
    team_id: str, user_id: str, metric_type: str | None = None
) -> str:
    """
    Get system performance metrics to monitor system health and efficiency.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        metric_type: Type of metrics (optional) - "response_time", "accuracy", "usage", or None for all

    Returns:
        System performance metrics or error
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
        if metric_type:
            metric_type = sanitize_input(metric_type, max_length=50)

        # Get monitoring service
        container = get_container()
        monitoring_service = container.get_service("MonitoringService")

        if not monitoring_service:
            return format_tool_error("Monitoring service not available")

        # Get system performance metrics
        success, message = monitoring_service.get_system_performance_metrics_sync(
            team_id=team_id, metric_type=metric_type
        )

        if success:
            metric_text = f" ({metric_type})" if metric_type else ""
            return f"""📊 System Performance Metrics{metric_text}

{message}

💡 Use /metrics [type] to view specific performance metrics"""
        else:
            return format_tool_error(f"Failed to get system performance metrics: {message}")

    except Exception as e:
        logger.error(f"Failed to get system performance metrics: {e}", exc_info=True)
        return format_tool_error(f"Failed to get system performance metrics: {e}")


@tool("generate_learning_insights")
def generate_learning_insights(
    team_id: str, user_id: str, insight_type: str | None = None
) -> str:
    """
    Generate learning insights and recommendations for system improvement.

    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        insight_type: Type of insights (optional) - "user_behavior", "system_optimization", "feature_usage", or None for all

    Returns:
        Learning insights and recommendations or error
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
        if insight_type:
            insight_type = sanitize_input(insight_type, max_length=50)

        # Get learning service
        container = get_container()
        learning_service = container.get_service("LearningService")

        if not learning_service:
            return format_tool_error("Learning service not available")

        # Generate learning insights
        success, message = learning_service.generate_learning_insights_sync(
            team_id=team_id, insight_type=insight_type
        )

        if success:
            insight_text = f" ({insight_type})" if insight_type else ""
            return f"""🎯 Learning Insights{insight_text}

{message}

💡 Use /insights [type] to generate specific types of insights"""
        else:
            return format_tool_error(f"Failed to generate learning insights: {message}")

    except Exception as e:
        logger.error(f"Failed to generate learning insights: {e}", exc_info=True)
        return format_tool_error(f"Failed to generate learning insights: {e}") 