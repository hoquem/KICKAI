"""
Command Types

This module provides type definitions and enums for the command system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes


class PermissionLevel(Enum):
    """Permission levels for commands."""
    PUBLIC = "public"
    PLAYER = "player"
    LEADERSHIP = "leadership"
    ADMIN = "admin"
    SYSTEM = "system"


class CommandType(Enum):
    """Types of commands supported by the system."""
    SLASH_COMMAND = "slash_command"
    NATURAL_LANGUAGE = "natural_language"
    ADMIN_COMMAND = "admin_command"
    SYSTEM_COMMAND = "system_command"


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