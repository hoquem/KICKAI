"""
Expense Service Interface

This module defines the interface for expense management services.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.expense import Expense, ExpenseCategory


class ExpenseServiceInterface(ABC):
    """Interface for expense management services."""
    
    @abstractmethod
    async def create_expense(self, amount: float, description: str, category: ExpenseCategory,
                           team_id: str, created_by: str, date: Optional[datetime] = None) -> Expense:
        """Create a new expense."""
        pass
    
    @abstractmethod
    async def get_expenses_by_team(self, team_id: str, limit: Optional[int] = None) -> List[Expense]:
        """Get expenses for a team."""
        pass
    
    @abstractmethod
    async def get_expenses_by_category(self, team_id: str, category: ExpenseCategory) -> List[Expense]:
        """Get expenses by category for a team."""
        pass
    
    @abstractmethod
    async def get_total_expenses(self, team_id: str, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> float:
        """Get total expenses for a team within a date range."""
        pass
    
    @abstractmethod
    async def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense."""
        pass 