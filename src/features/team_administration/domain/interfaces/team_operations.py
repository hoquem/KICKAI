"""
Team Operations Interface for Team Administration Feature

Defines the contract for team-related operations in the clean architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TeamInfo:
    id: str
    name: str
    description: str | None
    status: str
    created_at: str

class ITeamOperations(ABC):
    @abstractmethod
    async def create_team(self, name: str, description: str | None = None) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def delete_team(self, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def list_teams(self) -> str:
        pass
    @abstractmethod
    async def get_team_stats(self, team_id: str) -> str:
        pass
