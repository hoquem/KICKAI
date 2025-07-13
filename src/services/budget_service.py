"""
Budget Service Implementation

This service provides budget checking functionality for teams and expenses,
breaking circular dependencies between TeamService and ExpenseService.
"""

import logging
from typing import Tuple, Optional
from datetime import datetime

from database.interfaces import DataStoreInterface
from database.models_improved import ExpenseCategory, Team
from core.exceptions import BudgetError, create_error_context
from services.interfaces.budget_service_interface import IBudgetService

logger = logging.getLogger(__name__)


class BudgetService(IBudgetService):
    """Service for budget checking and management."""
    
    def __init__(self, data_store: DataStoreInterface):
        self._data_store = data_store
    
    async def check_expense_against_budget(self, team_id: str, category: ExpenseCategory, amount: float) -> Tuple[bool, float]:
        """
        Check if an expense can be afforded within the team's budget.
        
        Args:
            team_id: The team ID
            category: The expense category
            amount: The expense amount
            
        Returns:
            Tuple of (can_afford, remaining_budget)
        """
        try:
            # Get team budget
            team_budget = await self.get_team_budget(team_id)
            if team_budget is None:
                logger.warning(f"No budget found for team {team_id}, allowing expense")
                return True, 0.0
            
            # Get category budget
            category_budget = await self.get_category_budget(team_id, category)
            if category_budget is None:
                logger.warning(f"No category budget found for {category.value}, using total budget")
                category_budget = team_budget
            
            # Calculate remaining budget
            remaining_budget = category_budget - amount
            can_afford = remaining_budget >= 0
            
            logger.info(f"Budget check for team {team_id}, category {category.value}: "
                       f"budget={category_budget}, amount={amount}, remaining={remaining_budget}, can_afford={can_afford}")
            
            return can_afford, remaining_budget
            
        except Exception as e:
            logger.error(f"Failed to check budget for team {team_id}: {e}")
            # Default to allowing the expense if budget check fails
            return True, 0.0
    
    async def get_team_budget(self, team_id: str) -> float:
        """
        Get the total budget for a team.
        
        Args:
            team_id: The team ID
            
        Returns:
            The team's total budget
        """
        try:
            team_data = await self._data_store.get_document('teams', team_id)
            if team_data:
                team = Team.from_dict(team_data)
                return team.budget if hasattr(team, 'budget') else 0.0
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get team budget for {team_id}: {e}")
            return 0.0
    
    async def get_category_budget(self, team_id: str, category: ExpenseCategory) -> float:
        """
        Get the budget allocated for a specific category.
        
        Args:
            team_id: The team ID
            category: The expense category
            
        Returns:
            The budget allocated for the category
        """
        try:
            # For now, we'll use a simple percentage-based allocation
            # In a real implementation, this would be stored in the database
            team_budget = await self.get_team_budget(team_id)
            
            # Define category budget percentages
            category_percentages = {
                ExpenseCategory.PITCH_FEES: 0.40,  # 40% for pitch fees
                ExpenseCategory.REFEREE_FEES: 0.20,  # 20% for referee fees
                ExpenseCategory.EQUIPMENT: 0.15,  # 15% for equipment
                ExpenseCategory.TEAM_MEAL: 0.15,  # 15% for team meals
                ExpenseCategory.FA_FEES: 0.05,  # 5% for FA fees
                ExpenseCategory.OTHER: 0.05,  # 5% for other expenses
            }
            
            percentage = category_percentages.get(category, 0.05)
            return team_budget * percentage
            
        except Exception as e:
            logger.error(f"Failed to get category budget for {team_id}, {category.value}: {e}")
            return 0.0
    
    async def update_team_budget(self, team_id: str, new_budget: float) -> bool:
        """
        Update the budget for a team.
        
        Args:
            team_id: The team ID
            new_budget: The new budget amount
            
        Returns:
            True if successful, False otherwise
        """
        try:
            team_data = await self._data_store.get_document('teams', team_id)
            if team_data:
                team_data['budget'] = new_budget
                await self._data_store.update_document('teams', team_id, team_data)
                logger.info(f"Updated budget for team {team_id} to {new_budget}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update budget for team {team_id}: {e}")
            return False 