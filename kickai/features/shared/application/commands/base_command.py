"""
Base Command Classes

This module provides base classes and interfaces for command handlers
in the KICKAI system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from kickai.core.enums import PermissionLevel


@dataclass
class CommandContext:
    """Context for command execution."""
    update: Update
    context: ContextTypes.DEFAULT_TYPE
    team_id: str
    user_id: str
    message_text: str
    permission_level: PermissionLevel
    additional_data: dict[str, Any] = None


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str
    error: str | None = None
    data: dict[str, Any] | None = None


class Command(ABC):
    """Abstract base class for command handlers."""

    def __init__(self, name: str, description: str, permission_level: PermissionLevel):
        self.name = name
        self.description = description
        self.permission_level = permission_level

    @abstractmethod
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the command."""
        pass

    def can_execute(self, user_permission_level: PermissionLevel) -> bool:
        """Check if user has permission to execute this command."""
        permission_hierarchy = {
            PermissionLevel.PUBLIC: 0,
            PermissionLevel.PLAYER: 1,
            PermissionLevel.LEADERSHIP: 2,
            PermissionLevel.ADMIN: 3,
            PermissionLevel.SYSTEM: 4
        }

        user_level = permission_hierarchy.get(user_permission_level, 0)
        required_level = permission_hierarchy.get(self.permission_level, 0)

        return user_level >= required_level

    def get_help_text(self) -> str:
        """Get help text for this command."""
        return f"{self.name} - {self.description}\nPermission: {self.permission_level.value}"


class SimpleCommand(Command):
    """Simple command implementation for basic commands."""

    def __init__(self, name: str, description: str, handler_func, permission_level: PermissionLevel = PermissionLevel.PUBLIC):
        super().__init__(name, description, permission_level)
        self.handler_func = handler_func

    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the command using the handler function."""
        try:
            result = await self.handler_func(context.update, context.context, **context.additional_data or {})
            return CommandResult(success=True, message=str(result))
        except Exception as e:
            return CommandResult(success=False, message=f"Error executing command: {e!s}", error=str(e))
