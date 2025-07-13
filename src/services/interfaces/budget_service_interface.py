"""
Budget Service Interface

This interface defines the contract for budget checking operations,
allowing services to check budget limits without creating circular dependencies.
"""

from abc import ABC, abstractmethod
from typing import Tuple
from database.models_improved import ExpenseCategory


class IBudgetService(ABC):
    """Interface for budget checking operations."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def get_team_budget(self, team_id: str) -> float:
        """
        Get the total budget for a team.
        
        Args:
            team_id: The team ID
            
        Returns:
            The team's total budget
        """
        pass
    
    @abstractmethod
    async def get_category_budget(self, team_id: str, category: ExpenseCategory) -> float:
        """
        Get the budget allocated for a specific category.
        
        Args:
            team_id: The team ID
            category: The expense category
            
        Returns:
            The budget allocated for the category
        """
        pass 