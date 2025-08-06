"""
Helper System Tools

CrewAI tools for providing intelligent assistance and guidance to users.
"""

import uuid
from typing import Any

from loguru import logger

from kickai.core.dependency_container import get_container
from kickai.utils.crewai_tool_decorator import tool


def _generate_id(prefix: str = "help") -> str:
    """Generate a simple ID for helper system entities."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@tool("get_personalized_feature_recommendations")
async def get_personalized_feature_recommendations(user_id: str, team_id: str) -> str:
    """
    Get personalized feature recommendations for a user based on their learning profile.

    Args:
        user_id: The user's ID
        team_id: The team's ID

    Returns:
        Personalized feature recommendations
    """
    try:
        container = get_container()
        feature_service = container.get_service("IFeatureSuggestionService")

        # Get personalized feature suggestions
        suggestions = await feature_service.get_feature_suggestions(user_id, team_id)
        if suggestions:
            return "\n".join(suggestions)

        # Fallback to basic recommendations
        return (
            "🎯 Welcome to KICKAI! Here are some great features to start with:\n\n"
            + "• Player Management: Use /addplayer to add new team members\n"
            + "• Team Overview: Use /list to see all team members\n"
            + "• Help System: The system will proactively provide assistance when needed\n"
            + "• Status Check: Use /status to check player availability"
        )

    except Exception as e:
        logger.error(f"Error getting feature recommendations for user {user_id}: {e}")
        return "❌ Sorry, I encountered an error while getting recommendations. Please try again."


@tool("send_learning_reminder")
async def send_learning_reminder(
    user_id: str, team_id: str, reminder_type: str, message: str
) -> str:
    """
    Send a learning reminder to a user.

    Args:
        user_id: The user's ID
        team_id: The team's ID
        reminder_type: Type of reminder (task, feature, learning, best_practice)
        message: The reminder message

    Returns:
        Confirmation of reminder sent
    """
    try:
        container = get_container()
        reminder_service = container.get_service("IReminderService")

        # Create reminder
        await reminder_service.create_reminder(user_id, team_id, reminder_type, message)

        return f"✅ Learning reminder sent to user {user_id}: {message}"

    except Exception as e:
        logger.error(f"Error sending learning reminder to user {user_id}: {e}")
        return f"❌ Error sending reminder: {e}"


@tool("track_user_progress")
async def track_user_progress(user_id: str, team_id: str, action: str) -> str:
    """
    Track a user's progress for learning analytics.

    Args:
        user_id: The user's ID
        team_id: The team's ID
        action: The action being tracked

    Returns:
        Confirmation of progress tracked
    """
    try:
        container = get_container()
        user_analytics_service = container.get_service("IUserAnalyticsService")

        # Track the action
        await user_analytics_service.track_user_action(user_id, team_id, action)

        return f"✅ Progress tracked for user {user_id}: {action}"

    except Exception as e:
        logger.error(f"Error tracking progress for user {user_id}: {e}")
        return f"❌ Error tracking progress: {e}"


@tool("get_contextual_suggestions")
async def get_contextual_suggestions(user_id: str, team_id: str, context: str) -> str:
    """
    Get contextual suggestions based on user's current activity.

    Args:
        user_id: The user's ID
        team_id: The team's ID
        context: Context about the user's current activity

    Returns:
        Contextual suggestions
    """
    try:
        container = get_container()
        feature_service = container.get_service("IFeatureSuggestionService")

        # Get contextual suggestions
        suggestions = await feature_service.get_contextual_suggestions(user_id, team_id, context)
        if suggestions:
            return "💡 Contextual Tips:\n" + "\n".join([f"• {tip}" for tip in suggestions])

        return "💡 Continue exploring KICKAI features! The system will proactively provide assistance when needed."

    except Exception as e:
        logger.error(f"Error getting contextual suggestions for user {user_id}: {e}")
        return "❌ Error getting suggestions. Please try again."


@tool("format_help_response")
async def format_help_response(help_data: str) -> str:
    """
    Format help response with emojis and clear structure.

    Args:
        help_data: JSON string containing help information

    Returns:
        Formatted help response
    """
    try:
        import json

        help_dict = json.loads(help_data) if isinstance(help_data, str) else help_data

        container = get_container()
        guidance_service = container.get_service("IGuidanceService")

        return await guidance_service.format_help_response(help_dict)

    except Exception as e:
        logger.error(f"Error formatting help response: {e}")
        return "❌ Error formatting help response. Please try again."


@tool("send_proactive_notification")
async def send_proactive_notification(
    user_id: str, team_id: str, notification_type: str, message: str
) -> str:
    """
    Send a proactive notification to a user.

    Args:
        user_id: The user's ID
        team_id: The team's ID
        notification_type: Type of notification
        message: The notification message

    Returns:
        Confirmation of notification sent
    """
    try:
        container = get_container()
        reminder_service = container.get_service("IReminderService")

        # Send proactive suggestion
        suggestion = await reminder_service.send_proactive_suggestion(user_id, team_id, message)

        if suggestion:
            return f"✅ Proactive notification sent to user {user_id}: {suggestion}"
        else:
            return f"ℹ️ No proactive notification needed for user {user_id}"

    except Exception as e:
        logger.error(f"Error sending proactive notification to user {user_id}: {e}")
        return f"❌ Error sending notification: {e}"


@tool("get_learning_analytics")
async def get_learning_analytics(team_id: str, user_id: str = None) -> str:
    """
    Get learning analytics for a team or specific user.

    Args:
        team_id: The team's ID
        user_id: Optional user ID for user-specific analytics

    Returns:
        Learning analytics summary
    """
    try:
        container = get_container()

        if user_id:
            # Get user analytics
            user_analytics_service = container.get_service("IUserAnalyticsService")
            analytics = await user_analytics_service.get_user_analytics(user_id, team_id)
            return _format_user_analytics(analytics.to_dict())
        else:
            # Get team analytics
            learning_service = container.get_service("ILearningAnalyticsService")
            analytics = await learning_service.get_team_analytics(team_id)
            return _format_team_analytics(analytics.to_dict())

    except Exception as e:
        logger.error(f"Error getting learning analytics for team {team_id}: {e}")
        return "❌ Error getting analytics. Please try again."


@tool("celebrate_progress")
async def celebrate_progress(user_id: str, team_id: str, achievement: str) -> str:
    """
    Celebrate a user's progress or achievement.

    Args:
        user_id: The user's ID
        team_id: The team's ID
        achievement: Description of the achievement

    Returns:
        Celebration message
    """
    try:
        container = get_container()
        user_analytics_service = container.get_service("IUserAnalyticsService")

        # Get user profile for personalized celebration
        profile = await user_analytics_service.get_user_profile(user_id, team_id)
        if profile:
            level = profile.experience_level
            if level == "beginner":
                return f"🎉 Congratulations {user_id}! {achievement}\n\nKeep up the great work! You're making excellent progress as a beginner."
            elif level == "intermediate":
                return f"🚀 Amazing work {user_id}! {achievement}\n\nYou're becoming a KICKAI pro! Ready for advanced features?"
            elif level == "advanced":
                return f"🏆 Outstanding {user_id}! {achievement}\n\nYou're a KICKAI expert! Consider helping others learn."
            else:
                return f"👑 Legendary {user_id}! {achievement}\n\nYou're a KICKAI master! Thank you for being an inspiration."

        return f"🎉 Congratulations {user_id}! {achievement}\n\nKeep up the great work!"

    except Exception as e:
        logger.error(f"Error celebrating progress for user {user_id}: {e}")
        return f"🎉 Congratulations on your achievement: {achievement}!"


def _format_user_analytics(analytics: dict[str, Any]) -> str:
    """Format user analytics for display."""
    try:
        return f"""📊 User Analytics

