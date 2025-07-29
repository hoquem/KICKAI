#!/usr/bin/env python3
"""
Training Session Domain Entities

This module defines the core entities for training session management.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class TrainingSessionType(Enum):
    """Training session types."""
    TECHNICAL_SKILLS = "technical_skills"
    TACTICAL_AWARENESS = "tactical_awareness"
    FITNESS_CONDITIONING = "fitness_conditioning"
    MATCH_PRACTICE = "match_practice"
    RECOVERY_SESSION = "recovery_session"


class TrainingSessionStatus(Enum):
    """Training session status."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


@dataclass
class TrainingSession:
    """Training session entity representing a football training session."""
    
    id: str
    team_id: str
    session_type: str  # TrainingSessionType value
    date: str  # ISO format string
    start_time: str  # HH:MM format
    duration_minutes: int
    location: str
    focus_areas: List[str]  # ["Passing", "Shooting", "Defending", "Fitness"]
    max_participants: Optional[int] = None
    status: str = "scheduled"  # TrainingSessionStatus value
    coach_notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        team_id: str,
        session_type: TrainingSessionType,
        date: datetime,
        start_time: str,
        duration_minutes: int,
        location: str,
        focus_areas: List[str],
        max_participants: Optional[int] = None,
        coach_notes: Optional[str] = None,
    ) -> "TrainingSession":
        """Create a new training session instance."""
        now = datetime.utcnow().isoformat()
        
        return cls(
            id="",  # Will be set by service layer
            team_id=team_id,
            session_type=session_type.value,
            date=date.isoformat(),
            start_time=start_time,
            duration_minutes=duration_minutes,
            location=location,
            focus_areas=focus_areas,
            max_participants=max_participants,
            coach_notes=coach_notes,
            created_at=now,
            updated_at=now,
        )
    
    def update(self, **updates):
        """Update training session fields."""
        for field, value in updates.items():
            if hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert training session to dictionary."""
        return {
            "id": self.id,
            "team_id": self.team_id,
            "session_type": self.session_type,
            "date": self.date,
            "start_time": self.start_time,
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "focus_areas": self.focus_areas,
            "max_participants": self.max_participants,
            "status": self.status,
            "coach_notes": self.coach_notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TrainingSession":
        """Create training session from dictionary."""
        return cls(**data)
    
    def get_session_type_display(self) -> str:
        """Get display name for session type."""
        display_names = {
            TrainingSessionType.TECHNICAL_SKILLS.value: "Technical Skills",
            TrainingSessionType.TACTICAL_AWARENESS.value: "Tactical Awareness",
            TrainingSessionType.FITNESS_CONDITIONING.value: "Fitness Conditioning",
            TrainingSessionType.MATCH_PRACTICE.value: "Match Practice",
            TrainingSessionType.RECOVERY_SESSION.value: "Recovery Session",
        }
        return display_names.get(self.session_type, self.session_type)
    
    def get_status_emoji(self) -> str:
        """Get emoji representation of session status."""
        status_emojis = {
            TrainingSessionStatus.SCHEDULED.value: "📅",
            TrainingSessionStatus.IN_PROGRESS.value: "⚽",
            TrainingSessionStatus.COMPLETED.value: "✅",
            TrainingSessionStatus.CANCELLED.value: "❌",
            TrainingSessionStatus.POSTPONED.value: "⏰",
        }
        return status_emojis.get(self.status, "❓")
    
    def is_upcoming(self) -> bool:
        """Check if session is upcoming."""
        session_datetime = datetime.fromisoformat(self.date)
        return session_datetime > datetime.now()
    
    def is_today(self) -> bool:
        """Check if session is today."""
        session_datetime = datetime.fromisoformat(self.date)
        today = datetime.now().date()
        return session_datetime.date() == today 