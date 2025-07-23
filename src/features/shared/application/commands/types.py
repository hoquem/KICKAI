"""
Command Types

This module provides type definitions and enums for the command system.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

from core.enums import PermissionLevel, CommandType


@dataclass
class CommandContext:
    """Context for command execution."""
    update: Update
    context: ContextTypes.DEFAULT_TYPE
    team_id: str
    user_id: str
    message_text: str
    permission_level: PermissionLevel
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class CommandMetadata:
    """Metadata for a command."""
    name: str
    description: str
    command_type: CommandType
    permission_level: PermissionLevel
    feature: str
    aliases: list[str]
    examples: list[str]
    parameters: Dict[str, str]
    help_text: Optional[str] = None 