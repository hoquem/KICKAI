from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AvailabilityStatus(Enum):
    """Availability status enumeration."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAYBE = "maybe"
    PENDING = "pending"


@dataclass
class Availability:
    """Availability entity for tracking player availability for matches."""

    availability_id: str
    match_id: str
    player_id: str
    status: AvailabilityStatus
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: str = ""  # Player ID

    @classmethod
    def create(
        cls,
        match_id: str,
        player_id: str,
        status: AvailabilityStatus,
        reason: Optional[str] = None,
        availability_id: str = "",
    ) -> "Availability":
        """Create a new availability instance."""
        now = datetime.utcnow()

        return cls(
            availability_id=availability_id,
            match_id=match_id,
            player_id=player_id,
            status=status,
            reason=reason,
            created_at=now,
            updated_at=now,
            updated_by=player_id,
        )

    def update(self, status: AvailabilityStatus, reason: Optional[str] = None, updated_by: str = ""):
        """Update availability status."""
        self.status = status
        if reason is not None:
            self.reason = reason
        if updated_by:
            self.updated_by = updated_by
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert availability to dictionary."""
        return {
            "availability_id": self.availability_id,
            "match_id": self.match_id,
            "player_id": self.player_id,
            "status": self.status.value,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "updated_by": self.updated_by,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Availability":
        """Create availability from dictionary."""
        # Convert string dates back to datetime objects
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Convert status string to enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = AvailabilityStatus(data["status"])

        return cls(**data)

    @property
    def is_available(self) -> bool:
        """Check if player is available."""
        return self.status == AvailabilityStatus.AVAILABLE

    @property
    def is_unavailable(self) -> bool:
        """Check if player is unavailable."""
        return self.status == AvailabilityStatus.UNAVAILABLE

    @property
    def is_maybe(self) -> bool:
        """Check if player status is maybe."""
        return self.status == AvailabilityStatus.MAYBE

    @property
    def is_pending(self) -> bool:
        """Check if player hasn't responded."""
        return self.status == AvailabilityStatus.PENDING

    @property
    def status_emoji(self) -> str:
        """Get emoji for availability status."""
        status_emojis = {
            AvailabilityStatus.AVAILABLE: "✅",
            AvailabilityStatus.UNAVAILABLE: "❌",
            AvailabilityStatus.MAYBE: "❓",
            AvailabilityStatus.PENDING: "⏳",
        }
        return status_emojis.get(self.status, "❓")
