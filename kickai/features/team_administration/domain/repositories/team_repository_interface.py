
#!/usr/bin/env python3
"""
Team Repository Interface

This module defines the interface for team data access operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Team:
    """Team entity."""

    id: str
    name: str
    description: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class TeamRepositoryInterface(ABC):
    """Interface for team data access operations."""

    @abstractmethod
    async def create_team(self, team: Team) -> Team:
        """Create a new team."""
        pass

    # Alias used in some tests/mocks
    @abstractmethod
    async def create(self, team: Team) -> Team:
        """Create a new team (alias for create_team)."""
        pass

    @abstractmethod
    async def get_team_by_id(self, team_id: str) -> Team | None:
        """Get a team by ID."""
        pass

    # Alias used in some tests/mocks
    @abstractmethod
    async def get_by_id(self, team_id: str) -> Team | None:
        """Get a team by ID (alias)."""
        pass

    @abstractmethod
    async def get_all_teams(self) -> list[Team]:
        """Get all teams."""
        pass

    @abstractmethod
    async def get_by_status(self, status: str) -> list[Team]:
        """Get teams by status (alias used in tests)."""
        pass

    @abstractmethod
    async def update_team(self, team: Team) -> Team:
        """Update a team."""
        pass

    # Alias used in some tests/mocks
    @abstractmethod
    async def update(self, team: Team) -> Team:
        """Update a team (alias)."""
        pass

    @abstractmethod
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100) -> list[Team]:
        """List all teams with optional limit."""
        pass
