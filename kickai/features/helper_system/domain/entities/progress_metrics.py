"""
Progress Metrics Entity

Tracks user learning progress and performance metrics for the Helper System.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ProgressMetrics:
    """Tracks user learning progress and performance metrics."""

    total_commands_used: int = 0
    unique_commands_used: int = 0
    help_requests_count: int = 0
    days_since_registration: int = 0
    feature_adoption_rate: float = 0.0
    command_success_rate: float = 0.0
    learning_velocity: float = 0.0  # commands learned per day
    last_command_used: str = ""
    last_help_request: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "total_commands_used": self.total_commands_used,
            "unique_commands_used": self.unique_commands_used,
            "help_requests_count": self.help_requests_count,
            "days_since_registration": self.days_since_registration,
            "feature_adoption_rate": self.feature_adoption_rate,
            "command_success_rate": self.command_success_rate,
            "learning_velocity": self.learning_velocity,
            "last_command_used": self.last_command_used,
            "last_help_request": self.last_help_request,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProgressMetrics":
        """Create from dictionary."""
        return cls(**data)

    def update_command_usage(self, command: str) -> None:
        """Update metrics when a command is used."""
        self.total_commands_used += 1
        self.last_command_used = command

        # Recalculate learning velocity
        if self.days_since_registration > 0:
            self.learning_velocity = self.total_commands_used / self.days_since_registration

    def update_help_request(self, request_type: str) -> None:
        """Update metrics when help is requested."""
        self.help_requests_count += 1
        self.last_help_request = request_type

    def calculate_success_rate(self, successful_commands: int) -> None:
        """Calculate command success rate."""
        if self.total_commands_used > 0:
            self.command_success_rate = successful_commands / self.total_commands_used

    def calculate_feature_adoption(self, used_features: int, total_features: int) -> None:
        """Calculate feature adoption rate."""
        if total_features > 0:
            self.feature_adoption_rate = used_features / total_features
