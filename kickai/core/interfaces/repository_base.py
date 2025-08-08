"""
Base repository interfaces for common CRUD operations.

This module contains the fundamental repository interfaces that follow
the Interface Segregation Principle.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """Base repository interface for common CRUD operations."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity and return updated version."""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        pass

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Check if entity exists."""
        pass


class IQueryRepository(ABC):
    """Interface for query operations."""

    @abstractmethod
    async def find_by_criteria(self, criteria: dict[str, Any]) -> list[dict[str, Any]]:
        """Find entities matching criteria."""
        pass

    @abstractmethod
    async def count_by_criteria(self, criteria: dict[str, Any]) -> int:
        """Count entities matching criteria."""
        pass


class IBulkRepository(ABC):
    """Interface for bulk operations."""

    @abstractmethod
    async def save_many(self, entities: list[Any]) -> list[Any]:
        """Save multiple entities."""
        pass

    @abstractmethod
    async def delete_many(self, entity_ids: list[str]) -> int:
        """Delete multiple entities. Returns count of deleted entities."""
        pass
