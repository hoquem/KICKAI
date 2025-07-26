"""
Team Administration Service

This module provides team administration functionality.
"""

import logging
from datetime import datetime
from typing import Any, Union, Union

from ..entities.team import Team, TeamStatus
from ..repositories.team_repository_interface import TeamRepositoryInterface

logger = logging.getLogger(__name__)


class TeamAdministrationService:
    """Service for team administration tasks."""

    def __init__(self, team_repository: TeamRepositoryInterface):
        self.team_repository = team_repository

    async def get_all_teams(self) -> list[Team]:
        """Get all teams."""
        return await self.team_repository.list_all()

    async def get_team_by_id(self, *, team_id: str) -> Union[Team, None]:
        """Get a team by ID."""
        return await self.team_repository.get_by_id(team_id)

    async def get_team_by_name(self, name: str) -> Union[Team, None]:
        """Get a team by name."""
        return await self.team_repository.get_by_name(name)

    async def create_team(self, *, name: str, description: str, created_by: str,
                         settings: Union[dict[str, Any], None] = None) -> Team:
        """Create a new team."""
        team = Team(
            name=name,
            description=description,
            status=TeamStatus.ACTIVE,
            created_by=created_by,
            created_at=datetime.now(),
            settings=settings or {}
        )
        return await self.team_repository.create(team)

    async def update_team(self, team_id: str, name: Union[str, None] = None,
                         description: Union[str, None] = None,
                         status: Union[TeamStatus, None] = None,
                         settings: Union[dict[str, Any], None] = None) -> Team:
        """Update a team."""
        team = await self.team_repository.get_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")

        if name is not None:
            team.name = name
        if description is not None:
            team.description = description
        if status is not None:
            team.status = status
        if settings is not None:
            team.settings.update(settings)

        team.updated_at = datetime.now()

        return await self.team_repository.update(team)

    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        return await self.team_repository.delete(team_id)

    async def get_teams_by_status(self, status: TeamStatus) -> list[Team]:
        """Get teams by status."""
        return await self.team_repository.get_by_status(status)

    async def activate_team(self, team_id: str) -> Team:
        """Activate a team."""
        return await self.update_team(team_id, status=TeamStatus.ACTIVE)

    async def deactivate_team(self, team_id: str) -> Team:
        """Deactivate a team."""
        return await self.update_team(team_id, status=TeamStatus.INACTIVE)
