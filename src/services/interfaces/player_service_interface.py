from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from database.models_improved import Player, OnboardingStatus

class IPlayerService(ABC):
    @abstractmethod
    async def create_player(self, name: str, phone: str, team_id: str, 
                          email: Optional[str] = None, position=None, 
                          role=None, fa_registered: bool = False) -> Player:
        pass

    @abstractmethod
    async def get_player(self, player_id: str) -> Optional[Player]:
        pass

    @abstractmethod
    async def update_player(self, player_id: str, **updates) -> Player:
        pass

    @abstractmethod
    async def delete_player(self, player_id: str) -> bool:
        pass

    @abstractmethod
    async def get_players_by_team(self, team_id: str) -> List[Player]:
        pass

    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: Optional[str] = None) -> Optional[Player]:
        pass

    @abstractmethod
    async def get_player_by_telegram_id(self, telegram_id: str, team_id: Optional[str] = None) -> Optional[Player]:
        pass

    @abstractmethod
    async def get_team_players(self, team_id: str) -> List[Player]:
        pass

    @abstractmethod
    async def get_players_by_status(self, team_id: str, status: OnboardingStatus) -> List[Player]:
        pass

    @abstractmethod
    async def get_all_players(self, team_id: str) -> List[Player]:
        pass 