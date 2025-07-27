#!/usr/bin/env python3
"""
Command Registry Initializer

This module provides centralized initialization of the command registry,
ensuring all commands are properly registered before the registry is used.
This eliminates the initialization order problem with the global singleton pattern.
"""


from kickai.core.command_registry import CommandRegistry
from kickai.core.logging_config import logger


class CommandRegistryInitializer:
    """
    Centralized command registry initializer.

    This class ensures that all commands are properly registered before
    the registry is used by any other components.
    """

    def __init__(self):
        self.registry: CommandRegistry | None = None
        self._initialized = False

    def initialize(self) -> CommandRegistry:
        """
        Initialize the command registry with all commands.

        This method:
        1. Creates a new CommandRegistry instance
        2. Manually imports all command modules to ensure @command decorators are executed
        3. Performs auto-discovery as a backup
        4. Returns the fully populated registry

        Returns:
            CommandRegistry: Fully initialized command registry
        """
        if self._initialized and self.registry:
            return self.registry

        logger.info("🔧 Initializing command registry...")

        # Create new registry instance
        self.registry = CommandRegistry()

        # Manually import all command modules to ensure @command decorators are executed
        self._import_command_modules()

        # Copy commands from global registry to initialized registry
        self._copy_commands_from_global_registry()

        # Perform auto-discovery as backup (disabled for now to avoid conflicts)
        # logger.info("🔍 Performing command auto-discovery...")
        # self.registry.auto_discover_commands()

        # Log statistics
        stats = self.registry.get_command_statistics()
        logger.info(f"✅ Command registry initialized with {stats['total_commands']} commands")
        logger.info(f"📊 Commands by feature: {stats['commands_by_feature']}")

        self._initialized = True
        return self.registry

    def _import_command_modules(self):
        """Manually import all command modules to ensure @command decorators are executed."""
        command_modules = [
            # Player registration commands
            "kickai.features.player_registration.application.commands.player_commands",
            # Team administration commands
            "kickai.features.team_administration.application.commands.team_commands",
            # Match management commands
            "kickai.features.match_management.application.commands.match_commands",
            # Attendance management commands
            "kickai.features.attendance_management.application.commands.attendance_commands",
            # Payment management commands
            "kickai.features.payment_management.application.commands.payment_commands",
            # Communication commands
            "kickai.features.communication.application.commands.communication_commands",
            # Health monitoring commands
            "kickai.features.health_monitoring.application.commands.health_commands",
            # System infrastructure commands
            "kickai.features.system_infrastructure.application.commands.system_commands",
            # Shared commands
            "kickai.features.shared.application.commands.shared_commands",
            "kickai.features.shared.application.commands.help_commands",
        ]

        for module_name in command_modules:
            try:
                logger.debug(f"🔍 Importing command module: {module_name}")
                __import__(module_name)
                logger.debug(f"✅ Successfully imported: {module_name}")
            except ImportError as e:
                logger.warning(f"⚠️ Failed to import command module {module_name}: {e}")
            except Exception as e:
                logger.error(f"❌ Error importing command module {module_name}: {e}")

    def _copy_commands_from_global_registry(self):
        """Copy commands from the global registry to the initialized registry."""
        try:
            from kickai.core.command_registry import get_command_registry

            global_registry = get_command_registry()

            # Copy all commands from global registry
            for cmd_name, cmd_metadata in global_registry._commands.items():
                if cmd_name not in self.registry._commands:
                    self.registry._commands[cmd_name] = cmd_metadata

                    # Copy to feature commands
                    if cmd_metadata.feature not in self.registry._feature_commands:
                        self.registry._feature_commands[cmd_metadata.feature] = []
                    self.registry._feature_commands[cmd_metadata.feature].append(cmd_name)

                    logger.debug(f"📋 Copied command: {cmd_name} ({cmd_metadata.feature})")

            # Copy aliases
            for alias, target in global_registry._command_aliases.items():
                if alias not in self.registry._command_aliases:
                    self.registry._command_aliases[alias] = target

            # Copy chat-specific commands
            if hasattr(global_registry, "_chat_specific_commands"):
                for cmd_name, chat_commands in global_registry._chat_specific_commands.items():
                    if cmd_name not in self.registry._chat_specific_commands:
                        self.registry._chat_specific_commands[cmd_name] = {}
                    for chat_type, cmd_metadata in chat_commands.items():
                        self.registry._chat_specific_commands[cmd_name][chat_type] = cmd_metadata
                        logger.debug(f"📋 Copied chat-specific command: {cmd_name} for {chat_type}")

            logger.info(f"📋 Copied {len(global_registry._commands)} commands from global registry")

        except Exception as e:
            logger.error(f"❌ Error copying commands from global registry: {e}")

    def get_registry(self) -> CommandRegistry | None:
        """Get the initialized registry instance."""
        if not self._initialized:
            raise RuntimeError("Command registry not initialized. Call initialize() first.")
        return self.registry


# Global initializer instance
_command_registry_initializer = CommandRegistryInitializer()


def initialize_command_registry() -> CommandRegistry:
    """
    Initialize the command registry.

    This is the main entry point for command registry initialization.
    It should be called once during application startup.

    Returns:
        CommandRegistry: Fully initialized command registry
    """
    return _command_registry_initializer.initialize()


def get_initialized_command_registry() -> CommandRegistry:
    """
    Get the initialized command registry.

    This function should be used instead of the old get_command_registry()
    to ensure the registry is properly initialized.

    Returns:
        CommandRegistry: Fully initialized command registry

    Raises:
        RuntimeError: If the registry hasn't been initialized
    """
    return _command_registry_initializer.get_registry()
