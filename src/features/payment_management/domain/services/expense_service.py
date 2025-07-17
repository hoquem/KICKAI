"""
Expense Service

This module provides expense management functionality.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.expense import Expense, ExpenseCategory
from ..repositories.expense_repository_interface import ExpenseRepositoryInterface

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service for managing expenses."""
    
    def __init__(self, expense_repository: ExpenseRepositoryInterface):
        self.expense_repository = expense_repository
    
    async def create_expense(self, amount: float, description: str, category: ExpenseCategory,
                           team_id: str, created_by: str, date: Optional[datetime] = None) -> Expense:
        """Create a new expense."""
        expense = Expense(
            amount=amount,
            description=description,
            category=category,
            team_id=team_id,
            created_by=created_by,
            date=date or datetime.now()
        )
        return await self.expense_repository.create(expense)
    
    async def get_expenses_by_team(self, team_id: str, limit: Optional[int] = None) -> List[Expense]:
        """Get expenses for a team."""
        return await self.expense_repository.get_by_team(team_id, limit)
    
    async def get_expenses_by_category(self, team_id: str, category: ExpenseCategory) -> List[Expense]:
        """Get expenses by category for a team."""
        return await self.expense_repository.get_by_category(team_id, category)
    
    async def get_total_expenses(self, team_id: str, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> float:
        """Get total expenses for a team within a date range."""
        expenses = await self.expense_repository.get_by_team(team_id)
        
        if start_date or end_date:
            expenses = [
                expense for expense in expenses
                if (not start_date or expense.date >= start_date) and
                   (not end_date or expense.date <= end_date)
            ]
        
        return sum(expense.amount for expense in expenses)
    
    async def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense."""
        return await self.expense_repository.delete(expense_id) 