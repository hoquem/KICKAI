"""
Base registry classes for KICKAI system.

This module provides the foundation for all registry implementations
with common functionality and patterns.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar

from loguru import logger

T = TypeVar("T")


class RegistryType(Enum):
    """Types of registries supported by the system."""

    TOOL = "tool"
    COMMAND = "command"
    SERVICE = "service"
    AGENT = "agent"
    TASK = "task"


@dataclass
class RegistryItem(Generic[T]):
    """Metadata for a registry item."""

    name: str
    item: T
    metadata: dict[str, Any] = field(default_factory=dict)
    registry_type: RegistryType = RegistryType.TOOL
    version: str = "1.0.0"
    enabled: bool = True
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


class BaseRegistry(ABC, Generic[T]):
    """Base registry class with common functionality."""

    def __init__(self, registry_type: RegistryType, name: str):
        self._items: dict[str, RegistryItem[T]] = {}
        self._aliases: dict[str, str] = {}
        self._registry_type = registry_type
        self._name = name
        self._initialized = False
        self._discovery_hooks: list[callable] = []

        logger.info(f"🔧 Initialized {name} ({registry_type.value})")

    @abstractmethod
    def register(self, name: str, item: T, **metadata) -> None:
        """Register an item with metadata."""
        pass

    @abstractmethod
    def get(self, name: str) -> T | None:
        """Get an item by name."""
        pass

    def add_discovery_hook(self, hook: callable) -> None:
        """Add a discovery hook."""
        self._discovery_hooks.append(hook)

    def discover_from_entry_points(self, entry_point_group: str) -> None:
        """Discover items from setuptools entry points."""
        import pkg_resources

        for entry_point in pkg_resources.iter_entry_points(entry_point_group):
            try:
                item = entry_point.load()
                self.register(entry_point.name, item)
                logger.info(f"✅ Discovered {entry_point.name} from entry points")
            except Exception as e:
                logger.error(f"❌ Failed to load {entry_point.name}: {e}")

    def run_discovery_hooks(self) -> None:
        """Run all discovery hooks."""
        for hook in self._discovery_hooks:
            try:
                hook(self)
            except Exception as e:
                logger.error(f"❌ Discovery hook failed: {e}")

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics."""
        return {
            "name": self._name,
            "type": self._registry_type.value,
            "total_items": len(self._items),
            "total_aliases": len(self._aliases),
            "initialized": self._initialized,
            "enabled_items": len([item for item in self._items.values() if item.enabled]),
        }

    def validate(self) -> list[str]:
        """Validate registry state."""
        errors = []

        # Check for duplicate names
        names = list(self._items.keys())
        if len(names) != len(set(names)):
            errors.append("Duplicate item names found")

        # Check for circular aliases
        for alias, target in self._aliases.items():
            if target in self._aliases and self._aliases[target] == alias:
                errors.append(f"Circular alias detected: {alias} <-> {target}")

        return errors

    def cleanup(self) -> None:
        """Clean up registry resources."""
        self._items.clear()
        self._aliases.clear()
        self._initialized = False
        logger.info(f"🧹 Cleaned up {self._name}")
