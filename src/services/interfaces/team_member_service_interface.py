from abc import ABC, abstractmethod
from typing import List, Optional
from database.models_improved import TeamMember

class ITeamMemberService(ABC):
    @abstractmethod
    async def create_team_member(self, team_member: TeamMember) -> str:
        pass

    @abstractmethod
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        pass

    @abstractmethod
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        pass

    @abstractmethod
    async def update_team_member(self, team_member: TeamMember) -> bool:
        pass

    @abstractmethod
    async def delete_team_member(self, member_id: str) -> bool:
        pass

    @abstractmethod
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        pass

    @abstractmethod
    async def get_team_members_by_role(self, team_id: str, role: str) -> List[TeamMember]:
        pass

    @abstractmethod
    async def get_leadership_members(self, team_id: str) -> List[TeamMember]:
        pass

    @abstractmethod
    async def get_players(self, team_id: str) -> List[TeamMember]:
        pass

    @abstractmethod
    async def add_role_to_member(self, member_id: str, role: str) -> bool:
        pass

    @abstractmethod
    async def remove_role_from_member(self, member_id: str, role: str) -> bool:
        pass

    @abstractmethod
    async def update_chat_access(self, member_id: str, chat_type: str, has_access: bool) -> bool:
        pass

    @abstractmethod
    def is_leadership_role(self, role: str) -> bool:
        pass

    @abstractmethod
    def get_leadership_roles(self) -> set:
        pass

    @abstractmethod
    async def validate_member_roles(self, member: TeamMember) -> List[str]:
        pass 