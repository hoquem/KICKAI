from dataclasses import dataclass
from typing import Optional

@dataclass
class Match:
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