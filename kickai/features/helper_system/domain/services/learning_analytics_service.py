"""
Learning Analytics Service

Tracks and analyzes user learning progress and provides insights for the Helper System.
"""

from loguru import logger

from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile
from kickai.features.helper_system.domain.interfaces.learning_analytics_service_interface import (
    ILearningAnalyticsService,
)
from kickai.features.helper_system.domain.repositories.learning_profile_repository_interface import (
    LearningProfileRepositoryInterface,
)
from kickai.features.helper_system.domain.value_objects.analytics_value_objects import (
    TeamAnalytics,
    UserAnalytics,
)


class LearningAnalyticsService(ILearningAnalyticsService):
    """Service for tracking and analyzing user learning progress."""

    def __init__(self, profile_repository: LearningProfileRepositoryInterface):
        self.profile_repository = profile_repository

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

    async def calculate_experience_level(self, profile: LearningProfile) -> str:
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

    async def get_learning_recommendations(self, profile: LearningProfile) -> list[str]:
        """
        Get personalized learning recommendations for a user.

        Args:
            profile: The user's learning profile

        Returns:
            List of learning recommendations
        """
        try:
            recommendations = []

            # Get unused commands
            all_commands = [
                "/addplayer",
                "/list",
                "/status",
                "/help",
                "/myinfo",
                "/creatematch",
                "/attendance",
                "/announce",
                "/remind",
                "/pending",
                "/approve",
                "/reject",
                "/update",
            ]

            unused_commands = profile.get_unused_commands(all_commands)

            # Add recommendations based on unused commands
            for command in unused_commands[:3]:  # Limit to 3 recommendations
                if command == "/creatematch":
                    recommendations.append(
                        "🏟️ Try creating a match with /creatematch to organize your next game"
                    )
                elif command == "/attendance":
                    recommendations.append(
                        "📊 Use /attendance to track player availability for matches"
                    )
                elif command == "/announce":
                    recommendations.append(
                        "📢 Make team announcements with /announce to keep everyone informed"
                    )
                elif command == "/remind":
                    recommendations.append(
                        "⏰ Send targeted reminders with /remind for important events"
                    )
                elif command == "/pending":
                    recommendations.append("⏳ Check pending player approvals with /pending")

            # Add level-specific recommendations
            if profile.experience_level == "beginner":
                recommendations.append(
                    "💡 The system will proactively provide assistance when needed"
                )
            elif profile.experience_level == "intermediate":
                recommendations.append(
                    "🚀 Explore advanced features like match management and analytics"
                )
            elif profile.experience_level == "advanced":
                recommendations.append(
                    "🎯 Optimize your workflows and help mentor other team members"
                )

            return recommendations[:5]  # Limit to 5 recommendations

        except Exception as e:
            logger.error(f"Error getting learning recommendations: {e}")
            return ["💡 The system will proactively provide assistance when needed"]

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

    async def get_feature_recommendations(self, profile: LearningProfile) -> list[str]:
        """
        Get feature recommendations based on user's profile.

        Args:
            profile: The user's learning profile

        Returns:
            List of feature recommendations
        """
        try:
            recommendations = []

            # Check feature adoption
            feature_adoption_rate = profile.get_feature_adoption_rate()

            if feature_adoption_rate < 0.3:
                recommendations.append("🎯 **Player Management**: Master basic player operations")
                recommendations.append("📋 **Team Overview**: Learn to manage your team roster")
            elif feature_adoption_rate < 0.6:
                recommendations.append("🏟️ **Match Management**: Start organizing games and events")
                recommendations.append("📊 **Attendance Tracking**: Track player availability")
            elif feature_adoption_rate < 0.8:
                recommendations.append("📈 **Analytics**: Explore team performance insights")
                recommendations.append("🔧 **Automation**: Set up automated workflows")
            else:
                recommendations.append("🏆 **Mentorship**: Help other team members learn")
                recommendations.append(
                    "🚀 **Innovation**: Explore advanced features and integrations"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error getting feature recommendations: {e}")
            return ["💡 The system will proactively provide assistance when needed"]

    async def get_team_analytics(self, team_id: str) -> TeamAnalytics:
        """
        Get analytics for an entire team.

        Args:
            team_id: The team's ID

        Returns:
            TeamAnalytics value object containing team analytics
        """
        try:
            profiles = await self.profile_repository.get_team_profiles(team_id)

            if not profiles:
                return TeamAnalytics(
                    total_users=0,
                    active_users=0,
                    avg_commands_used=0,
                    avg_feature_adoption=0,
                    level_distribution={},
                    popular_commands=[],
                )

            # Calculate analytics
            total_users = len(profiles)
            active_users = len([p for p in profiles if p.is_active_user()])

            total_commands = sum(p.progress_metrics.total_commands_used for p in profiles)
            avg_commands_used = total_commands / total_users if total_users > 0 else 0

            total_feature_adoption = sum(p.get_feature_adoption_rate() for p in profiles)
            avg_feature_adoption = total_feature_adoption / total_users if total_users > 0 else 0

            # Level distribution
            level_distribution = {}
            for profile in profiles:
                level = profile.experience_level
                level_distribution[level] = level_distribution.get(level, 0) + 1

            # Popular commands
            command_usage = {}
            for profile in profiles:
                for command, count in profile.commands_used.items():
                    command_usage[command] = command_usage.get(command, 0) + count

            popular_commands = sorted(command_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            popular_commands = [cmd[0] for cmd in popular_commands]

            return TeamAnalytics(
                total_users=total_users,
                active_users=active_users,
                avg_commands_used=avg_commands_used,
                avg_feature_adoption=avg_feature_adoption,
                level_distribution=level_distribution,
                popular_commands=popular_commands,
            )

        except Exception as e:
            logger.error(f"Error getting team analytics for team {team_id}: {e}")
            return TeamAnalytics(
                total_users=0,
                active_users=0,
                avg_commands_used=0,
                avg_feature_adoption=0,
                level_distribution={},
                popular_commands=[],
            )

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
            new_level = await self.calculate_experience_level(profile)

            # Update if level changed
            if new_level != profile.experience_level:
                profile.update_experience_level(new_level)
                await self.profile_repository.save_profile(profile)

                logger.info(
                    f"User {user_id} leveled up from {profile.experience_level} to {new_level}"
                )

        except Exception as e:
            logger.error(f"Error checking level up for user {user_id}: {e}")

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
