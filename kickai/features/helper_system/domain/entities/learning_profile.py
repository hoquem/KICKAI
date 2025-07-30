"""
Learning Profile Entity

Main entity for tracking user learning progress and preferences in the Helper System.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .help_request import HelpRequest
from .learning_preferences import LearningPreferences
from .progress_metrics import ProgressMetrics


@dataclass
class LearningProfile:
    """Comprehensive learning profile for a user."""

    user_id: str
    team_id: str
    experience_level: str = "beginner"  # beginner, intermediate, advanced, expert
    commands_used: dict[str, int] = field(default_factory=dict)
    features_discovered: set[str] = field(default_factory=set)
    help_requests: list[HelpRequest] = field(default_factory=list)
    learning_preferences: LearningPreferences = field(default_factory=LearningPreferences)
    last_active: datetime = field(default_factory=datetime.now)
    progress_metrics: ProgressMetrics = field(default_factory=ProgressMetrics)
    registration_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "team_id": self.team_id,
            "experience_level": self.experience_level,
            "commands_used": self.commands_used,
            "features_discovered": list(self.features_discovered),
            "help_requests": [req.to_dict() for req in self.help_requests],
            "learning_preferences": self.learning_preferences.to_dict(),
            "last_active": self.last_active.isoformat(),
            "progress_metrics": self.progress_metrics.to_dict(),
            "registration_date": self.registration_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearningProfile":
        """Create from dictionary."""
        # Handle datetime conversion
        if "last_active" in data and isinstance(data["last_active"], str):
            data["last_active"] = datetime.fromisoformat(data["last_active"])
        if "registration_date" in data and isinstance(data["registration_date"], str):
            data["registration_date"] = datetime.fromisoformat(data["registration_date"])

        # Handle help requests conversion
        if "help_requests" in data:
            data["help_requests"] = [HelpRequest.from_dict(req) for req in data["help_requests"]]

        # Handle learning preferences conversion
        if "learning_preferences" in data:
            data["learning_preferences"] = LearningPreferences.from_dict(
                data["learning_preferences"]
            )

        # Handle progress metrics conversion
        if "progress_metrics" in data:
            data["progress_metrics"] = ProgressMetrics.from_dict(data["progress_metrics"])

        # Handle features_discovered conversion (set from list)
        if "features_discovered" in data and isinstance(data["features_discovered"], list):
            data["features_discovered"] = set(data["features_discovered"])

        return cls(**data)

    def update_command_usage(self, command: str) -> None:
        """Update command usage statistics."""
        self.commands_used[command] = self.commands_used.get(command, 0) + 1
        self.last_active = datetime.now()

        # Update progress metrics
        self.progress_metrics.update_command_usage(command)

        # Update unique commands count
        self.progress_metrics.unique_commands_used = len(self.commands_used)

        # Update days since registration
        days_since_reg = (datetime.now() - self.registration_date).days
        self.progress_metrics.days_since_registration = days_since_reg

    def add_feature_discovery(self, feature: str) -> None:
        """Mark a feature as discovered by the user."""
        self.features_discovered.add(feature)
        self.last_active = datetime.now()

        # Update feature adoption rate
        total_features = 20  # Approximate total features in KICKAI
        self.progress_metrics.calculate_feature_adoption(
            len(self.features_discovered), total_features
        )

    def add_help_request(self, help_request: HelpRequest) -> None:
        """Add a help request to the profile."""
        self.help_requests.append(help_request)
        self.last_active = datetime.now()

        # Update progress metrics
        self.progress_metrics.update_help_request(help_request.request_type)

    def update_experience_level(self, new_level: str) -> None:
        """Update the user's experience level."""
        valid_levels = ["beginner", "intermediate", "advanced", "expert"]
        if new_level in valid_levels:
            self.experience_level = new_level
            self.last_active = datetime.now()

    def get_most_used_commands(self, limit: int = 5) -> list[tuple]:
        """Get the most frequently used commands."""
        sorted_commands = sorted(self.commands_used.items(), key=lambda x: x[1], reverse=True)
        return sorted_commands[:limit]

    def get_least_used_commands(self, limit: int = 5) -> list[tuple]:
        """Get the least frequently used commands."""
        sorted_commands = sorted(self.commands_used.items(), key=lambda x: x[1])
        return sorted_commands[:limit]

    def get_unused_commands(self, all_commands: list[str]) -> list[str]:
        """Get commands that haven't been used yet."""
        used_commands = set(self.commands_used.keys())
        return [cmd for cmd in all_commands if cmd not in used_commands]

    def get_learning_velocity(self) -> float:
        """Get the user's learning velocity (commands per day)."""
        return self.progress_metrics.learning_velocity

    def get_feature_adoption_rate(self) -> float:
        """Get the user's feature adoption rate."""
        return self.progress_metrics.feature_adoption_rate

    def get_command_success_rate(self) -> float:
        """Get the user's command success rate."""
        return self.progress_metrics.command_success_rate

    def is_active_user(self, days_threshold: int = 7) -> bool:
        """Check if the user has been active recently."""
        days_since_active = (datetime.now() - self.last_active).days
        return days_since_active <= days_threshold

    def get_help_requests_count(self) -> int:
        """Get the total number of help requests."""
        return len(self.help_requests)

    def get_recent_help_requests(self, days: int = 7) -> list[HelpRequest]:
        """Get help requests from the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [req for req in self.help_requests if req.created_at >= cutoff_date]
