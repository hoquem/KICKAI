"""Shared Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for shared/common features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools with new naming convention
from .help_tools import (
    show_help_commands,
    show_help_final,
    show_help_usage,
    show_help_welcome,
    get_system_commands
)
from .system_tools import check_system_ping, check_system_version
from .status_tools import get_status_my, get_status_user, get_status_player
from .error_tools import show_error_permission, show_error_command
# Native CrewAI delegation - no custom delegation tools needed

# Export all tools for agent registration with new naming convention
__all__ = [
    "show_help_commands",
    "show_help_final", 
    "show_help_usage",
    "show_help_welcome",
    "get_system_commands",
    "check_system_ping",
    "check_system_version",
    "get_status_my",
    "get_status_user",
    "get_status_player",
    "show_error_permission",
    "show_error_command",
# Native CrewAI delegation tools are automatically provided
]