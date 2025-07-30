"""
Event Bus Interface

Abstract interface for domain event handling.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from kickai.features.helper_system.domain.events.learning_events import (
    CommandUsedEvent,
    HelpRequestCreatedEvent,
    HelpRequestResolvedEvent,
    LearningReminderSentEvent,
    UserLevelUpEvent,
)


class IEventBus(ABC):
    """Abstract interface for domain event bus operations."""

    @abstractmethod
    async def publish(self, event: Any) -> None:
        """
        Publish a domain event.

        Args:
            event: The domain event to publish
        """
        pass

    @abstractmethod
    def subscribe(self, event_type: type, handler: Callable) -> None:
        """
        Subscribe to a domain event type.

        Args:
            event_type: The type of event to subscribe to
            handler: The handler function to call when event occurs
        """
        pass

    @abstractmethod
    async def handle_command_used(self, event: CommandUsedEvent) -> None:
        """
        Handle command used event.

        Args:
            event: The command used event
        """
        pass

    @abstractmethod
    async def handle_user_level_up(self, event: UserLevelUpEvent) -> None:
        """
        Handle user level up event.

        Args:
            event: The user level up event
        """
        pass

    @abstractmethod
    async def handle_help_request_created(self, event: HelpRequestCreatedEvent) -> None:
        """
        Handle help request created event.

        Args:
            event: The help request created event
        """
        pass

    @abstractmethod
    async def handle_help_request_resolved(self, event: HelpRequestResolvedEvent) -> None:
        """
        Handle help request resolved event.

        Args:
            event: The help request resolved event
        """
        pass

    @abstractmethod
    async def handle_learning_reminder_sent(self, event: LearningReminderSentEvent) -> None:
        """
        Handle learning reminder sent event.

        Args:
            event: The learning reminder sent event
        """
        pass
