from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum


class AttendanceStatus(Enum):
    """Attendance status enumeration."""

    ATTENDED = "attended"
    ABSENT = "absent"
    LATE = "late"
    NOT_RECORDED = "not_recorded"


@dataclass
class MatchAttendance:
    """Match attendance entity for tracking actual match day attendance."""

    attendance_id: str
    match_id: str
    player_id: str
    status: AttendanceStatus
    reason: Optional[str] = None
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    recorded_by: str = ""  # Team member ID
    arrival_time: Optional[time] = None

    @classmethod
    def create(
        cls,
        match_id: str,
        player_id: str,
        status: AttendanceStatus,
        reason: Optional[str] = None,
        recorded_by: str = "",
        arrival_time: Optional[time] = None,
        attendance_id: str = "",
    ) -> "MatchAttendance":
        """Create a new match attendance instance."""
        now = datetime.utcnow()

        return cls(
            attendance_id=attendance_id,
            match_id=match_id,
            player_id=player_id,
            status=status,
            reason=reason,
            recorded_by=recorded_by,
            arrival_time=arrival_time,
            recorded_at=now,
        )

    def update(self, status: AttendanceStatus, reason: Optional[str] = None, arrival_time: Optional[time] = None):
        """Update attendance status."""
        self.status = status
        if reason is not None:
            self.reason = reason
        if arrival_time is not None:
            self.arrival_time = arrival_time
        self.recorded_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert attendance to dictionary."""
        return {
            "attendance_id": self.attendance_id,
            "match_id": self.match_id,
            "player_id": self.player_id,
            "status": self.status.value,
            "reason": self.reason,
            "recorded_at": self.recorded_at.isoformat(),
            "recorded_by": self.recorded_by,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MatchAttendance":
        """Create attendance from dictionary."""
        # Convert string dates back to datetime objects
        if "recorded_at" in data and isinstance(data["recorded_at"], str):
            data["recorded_at"] = datetime.fromisoformat(data["recorded_at"])
        if "arrival_time" in data and isinstance(data["arrival_time"], str):
            data["arrival_time"] = time.fromisoformat(data["arrival_time"])

        # Convert status string to enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = AttendanceStatus(data["status"])

        return cls(**data)

    @property
    def is_attended(self) -> bool:
        """Check if player attended."""
        return self.status == AttendanceStatus.ATTENDED

    @property
    def is_absent(self) -> bool:
        """Check if player was absent."""
        return self.status == AttendanceStatus.ABSENT

    @property
    def is_late(self) -> bool:
        """Check if player was late."""
        return self.status == AttendanceStatus.LATE

    @property
    def status_emoji(self) -> str:
        """Get emoji for attendance status."""
        status_emojis = {
            AttendanceStatus.ATTENDED: "✅",
            AttendanceStatus.ABSENT: "❌",
            AttendanceStatus.LATE: "⏰",
            AttendanceStatus.NOT_RECORDED: "❓",
        }
        return status_emojis.get(self.status, "❓")

    @property
    def formatted_arrival_time(self) -> str:
        """Get formatted arrival time string."""
        if self.arrival_time:
            return self.arrival_time.strftime("%I:%M %p")
        return "Not recorded"
