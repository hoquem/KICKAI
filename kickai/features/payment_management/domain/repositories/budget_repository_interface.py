"""
Budget Repository Interface for Payment Management.

This module defines the interface for budget repository operations,
following clean architecture principles and dependency inversion.
"""

from abc import ABC, abstractmethod
from typing import Any, Union

from kickai.features.payment_management.domain.entities.budget import Budget


class BudgetRepositoryInterface(ABC):
    """Interface for budget repository operations."""

    @abstractmethod
    async def create_budget(self, budget: Budget) -> Budget:
        """Create a new budget."""
        pass

    @abstractmethod
    async def get_budget_by_id(self, budget_id: str) -> Union[Budget, None]:
        """Get budget by ID."""
        pass

    @abstractmethod
    async def get_budget_by_team_id(self, team_id: str) -> Union[Budget, None]:
        """Get budget by team ID."""
        pass

    @abstractmethod
    async def update_budget(self, budget: Budget) -> Budget:
        """Update an existing budget."""
        pass

    @abstractmethod
    async def delete_budget(self, budget_id: str) -> bool:
        """Delete a budget."""
        pass

    @abstractmethod
    async def list_budgets(self, team_id: Union[str, None] = None) -> list[Budget]:
        """List budgets, optionally filtered by team ID."""
        pass

    @abstractmethod
    async def get_budget_summary(self, team_id: str) -> dict[str, Any]:
        """Get budget summary for a team."""
        pass
