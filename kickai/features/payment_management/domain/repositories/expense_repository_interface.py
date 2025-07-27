#!/usr/bin/env python3
"""
Expense Repository Interface

This module defines the interface for expense data access operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Expense:
    """Expense entity."""

    id: str
    team_id: str
    description: str
    amount: float
    category: str
    created_by: str
    created_at: str | None = None
    updated_at: str | None = None


class ExpenseRepositoryInterface(ABC):
    """Interface for expense data access operations."""

    @abstractmethod
    async def create_expense(self, expense: Expense) -> Expense:
        """Create a new expense."""
        pass

    @abstractmethod
    async def get_expense_by_id(self, expense_id: str, team_id: str) -> Expense | None:
        """Get an expense by ID."""
        pass

    @abstractmethod
    async def get_all_expenses(self, team_id: str) -> list[Expense]:
        """Get all expenses for a team."""
        pass

    @abstractmethod
    async def update_expense(self, expense: Expense) -> Expense:
        """Update an expense."""
        pass

    @abstractmethod
    async def delete_expense(self, expense_id: str, team_id: str) -> bool:
        """Delete an expense."""
        pass

    @abstractmethod
    async def get_expenses_by_category(self, team_id: str, category: str) -> list[Expense]:
        """Get expenses by category."""
        pass
