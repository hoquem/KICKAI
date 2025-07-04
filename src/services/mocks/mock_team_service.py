"""
Mock Team Service

This module provides a mock implementation of the TeamService interface
for testing purposes.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..interfaces.team_service_interface import ITeamService
from ...database.models import Team, TeamStatus, TeamMember, BotMapping


class MockTeamService(ITeamService):
    """Mock implementation of TeamService for testing."""
    
    def __init__(self):
        self._teams: Dict[str, Team] = {}
        self._team_members: Dict[str, List[TeamMember]] = {}
        self._bot_mappings: Dict[str, BotMapping] = {}
        self._next_id = 1
        self.logger = logging.getLogger(__name__)
    
    async def create_team(self, name: str, description: Optional[str] = None,
                         settings: Optional[Dict[str, Any]] = None) -> Team:
        """Create a new team with validation."""
        team_id = f"T{self._next_id:03d}"
        self._next_id += 1
        
        team = Team(
            id=team_id,
            name=name.strip(),
            description=description.strip() if description else None,
            status=TeamStatus.ACTIVE,
            settings=settings or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._teams[team_id] = team
        self._team_members[team_id] = []
        self.logger.info(f"Mock: Team created: {team.name} ({team_id})")
        return team
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        team = self._teams.get(team_id)
        if team:
            self.logger.info(f"Mock: Team retrieved: {team.name}")
        return team
    
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get a team by name."""
        for team in self._teams.values():
            if team.name == name:
                return team
        return None
    
    async def update_team(self, team_id: str, **updates) -> Team:
        """Update a team with validation."""
        team = self._teams.get(team_id)
        if not team:
            raise ValueError(f"Team not found: {team_id}")
        
        # Update the team
        for key, value in updates.items():
            if hasattr(team, key):
                setattr(team, key, value)
        
        team.updated_at = datetime.now()
        self.logger.info(f"Mock: Team updated: {team.name}")
        return team
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        if team_id not in self._teams:
            raise ValueError(f"Team not found: {team_id}")
        
        team = self._teams[team_id]
        del self._teams[team_id]
        if team_id in self._team_members:
            del self._team_members[team_id]
        self.logger.info(f"Mock: Team deleted: {team.name}")
        return True
    
    async def get_all_teams(self, status: Optional[TeamStatus] = None) -> List[Team]:
        """Get all teams, optionally filtered by status."""
        teams = list(self._teams.values())
        if status:
            teams = [t for t in teams if t.status == status]
        self.logger.info(f"Mock: Retrieved {len(teams)} teams")
        return teams
    
    async def add_team_member(self, team_id: str, user_id: str, role: str = "player",
                            permissions: Optional[List[str]] = None) -> TeamMember:
        """Add a member to a team."""
        if team_id not in self._teams:
            raise ValueError(f"Team not found: {team_id}")
        
        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            roles=[role],
            permissions=permissions or [],
            joined_at=datetime.now()
        )
        
        if team_id not in self._team_members:
            self._team_members[team_id] = []
        
        self._team_members[team_id].append(member)
        self.logger.info(f"Mock: Team member added: {user_id} to team {team_id}")
        return member
    
    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        if team_id not in self._team_members:
            return False
        
        members = self._team_members[team_id]
        for i, member in enumerate(members):
            if member.user_id == user_id:
                del members[i]
                self.logger.info(f"Mock: Team member removed: {user_id} from team {team_id}")
                return True
        
        return False
    
    async def get_team_members(self, team_id: str) -> List[TeamMember]:
        """Get all members of a team."""
        members = self._team_members.get(team_id, [])
        self.logger.info(f"Mock: Retrieved {len(members)} members for team {team_id}")
        return members
    
    async def create_bot_mapping(self, team_name: str, bot_username: str, 
                               chat_id: str, bot_token: str) -> BotMapping:
        """Create a bot mapping for a team."""
        mapping = BotMapping(
            team_name=team_name,
            bot_username=bot_username,
            chat_id=chat_id,
            bot_token=bot_token,
            created_at=datetime.now()
        )
        
        self._bot_mappings[team_name] = mapping
        self.logger.info(f"Mock: Bot mapping created for team: {team_name}")
        return mapping
    
    async def get_bot_mapping(self, team_name: str) -> Optional[BotMapping]:
        """Get bot mapping for a team."""
        return self._bot_mappings.get(team_name)
    
    def reset(self):
        """Reset the mock service state."""
        self._teams.clear()
        self._team_members.clear()
        self._bot_mappings.clear()
        self._next_id = 1
        self.logger.info("Mock: Team service reset") 