"""Shared Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for shared/common features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools with new naming convention
from .error_tools import (
    show_command_error,
    show_permission_error,
    show_system_error,
    show_validation_error,
)
from .help_tools import (
    get_system_commands,
    show_help_commands,
    show_help_final,
    show_help_usage,
    show_help_welcome,
)
from .status_tools import (
    get_member_status_by_identifier,
    get_member_status_self,
    get_player_status_by_identifier,
    get_player_status_self,
)
from .system_tools import check_system_ping, check_system_version

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
    "get_player_status_self",
    "get_player_status_by_identifier",
    "get_member_status_self",
    "get_member_status_by_identifier",
    "show_permission_error",
    "show_command_error",
    "show_system_error",
    "show_validation_error",
    # Native CrewAI delegation tools are automatically provided
]
