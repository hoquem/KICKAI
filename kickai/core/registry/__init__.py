"""
Registry module for KICKAI system.

This module provides base classes and utilities for implementing
consistent registry patterns across the system.
"""

from .base import BaseRegistry, RegistryType, RegistryItem
from .discovery import EntryPointDiscovery
from .validator import RegistryValidator
from .consolidated_tool_registry import ConsolidatedToolRegistry, get_consolidated_tool_registry

__all__ = [
    'BaseRegistry',
    'RegistryType', 
    'RegistryItem',
    'EntryPointDiscovery',
    'RegistryValidator',
    'ConsolidatedToolRegistry',
    'get_consolidated_tool_registry'
] 