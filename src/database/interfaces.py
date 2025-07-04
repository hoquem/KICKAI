"""
Data Access Interfaces for KICKAI

This module defines interfaces for data access operations to support
dependency injection and clean architecture principles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import (
    Player, Team, TeamMember, BotMapping, Match, 
    PlayerRole, PlayerPosition, OnboardingStatus, TeamStatus
)


class DataStoreInterface(ABC):
    """Interface for data store operations."""
    
    # Player operations
    @abstractmethod
    async def create_player(self, player: Player) -> str:
        """Create a new player."""
        pass
    
    @abstractmethod
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID."""
        pass
    
    @abstractmethod
    async def get_player_by_phone(self, phone: str) -> Optional[Player]:
        """Get a player by phone number."""
        pass
    
    @abstractmethod
    async def update_player(self, player: Player) -> bool:
        """Update a player."""
        pass
    
    @abstractmethod
    async def delete_player(self, player_id: str) -> bool:
        """Delete a player."""
        pass
    
    @abstractmethod
    async def get_team_players(self, team_id: str) -> List[Player]:
        """Get all players for a team."""
        pass
    
    @abstractmethod
    async def get_players_by_status(self, team_id: str, status: OnboardingStatus) -> List[Player]:
        """Get players by onboarding status."""
        pass
    
    # Team operations
    @abstractmethod
    async def create_team(self, team: Team) -> str:
        """Create a new team."""
        pass
    
    @abstractmethod
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        pass
    
    @abstractmethod
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get a team by name."""
        pass
    
    @abstractmethod
    async def update_team(self, team: Team) -> bool:
        """Update a team."""
        pass
    
    @abstractmethod
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        pass
    
    @abstractmethod
    async def get_all_teams(self, status: Optional[TeamStatus] = None) -> List[Team]:
        """Get all teams, optionally filtered by status."""
        pass
    
    # Team member operations
    @abstractmethod
    async def create_team_member(self, team_member: TeamMember) -> str:
        """Create a new team member."""
        pass
    
    @abstractmethod
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        """Get a team member by ID."""
        pass
    
    @abstractmethod
    async def get_team_member_by_telegram_id(self, telegram_id: str, team_id: str) -> Optional[TeamMember]:
        """Get a team member by telegram ID and team ID."""
        pass
    
    @abstractmethod
    async def update_team_member(self, team_member: TeamMember) -> bool:
        """Update a team member."""
        pass
    
    @abstractmethod
    async def delete_team_member(self, member_id: str) -> bool:
        """Delete a team member."""
        pass
    
    @abstractmethod
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        """Get all team members for a team."""
        pass
    
    # Bot mapping operations
    @abstractmethod
    async def create_bot_mapping(self, bot_mapping: BotMapping) -> str:
        """Create a new bot mapping."""
        pass
    
    @abstractmethod
    async def get_bot_mapping(self, team_name: str) -> Optional[BotMapping]:
        """Get a bot mapping by team name."""
        pass
    
    @abstractmethod
    async def update_bot_mapping(self, bot_mapping: BotMapping) -> bool:
        """Update a bot mapping."""
        pass
    
    @abstractmethod
    async def delete_bot_mapping(self, team_name: str) -> bool:
        """Delete a bot mapping."""
        pass
    
    # Match operations
    @abstractmethod
    async def create_match(self, match: Match) -> str:
        """Create a new match."""
        pass
    
    @abstractmethod
    async def get_match(self, match_id: str) -> Optional[Match]:
        """Get a match by ID."""
        pass
    
    @abstractmethod
    async def update_match(self, match: Match) -> bool:
        """Update a match."""
        pass
    
    @abstractmethod
    async def delete_match(self, match_id: str) -> bool:
        """Delete a match."""
        pass
    
    @abstractmethod
    async def get_team_matches(self, team_id: str) -> List[Match]:
        """Get all matches for a team."""
        pass
    
 