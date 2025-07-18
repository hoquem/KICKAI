"""
Team Member Service

This module provides team member management functionality.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from features.team_administration.domain.entities.team_member import TeamMember
# from ..repositories.team_member_repository_interface import TeamMemberRepositoryInterface
from .player_service import PlayerService
from features.team_administration.domain.services.team_service import TeamService

logger = logging.getLogger(__name__)


class TeamMemberService:
    """Service for managing team members."""
    
    def __init__(self, team_member_repository,  # : TeamMemberRepositoryInterface,
                 player_service: PlayerService, team_service: TeamService):
        self.team_member_repository = team_member_repository
        self.player_service = player_service
        self.team_service = team_service
    
    async def add_member(self, player_id: str, team_id: str, role: str,
                        added_by: str) -> TeamMember:
        """Add a member to a team."""
        # Verify player exists
        player = await self.player_service.get_player_by_id(player_id)
        if not player:
            raise ValueError(f"Player with ID {player_id} not found")
        
        # Verify team exists
        team = await self.team_service.get_team_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        team_member = TeamMember(
            id=f"{team_id}_{player_id}",
            user_id=player_id,
            team_id=team_id,
            telegram_id=None,
            roles=[role],
            permissions=[],
            created_at=datetime.now()
        )
        
        return await self.team_member_repository.create(team_member)
    
    async def get_members_by_team(self, *, team_id: str, role: Optional[str] = None) -> List[TeamMember]:
        """Get team members, optionally filtered by role."""
        members = await self.team_member_repository.get_by_team(team_id)
        
        if role:
            members = [member for member in members if member.role == role]
        
        return members
    
    async def get_member_by_player(self, *, player_id: str, team_id: str) -> Optional[TeamMember]:
        """Get team member by player ID and team ID."""
        return await self.team_member_repository.get_by_player(player_id, team_id)
    
    async def update_member_role(self, *, player_id: str, team_id: str, new_role: str) -> TeamMember:
        """Update a team member's role."""
        member = await self.get_member_by_player(player_id=player_id, team_id=team_id)
        if not member:
            raise ValueError(f"Team member not found for player {player_id} in team {team_id}")
        
        member.role = new_role
        member.updated_at = datetime.now()
        
        return await self.team_member_repository.update(member)
    
    async def remove_member(self, *, player_id: str, team_id: str) -> bool:
        """Remove a member from a team."""
        return await self.team_member_repository.delete_by_player(player_id, team_id)
    
    async def get_member_with_details(self, *, player_id: str, team_id: str) -> Dict[str, Any]:
        """Get team member information including player and team details."""
        member = await self.get_member_by_player(player_id=player_id, team_id=team_id)
        if not member:
            return {}
        
        # Get player and team details using injected services
        player = await self.player_service.get_player_by_id(player_id)
        team = await self.team_service.get_team_by_id(team_id)
        
        return {
            'member': member,
            'player': player,
            'team': team
        } 