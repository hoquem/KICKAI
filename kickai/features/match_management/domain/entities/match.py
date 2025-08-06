from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum


class MatchStatus(Enum):
    """Match status enumeration."""

    SCHEDULED = "scheduled"
    AVAILABILITY_OPEN = "availability_open"
    SQUAD_SELECTION = "squad_selection"
    SQUAD_SELECTED = "squad_selected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class MatchResult:
    """Match result entity."""

    match_id: str
    home_score: int
    away_score: int
    scorers: list[str] = field(default_factory=list)  # Player IDs
    assists: list[str] = field(default_factory=list)  # Player IDs
    notes: str | None = None
    recorded_by: str = ""  # Team member ID
    recorded_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert match result to dictionary."""
        return {
            "match_id": self.match_id,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "scorers": self.scorers,
            "assists": self.assists,
            "notes": self.notes,
            "recorded_by": self.recorded_by,
            "recorded_at": self.recorded_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MatchResult":
        """Create match result from dictionary."""
        if "recorded_at" in data and isinstance(data["recorded_at"], str):
            data["recorded_at"] = datetime.fromisoformat(data["recorded_at"])
        return cls(**data)


@dataclass
class Match:
    """Match entity representing a football match."""

    match_id: str
    team_id: str
    opponent: str
    match_date: datetime
    match_time: time
    venue: str
    competition: str
    status: MatchStatus = MatchStatus.SCHEDULED
    notes: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""  # Team member ID
    squad_size: int = 11
    result: MatchResult | None = None

    @classmethod
    def create(
        cls,
        team_id: str,
        opponent: str,
        match_date: datetime,
        match_time: time,
        venue: str,
        competition: str = "League Match",
        notes: str | None = None,
        created_by: str = "",
        squad_size: int = 11,
    ) -> "Match":
        """Create a new match instance."""
        now = datetime.utcnow()

        return cls(
            match_id="",  # Will be set by service layer
            team_id=team_id,
            opponent=opponent,
            match_date=match_date,
            match_time=match_time,
            venue=venue,
            competition=competition,
            notes=notes,
            created_by=created_by,
            squad_size=squad_size,
            created_at=now,
            updated_at=now,
        )

    def update(self, **updates):
        """Update match fields."""
        for field, value in updates.items():
            if hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert match to dictionary."""
        return {
            "match_id": self.match_id,
            "team_id": self.team_id,
            "opponent": self.opponent,
            "match_date": self.match_date.isoformat(),
            "match_time": self.match_time.isoformat(),
            "venue": self.venue,
            "competition": self.competition,
            "status": self.status.value,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "squad_size": self.squad_size,
            "result": self.result.to_dict() if self.result else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Match":
        """Create match from dictionary."""
        # Convert string dates back to datetime objects
        if "match_date" in data and isinstance(data["match_date"], str):
            data["match_date"] = datetime.fromisoformat(data["match_date"])
        if "match_time" in data and isinstance(data["match_time"], str):
            data["match_time"] = time.fromisoformat(data["match_time"])
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Convert status string to enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = MatchStatus(data["status"])

        # Convert result dict to MatchResult object
        if data.get("result"):
            data["result"] = MatchResult.from_dict(data["result"])

        return cls(**data)

    @property
    def is_upcoming(self) -> bool:
        """Check if match is upcoming."""
        return self.status in [MatchStatus.SCHEDULED, MatchStatus.AVAILABILITY_OPEN, MatchStatus.SQUAD_SELECTION]

    @property
    def is_completed(self) -> bool:
        """Check if match is completed."""
        return self.status == MatchStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Check if match is cancelled."""
        return self.status == MatchStatus.CANCELLED

    @property
    def formatted_date(self) -> str:
        """Get formatted date string."""
        return self.match_date.strftime("%A, %dth %B %Y")

    @property
    def formatted_time(self) -> str:
        """Get formatted time string."""
        return self.match_time.strftime("%I:%M %p")

    @property
    def display_name(self) -> str:
        """Get display name for the match."""
        return f"vs {self.opponent} ({self.formatted_date})"
