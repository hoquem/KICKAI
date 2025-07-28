from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from typing import Optional


class MatchStatus(Enum):
    """Match status enumeration."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


@dataclass
class Match:
    """Match entity representing a football match."""
    
    id: str
    team_id: str
    opponent: str
    date: str  # ISO format string
    location: Optional[str] = None
    status: str = "scheduled"
    home_away: Optional[str] = None
    competition: Optional[str] = None
    score: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        team_id: str,
        opponent: str,
        date: datetime,
        location: Optional[str] = None,
        status: MatchStatus = MatchStatus.SCHEDULED,
        home_away: str = "home",
        competition: Optional[str] = None,
    ) -> "Match":
        """Create a new match instance."""
        now = datetime.utcnow().isoformat()
        
        return cls(
            id="",  # Will be set by service layer
            team_id=team_id,
            opponent=opponent,
            date=date.isoformat(),
            location=location,
            status=status.value,
            home_away=home_away,
            competition=competition,
            created_at=now,
            updated_at=now,
        )
    
    def update(self, **updates):
        """Update match fields."""
        for field, value in updates.items():
            if hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert match to dictionary."""
        return {
            "id": self.id,
            "team_id": self.team_id,
            "opponent": self.opponent,
            "date": self.date,
            "location": self.location,
            "status": self.status,
            "home_away": self.home_away,
            "competition": self.competition,
            "score": self.score,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        """Create match from dictionary."""
        return cls(**data)
