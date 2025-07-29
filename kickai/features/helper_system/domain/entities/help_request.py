"""
Help Request Entity

Tracks help requests and interactions for learning analytics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class HelpRequest:
    """Represents a help request from a user."""

    id: str
    user_id: str
    team_id: str
    request_type: str  # command_help, feature_question, general_help, troubleshooting
    query: str
    response: str
    helpful: bool | None = None
    rating: int | None = None  # 1-5 rating
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
    response_time_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "team_id": self.team_id,
            "request_type": self.request_type,
            "query": self.query,
            "response": self.response,
            "helpful": self.helpful,
            "rating": self.rating,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "response_time_seconds": self.response_time_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HelpRequest":
        """Create from dictionary."""
        # Handle datetime conversion
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "resolved_at" in data and data["resolved_at"] and isinstance(data["resolved_at"], str):
            data["resolved_at"] = datetime.fromisoformat(data["resolved_at"])

        return cls(**data)

    def mark_resolved(self, response: str, helpful: bool = None, rating: int = None) -> None:
        """Mark the help request as resolved."""
        self.response = response
        self.helpful = helpful
        self.rating = rating
        self.resolved_at = datetime.now()

        if self.created_at:
            self.response_time_seconds = (self.resolved_at - self.created_at).total_seconds()

    def is_resolved(self) -> bool:
        """Check if the help request has been resolved."""
        return self.resolved_at is not None

    def get_response_time_minutes(self) -> float | None:
        """Get response time in minutes."""
        if self.response_time_seconds:
            return self.response_time_seconds / 60
        return None
