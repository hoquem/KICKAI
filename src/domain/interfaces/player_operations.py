"""
Domain interface for player operations.

This interface defines the contract for player-related operations
without depending on the application layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class PlayerInfo:
    """Player information data structure."""
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
    """Interface for player operations."""
    
    @abstractmethod
    async def get_player_info(self, user_id: str, team_id: str) -> tuple[bool, str]:
        """Get player information by user ID."""
        pass
    
    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[PlayerInfo]:
        """Get player information by phone number."""
        pass
    
    @abstractmethod
    async def list_players(self, team_id: str, is_leadership_chat: bool = False) -> str:
        """List all players in a team."""
        pass
    
    @abstractmethod
    async def register_player(self, user_id: str, team_id: str, player_id: Optional[str] = None) -> tuple[bool, str]:
        """Register a new player."""
        pass
    
    @abstractmethod
    async def add_player(self, name: str, phone: str, position: str, team_id: str) -> tuple[bool, str]:
        """Add a new player to the team."""
        pass
    
    @abstractmethod
    async def remove_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Remove a player from the team."""
        pass
    
    @abstractmethod
    async def approve_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Approve a player for match squad selection."""
        pass
    
    @abstractmethod
    async def reject_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player for match squad selection."""
        pass
    
    @abstractmethod
    async def reject_player_by_identifier(self, identifier: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Reject a player by player ID or phone number."""
        pass

    @abstractmethod
    async def update_player_info(self, user_id: str, field: str, value: str, team_id: str) -> tuple[bool, str]:
        """Update a player's information."""
        pass
    
    @abstractmethod
    async def get_pending_approvals(self, team_id: str) -> str:
        """Get list of players pending approval."""
        pass
    
    @abstractmethod
    async def injure_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as injured."""
        pass
    
    @abstractmethod
    async def suspend_player(self, player_id: str, reason: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as suspended."""
        pass
    
    @abstractmethod
    async def recover_player(self, player_id: str, team_id: str) -> tuple[bool, str]:
        """Mark a player as recovered."""
        pass 