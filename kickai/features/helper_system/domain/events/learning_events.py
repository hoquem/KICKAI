"""
Learning Domain Events

Domain events for the Helper System to maintain clean architecture.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommandUsedEvent:
    """Event raised when a user uses a command."""

    user_id: str
    team_id: str
    command: str
    timestamp: datetime
    context: dict | None = None


@dataclass
class UserLevelUpEvent:
    """Event raised when a user levels up."""

    user_id: str
    team_id: str
    old_level: str
    new_level: str
    timestamp: datetime
    trigger_command: str | None = None


@dataclass
class HelpRequestCreatedEvent:
    """Event raised when a help request is created."""

    request_id: str
    user_id: str
    team_id: str
    topic: str
    description: str
    timestamp: datetime


@dataclass
class HelpRequestResolvedEvent:
    """Event raised when a help request is resolved."""

    request_id: str
    user_id: str
    team_id: str
    resolution_time: float  # in hours
    helpful: bool | None = None
    rating: int | None = None
    timestamp: datetime = None


@dataclass
class LearningReminderSentEvent:
    """Event raised when a learning reminder is sent."""

    user_id: str
    team_id: str
    reminder_type: str
    message: str
    timestamp: datetime
