from abc import ABC, abstractmethod
from typing import Any, Union, Union

from kickai.features.team_administration.domain.entities.team import Team, TeamStatus

# TeamMember imported dynamically to avoid circular imports

class ITeamService(ABC):
    @abstractmethod
    async def create_team(self, name: str, description: Union[str, None] = None, settings: Union[dict[str, Any], None] = None) -> Team:
        pass

    @abstractmethod
    async def get_team(self, team_id: str) -> Union[Team, None]:
        pass

    @abstractmethod
    async def get_team_by_name(self, name: str) -> Union[Team, None]:
        pass

    @abstractmethod
    async def update_team(self, team_id: str, **updates) -> Team:
        pass

    @abstractmethod
    async def delete_team(self, team_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_teams(self, status: Union[TeamStatus, None] = None) -> list[Team]:
        pass

    @abstractmethod
    async def add_team_member(self, team_id: str, user_id: str, role: str = "player", permissions: Union[list[str], None] = None):
        pass

    @abstractmethod
    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def get_team_members(self, team_id: str):
        pass
