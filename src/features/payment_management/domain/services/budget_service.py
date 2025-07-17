"""
Budget Service

This module provides budget management functionality.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..entities.budget import Budget
from ..repositories.budget_repository_interface import BudgetRepositoryInterface
from features.team_administration.domain.entities.team import Team

logger = logging.getLogger(__name__)


class BudgetService:
    """Service for managing budgets."""
    
    def __init__(self, budget_repository: BudgetRepositoryInterface):
        self.budget_repository = budget_repository
    
    async def create_budget(self, team_id: str, amount: float, category: str,
                          description: str, created_by: str) -> Budget:
        """Create a new budget."""
        budget = Budget(
            team_id=team_id,
            amount=amount,
            category=category,
            description=description,
            created_by=created_by,
            created_at=datetime.now()
        )
        return await self.budget_repository.create(budget)
    
    async def get_budget_by_team(self, team_id: str) -> Optional[Budget]:
        """Get budget for a team."""
        return await self.budget_repository.get_by_team(team_id)
    
    async def update_budget(self, budget_id: str, amount: float, description: str) -> Budget:
        """Update a budget."""
        budget = await self.budget_repository.get_by_id(budget_id)
        if not budget:
            raise ValueError(f"Budget with ID {budget_id} not found")
        
        budget.amount = amount
        budget.description = description
        budget.updated_at = datetime.now()
        
        return await self.budget_repository.update(budget)
    
    async def delete_budget(self, budget_id: str) -> bool:
        """Delete a budget."""
        return await self.budget_repository.delete(budget_id)
    
    async def get_budget_utilization(self, team_id: str) -> Dict[str, Any]:
        """Get budget utilization for a team."""
        budget = await self.get_budget_by_team(team_id)
        if not budget:
            return {"utilization": 0.0, "remaining": 0.0, "spent": 0.0}
        
        # This would typically get expenses from expense service
        # For now, return placeholder data
        spent = 0.0  # Would be calculated from expenses
        remaining = budget.amount - spent
        utilization = (spent / budget.amount) * 100 if budget.amount > 0 else 0
        
        return {
            "utilization": utilization,
            "remaining": remaining,
            "spent": spent,
            "total_budget": budget.amount
        } 