from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.database.models_improved import Team, TeamStatus, TeamMember, BotMapping

class ITeamService(ABC):
    @abstractmethod
    async def create_team(self, name: str, description: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> Team:
        pass

    @abstractmethod
    async def get_team(self, team_id: str) -> Optional[Team]:
        pass

    @abstractmethod
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        pass

    @abstractmethod
    async def update_team(self, team_id: str, **updates) -> Team:
        pass

    @abstractmethod
    async def delete_team(self, team_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_teams(self, status: Optional[TeamStatus] = None) -> List[Team]:
        pass

    @abstractmethod
    async def add_team_member(self, team_id: str, user_id: str, role: str = "player", permissions: Optional[List[str]] = None) -> TeamMember:
        pass

    @abstractmethod
    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        pass

    @abstractmethod
    async def create_bot_mapping(self, team_name: str, bot_username: str, chat_id: str, bot_token: str) -> BotMapping:
        pass

    @abstractmethod
    async def get_bot_mapping(self, team_name: str) -> Optional[BotMapping]:
        pass 