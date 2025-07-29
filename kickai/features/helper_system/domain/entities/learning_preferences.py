"""
Learning Preferences Entity

Stores user learning preferences and customization settings.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LearningPreferences:
    """User learning preferences and customization settings."""

    preferred_style: str = "step_by_step"  # step_by_step, visual, quick_tips, detailed
    notification_frequency: str = "daily"  # immediate, daily, weekly, never
    preferred_commands: list[str] = field(default_factory=list)
    avoided_commands: list[str] = field(default_factory=list)
    learning_pace: str = "normal"  # slow, normal, fast
    show_examples: bool = True
    show_tips: bool = True
    show_celebrations: bool = True
    language: str = "en"
    timezone: str = "UTC"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "preferred_style": self.preferred_style,
            "notification_frequency": self.notification_frequency,
            "preferred_commands": self.preferred_commands,
            "avoided_commands": self.avoided_commands,
            "learning_pace": self.learning_pace,
            "show_examples": self.show_examples,
            "show_tips": self.show_tips,
            "show_celebrations": self.show_celebrations,
            "language": self.language,
            "timezone": self.timezone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearningPreferences":
        """Create from dictionary."""
        return cls(**data)

    def update_preference(self, key: str, value: Any) -> None:
        """Update a specific preference."""
        if hasattr(self, key):
            setattr(self, key, value)

    def get_help_style(self) -> str:
        """Get the preferred help style for this user."""
        return self.preferred_style

    def should_show_examples(self) -> bool:
        """Check if examples should be shown."""
        return self.show_examples

    def should_show_tips(self) -> bool:
        """Check if tips should be shown."""
        return self.show_tips

    def should_show_celebrations(self) -> bool:
        """Check if celebrations should be shown."""
        return self.show_celebrations

    def get_notification_frequency(self) -> str:
        """Get notification frequency preference."""
        return self.notification_frequency
