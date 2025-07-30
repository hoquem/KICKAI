#!/usr/bin/env python3
"""
Training Attendance Domain Entities

This module defines the core entities for tracking training session attendance.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TrainingAttendanceStatus(Enum):
    """Training attendance status."""
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    NOT_RESPONDED = "not_responded"
    LATE_CANCELLATION = "late_cancellation"


class TrainingAttendanceResponseMethod(Enum):
    """Method used to record training attendance response."""
    COMMAND = "command"
    NATURAL_LANGUAGE = "natural_language"
    AUTO_REMINDER = "auto_reminder"
    MANUAL_ENTRY = "manual_entry"


@dataclass
class TrainingAttendance:
    """Training attendance entity representing a player's attendance for a training session."""
    
    id: str
    player_id: str
    training_session_id: str
    team_id: str
    status: str  # TrainingAttendanceStatus value
    response_timestamp: str  # ISO format
    response_method: str = "command"  # TrainingAttendanceResponseMethod value
    player_name: Optional[str] = None  # Cached for performance
    training_session_type: Optional[str] = None  # Cached for performance
    training_date: Optional[str] = None  # Cached for performance
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        player_id: str,
        training_session_id: str,
        team_id: str,
        status: TrainingAttendanceStatus,
        response_method: TrainingAttendanceResponseMethod = TrainingAttendanceResponseMethod.COMMAND,
        player_name: Optional[str] = None,
        training_session_type: Optional[str] = None,
        training_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> "TrainingAttendance":
        """Create a new training attendance record."""
        now = datetime.utcnow().isoformat()
        
        # Generate attendance ID: {team_id}_{training_session_id}_{player_id}
        attendance_id = f"{team_id}_{training_session_id}_{player_id}"
        
        return cls(
            id=attendance_id,
            player_id=player_id,
            training_session_id=training_session_id,
            team_id=team_id,
            status=status.value,
            response_timestamp=now,
            response_method=response_method.value,
            player_name=player_name,
            training_session_type=training_session_type,
            training_date=training_date,
            notes=notes,
            created_at=now,
            updated_at=now,
        )
    
    def update_status(
        self,
        status: TrainingAttendanceStatus,
        response_method: TrainingAttendanceResponseMethod = TrainingAttendanceResponseMethod.COMMAND,
        notes: Optional[str] = None,
    ) -> None:
        """Update training attendance status."""
        self.status = status.value
        self.response_method = response_method.value
        self.response_timestamp = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        
        if notes is not None:
            self.notes = notes
    
    def to_dict(self) -> dict:
        """Convert training attendance to dictionary for storage."""
        return {
            "id": self.id,
            "player_id": self.player_id,
            "training_session_id": self.training_session_id,
            "team_id": self.team_id,
            "status": self.status,
            "response_timestamp": self.response_timestamp,
            "response_method": self.response_method,
            "player_name": self.player_name,
            "training_session_type": self.training_session_type,
            "training_date": self.training_date,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TrainingAttendance":
        """Create training attendance from dictionary."""
        return cls(**{k: v for k, v in data.items() if v is not None})
    
    def get_status_emoji(self) -> str:
        """Get emoji representation of training attendance status."""
        status_emojis = {
            TrainingAttendanceStatus.CONFIRMED.value: "✅",
            TrainingAttendanceStatus.DECLINED.value: "❌", 
            TrainingAttendanceStatus.TENTATIVE.value: "❔",
            TrainingAttendanceStatus.NOT_RESPONDED.value: "⏳",
            TrainingAttendanceStatus.LATE_CANCELLATION.value: "⚠️",
        }
        return status_emojis.get(self.status, "❓")
    
    def get_status_display(self) -> str:
        """Get display text for training attendance status."""
        status_display = {
            TrainingAttendanceStatus.CONFIRMED.value: "Confirmed",
            TrainingAttendanceStatus.DECLINED.value: "Declined",
            TrainingAttendanceStatus.TENTATIVE.value: "Tentative",
            TrainingAttendanceStatus.NOT_RESPONDED.value: "No Response",
            TrainingAttendanceStatus.LATE_CANCELLATION.value: "Late Cancellation",
        }
        return status_display.get(self.status, "Unknown")
    
    def is_confirmed(self) -> bool:
        """Check if player is confirmed for training."""
        return self.status == TrainingAttendanceStatus.CONFIRMED.value
    
    def has_responded(self) -> bool:
        """Check if player has provided any response."""
        return self.status != TrainingAttendanceStatus.NOT_RESPONDED.value


@dataclass
class TrainingAttendanceSummary:
    """Summary of training attendance for a session."""
    
    training_session_id: str
    team_id: str
    total_players: int
    confirmed_count: int
    declined_count: int
    tentative_count: int
    no_response_count: int
    late_cancellation_count: int
    response_rate: float
    last_updated: str
    
    @classmethod
    def from_attendance_list(cls, training_session_id: str, team_id: str, attendance_list: list) -> "TrainingAttendanceSummary":
        """Create summary from list of training attendance records."""
        total = len(attendance_list)
        confirmed = sum(1 for a in attendance_list if a.status == TrainingAttendanceStatus.CONFIRMED.value)
        declined = sum(1 for a in attendance_list if a.status == TrainingAttendanceStatus.DECLINED.value)
        tentative = sum(1 for a in attendance_list if a.status == TrainingAttendanceStatus.TENTATIVE.value)
        no_response = sum(1 for a in attendance_list if a.status == TrainingAttendanceStatus.NOT_RESPONDED.value)
        late_cancellation = sum(1 for a in attendance_list if a.status == TrainingAttendanceStatus.LATE_CANCELLATION.value)
        
        response_rate = ((total - no_response) / total * 100) if total > 0 else 0.0
        
        last_updated = max(
            (a.updated_at for a in attendance_list if a.updated_at),
            default=datetime.utcnow().isoformat()
        )
        
        return cls(
            training_session_id=training_session_id,
            team_id=team_id,
            total_players=total,
            confirmed_count=confirmed,
            declined_count=declined,
            tentative_count=tentative,
            no_response_count=no_response,
            late_cancellation_count=late_cancellation,
            response_rate=round(response_rate, 1),
            last_updated=last_updated,
        ) 