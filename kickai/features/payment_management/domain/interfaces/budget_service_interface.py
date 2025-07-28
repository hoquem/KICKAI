"""
Budget Service Interface

This module defines the interface for budget management services.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..entities.budget import Budget


class BudgetServiceInterface(ABC):
    """Interface for budget management services."""

    @abstractmethod
    async def create_budget(
        self, team_id: str, amount: float, category: str, description: str, created_by: str
    ) -> Budget:
        """Create a new budget."""
        pass

    @abstractmethod
    async def get_budget_by_team(self, team_id: str) -> Optional[Budget]:
        """Get budget for a team."""
        pass

    @abstractmethod
    async def update_budget(self, budget_id: str, amount: float, description: str) -> Budget:
        """Update a budget."""
        pass

    @abstractmethod
    async def delete_budget(self, budget_id: str) -> bool:
        """Delete a budget."""
        pass

    @abstractmethod
    async def get_budget_utilization(self, team_id: str) -> Dict[str, Any]:
        """Get budget utilization for a team."""
        pass
