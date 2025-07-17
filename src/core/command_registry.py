"""
Unified Command Registry

This module provides a centralized command registry for the KICKAI system.
It discovers, registers, and manages all commands across the feature-based modular architecture.
"""

import logging
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Type
from pathlib import Path

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Types of commands supported by the system."""
    SLASH_COMMAND = "slash_command"
    NATURAL_LANGUAGE = "natural_language"
    ADMIN_COMMAND = "admin_command"
    SYSTEM_COMMAND = "system_command"


class PermissionLevel(Enum):
    """Permission levels for commands."""
    PUBLIC = "public"
    PLAYER = "player"
    LEADERSHIP = "leadership"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class CommandMetadata:
    """Metadata for a command."""
    name: str
    description: str
    command_type: CommandType
    permission_level: PermissionLevel
    feature: str
    handler: Callable
    aliases: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    parameters: Dict[str, str] = field(default_factory=dict)
    help_text: Optional[str] = None


class CommandHandler(ABC):
    """Abstract base class for command handlers."""
    
    @abstractmethod
    async def execute(self, update, context, **kwargs) -> str:
        """Execute the command."""
        pass


class CommandRegistry:
    """
    Unified command registry for the KICKAI system.
    
    This registry provides:
    - Automatic command discovery from feature modules
    - Centralized command registration and management
    - Command metadata and documentation
    - Permission-based command filtering
    - Command help and examples
    """
    
    def __init__(self):
        self._commands: Dict[str, CommandMetadata] = {}
        self._command_aliases: Dict[str, str] = {}
        self._feature_commands: Dict[str, List[str]] = {}
        self._discovered = False
    
    def register_command(
        self,
        name: str,
        description: str,
        handler: Callable,
        command_type: CommandType = CommandType.SLASH_COMMAND,
        permission_level: PermissionLevel = PermissionLevel.PUBLIC,
        feature: str = "unknown",
        aliases: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        parameters: Optional[Dict[str, str]] = None,
        help_text: Optional[str] = None
    ) -> None:
        """
        Register a command with the registry.
        
        Args:
            name: Command name (e.g., "/add", "/status")
            description: Command description
            handler: Command handler function
            command_type: Type of command
            permission_level: Required permission level
            feature: Feature module name
            aliases: Alternative command names
            examples: Example usage
            parameters: Parameter descriptions
            help_text: Detailed help text
        """
        if name in self._commands:
            logger.warning(f"Command '{name}' already registered, overwriting")
        
        metadata = CommandMetadata(
            name=name,
            description=description,
            command_type=command_type,
            permission_level=permission_level,
            feature=feature,
            handler=handler,
            aliases=aliases or [],
            examples=examples or [],
            parameters=parameters or {},
            help_text=help_text
        )
        
        self._commands[name] = metadata
        
        # Register aliases
        for alias in metadata.aliases:
            if alias in self._command_aliases:
                logger.warning(f"Alias '{alias}' already registered for '{self._command_aliases[alias]}', overwriting with '{name}'")
            self._command_aliases[alias] = name
        
        # Group by feature
        if feature not in self._feature_commands:
            self._feature_commands[feature] = []
        self._feature_commands[feature].append(name)
        
        logger.info(f"Registered command: {name} ({feature})")
    
    def get_command(self, name: str) -> Optional[CommandMetadata]:
        """Get command metadata by name or alias."""
        # Check direct name
        if name in self._commands:
            return self._commands[name]
        
        # Check aliases
        if name in self._command_aliases:
            alias_target = self._command_aliases[name]
            return self._commands.get(alias_target)
        
        return None
    
    def get_commands_by_feature(self, feature: str) -> List[CommandMetadata]:
        """Get all commands for a specific feature."""
        command_names = self._feature_commands.get(feature, [])
        return [self._commands[name] for name in command_names if name in self._commands]
    
    def get_commands_by_permission(self, permission_level: PermissionLevel) -> List[CommandMetadata]:
        """Get all commands for a specific permission level."""
        return [
            cmd for cmd in self._commands.values()
            if cmd.permission_level == permission_level
        ]
    
    def get_commands_by_type(self, command_type: CommandType) -> List[CommandMetadata]:
        """Get all commands of a specific type."""
        return [
            cmd for cmd in self._commands.values()
            if cmd.command_type == command_type
        ]
    
    def list_all_commands(self) -> List[CommandMetadata]:
        """Get all registered commands."""
        return list(self._commands.values())
    
    def search_commands(self, query: str) -> List[CommandMetadata]:
        """Search commands by name, description, or feature."""
        query_lower = query.lower()
        results = []
        
        for cmd in self._commands.values():
            if (query_lower in cmd.name.lower() or
                query_lower in cmd.description.lower() or
                query_lower in cmd.feature.lower() or
                any(query_lower in alias.lower() for alias in cmd.aliases)):
                results.append(cmd)
        
        return results
    
    def generate_help_text(self, command_name: str) -> Optional[str]:
        """Generate help text for a specific command."""
        cmd = self.get_command(command_name)
        if not cmd:
            return None
        
        help_parts = [f"📖 **{cmd.name}** - {cmd.description}"]
        
        if cmd.help_text:
            help_parts.append(f"\n{cmd.help_text}")
        
        if cmd.parameters:
            help_parts.append("\n**Parameters:**")
            for param, desc in cmd.parameters.items():
                help_parts.append(f"• `{param}`: {desc}")
        
        if cmd.examples:
            help_parts.append("\n**Examples:**")
            for example in cmd.examples:
                help_parts.append(f"• `{example}`")
        
        if cmd.aliases:
            help_parts.append(f"\n**Aliases:** {', '.join(cmd.aliases)}")
        
        help_parts.append(f"\n**Permission:** {cmd.permission_level.value}")
        help_parts.append(f"**Feature:** {cmd.feature}")
        
        return "\n".join(help_parts)
    
    def generate_feature_help(self, feature: str) -> Optional[str]:
        """Generate help text for all commands in a feature."""
        commands = self.get_commands_by_feature(feature)
        if not commands:
            return None
        
        help_parts = [f"📚 **{feature.replace('_', ' ').title()} Commands**"]
        
        for cmd in sorted(commands, key=lambda x: x.name):
            help_parts.append(f"\n• `{cmd.name}` - {cmd.description}")
            if cmd.aliases:
                help_parts.append(f"  Aliases: {', '.join(cmd.aliases)}")
        
        return "\n".join(help_parts)
    
    def auto_discover_commands(self, src_path: str = "src") -> None:
        """
        Automatically discover and register commands from feature modules.
        
        This method scans the features directory and looks for command handlers
        in the application/commands directories.
        """
        if self._discovered:
            logger.info("Commands already discovered, skipping auto-discovery")
            return
        
        src_path = Path(src_path)
        features_path = src_path / "features"
        
        if not features_path.exists():
            logger.warning(f"Features path not found: {features_path}")
            return
        
        for feature_dir in features_path.iterdir():
            if not feature_dir.is_dir() or feature_dir.name.startswith('_'):
                continue
            
            feature_name = feature_dir.name
            commands_path = feature_dir / "application" / "commands"
            
            if not commands_path.exists():
                continue
            
            logger.info(f"Discovering commands for feature: {feature_name}")
            self._discover_commands_from_path(commands_path, feature_name)
        
        self._discovered = True
        logger.info(f"Auto-discovery complete. Registered {len(self._commands)} commands")
    
    def _discover_commands_from_path(self, commands_path: Path, feature_name: str) -> None:
        """Discover commands from a specific path."""
        for py_file in commands_path.glob("*.py"):
            if py_file.name.startswith('_') or py_file.name == "__init__.py":
                continue
            
            try:
                self._discover_commands_from_file(py_file, feature_name)
            except Exception as e:
                logger.error(f"Error discovering commands from {py_file}: {e}")
    
    def _discover_commands_from_file(self, file_path: Path, feature_name: str) -> None:
        """Discover commands from a specific Python file."""
        import importlib.util
        
        # Load the module
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec is None or spec.loader is None:
            return
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for command handlers
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and name.startswith('handle_'):
                # Extract command name from function name
                command_name = name.replace('handle_', '/')
                if not command_name.startswith('/'):
                    command_name = f"/{command_name}"
                
                # Get docstring as description
                description = obj.__doc__ or f"Handle {command_name} command"
                
                # Determine permission level based on function name
                permission_level = self._determine_permission_level(name, feature_name)
                
                # Register the command
                self.register_command(
                    name=command_name,
                    description=description,
                    handler=obj,
                    feature=feature_name,
                    permission_level=permission_level
                )
            
            elif inspect.isclass(obj) and issubclass(obj, CommandHandler):
                # Handle class-based command handlers
                command_name = getattr(obj, 'command_name', f"/{obj.__name__.lower()}")
                description = getattr(obj, 'description', f"Handle {command_name} command")
                permission_level = getattr(obj, 'permission_level', PermissionLevel.PUBLIC)
                
                # Create instance and register
                handler_instance = obj()
                self.register_command(
                    name=command_name,
                    description=description,
                    handler=handler_instance.execute,
                    feature=feature_name,
                    permission_level=permission_level
                )
    
    def _determine_permission_level(self, function_name: str, feature_name: str) -> PermissionLevel:
        """Determine permission level based on function name and feature."""
        function_lower = function_name.lower()
        
        # Admin commands
        if any(keyword in function_lower for keyword in ['admin', 'approve', 'reject', 'delete']):
            return PermissionLevel.ADMIN
        
        # Leadership commands
        if any(keyword in function_lower for keyword in ['leadership', 'team', 'squad', 'announce']):
            return PermissionLevel.LEADERSHIP
        
        # Player commands
        if any(keyword in function_lower for keyword in ['player', 'register', 'status', 'myinfo']):
            return PermissionLevel.PLAYER
        
        # System commands
        if any(keyword in function_lower for keyword in ['system', 'health', 'config']):
            return PermissionLevel.SYSTEM
        
        # Default to public
        return PermissionLevel.PUBLIC
    
    def get_command_statistics(self) -> Dict[str, Any]:
        """Get statistics about registered commands."""
        total_commands = len(self._commands)
        total_aliases = len(self._command_aliases)
        
        commands_by_type = {}
        for cmd_type in CommandType:
            commands_by_type[cmd_type.value] = len(self.get_commands_by_type(cmd_type))
        
        commands_by_permission = {}
        for perm_level in PermissionLevel:
            commands_by_permission[perm_level.value] = len(self.get_commands_by_permission(perm_level))
        
        commands_by_feature = {}
        for feature in self._feature_commands:
            commands_by_feature[feature] = len(self._feature_commands[feature])
        
        return {
            "total_commands": total_commands,
            "total_aliases": total_aliases,
            "commands_by_type": commands_by_type,
            "commands_by_permission": commands_by_permission,
            "commands_by_feature": commands_by_feature,
            "features": list(self._feature_commands.keys())
        }


# Global command registry instance
_command_registry: Optional[CommandRegistry] = None


def get_command_registry() -> CommandRegistry:
    """Get the global command registry instance."""
    global _command_registry
    if _command_registry is None:
        _command_registry = CommandRegistry()
    return _command_registry


def register_command(
    name: str,
    description: str,
    handler: Callable,
    **kwargs
) -> None:
    """Convenience function to register a command."""
    registry = get_command_registry()
    registry.register_command(name, description, handler, **kwargs)


def command(
    name: str,
    description: str,
    command_type: CommandType = CommandType.SLASH_COMMAND,
    permission_level: PermissionLevel = PermissionLevel.PUBLIC,
    feature: str = "unknown",
    **kwargs
):
    """
    Decorator to register a command handler.
    
    Usage:
        @command("/add", "Add a new player", feature="player_registration")
        async def handle_add_player(update, context, **kwargs):
            # Command implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        register_command(
            name=name,
            description=description,
            handler=func,
            command_type=command_type,
            permission_level=permission_level,
            feature=feature,
            **kwargs
        )
        return func
    return decorator 