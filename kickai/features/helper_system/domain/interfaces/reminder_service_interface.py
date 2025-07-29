"""
Reminder Service Interface

Abstract interface for reminder service operations.
"""

from abc import ABC, abstractmethod


class IReminderService(ABC):
    """Abstract interface for reminder service operations."""

    @abstractmethod
    async def create_reminder(
        self, user_id: str, team_id: str, reminder_type: str, message: str, title: str = None
    ) -> "Reminder":
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
        pass

    @abstractmethod
    async def create_task_reminder(self, user_id: str, team_id: str, task: str) -> "Reminder":
        """
        Create a task reminder for pending actions.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            task: The task to remind about

        Returns:
            Created task reminder
        """
        pass

    @abstractmethod
    async def create_feature_suggestion(
        self, user_id: str, team_id: str, feature: str
    ) -> "Reminder":
        """
        Create a feature suggestion reminder.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            feature: The feature to suggest

        Returns:
            Created feature suggestion reminder
        """
        pass

    @abstractmethod
    async def create_learning_reminder(
        self, user_id: str, team_id: str, learning_goal: str
    ) -> "Reminder":
        """
        Create a learning reminder.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            learning_goal: The learning goal to remind about

        Returns:
            Created learning reminder
        """
        pass

    @abstractmethod
    async def create_best_practice_reminder(
        self, user_id: str, team_id: str, practice: str
    ) -> "Reminder":
        """
        Create a best practice reminder.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            practice: The best practice to remind about

        Returns:
            Created best practice reminder
        """
        pass

    @abstractmethod
    async def get_pending_reminders(self, user_id: str, team_id: str) -> list["Reminder"]:
        """
        Get pending reminders for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            List of pending reminders
        """
        pass

    @abstractmethod
    async def mark_reminder_sent(self, reminder_id: str, user_id: str, team_id: str) -> bool:
        """
        Mark a reminder as sent.

        Args:
            reminder_id: The reminder ID
            user_id: The user's ID
            team_id: The team's ID

        Returns:
            True if marked successfully, False otherwise
        """
        pass

    @abstractmethod
    async def send_proactive_suggestion(
        self, user_id: str, team_id: str, context: str
    ) -> str | None:
        """
        Send a proactive suggestion to a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
            context: Context for the suggestion

        Returns:
            Suggestion message if sent, None otherwise
        """
        pass

    @abstractmethod
    async def schedule_periodic_reminders(self, user_id: str, team_id: str) -> None:
        """
        Schedule periodic reminders for a user.

        Args:
            user_id: The user's ID
            team_id: The team's ID
        """
        pass
