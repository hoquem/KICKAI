"""
Reminder Service

Manages learning reminders and proactive notifications for the Helper System.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from kickai.features.helper_system.domain.entities.learning_profile import LearningProfile
from kickai.features.helper_system.domain.interfaces.reminder_service_interface import (
    IReminderService,
)
from kickai.features.helper_system.domain.repositories.learning_profile_repository_interface import (
    LearningProfileRepositoryInterface,
)


def _generate_reminder_id() -> str:
    """Generate a simple ID for reminders."""
    return f"reminder_{uuid.uuid4().hex[:8]}"


@dataclass
class Reminder:
    """Represents a learning reminder."""

    id: str
    user_id: str
    team_id: str
    reminder_type: str  # task, feature, learning, best_practice
    title: str
    message: str
    trigger_conditions: dict[str, Any]
    scheduled_time: datetime | None = None
    sent: bool = False
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class ReminderService(IReminderService):
    """Service for managing learning reminders and notifications."""

    def __init__(self, profile_repository: LearningProfileRepositoryInterface):
        self.profile_repository = profile_repository

    async def create_reminder(
        self, user_id: str, team_id: str, reminder_type: str, message: str, title: str = None
    ) -> Reminder:
        """
        Create a reminder for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            reminder_type: Type of reminder
            message: The reminder message
            title: Optional title for the reminder

        Returns:
            Created reminder
        """
        try:
            reminder_id = _generate_reminder_id()

            if not title:
                title = f"{reminder_type.title()} Reminder"

            reminder = Reminder(
                id=reminder_id,
                user_id=user_id,
                team_id=team_id,
                reminder_type=reminder_type,
                title=title,
                message=message,
                trigger_conditions={},
                scheduled_time=datetime.now() + timedelta(hours=1),  # Default to 1 hour from now
            )

            # For now, we'll just log the reminder
            # In a full implementation, this would be stored in a database
            logger.info(f"Created reminder for user {user_id}: {title} - {message}")

            return reminder

        except Exception as e:
            logger.error(f"Error creating reminder for user {user_id}: {e}")
            raise

    async def create_task_reminder(self, user_id: str, team_id: str, task: str) -> Reminder:
        """
        Create a task reminder for pending actions.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            task: The task to remind about

        Returns:
            Created task reminder
        """
        message = f"⏰ **Task Reminder**: {task}\n\nThis task might need your attention. The system will provide assistance when needed!"
        return await self.create_reminder(
            user_id, team_id, "task", message, f"Task Reminder: {task}"
        )

    async def create_feature_suggestion(self, user_id: str, team_id: str, feature: str) -> Reminder:
        """
        Create a feature suggestion reminder.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            feature: The feature to suggest

        Returns:
            Created feature suggestion
        """
        message = f"💡 **Feature Suggestion**: {feature}\n\nThis feature might help you be more efficient. Try it out!"
        return await self.create_reminder(
            user_id, team_id, "feature", message, f"Feature Suggestion: {feature}"
        )

    async def create_learning_reminder(
        self, user_id: str, team_id: str, learning_goal: str
    ) -> Reminder:
        """
        Create a learning reminder.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            learning_goal: The learning goal to remind about

        Returns:
            Created learning reminder
        """
        message = f"📚 **Learning Goal**: {learning_goal}\n\nKeep up the great work! The system will provide guidance when needed."
        return await self.create_reminder(
            user_id, team_id, "learning", message, f"Learning Goal: {learning_goal}"
        )

    async def create_best_practice_reminder(
        self, user_id: str, team_id: str, practice: str
    ) -> Reminder:
        """
        Create a best practice reminder.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            practice: The best practice to remind about

        Returns:
            Created best practice reminder
        """
        message = f"⭐ **Best Practice**: {practice}\n\nThis tip will help you use KICKAI more effectively!"
        return await self.create_reminder(
            user_id, team_id, "best_practice", message, f"Best Practice: {practice}"
        )

    async def get_pending_reminders(self, user_id: str, team_id: str) -> list[Reminder]:
        """
        Get pending reminders for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            List of pending reminders
        """
        try:
            # For now, return empty list
            # In a full implementation, this would query a database
            return []

        except Exception as e:
            logger.error(f"Error getting pending reminders for user {user_id}: {e}")
            return []

    async def mark_reminder_sent(self, reminder_id: str, user_id: str, team_id: str) -> bool:
        """
        Mark a reminder as sent.

        Args:
            reminder_id: The reminder ID
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            True if marked as sent, False otherwise
        """
        try:
            # For now, just log
            logger.info(f"Marked reminder {reminder_id} as sent for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error marking reminder {reminder_id} as sent: {e}")
            return False

    async def send_proactive_suggestion(
        self, user_id: str, team_id: str, context: str
    ) -> str | None:
        """
        Send a proactive suggestion based on user context.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            context: Context about the user's current activity

        Returns:
            Suggestion message if one should be sent, None otherwise
        """
        try:
            # Get user's learning profile
            profile = await self.profile_repository.get_profile(user_id, team_id)
            if not profile:
                return None

            # Generate suggestion based on context and profile
            suggestion = await self._generate_contextual_suggestion(profile, context)

            if suggestion:
                # Create and send reminder
                await self.create_reminder(
                    user_id, team_id, "suggestion", suggestion, "Proactive Suggestion"
                )
                return suggestion

            return None

        except Exception as e:
            logger.error(f"Error sending proactive suggestion to user {user_id}: {e}")
            return None

    async def _generate_contextual_suggestion(
        self, profile: LearningProfile, context: str
    ) -> str | None:
        """
        Generate a contextual suggestion based on user profile and context.

        Args:
            profile: The user's learning profile
            context: Current context

        Returns:
            Suggestion message if one should be generated, None otherwise
        """
        try:
            # Simple suggestion logic based on user level and context
            if "addplayer" in context.lower() and profile.experience_level == "beginner":
                return "💡 **Pro Tip**: After adding a player, use /list to verify they appear correctly and /status to check their availability!"

            elif "list" in context.lower() and profile.experience_level == "beginner":
                return "💡 **Pro Tip**: Use /list with filters like --status active to find specific players quickly!"

            elif "status" in context.lower() and profile.experience_level == "beginner":
                return "💡 **Pro Tip**: You can search by phone number or player ID. Use /list to see all available players!"

            elif (
                profile.experience_level == "beginner"
                and profile.progress_metrics.total_commands_used < 5
            ):
                return "🎯 **Getting Started**: The system will proactively provide assistance when needed!"

            elif (
                profile.experience_level == "intermediate"
                and "creatematch" not in profile.commands_used
            ):
                return "🏟️ **Next Level**: Ready to organize games? Try /creatematch to set up your first match!"

            elif (
                profile.experience_level == "intermediate"
                and "attendance" not in profile.commands_used
            ):
                return "📊 **Attendance Tracking**: Use /attendance to track player availability for your matches!"

            return None

        except Exception as e:
            logger.error(f"Error generating contextual suggestion: {e}")
            return None

    async def schedule_periodic_reminders(self, user_id: str, team_id: str) -> None:
        """
        Schedule periodic reminders for a user based on their activity.

        Args:
            user_id: The user's ID
            team_id: The team's ID
        """
        try:
            profile = await self.profile_repository.get_profile(user_id, team_id)
            if not profile:
                return

            # Check if user has been inactive
            if not profile.is_active_user(days_threshold=3):
                await self.create_reminder(
                    user_id,
                    team_id,
                    "engagement",
                    "👋 **Welcome Back!** We miss you! The system will help you get back up to speed with KICKAI.",
                    "Welcome Back Reminder",
                )

            # Check for level-up opportunities
            if (
                profile.experience_level == "beginner"
                and profile.progress_metrics.total_commands_used >= 10
            ):
                await self.create_reminder(
                    user_id,
                    team_id,
                    "level_up",
                    "🚀 **Level Up Opportunity!** You're doing great! Try some intermediate features like /creatematch.",
                    "Level Up Opportunity",
                )

        except Exception as e:
            logger.error(f"Error scheduling periodic reminders for user {user_id}: {e}")
