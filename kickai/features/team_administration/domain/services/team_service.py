"""
Team Service

This module provides team management functionality.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger

from kickai.features.payment_management.domain.services.expense_service import ExpenseService

from ..entities.team import Team, TeamStatus
from ..entities.team_member import TeamMember
from ..repositories.team_repository_interface import TeamRepositoryInterface

logger = logging.getLogger(__name__)


@dataclass
class TeamCreateParams:
    name: str
    description: str = ""
    status: TeamStatus = TeamStatus.ACTIVE
    created_by: str = "system"
    settings: dict[str, Any] | None = None
    bot_token: str | None = None
    main_chat_id: str | None = None
    leadership_chat_id: str | None = None


class TeamService:
    """Service for managing teams."""

    def __init__(self, team_repository: TeamRepositoryInterface, expense_service: ExpenseService):
        self.team_repository = team_repository
        self.expense_service = expense_service
        self.logger = logger

    async def create_team(self, params: TeamCreateParams) -> Team:
        """Create a new team."""
        team = Team(
            name=params.name,
            description=params.description,
            status=params.status,
            created_by=params.created_by,
            created_at=datetime.now(),
            settings=params.settings or {},
            bot_token=params.bot_token,
            main_chat_id=params.main_chat_id,
            leadership_chat_id=params.leadership_chat_id
        )
        return await self.team_repository.create_team(team)

    async def get_team(self, *, team_id: str) -> Team | None:
        """Get a team by ID."""
        return await self.team_repository.get_team_by_id(team_id)

    async def get_team_by_id(self, *, team_id: str) -> Team | None:
        """Get a team by ID (alias for get_team)."""
        return await self.get_team(team_id=team_id)

    async def get_team_by_name(self, name: str) -> Team | None:
        """Get a team by name."""
        # This would need to be implemented in the repository
        # For now, get all teams and filter by name
        all_teams = await self.get_all_teams()
        for team in all_teams:
            if team.name == name:
                return team
        return None

    async def get_all_teams(self) -> list[Team]:
        """Get all teams from the repository."""
        try:
            teams = await self.team_repository.list_all()
            self.logger.info(f"📊 Retrieved {len(teams)} teams from repository")
            return teams
        except Exception as e:
            self.logger.error(f"❌ Failed to get all teams: {e}")
            return []

    async def get_teams_by_status(self, status: TeamStatus) -> list[Team]:
        """Get teams by status."""
        return await self.team_repository.get_by_status(status)

    async def update_team(self, team_id: str, **updates) -> Team:
        """Update a team with provided updates."""
        team = await self.team_repository.get_team_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")

        # Apply updates
        for key, value in updates.items():
            if hasattr(team, key):
                setattr(team, key, value)

        team.updated_at = datetime.now()

        return await self.team_repository.update_team(team)

    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        return await self.team_repository.delete(team_id)

    async def add_team_member(self, team_id: str, user_id: str, role: str = "player",
                             permissions: list[str] | None = None, name: str = "", phone: str = ""):
        """Add a member to a team."""
        # Import TeamMember dynamically to avoid circular imports
        from kickai.features.team_administration.domain.entities.team_member import TeamMember

        # Create team member entity
        team_member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            name=name,
            phone=phone,
            telegram_id=user_id,  # Set telegram_id to user_id for telegram users
            roles=[role],  # Convert single role to list
            permissions=permissions or [],
            joined_at=datetime.now()
        )

        # Save to repository
        return await self.team_repository.create_team_member(team_member)

    async def remove_team_member(self, team_id: str, user_id: str) -> bool:
        """Remove a member from a team."""
        # Get team member first
        team_members = await self.get_team_members(team_id)
        for member in team_members:
            if member.user_id == user_id:
                return await self.team_repository.delete_team_member(member.id)
        return False

    async def get_team_members(self, team_id: str) -> list[TeamMember]:
        """Get all members of a team."""
        return await self.team_repository.get_team_members(team_id)

    async def get_team_member_by_telegram_id(self, team_id: str, telegram_id: str) -> TeamMember | None:
        """Get a team member by Telegram ID."""
        return await self.team_repository.get_team_member_by_telegram_id(team_id, telegram_id)

    async def get_team_financial_summary(self, team_id: str) -> dict[str, Any]:
        """Get financial summary for a team including expenses."""
        team = await self.get_team_by_id(team_id=team_id)
        if not team:
            return {}

        # Get total expenses using injected expense service
        total_expenses = await self.expense_service.get_total_expenses(team_id)

        # Get budget information (would need budget service injection)
        budget_info = {
            'total_budget': 0.0,  # Would be calculated from budget service
            'remaining_budget': 0.0,
            'utilization_percentage': 0.0
        }

        return {
            'team_id': team_id,
            'team_name': team.name,
            'total_expenses': total_expenses,
            'budget_info': budget_info,
            'last_updated': datetime.now().isoformat()
        }
