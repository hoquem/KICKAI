"""
Registry module for KICKAI system.

This module provides base classes and utilities for implementing
consistent registry patterns across the system.
"""

from .base import BaseRegistry, RegistryItem, RegistryType
from .discovery import EntryPointDiscovery
from .validator import RegistryValidator

__all__ = [
    "BaseRegistry",
    "EntryPointDiscovery",
    "RegistryItem",
    "RegistryType",
    "RegistryValidator",
]
