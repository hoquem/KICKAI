"""
Command Types

This module provides type definitions and enums for the command system.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from telegram import Update
from telegram.ext import ContextTypes

from kickai.core.enums import CommandType, PermissionLevel


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
    aliases: List[str]
    examples: List[str]
    parameters: Dict[str, str]
    help_text: Optional[str] = None
