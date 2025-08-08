#!/usr/bin/env python3
"""
Attendance Management Domain Entities

This module defines the core entities for tracking player attendance and availability.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List


class AttendanceStatus(Enum):
    """Player attendance status for matches."""

    YES = "yes"
    NO = "no"
    MAYBE = "maybe"
    NOT_RESPONDED = "not_responded"


class AttendanceResponseMethod(Enum):
    """Method used to record attendance response."""

    COMMAND = "command"
    NATURAL_LANGUAGE = "natural_language"
    AUTO_REMINDER = "auto_reminder"
    MANUAL_ENTRY = "manual_entry"


@dataclass
class Attendance:
    """
    Attendance entity representing a player's availability for a specific match.

    This entity captures the relationship between players and matches,
    tracking their availability status and response history.
    """

    id: str
    player_id: str
    match_id: str
    team_id: str
    status: str  # AttendanceStatus value
    response_timestamp: str  # ISO format
    response_method: str = "command"  # AttendanceResponseMethod value
    player_name: Optional[str] = None  # Cached for performance
    match_opponent: Optional[str] = None  # Cached for performance
    match_date: Optional[str] = None  # Cached for performance
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def create(
        cls,
        player_id: str,
        match_id: str,
        team_id: str,
        status: AttendanceStatus,
        response_method: AttendanceResponseMethod = AttendanceResponseMethod.COMMAND,
        player_name: Optional[str] = None,
        match_opponent: Optional[str] = None,
        match_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> "Attendance":
        """Create a new attendance record."""
        now = datetime.utcnow().isoformat()

        # Generate attendance ID: {team_id}_{match_id}_{player_id}
        attendance_id = f"{team_id}_{match_id}_{player_id}"

        return cls(
            id=attendance_id,
            player_id=player_id,
            match_id=match_id,
            team_id=team_id,
            status=status.value,
            response_timestamp=now,
            response_method=response_method.value,
            player_name=player_name,
            match_opponent=match_opponent,
            match_date=match_date,
            notes=notes,
            created_at=now,
            updated_at=now,
        )

    def update_status(
        self,
        status: AttendanceStatus,
        response_method: AttendanceResponseMethod = AttendanceResponseMethod.COMMAND,
        notes: Optional[str] = None,
    ) -> None:
        """Update attendance status."""
        self.status = status.value
        self.response_method = response_method.value
        self.response_timestamp = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

        if notes is not None:
            self.notes = notes

    def to_dict(self) -> dict:
        """Convert attendance to dictionary for storage."""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "match_id": self.match_id,
            "team_id": self.team_id,
            "status": self.status,
            "response_timestamp": self.response_timestamp,
            "response_method": self.response_method,
            "player_name": self.player_name,
            "match_opponent": self.match_opponent,
            "match_date": self.match_date,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Attendance":
        """Create attendance from dictionary."""
        return cls(**{k: v for k, v in data.items() if v is not None})

    def get_status_emoji(self) -> str:
        """Get emoji representation of attendance status."""
        status_emojis = {
            AttendanceStatus.YES.value: "✅",
            AttendanceStatus.NO.value: "❌",
            AttendanceStatus.MAYBE.value: "❔",
            AttendanceStatus.NOT_RESPONDED.value: "⏳",
        }
        return status_emojis.get(self.status, "❓")

    def get_status_display(self) -> str:
        """Get display text for attendance status."""
        status_display = {
            AttendanceStatus.YES.value: "Available",
            AttendanceStatus.NO.value: "Unavailable",
            AttendanceStatus.MAYBE.value: "Maybe",
            AttendanceStatus.NOT_RESPONDED.value: "No Response",
        }
        return status_display.get(self.status, "Unknown")

    def is_available(self) -> bool:
        """Check if player is definitely available."""
        return self.status == AttendanceStatus.YES.value

    def has_responded(self) -> bool:
        """Check if player has provided any response."""
        return self.status != AttendanceStatus.NOT_RESPONDED.value


@dataclass
class AttendanceSummary:
    """Summary of attendance for a match."""

    match_id: str
    team_id: str
    total_players: int
    available_count: int
    unavailable_count: int
    maybe_count: int
    no_response_count: int
    response_rate: float
    last_updated: str

    @classmethod
    def from_attendance_list(
        cls, match_id: str, team_id: str, attendance_list: List[Attendance]
    ) -> "AttendanceSummary":
        """Create summary from list of attendance records."""
        total = len(attendance_list)
        available = sum(1 for a in attendance_list if a.status == AttendanceStatus.YES.value)
        unavailable = sum(1 for a in attendance_list if a.status == AttendanceStatus.NO.value)
        maybe = sum(1 for a in attendance_list if a.status == AttendanceStatus.MAYBE.value)
        no_response = sum(
            1 for a in attendance_list if a.status == AttendanceStatus.NOT_RESPONDED.value
        )

        response_rate = ((total - no_response) / total * 100) if total > 0 else 0.0

        last_updated = max(
            (a.updated_at for a in attendance_list if a.updated_at),
            default=datetime.utcnow().isoformat(),
        )

        return cls(
            match_id=match_id,
            team_id=team_id,
            total_players=total,
            available_count=available,
            unavailable_count=unavailable,
            maybe_count=maybe,
            no_response_count=no_response,
            response_rate=round(response_rate, 1),
            last_updated=last_updated,
        )
