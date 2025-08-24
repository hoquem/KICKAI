"""
Unified Command Registry

This module provides a centralized command registry for the KICKAI system.
It discovers, registers, and manages all commands across the feature-based modular architecture.
"""

import inspect
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from kickai.core.enums import CommandType, PermissionLevel

logger = logging.getLogger(__name__)


@dataclass
class CommandMetadata:
    """
    Enhanced metadata for a command with NLP classification support.
    
    This metadata structure supports both traditional command routing
    and advanced NLP-based natural language understanding for determining
    command clarity and processing requirements.
    
    Attributes:
        name: Command name (e.g., "/help", "/status")
        description: Brief description of command functionality
        command_type: Type classification for routing decisions
        permission_level: Required permission level for execution
        feature: Feature module that owns this command
        handler: Command handler function
        aliases: Alternative command names
        examples: Usage examples for documentation
        parameters: Parameter descriptions for help text
        help_text: Detailed help documentation
        chat_type: Chat context restrictions
        requires_nlp: Whether command needs NLP processing
        clarity_level: Command clarity classification
        parameter_optional: Whether parameters are optional for clarity
        semantic_tags: Tags for semantic routing and classification
    """

    name: str
    description: str
    command_type: CommandType
    permission_level: PermissionLevel
    feature: str
    handler: Callable
    aliases: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    parameters: dict[str, str] = field(default_factory=dict)
    help_text: Optional[str] = None
    chat_type: Optional[str] = None  # ChatType.MAIN, ChatType.LEADERSHIP, or None for all
    # NLP-related metadata fields
    requires_nlp: bool = False
    clarity_level: str = "clear"  # "clear", "ambiguous", "contextual"
    parameter_optional: bool = True
    semantic_tags: list[str] = field(default_factory=list)


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
        self._commands: dict[str, CommandMetadata] = {}
        self._command_aliases: dict[str, str] = {}
        self._feature_commands: dict[str, list[str]] = {}
        self._discovered = False

        # Support for chat-specific commands with same name
        self._chat_specific_commands: dict[str, dict[str, CommandMetadata]] = {}

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
        help_text: Optional[str] = None,
        chat_type: Optional[str] = None,
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
        # Handle chat-specific commands
        if chat_type:
            # This is a chat-specific command
            if name not in self._chat_specific_commands:
                self._chat_specific_commands[name] = {}

            # Check if this chat type is already registered for this command
            if chat_type in self._chat_specific_commands[name]:
                existing_cmd = self._chat_specific_commands[name][chat_type]
                # Check if this is the same registration
                if (
                    existing_cmd.handler == handler
                    and existing_cmd.feature == feature
                    and existing_cmd.description == description
                ):
                    # Same registration, skip silently
                    return
                else:
                    # Different registration, log warning but allow overwrite
                    logger.warning(
                        f"Command '{name}' for chat type '{chat_type}' already registered by {existing_cmd.feature}, overwriting with {feature}"
                    )

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
                help_text=help_text,
                chat_type=chat_type,
            )

            self._chat_specific_commands[name][chat_type] = metadata

            # Also store in main commands dict for backward compatibility
            # Use the first chat-specific command as the "default"
            if name not in self._commands:
                self._commands[name] = metadata
            else:
                # If we already have a universal command, keep it
                # Only overwrite if the existing command is also chat-specific
                existing_cmd = self._commands[name]
                if existing_cmd.chat_type:
                    # Both are chat-specific, use the new one as default
                    self._commands[name] = metadata
        else:
            # This is a universal command (no chat_type specified)
            if name in self._commands:
                existing_cmd = self._commands[name]
                # Check if this is the same registration (same handler, feature, and description)
                if (
                    existing_cmd.handler == handler
                    and existing_cmd.feature == feature
                    and existing_cmd.description == description
                ):
                    # Same registration, skip silently
                    return
                elif existing_cmd.feature == feature:
                    # Same feature registering the same command again, skip silently
                    return
                else:
                    # Different registration, log warning but allow overwrite
                    logger.warning(
                        f"Command '{name}' already registered by {existing_cmd.feature}, overwriting with {feature}"
                    )

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
            help_text=help_text,
            chat_type=chat_type,
        )

        self._commands[name] = metadata

        # Register aliases
        for alias in metadata.aliases:
            if alias in self._command_aliases:
                logger.warning(
                    f"Alias '{alias}' already registered for '{self._command_aliases[alias]}', overwriting with '{name}'"
                )
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

    def get_commands_by_feature(self, feature: str) -> list[CommandMetadata]:
        """Get all commands for a specific feature."""
        command_names = self._feature_commands.get(feature, [])
        return [self._commands[name] for name in command_names if name in self._commands]

    def get_commands_by_permission(
        self, permission_level: PermissionLevel
    ) -> list[CommandMetadata]:
        """Get all commands for a specific permission level."""
        return [cmd for cmd in self._commands.values() if cmd.permission_level == permission_level]

    def get_commands_by_type(self, command_type: CommandType) -> list[CommandMetadata]:
        """Get all commands of a specific type."""
        return [cmd for cmd in self._commands.values() if cmd.command_type == command_type]

    def get_commands_by_chat_type(self, chat_type: str) -> list[CommandMetadata]:
        """Get all commands available in a specific chat type."""
        commands = []

        # Add universal commands (no chat_type specified)
        for cmd in self._commands.values():
            if cmd.chat_type is None or cmd.chat_type == chat_type:
                commands.append(cmd)

        # Add chat-specific commands for this chat type
        for command_name, chat_commands in self._chat_specific_commands.items():
            if chat_type in chat_commands:
                commands.append(chat_commands[chat_type])

        return commands

    def get_command_for_chat(self, name: str, chat_type: str) -> Optional[CommandMetadata]:
        """Get a specific command for a chat type, considering chat-specific and universal commands."""
        # First check for chat-specific command
        if name in self._chat_specific_commands:
            # Convert string chat_type to enum for comparison
            from kickai.core.enums import ChatType

            chat_type_enum = None
            if chat_type == "main_chat":
                chat_type_enum = ChatType.MAIN
            elif chat_type == "leadership_chat":
                chat_type_enum = ChatType.LEADERSHIP

            if chat_type_enum and chat_type_enum in self._chat_specific_commands[name]:
                return self._chat_specific_commands[name][chat_type_enum]

        # Then check for universal command (no chat_type specified)
        if name in self._commands:
            cmd = self._commands[name]
            # Return if command is universal (no chat_type) or matches the chat type
            if cmd.chat_type is None:
                return cmd
            # Convert string chat_type to enum for comparison
            from kickai.core.enums import ChatType

            chat_type_enum = None
            if chat_type == "main_chat":
                chat_type_enum = ChatType.MAIN
            elif chat_type == "leadership_chat":
                chat_type_enum = ChatType.LEADERSHIP

            if chat_type_enum and cmd.chat_type == chat_type_enum:
                return cmd

        return None

    def list_all_commands(self) -> list[CommandMetadata]:
        """Get all registered commands."""
        return list(self._commands.values())

    def search_commands(self, query: str) -> list[CommandMetadata]:
        """Search commands by name, description, or feature."""
        query_lower = query.lower()
        results = []

        for cmd in self._commands.values():
            if (
                query_lower in cmd.name.lower()
                or query_lower in cmd.description.lower()
                or query_lower in cmd.feature.lower()
                or any(query_lower in alias.lower() for alias in cmd.aliases)
            ):
                results.append(cmd)

        return results

    def generate_help_text(self, command_name: str) -> Optional[str]:
        """Generate help text for a specific command."""
        cmd = self.get_command(command_name)
        if not cmd:
            return None

        help_parts = [f"📖 {cmd.name} - {cmd.description}"]

        if cmd.help_text:
            help_parts.append(f"\n{cmd.help_text}")

        if cmd.parameters:
            help_parts.append("\nParameters:")
            for param, desc in cmd.parameters.items():
                help_parts.append(f"• {param}: {desc}")

        if cmd.examples:
            help_parts.append("\nExamples:")
            for example in cmd.examples:
                help_parts.append(f"• {example}")

        if cmd.aliases:
            help_parts.append(f"\nAliases: {', '.join(cmd.aliases)}")

        help_parts.append(f"\nPermission: {cmd.permission_level.value}")
        help_parts.append(f"Feature: {cmd.feature}")

        return "\n".join(help_parts)

    def generate_feature_help(self, feature: str) -> Optional[str]:
        """Generate help text for all commands in a feature."""
        commands = self.get_commands_by_feature(feature)
        if not commands:
            return None

        help_parts = [f"📚 {feature.replace('_', ' ').title()} Commands"]

        for cmd in sorted(commands, key=lambda x: x.name):
            help_parts.append(f"\n• {cmd.name} - {cmd.description}")
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
            logger.debug("Commands already discovered, skipping auto-discovery")
            return

        logger.info("🔍 Starting command auto-discovery...")

        src_path = Path(src_path)
        features_path = src_path / "features"

        if not features_path.exists():
            logger.warning(f"Features path not found: {features_path}")
            return

        for feature_dir in features_path.iterdir():
            if not feature_dir.is_dir() or feature_dir.name.startswith("_"):
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
            if py_file.name.startswith("_") or py_file.name == "__init__.py":
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
            # Check for functions that start with 'handle_' and are NOT already decorated
            if (
                inspect.isfunction(obj)
                and name.startswith("handle_")
                and not hasattr(obj, "_command_registered")
            ):
                # Extract command name from function name
                command_name = name.replace("handle_", "/")
                if not command_name.startswith("/"):
                    command_name = f"/{command_name}"

                # Skip if command is already registered (might be decorated)
                if command_name in self._commands:
                    logger.debug(f"Skipping {command_name} - already registered")
                    continue

                # Register the command
                self.register_command(
                    name=command_name,
                    description=f"Handler for {command_name}",
                    handler=obj,
                    feature=feature_name,
                )

    def _determine_permission_level(self, function_name: str, feature_name: str) -> PermissionLevel:
        """Determine permission level based on function name and feature."""
        function_lower = function_name.lower()

        # Admin commands
        if any(keyword in function_lower for keyword in ["admin", "approve", "reject", "delete"]):
            return PermissionLevel.ADMIN

        # Leadership commands
        if any(
            keyword in function_lower for keyword in ["leadership", "team", "squad", "announce"]
        ):
            return PermissionLevel.LEADERSHIP

        # Player commands
        if any(keyword in function_lower for keyword in ["player", "register", "status", "myinfo"]):
            return PermissionLevel.PLAYER

        # System commands
        if any(keyword in function_lower for keyword in ["system", "health", "config"]):
            return PermissionLevel.SYSTEM

        # Default to public
        return PermissionLevel.PUBLIC

    def get_command_statistics(self) -> dict[str, Any]:
        """Get statistics about registered commands."""
        total_commands = len(self._commands)
        total_aliases = len(self._command_aliases)

        commands_by_type = {}
        for cmd_type in CommandType:
            commands_by_type[cmd_type.value] = len(self.get_commands_by_type(cmd_type))

        commands_by_permission = {}
        for perm_level in PermissionLevel:
            commands_by_permission[perm_level.value] = len(
                self.get_commands_by_permission(perm_level)
            )

        commands_by_feature = {}
        for feature in self._feature_commands:
            commands_by_feature[feature] = len(self._feature_commands[feature])

        return {
            "total_commands": total_commands,
            "total_aliases": total_aliases,
            "commands_by_type": commands_by_type,
            "commands_by_permission": commands_by_permission,
            "commands_by_feature": commands_by_feature,
            "features": list(self._feature_commands.keys()),
        }

    def classify_command_for_nlp(self, command_name: str, metadata: CommandMetadata) -> dict[str, Any]:
        """
        Classify command for NLP processing requirements.
        
        Analyzes command metadata to determine if NLP processing is needed
        and provides classification details for routing decisions.
        
        Args:
            command_name: The command name to classify
            metadata: Command metadata from registry
            
        Returns:
            Dictionary containing classification results with keys:
            - requires_nlp: bool indicating if NLP processing needed
            - clarity_level: str classification ("clear", "ambiguous", "contextual") 
            - confidence: float confidence score (0.0-1.0)
            - routing_recommendation: dict with recommended agent and priority
            - parameter_analysis: dict analyzing parameter requirements
            
        Raises:
            ValidationError: When command classification fails
            
        Example:
            >>> result = registry.classify_command_for_nlp("/help", help_metadata)
            >>> result["requires_nlp"]
            False
            >>> result["clarity_level"]
            "clear"
        """
        try:
            # Validate inputs
            if not command_name or not isinstance(command_name, str):
                raise ValueError("Command name must be a non-empty string")
            
            if not isinstance(metadata, CommandMetadata):
                raise ValueError("Metadata must be a CommandMetadata instance")
            
            # Calculate clarity confidence based on metadata characteristics
            clarity_confidence = self._calculate_clarity_confidence(metadata)
            
            # Get routing recommendation based on command characteristics
            routing_recommendation = self._get_routing_recommendation(metadata)
            
            # Analyze parameter requirements
            parameter_analysis = self._analyze_parameters(metadata)
            
            # Build comprehensive classification result
            classification = {
                "requires_nlp": metadata.requires_nlp,
                "clarity_level": metadata.clarity_level,
                "confidence": clarity_confidence,
                "routing_recommendation": routing_recommendation,
                "parameter_analysis": parameter_analysis,
                "semantic_tags": metadata.semantic_tags,
                "command_type": metadata.command_type.value if metadata.command_type else "unknown"
            }
            
            logger.debug(f"🔍 Classified command '{command_name}': {classification}")
            return classification
            
        except Exception as e:
            logger.error(f"❌ Error in classify_command_for_nlp: {e}")
            from kickai.core.exceptions import ValidationError
            raise ValidationError(f"Command classification failed: {str(e)}")

    def _calculate_clarity_confidence(self, metadata: CommandMetadata) -> float:
        """
        Calculate confidence score for command clarity classification.
        
        Args:
            metadata: Command metadata to analyze
            
        Returns:
            Float confidence score between 0.0 and 1.0
        """
        try:
            confidence_factors = []
            
            # System commands have high confidence
            if metadata.command_type in ["system", "utility"]:
                confidence_factors.append(0.95)
            
            # Commands without parameters are clearer
            if not metadata.parameters or metadata.parameter_optional:
                confidence_factors.append(0.9)
            
            # Commands with clear descriptions have higher confidence
            if metadata.description and len(metadata.description) > 10:
                confidence_factors.append(0.85)
            
            # Commands with examples are clearer
            if metadata.examples:
                confidence_factors.append(0.8)
            
            # Commands with aliases suggest clarity
            if metadata.aliases:
                confidence_factors.append(0.75)
            
            # Base confidence for any registered command
            confidence_factors.append(0.6)
            
            # Return maximum confidence factor found
            return max(confidence_factors) if confidence_factors else 0.5
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculating clarity confidence: {e}")
            return 0.5  # Default safe confidence

    def _get_routing_recommendation(self, metadata: CommandMetadata) -> dict[str, Any]:
        """
        Get routing recommendation based on command metadata.
        
        Args:
            metadata: Command metadata to analyze
            
        Returns:
            Dictionary with routing recommendations
        """
        try:
            # Map command types to recommended agents
            type_to_agent_mapping = {
                "system": "message_processor",
                "utility": "message_processor", 
                "help": "help_assistant",
                "player": "player_coordinator",
                "team": "team_administrator",
                "squad": "squad_selector",
                "match": "squad_selector"
            }
            
            # Determine recommended agent based on command type or semantic tags
            recommended_agent = type_to_agent_mapping.get(
                metadata.command_type.value if metadata.command_type else "unknown",
                "message_processor"  # Default fallback
            )
            
            # Check semantic tags for more specific routing
            for tag in metadata.semantic_tags:
                if tag in type_to_agent_mapping:
                    recommended_agent = type_to_agent_mapping[tag]
                    break
            
            # Determine priority based on command characteristics
            priority = "high" if metadata.command_type in ["system", "help"] else "medium"
            
            return {
                "agent": recommended_agent,
                "priority": priority,
                "reason": f"Based on command type: {metadata.command_type.value if metadata.command_type else 'unknown'}"
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Error getting routing recommendation: {e}")
            return {
                "agent": "message_processor",
                "priority": "medium",
                "reason": "Default fallback due to analysis error"
            }

    def _analyze_parameters(self, metadata: CommandMetadata) -> dict[str, Any]:
        """
        Analyze parameter requirements for command clarity.
        
        Args:
            metadata: Command metadata to analyze
            
        Returns:
            Dictionary with parameter analysis results
        """
        try:
            parameter_count = len(metadata.parameters) if metadata.parameters else 0
            
            analysis = {
                "has_parameters": parameter_count > 0,
                "parameter_count": parameter_count,
                "parameters_optional": metadata.parameter_optional,
                "complexity_score": self._calculate_parameter_complexity(metadata.parameters),
                "clarity_impact": "high" if parameter_count == 0 else "medium" if metadata.parameter_optional else "low"
            }
            
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Error analyzing parameters: {e}")
            return {
                "has_parameters": False,
                "parameter_count": 0,
                "parameters_optional": True,
                "complexity_score": 0.0,
                "clarity_impact": "high"
            }

    def _calculate_parameter_complexity(self, parameters: Optional[dict[str, str]]) -> float:
        """
        Calculate complexity score based on parameter requirements.
        
        Args:
            parameters: Parameter dictionary from metadata
            
        Returns:
            Float complexity score (0.0 = simple, 1.0 = complex)
        """
        try:
            if not parameters:
                return 0.0
            
            # Base complexity from parameter count
            param_count = len(parameters)
            base_complexity = min(param_count / 5.0, 1.0)  # Scale to max 1.0
            
            # Additional complexity factors
            complexity_keywords = ["optional", "required", "multiple", "complex"]
            keyword_complexity = 0.0
            
            for param_desc in parameters.values():
                if isinstance(param_desc, str):
                    for keyword in complexity_keywords:
                        if keyword.lower() in param_desc.lower():
                            keyword_complexity += 0.1
            
            total_complexity = min(base_complexity + keyword_complexity, 1.0)
            return total_complexity
            
        except Exception as e:
            logger.warning(f"⚠️ Error calculating parameter complexity: {e}")
            return 0.5  # Default medium complexity

    def get_commands_requiring_nlp(self) -> list[CommandMetadata]:
        """
        Get all commands that require NLP processing.
        
        Returns:
            List of CommandMetadata for commands needing NLP
        """
        try:
            return [cmd for cmd in self._commands.values() if cmd.requires_nlp]
        except Exception as e:
            logger.error(f"❌ Error getting NLP commands: {e}")
            return []

    def get_clear_commands(self) -> list[CommandMetadata]:
        """
        Get all commands classified as clear (not requiring NLP).
        
        Returns:
            List of CommandMetadata for clear commands
        """
        try:
            return [
                cmd for cmd in self._commands.values() 
                if not cmd.requires_nlp and cmd.clarity_level == "clear"
            ]
        except Exception as e:
            logger.error(f"❌ Error getting clear commands: {e}")
            return []


# Global command registry instance (DEPRECATED - use CommandRegistryInitializer instead)
_command_registry: Optional[CommandRegistry] = None


def get_command_registry() -> CommandRegistry:
    """
    Get the global command registry instance.

    DEPRECATED: Use get_initialized_command_registry() from command_registry_initializer.py instead.
    This function is kept for backward compatibility but will be removed in a future version.
    """
    global _command_registry
    if _command_registry is None:
        _command_registry = CommandRegistry()
    return _command_registry


def register_command(name: str, description: str, handler: Callable, **kwargs) -> None:
    """
    Convenience function to register a command.

    DEPRECATED: Use the @command decorator instead.
    """
    registry = get_command_registry()
    registry.register_command(name, description, handler, **kwargs)


def command(
    name: str,
    description: str,
    command_type: CommandType = CommandType.SLASH_COMMAND,
    permission_level: PermissionLevel = PermissionLevel.PUBLIC,
    feature: str = "unknown",
    chat_type: Optional[Union[str, 'ChatType']] = None,
    **kwargs,
):
    """
    Decorator to register a command handler.

    This decorator registers commands with the global registry during import.
    The CommandRegistryInitializer will then copy these commands to the initialized registry.

    Usage:
        @command("/add", "Add a new player", feature="player_registration")
        async def handle_add_player(update, context, **kwargs):
            # Command implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Always use the global registry during import
        registry = get_command_registry()
        
        # Convert enum chat_type to string if needed
        chat_type_str = chat_type
        if chat_type is not None and hasattr(chat_type, 'value'):
            chat_type_str = chat_type.value

        registry.register_command(
            name=name,
            description=description,
            handler=func,
            command_type=command_type,
            permission_level=permission_level,
            feature=feature,
            chat_type=chat_type_str,
            **kwargs,
        )
        # Mark function as registered to avoid duplicate discovery
        func._command_registered = True
        return func

    return decorator
