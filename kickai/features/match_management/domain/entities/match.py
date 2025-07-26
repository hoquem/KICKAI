from typing import Union
from dataclasses import dataclass


@dataclass
class Match:
    id: str
    team_id: str
    opponent: str
    date: str  # ISO format string
    location: Union[str, None] = None
    status: str = "scheduled"
    home_away: Union[str, None] = None
    competition: Union[str, None] = None
    score: Union[str, None] = None
    created_at: Union[str, None] = None
    updated_at: Union[str, None] = None
