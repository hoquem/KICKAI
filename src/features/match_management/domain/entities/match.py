from dataclasses import dataclass


@dataclass
class Match:
    id: str
    team_id: str
    opponent: str
    date: str  # ISO format string
    location: str | None = None
    status: str = "scheduled"
    home_away: str | None = None
    competition: str | None = None
    score: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
