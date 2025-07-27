"""
Registry module for KICKAI system.

This module provides base classes and utilities for implementing
consistent registry patterns across the system.
"""

from .base import BaseRegistry, RegistryItem, RegistryType
from .consolidated_tool_registry import ConsolidatedToolRegistry, get_consolidated_tool_registry
from .discovery import EntryPointDiscovery
from .validator import RegistryValidator

__all__ = [
    "BaseRegistry",
    "RegistryType",
    "RegistryItem",
    "EntryPointDiscovery",
    "RegistryValidator",
    "ConsolidatedToolRegistry",
    "get_consolidated_tool_registry",
]
