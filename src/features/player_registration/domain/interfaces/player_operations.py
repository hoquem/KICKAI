"""
Player Operations Interface for Player Registration Feature

Defines the contract for player-related operations in the clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class PlayerInfo:
    id: str
    name: str
    phone: str
    position: str
    status: str
    team_id: str
    telegram_id: Optional[str] = None
    is_approved: bool = False
    is_injured: bool = False
    is_suspended: bool = False

class IPlayerOperations(ABC):
    @abstractmethod
    async def get_player_info(self, user_id: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[PlayerInfo]:
        pass
    @abstractmethod
    async def list_players(self, team_id: str, is_leadership_chat: bool = False) -> str:
        pass
    @abstractmethod
    async def register_player(self, user_id: str, team_id: str, player_id: Optional[str] = None) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def add_player(self, name: str, phone: str, position: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def remove_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def approve_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def reject_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def reject_player_by_identifier(self, identifier: str, reason: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def update_player_info(self, user_id: str, field: str, value: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def get_pending_approvals(self, team_id: str) -> str:
        pass
    @abstractmethod
    async def injure_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def suspend_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        pass
    @abstractmethod
    async def recover_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        pass 