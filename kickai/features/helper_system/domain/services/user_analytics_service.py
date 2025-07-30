"""
User Analytics Service

Handles user-specific analytics and progress tracking.
"""

from loguru import logger

from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile
from kickai.features.helper_system.domain.interfaces.user_analytics_service_interface import (
    IUserAnalyticsService,
)
from kickai.features.helper_system.domain.repositories.learning_profile_repository_interface import (
    LearningProfileRepositoryInterface,
)
from kickai.features.helper_system.domain.value_objects.analytics_value_objects import UserAnalytics


class UserAnalyticsService(IUserAnalyticsService):
    """Service for user-specific analytics and progress tracking."""

    def __init__(self, profile_repository: LearningProfileRepositoryInterface):
        self.profile_repository = profile_repository

    async def get_user_profile(self, user_id: str, team_id: str) -> LearningProfile | None:
        """
        Get user's learning profile, creating one if it doesn't exist.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            LearningProfile if found or created, None otherwise
        """
        try:
            profile = await self.profile_repository.get_profile(user_id, team_id)

            if not profile:
                # Create new profile
                profile = LearningProfile(user_id=user_id, team_id=team_id)
                await self.profile_repository.save_profile(profile)

            return profile

        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            return None

    async def get_user_analytics(self, user_id: str, team_id: str) -> UserAnalytics:
        """
        Get analytics for a specific user.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            UserAnalytics value object containing user analytics
        """
        try:
            profile = await self.get_user_profile(user_id, team_id)

            if not profile:
                return UserAnalytics(
                    experience_level="beginner",
                    total_commands=0,
                    unique_commands=0,
                    learning_velocity=0,
                    help_requests=0,
                    feature_adoption_rate=0,
                    most_used_commands=[],
                    days_since_registration=0,
                )

            return UserAnalytics(
                experience_level=profile.experience_level,
                total_commands=profile.progress_metrics.total_commands_used,
                unique_commands=profile.progress_metrics.unique_commands_used,
                learning_velocity=profile.progress_metrics.learning_velocity,
                help_requests=profile.progress_metrics.help_requests_count,
                feature_adoption_rate=profile.get_feature_adoption_rate(),
                most_used_commands=profile.get_most_used_commands(5),
                days_since_registration=profile.progress_metrics.days_since_registration,
            )

        except Exception as e:
            logger.error(f"Error getting user analytics for {user_id}: {e}")
            return UserAnalytics(
                experience_level="beginner",
                total_commands=0,
                unique_commands=0,
                learning_velocity=0,
                help_requests=0,
                feature_adoption_rate=0,
                most_used_commands=[],
                days_since_registration=0,
            )

    async def track_user_action(self, user_id: str, team_id: str, action: str) -> None:
        """
        Track a user action for analytics.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            action: The action being tracked
        """
        try:
            # For now, we'll track command usage
            if action.startswith("/"):
                await self.track_command_usage(user_id, team_id, action)

        except Exception as e:
            logger.error(f"Error tracking user action for {user_id}: {e}")

    async def track_command_usage(self, user_id: str, team_id: str, command: str) -> None:
        """
        Track command usage and update learning profile.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            command: The command that was used
        """
        try:
            await self.profile_repository.update_command_usage(user_id, team_id, command)

            # Check if user should level up
            await self._check_level_up(user_id, team_id)

        except Exception as e:
            logger.error(f"Error tracking command usage for user {user_id}: {e}")

    async def _check_level_up(self, user_id: str, team_id: str) -> None:
        """
        Check if user should level up and update their level if needed.

        Args:
            user_id: The user's ID
            team_id: The team's ID
        """
        try:
            profile = await self.get_user_profile(user_id, team_id)
            if not profile:
                return

            # Calculate new level
            new_level = await self._calculate_experience_level(profile)

            # Update if level changed
            if new_level != profile.experience_level:
                profile.update_experience_level(new_level)
                await self.profile_repository.save_profile(profile)

                logger.info(
                    f"User {user_id} leveled up from {profile.experience_level} to {new_level}"
                )

        except Exception as e:
            logger.error(f"Error checking level up for user {user_id}: {e}")

    async def _calculate_experience_level(self, profile: LearningProfile) -> str:
        """
        Calculate user's experience level based on usage patterns.

        Args:
            profile: The user's learning profile

        Returns:
            Experience level (beginner, intermediate, advanced, expert)
        """
        try:
            total_commands = profile.progress_metrics.total_commands_used
            unique_commands = profile.progress_metrics.unique_commands_used
            days_since_reg = profile.progress_metrics.days_since_registration
            learning_velocity = profile.progress_metrics.learning_velocity

            # Calculate level based on multiple factors
            level_score = 0

            # Command usage factor
            if total_commands >= 50:
                level_score += 3
            elif total_commands >= 25:
                level_score += 2
            elif total_commands >= 10:
                level_score += 1

            # Unique commands factor
            if unique_commands >= 15:
                level_score += 3
            elif unique_commands >= 10:
                level_score += 2
            elif unique_commands >= 5:
                level_score += 1

            # Learning velocity factor
            if learning_velocity >= 3.0:
                level_score += 2
            elif learning_velocity >= 1.5:
                level_score += 1

            # Time factor (minimum time requirements)
            if days_since_reg < 7:
                level_score = min(level_score, 1)  # Cap at beginner for new users

            # Determine level based on score
            if level_score >= 7:
                return "expert"
            elif level_score >= 5:
                return "advanced"
            elif level_score >= 3:
                return "intermediate"
            else:
                return "beginner"

        except Exception as e:
            logger.error(f"Error calculating experience level: {e}")
            return "beginner"
