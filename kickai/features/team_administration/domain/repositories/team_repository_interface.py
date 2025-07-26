#!/usr/bin/env python3
"""
Team Repository Interface

This module defines the interface for team data access operations.
"""

from typing import Union
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Team:
    """Team entity."""
    id: str
    name: str
    description: Union[str, None] = None
    created_at: Union[str, None] = None
    updated_at: Union[str, None] = None


class TeamRepositoryInterface(ABC):
    """Interface for team data access operations."""

    @abstractmethod
    async def create_team(self, team: Team) -> Team:
        """Create a new team."""
        pass

    @abstractmethod
    async def get_team_by_id(self, team_id: str) -> Union[Team, None]:
        """Get a team by ID."""
        pass

    @abstractmethod
    async def get_all_teams(self) -> list[Team]:
        """Get all teams."""
        pass

    @abstractmethod
    async def update_team(self, team: Team) -> Team:
        """Update a team."""
        pass

    @abstractmethod
    async def delete_team(self, team_id: str) -> bool:
        """Delete a team."""
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100) -> list[Team]:
        """List all teams with optional limit."""
        pass
