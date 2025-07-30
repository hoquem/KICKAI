"""
Command Types

This module provides type definitions and enums for the command system.
"""

from dataclasses import dataclass
from typing import Any

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
    additional_data: dict[str, Any] | None = None


@dataclass
class CommandResult:
    """Result of command execution."""

    success: bool
    message: str
    error: str | None = None
    data: dict[str, Any] | None = None


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
    parameters: dict[str, str]
    help_text: str | None = None
