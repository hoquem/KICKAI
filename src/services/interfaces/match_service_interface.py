from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.database.models_improved import Match, MatchStatus

class IMatchService(ABC):
    @abstractmethod
    async def create_match(self, team_id: str, opponent: str, date: datetime, location: Optional[str] = None, status: MatchStatus = MatchStatus.SCHEDULED, home_away: str = "home", competition: Optional[str] = None) -> Match:
        pass

    @abstractmethod
    async def get_match(self, match_id: str) -> Optional[Match]:
        pass

    @abstractmethod
    async def update_match(self, match_id: str, **updates) -> Match:
        pass

    @abstractmethod
    async def delete_match(self, match_id: str) -> bool:
        pass

    @abstractmethod
    async def list_matches(self, team_id: str, status: Optional[MatchStatus] = None) -> List[Match]:
        pass

    @abstractmethod
    async def generate_fixtures(self, team_id: str, num_matches: int, opponents: List[str]) -> List[Match]:
        pass 