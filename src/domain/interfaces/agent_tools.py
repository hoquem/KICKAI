"""
Domain interfaces for agent tools.

These interfaces define the contract for agent tools without depending
on specific implementations or layers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PlayerInfo:
    """Player information for tools."""
    id: str
    name: str
    phone: str
    position: str
    status: str
    team_id: str
    telegram_id: Optional[str] = None
    is_approved: bool = False


@dataclass
class MatchInfo:
    """Match information for tools."""
    id: str
    opponent: str
    date: str
    time: str
    venue: str
    competition: str
    team_id: str
    status: str
    result: Optional[str] = None


@dataclass
class TeamInfo:
    """Team information for tools."""
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: str


class IPlayerTools(ABC):
    """Interface for player-related tools."""
    
    @abstractmethod
    async def get_all_players(self, team_id: str) -> List[PlayerInfo]:
        """Get all players for a team."""
        pass
    
    @abstractmethod
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[PlayerInfo]:
        """Get player by ID."""
        pass
    
    @abstractmethod
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[PlayerInfo]:
        """Get player by phone number."""
        pass
    
    @abstractmethod
    async def get_pending_approvals(self, team_id: str) -> List[PlayerInfo]:
        """Get players pending approval."""
        pass


class IMatchTools(ABC):
    """Interface for match-related tools."""
    
    @abstractmethod
    async def get_all_matches(self, team_id: str) -> List[MatchInfo]:
        """Get all matches for a team."""
        pass
    
    @abstractmethod
    async def get_match_by_id(self, match_id: str, team_id: str) -> Optional[MatchInfo]:
        """Get match by ID."""
        pass
    
    @abstractmethod
    async def get_upcoming_matches(self, team_id: str) -> List[MatchInfo]:
        """Get upcoming matches."""
        pass


class ITeamTools(ABC):
    """Interface for team-related tools."""
    
    @abstractmethod
    async def get_team_info(self, team_id: str) -> Optional[TeamInfo]:
        """Get team information."""
        pass
    
    @abstractmethod
    async def get_team_stats(self, team_id: str) -> Dict[str, Any]:
        """Get team statistics."""
        pass


class ICommunicationTools(ABC):
    """Interface for communication tools."""
    
    @abstractmethod
    async def send_message(self, chat_id: str, message: str, team_id: str) -> bool:
        """Send a message to a chat."""
        pass
    
    @abstractmethod
    async def send_poll(self, chat_id: str, question: str, options: List[str], team_id: str) -> bool:
        """Send a poll to a chat."""
        pass
    
    @abstractmethod
    async def send_announcement(self, chat_id: str, announcement: str, team_id: str) -> bool:
        """Send an announcement to a chat."""
        pass


class ILoggingTools(ABC):
    """Interface for logging tools."""
    
    @abstractmethod
    async def log_command(self, user_id: str, command: str, team_id: str, success: bool) -> None:
        """Log a command execution."""
        pass
    
    @abstractmethod
    async def log_event(self, event_type: str, details: Dict[str, Any], team_id: str) -> None:
        """Log an event."""
        pass 