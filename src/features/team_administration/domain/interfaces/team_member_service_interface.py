from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class ITeamMemberService(ABC):
    @abstractmethod
    async def create_team_member(self, member_data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_team_member(self, member_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_team_member(self, member_id: str, updates: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_team_member(self, member_id: str) -> bool:
        pass

    @abstractmethod
    async def list_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def find_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[Dict[str, Any]]:
        pass 