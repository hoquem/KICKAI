"""
Analytics Value Objects

Value objects for analytics data to ensure consistent return types.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class UserAnalytics:
    """Value object for user analytics data."""

    experience_level: str
    total_commands: int
    unique_commands: int
    learning_velocity: float
    help_requests: int
    feature_adoption_rate: float
    most_used_commands: list[str]
    days_since_registration: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experience_level": self.experience_level,
            "total_commands": self.total_commands,
            "unique_commands": self.unique_commands,
            "learning_velocity": self.learning_velocity,
            "help_requests": self.help_requests,
            "feature_adoption_rate": self.feature_adoption_rate,
            "most_used_commands": self.most_used_commands,
            "days_since_registration": self.days_since_registration,
        }


@dataclass
class TeamAnalytics:
    """Value object for team analytics data."""

    total_users: int
    active_users: int
    avg_commands_used: float
    avg_feature_adoption: float
    level_distribution: dict[str, int]
    popular_commands: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_users": self.total_users,
            "active_users": self.active_users,
            "avg_commands_used": self.avg_commands_used,
            "avg_feature_adoption": self.avg_feature_adoption,
            "level_distribution": self.level_distribution,
            "popular_commands": self.popular_commands,
        }


@dataclass
class HelpRequestStatistics:
    """Value object for help request statistics."""

    total_requests: int
    resolved_requests: int
    pending_requests: int
    avg_resolution_time: float
    popular_topics: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_requests": self.total_requests,
            "resolved_requests": self.resolved_requests,
            "pending_requests": self.pending_requests,
            "avg_resolution_time": self.avg_resolution_time,
            "popular_topics": self.popular_topics,
        }


@dataclass
class HelpRequestAnalytics:
    """Value object for help request analytics."""

    total_requests: int
    pending_requests: int
    resolved_requests: int
    avg_resolution_time: float
    common_topics: list[str]
    user_activity: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_requests": self.total_requests,
            "pending_requests": self.pending_requests,
            "resolved_requests": self.resolved_requests,
            "avg_resolution_time": self.avg_resolution_time,
            "common_topics": self.common_topics,
            "user_activity": self.user_activity,
        }


@dataclass
class PopularHelpTopic:
    """Value object for popular help topic data."""

    topic: str
    count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {"topic": self.topic, "count": self.count}
