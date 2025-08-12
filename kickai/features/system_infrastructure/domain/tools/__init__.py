#!/usr/bin/env python3
"""
System infrastructure tools module.

This module provides tools for system infrastructure operations.
"""

# Note: Most system infrastructure tools are currently unused by agents
# These tools are kept for potential future use but not exported to avoid clutter
# - log_command: Not used by any agent
# - log_error: Not used by any agent
# - get_firebase_document: Not used by any agent

# Export tools that are used by agents (using native CrewAI tools)
from .system_tools_native import get_system_available_commands, get_version_info

__all__ = [
    "get_system_available_commands", 
    "get_version_info",
]

# Note: JSON versions of these tools are deprecated and should not be used
# All imports now use native CrewAI tools with plain string returns
