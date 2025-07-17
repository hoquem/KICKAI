"""
Team Service

This module provides team management functionality.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.team import Team, TeamStatus
from ..repositories.team_repository_interface import TeamRepositoryInterface
from features.payment_management.domain.services.expense_service import ExpenseService

logger = logging.getLogger(__name__)


class TeamService:
    """Service for managing teams."""
    
    def __init__(self, team_repository: TeamRepositoryInterface, expense_service: ExpenseService):
        self.team_repository = team_repository
        self.expense_service = expense_service
    
    async def create_team(self, name: str, description: str, created_by: str,
                         settings: Optional[Dict[str, Any]] = None) -> Team:
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
    
    async def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """Get a team by ID."""
        return await self.team_repository.get_by_id(team_id)
    
    async def get_teams_by_status(self, status: TeamStatus) -> List[Team]:
        """Get teams by status."""
        return await self.team_repository.get_by_status(status)
    
    async def update_team(self, team_id: str, name: Optional[str] = None,
                         description: Optional[str] = None,
                         settings: Optional[Dict[str, Any]] = None) -> Team:
        """Update a team."""
        team = await self.team_repository.get_by_id(team_id)
        if not team:
            raise ValueError(f"Team with ID {team_id} not found")
        
        if name:
            team.name = name
        if description:
            team.description = description
        if settings:
            team.settings.update(settings)
        
        team.updated_at = datetime.now()
        
        return await self.team_repository.update(team)
    
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        return await self.team_repository.delete(team_id)
    
    async def get_team_financial_summary(self, team_id: str) -> Dict[str, Any]:
        """Get financial summary for a team including expenses."""
        team = await self.get_team_by_id(team_id)
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