Experience Level: {analytics.get("experience_level", "Unknown")}
Total Commands Used: {analytics.get("total_commands", 0)}
Unique Commands: {analytics.get("unique_commands", 0)}
Learning Velocity: {analytics.get("learning_velocity", 0):.2f}
Feature Adoption Rate: {analytics.get("feature_adoption_rate", 0):.1%}
Days Since Registration: {analytics.get("days_since_registration", 0)}

Most Used Commands:
{chr(10).join([f"• {cmd}" for cmd in analytics.get("most_used_commands", [])])}"""
    except Exception as e:
        logger.error(f"Error formatting user analytics: {e}")
        return "❌ Error formatting user analytics"


def _format_team_analytics(analytics: dict[str, Any]) -> str:
    """Format team analytics for display."""
    try:
        level_distribution = analytics.get("level_distribution", {})
        level_text = "\n".join(
            [f"• {level.title()}: {count}" for level, count in level_distribution.items()]
        )

        return f"""📊 Team Analytics

Total Users: {analytics.get("total_users", 0)}
Active Users: {analytics.get("active_users", 0)}
Average Commands Used: {analytics.get("avg_commands_used", 0):.1f}
Average Feature Adoption: {analytics.get("avg_feature_adoption", 0):.1%}

Experience Level Distribution:
{level_text}

Popular Commands:
{chr(10).join([f"• {cmd}" for cmd in analytics.get("popular_commands", [])])}"""
    except Exception as e:
        logger.error(f"Error formatting team analytics: {e}")
        return "❌ Error formatting team analytics"
