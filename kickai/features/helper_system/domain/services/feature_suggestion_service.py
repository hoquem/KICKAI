"""
Feature Suggestion Service

Provides personalized feature suggestions and recommendations to users.
"""

from loguru import logger

from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile
from kickai.features.helper_system.domain.interfaces.feature_suggestion_service_interface import (
    IFeatureSuggestionService,
)
from kickai.features.helper_system.domain.repositories.learning_profile_repository_interface import (
    LearningProfileRepositoryInterface,
)


class FeatureSuggestionService(IFeatureSuggestionService):
    """Service for providing personalized feature suggestions."""

    def __init__(self, profile_repository: LearningProfileRepositoryInterface):
        self.profile_repository = profile_repository

    async def get_feature_suggestions(self, user_id: str, team_id: str) -> list[str]:
        """
        Get personalized feature suggestions for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            List of feature suggestions
        """
        try:
            # Get user's learning profile
            profile = await self.profile_repository.get_profile(user_id, team_id)
            if not profile:
                return self._get_beginner_suggestions()

            # Get suggestions based on user's level and usage
            suggestions = []

            if profile.experience_level == "beginner":
                suggestions = self._get_beginner_suggestions()
            elif profile.experience_level == "intermediate":
                suggestions = await self._get_intermediate_suggestions(profile)
            elif profile.experience_level == "advanced":
                suggestions = await self._get_advanced_suggestions(profile)
            elif profile.experience_level == "expert":
                suggestions = await self._get_expert_suggestions(profile)

            return suggestions[:5]  # Limit to 5 suggestions

        except Exception as e:
            logger.error(f"Error getting feature suggestions for user {user_id}: {e}")
            return self._get_beginner_suggestions()

    async def get_contextual_suggestions(
        self, user_id: str, team_id: str, current_context: str
    ) -> list[str]:
        """
        Get contextual suggestions based on current activity.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            current_context: Current activity context

        Returns:
            List of contextual suggestions
        """
        try:
            profile = await self.profile_repository.get_profile(user_id, team_id)
            if not profile:
                return ["💡 The system will proactively provide assistance when needed"]

            suggestions = []

            # Context-based suggestions
            if "player" in current_context.lower():
                suggestions.extend(
                    [
                        "👥 Try /list to see all team members",
                        "📊 Use /status to check player availability",
                    ]
                )

            if "match" in current_context.lower():
                suggestions.extend(
                    [
                        "🏟️ Use /creatematch to organize games",
                        "📋 Use /attendance to track availability",
                    ]
                )

            if "help" in current_context.lower():
                suggestions.extend(
                    [
                        "💡 The system will proactively provide assistance when needed",
                        "📚 The system will track your progress automatically",
                    ]
                )

            # Level-based suggestions
            if profile.experience_level == "beginner":
                suggestions.append("🎯 Start with basic commands like /list and /status")
            elif profile.experience_level == "intermediate":
                suggestions.append("🚀 Explore advanced features like match management")
            elif profile.experience_level == "advanced":
                suggestions.append("🎯 Optimize your workflows and help mentor others")

            return suggestions[:3]  # Limit to 3 contextual suggestions

        except Exception as e:
            logger.error(f"Error getting contextual suggestions for user {user_id}: {e}")
            return ["💡 The system will proactively provide assistance when needed"]

    async def get_workflow_suggestions(
        self, user_id: str, team_id: str, current_task: str
    ) -> list[str]:
        """
        Get workflow suggestions for a specific task.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            current_task: The current task being performed

        Returns:
            List of workflow suggestions
        """
        try:
            profile = await self.profile_repository.get_profile(user_id, team_id)
            if not profile:
                return ["💡 The system will proactively provide assistance when needed"]

            suggestions = []

            # Task-based workflow suggestions
            if "add" in current_task.lower():
                suggestions.extend(
                    [
                        "📋 After adding players, use /list to verify",
                        "📊 Use /status to check their availability",
                    ]
                )

            if "match" in current_task.lower():
                suggestions.extend(
                    ["📋 Use /attendance to track responses", "📢 Use /announce to send reminders"]
                )

            if "organize" in current_task.lower():
                suggestions.extend(
                    [
                        "📅 Use /creatematch for game scheduling",
                        "📊 Use /attendance for availability tracking",
                    ]
                )

            return suggestions[:3]  # Limit to 3 workflow suggestions

        except Exception as e:
            logger.error(f"Error getting workflow suggestions for user {user_id}: {e}")
            return ["💡 The system will proactively provide assistance when needed"]

    def _get_beginner_suggestions(self) -> list[str]:
        """Get suggestions for beginner users."""
        return [
            "🎯 **Player Management**: Use /addplayer to add new team members",
            "📋 **Team Overview**: Use /list to see all team members",
            "📊 **Status Check**: Use /status to check player availability",
            "💡 **Help System**: The system will proactively provide assistance when needed",
            "📚 **Learning**: The system will track your progress automatically",
        ]

    async def _get_intermediate_suggestions(self, profile: LearningProfile) -> list[str]:
        """Get suggestions for intermediate users."""
        suggestions = [
            "🏟️ **Match Management**: Use /creatematch to organize games",
            "📊 **Attendance Tracking**: Use /attendance to track availability",
            "📢 **Communication**: Use /announce to send team messages",
            "⏰ **Reminders**: Use /remind for important notifications",
        ]

        # Add personalized suggestions based on usage
        if profile.get_feature_adoption_rate() < 0.5:
            suggestions.append("🚀 **Advanced Features**: Explore analytics and automation")

        return suggestions

    async def _get_advanced_suggestions(self, profile: LearningProfile) -> list[str]:
        """Get suggestions for advanced users."""
        suggestions = [
            "📈 **Analytics**: Use advanced reporting features",
            "🔧 **Automation**: Set up automated workflows",
            "🏆 **Mentorship**: Help other team members learn",
            "⚙️ **Customization**: Configure advanced settings",
        ]

        return suggestions

    async def _get_expert_suggestions(self, profile: LearningProfile) -> list[str]:
        """Get suggestions for expert users."""
        suggestions = [
            "👑 **Leadership**: Mentor and guide other users",
            "🚀 **Innovation**: Explore cutting-edge features",
            "🔧 **Integration**: Connect with external systems",
            "📊 **Analytics**: Use advanced data insights",
        ]

        return suggestions
