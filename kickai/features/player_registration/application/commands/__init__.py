"""
Player Registration Commands

This module provides command handlers for player registration functionality.
Commands are registered using @command decorators in individual files.
"""

# Import command modules to ensure decorators are executed
from . import check_fa_command, player_commands, update_commands

__all__ = ["check_fa_command", "player_commands", "update_commands"]
