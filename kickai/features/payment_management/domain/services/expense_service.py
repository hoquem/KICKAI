"""
Expense Service

This module provides expense management functionality.
"""
from typing import Optional, List

import logging
from datetime import datetime

from ..entities.expense import Expense
from ..repositories.expense_repository_interface import ExpenseRepositoryInterface

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service for managing expenses."""

    def __init__(self, expense_repository: ExpenseRepositoryInterface):
        self.expense_repository = expense_repository

    async def create_expense(
        self, *, team_id: str, amount: float, description: str, category: str, created_by: str
    ) -> Expense:
        """Create a new expense."""
        expense = Expense(
            team_id=team_id,
            amount=amount,
            description=description,
            category=category,
            created_by=created_by,
            created_at=datetime.now(),
        )
        return await self.expense_repository.create(expense)

    async def get_expense_by_id(self, expense_id: str) -> Optional[Expense]:
        """Get an expense by ID."""
        return await self.expense_repository.get_by_id(expense_id)

    async def get_expenses_by_team(self, *, team_id: str) -> List[Expense]:
        """Get all expenses for a team."""
        return await self.expense_repository.get_by_team(team_id)

    async def get_total_expenses(self, *, team_id: str) -> float:
        """Get total expenses for a team."""
        expenses = await self.get_expenses_by_team(team_id=team_id)
        return sum(expense.amount for expense in expenses)

    async def update_expense(
        self,
        expense_id: str,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Expense:
        """Update an expense."""
        expense = await self.expense_repository.get_by_id(expense_id)
        if not expense:
            raise ValueError(f"Expense with ID {expense_id} not found")

        if amount is not None:
            expense.amount = amount
        if description is not None:
            expense.description = description
        if category is not None:
            expense.category = category

        expense.updated_at = datetime.now()

        return await self.expense_repository.update(expense)

    async def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense."""
        return await self.expense_repository.delete(expense_id)
