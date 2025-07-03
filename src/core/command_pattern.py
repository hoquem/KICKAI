#!/usr/bin/env python3
"""
Command Pattern Implementation for KICKAI Bot

This module implements a clean Command Pattern with Strategy Pattern for
permission handling and context-aware command execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ChatType(Enum):
    """Chat types for permission checking."""
    MAIN = "main"
    LEADERSHIP = "leadership"
    PRIVATE = "private"


class PermissionLevel(Enum):
    """Permission levels for commands."""
    PUBLIC = "public"           # Available to everyone
    PLAYER = "player"           # Available to registered players
    LEADERSHIP = "leadership"   # Available to leadership team
    ADMIN = "admin"             # Available to admins only


@dataclass
class CommandContext:
    """Context for command execution."""
    user_id: str
    chat_id: str
    chat_type: ChatType
    user_role: str
    team_id: str
    message_text: str


class Command(ABC):
    """Abstract base class for all commands."""
    
    def __init__(self, name: str, description: str, permission_level: PermissionLevel):
        self.name = name
        self.description = description
        self.permission_level = permission_level
    
    @abstractmethod
    async def execute(self, context: CommandContext) -> str:
        """Execute the command with given context."""
        pass
    
    def can_execute(self, context: CommandContext) -> bool:
        """Check if command can be executed in given context."""
        if self.permission_level == PermissionLevel.PUBLIC:
            return True
        
        if self.permission_level == PermissionLevel.PLAYER:
            return context.user_role in ['player', 'admin', 'captain', 'secretary', 'manager', 'treasurer']
        
        if self.permission_level == PermissionLevel.LEADERSHIP:
            return context.chat_type == ChatType.LEADERSHIP and context.user_role in ['admin', 'captain', 'secretary', 'manager', 'treasurer']
        
        if self.permission_level == PermissionLevel.ADMIN:
            return context.chat_type == ChatType.LEADERSHIP and context.user_role in ['admin', 'captain']
        
        return False
    
    def get_help_text(self, context: CommandContext) -> str:
        """Get help text for this command based on context."""
        if not self.can_execute(context):
            return ""
        
        return f"• `{self.name}` - {self.description}"


class CommandRegistry:
    """Registry for all available commands."""
    
    def __init__(self):
        self._commands: Dict[str, Command] = {}
    
    def register(self, command: Command):
        """Register a command."""
        self._commands[command.name] = command
        logger.info(f"Registered command: {command.name}")
    
    def get_command(self, name: str) -> Optional[Command]:
        """Get a command by name."""
        return self._commands.get(name)
    
    def get_available_commands(self, context: CommandContext) -> List[Command]:
        """Get all commands available in given context."""
        return [cmd for cmd in self._commands.values() if cmd.can_execute(context)]
    
    def get_help_message(self, context: CommandContext) -> str:
        """Generate help message based on context."""
        available_commands = self.get_available_commands(context)
        
        if context.chat_type == ChatType.LEADERSHIP:
            title = "🤖 **KICKAI Bot Help (Leadership)**"
        else:
            title = "🤖 **KICKAI Bot Help**"
        
        message = f"{title}\n\n📋 **Available Commands:**\n\n"
        
        # Group commands by permission level
        public_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PUBLIC]
        player_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.PLAYER]
        leadership_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.LEADERSHIP]
        admin_commands = [cmd for cmd in available_commands if cmd.permission_level == PermissionLevel.ADMIN]
        
        if public_commands:
            message += "🌐 **General Commands:**\n"
            for cmd in public_commands:
                message += f"{cmd.get_help_text(context)}\n"
            message += "\n"
        
        if player_commands:
            message += "👥 **Player Commands:**\n"
            for cmd in player_commands:
                message += f"{cmd.get_help_text(context)}\n"
            message += "\n"
        
        if leadership_commands:
            message += "👑 **Leadership Commands:**\n"
            for cmd in leadership_commands:
                message += f"{cmd.get_help_text(context)}\n"
            message += "\n"
        
        if admin_commands:
            message += "🔧 **Admin Commands:**\n"
            for cmd in admin_commands:
                message += f"{cmd.get_help_text(context)}\n"
            message += "\n"
        
        message += "💡 **Tips:**\n"
        message += "• You can use natural language or specific commands\n"
        if context.chat_type != ChatType.LEADERSHIP:
            message += "• Admin commands are only available in the leadership chat\n"
        
        return message


class CommandExecutor:
    """Main command executor with permission checking."""
    
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
    
    async def execute_command(self, command_name: str, context: CommandContext) -> str:
        """Execute a command with proper permission checking."""
        command = self.registry.get_command(command_name)
        
        if not command:
            return f"❌ Unknown command: `{command_name}`\n\nType `/help` for available commands."
        
        if not command.can_execute(context):
            return self._get_access_denied_message(command, context)
        
        try:
            return await command.execute(context)
        except Exception as e:
            logger.error(f"Error executing command {command_name}: {e}")
            return f"❌ Error executing command: {str(e)}"
    
    def _get_access_denied_message(self, command: Command, context: CommandContext) -> str:
        """Get access denied message."""
        if context.chat_type != ChatType.LEADERSHIP and command.permission_level in [PermissionLevel.LEADERSHIP, PermissionLevel.ADMIN]:
            return f"""❌ **Access Denied**

🔒 This command requires leadership chat access.
💡 Please use the leadership chat for admin functions.

Command: `{command.name}`
Required: {command.permission_level.value.title()} access"""
        
        return f"""❌ **Access Denied**

🔒 You don't have permission to use this command.
💡 Contact your team admin for access.

Command: `{command.name}`
Required: {command.permission_level.value.title()} access
Your Role: {context.user_role.title()}"""


# Global command registry instance
command_registry = CommandRegistry()
command_executor = CommandExecutor(command_registry)


def register_command(cls):
    """Decorator to register command classes."""
    instance = cls()
    command_registry.register(instance)
    return cls


def get_command_executor() -> CommandExecutor:
    """Get the global command executor."""
    return command_executor


def get_command_registry() -> CommandRegistry:
    """Get the global command registry."""
    return command_registry 