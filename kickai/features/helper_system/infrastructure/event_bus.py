"""
Event Bus Implementation

Concrete implementation of the event bus for domain event handling.
"""

from collections.abc import Callable
from typing import Any

from loguru import logger

from kickai.features.helper_system.domain.events.learning_events import (
    CommandUsedEvent,
    HelpRequestCreatedEvent,
    HelpRequestResolvedEvent,
    LearningReminderSentEvent,
    UserLevelUpEvent,
)
from kickai.features.helper_system.domain.interfaces.event_bus_interface import IEventBus


class EventBus(IEventBus):
    """Concrete implementation of the event bus."""

    def __init__(self):
        self._subscribers: dict[type, list[Callable]] = {}
        self._handlers: dict[type, Callable] = {}

    async def publish(self, event: Any) -> None:
        """
        Publish a domain event.

        Args:
            event: The domain event to publish
        """
        try:
            event_type = type(event)

            # Call registered subscribers
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type.__name__}: {e}")

            # Call specific event handlers
            if event_type in self._handlers:
                try:
                    await self._handlers[event_type](event)
                except Exception as e:
                    logger.error(f"Error in specific event handler for {event_type.__name__}: {e}")

            logger.info(f"Published event: {event_type.__name__}")

        except Exception as e:
            logger.error(f"Error publishing event: {e}")

    def subscribe(self, event_type: type, handler: Callable) -> None:
        """
        Subscribe to a domain event type.

        Args:
            event_type: The type of event to subscribe to
            handler: The handler function to call when event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed to event: {event_type.__name__}")

    async def handle_command_used(self, event: CommandUsedEvent) -> None:
        """
        Handle command used event.

        Args:
            event: The command used event
        """
        try:
            logger.info(
                f"Command used: {event.command} by user {event.user_id} in team {event.team_id}"
            )

            # In a full implementation, this would trigger analytics updates
            # For now, we just log the event

        except Exception as e:
            logger.error(f"Error handling command used event: {e}")

    async def handle_user_level_up(self, event: UserLevelUpEvent) -> None:
        """
        Handle user level up event.

        Args:
            event: The user level up event
        """
        try:
            logger.info(
                f"User {event.user_id} leveled up from {event.old_level} to {event.new_level}"
            )

            # In a full implementation, this would trigger notifications
            # For now, we just log the event

        except Exception as e:
            logger.error(f"Error handling user level up event: {e}")

    async def handle_help_request_created(self, event: HelpRequestCreatedEvent) -> None:
        """
        Handle help request created event.

        Args:
            event: The help request created event
        """
        try:
            logger.info(f"Help request created: {event.request_id} by user {event.user_id}")

            # In a full implementation, this would trigger notifications to helpers
            # For now, we just log the event

        except Exception as e:
            logger.error(f"Error handling help request created event: {e}")

    async def handle_help_request_resolved(self, event: HelpRequestResolvedEvent) -> None:
        """
        Handle help request resolved event.

        Args:
            event: The help request resolved event
        """
        try:
            logger.info(
                f"Help request resolved: {event.request_id} in {event.resolution_time:.2f} hours"
            )

            # In a full implementation, this would trigger analytics updates
            # For now, we just log the event

        except Exception as e:
            logger.error(f"Error handling help request resolved event: {e}")

    async def handle_learning_reminder_sent(self, event: LearningReminderSentEvent) -> None:
        """
        Handle learning reminder sent event.

        Args:
            event: The learning reminder sent event
        """
        try:
            logger.info(f"Learning reminder sent to user {event.user_id}: {event.reminder_type}")

            # In a full implementation, this would trigger analytics updates
            # For now, we just log the event

        except Exception as e:
            logger.error(f"Error handling learning reminder sent event: {e}")

    def register_handler(self, event_type: type, handler: Callable) -> None:
        """
        Register a specific event handler.

        Args:
            event_type: The type of event to handle
            handler: The handler function
        """
        self._handlers[event_type] = handler
        logger.info(f"Registered handler for event: {event_type.__name__}")

    def unregister_handler(self, event_type: type) -> None:
        """
        Unregister a specific event handler.

        Args:
            event_type: The type of event to unregister
        """
        if event_type in self._handlers:
            del self._handlers[event_type]
            logger.info(f"Unregistered handler for event: {event_type.__name__}")

    def get_subscriber_count(self, event_type: type) -> int:
        """
        Get the number of subscribers for an event type.

        Args:
            event_type: The type of event

        Returns:
            Number of subscribers
        """
        return len(self._subscribers.get(event_type, []))

    def get_registered_handlers(self) -> list[type]:
        """
        Get list of registered event types.

        Returns:
            List of registered event types
        """
        return list(self._handlers.keys())
