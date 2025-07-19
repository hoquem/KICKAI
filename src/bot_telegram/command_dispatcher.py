"""
Command Dispatcher

This module provides a command dispatcher that uses the unified command registry
to route commands to their appropriate handlers.
"""

import logging
import re
from typing import Optional, Tuple
from telegram import Update
from telegram.ext import ContextTypes

from core.command_registry import get_command_registry, CommandType, PermissionLevel
from core.context_manager import get_context_manager, UserContext
from features.system_infrastructure.domain.services.permission_service import PermissionService

logger = logging.getLogger(__name__)


class CommandDispatcher:
    """
    Command dispatcher that routes commands to their handlers using the unified registry.
    """
    
    def __init__(self):
        self.registry = get_command_registry()
        self.context_manager = get_context_manager()
        
        # Get PermissionService from dependency container instead of creating it directly
        try:
            from core.dependency_container import get_service
            from features.system_infrastructure.domain.services.permission_service import PermissionService
            
            self.permission_service = get_service(PermissionService)
        except Exception as e:
            logger.warning(f"⚠️ Could not get PermissionService from dependency container: {e}")
            # Fallback to mock service
            self.permission_service = self._create_mock_permission_service()
    
    def _create_mock_permission_service(self):
        """Create a mock permission service for fallback."""
        class MockPermissionService:
            async def check_user_permission(self, user_id: str, team_id: str, required_permission: str, chat_type: str):
                return True  # Allow all permissions in mock mode
        
        return MockPermissionService()
    
    async def dispatch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        """
        Dispatch a command to its appropriate handler.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            Response message or None if no command was found
        """
        if not update.message or not update.message.text:
            return None
        
        message_text = update.message.text.strip()
        user_id = str(update.effective_user.id)
        
        # Parse command
        command_name, args = self._parse_command(message_text)
        if not command_name:
            return None
        
        # Get user context
        user_context = await self.context_manager.get_user_context(user_id)
        if not user_context:
            logger.warning(f"No user context found for user {user_id}")
            return "❌ Unable to determine your team context. Please try again."
        
        # Get command from registry
        command_metadata = self.registry.get_command(command_name)
        if not command_metadata:
            # Try natural language processing
            return await self._handle_natural_language(update, context, message_text, user_context)
        
        # Check permissions
        if not await self._check_permissions(command_metadata, user_context):
            return f"❌ You don't have permission to use the {command_name} command."
        
        # Execute command
        try:
            result = await self._execute_command(command_metadata, update, context, user_context, args)
            return result
        except Exception as e:
            logger.error(f"Error executing command {command_name}: {e}", exc_info=True)
            return f"❌ An error occurred while executing {command_name}. Please try again."
    
    def _parse_command(self, message_text: str) -> Tuple[Optional[str], list[str]]:
        """
        Parse a message to extract command name and arguments.
        
        Args:
            message_text: The message text to parse
            
        Returns:
            Tuple of (command_name, args) or (None, []) if no command found
        """
        # Check for slash commands
        if message_text.startswith('/'):
            parts = message_text.split()
            command_name = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            return command_name, args
        
        # Check for natural language patterns
        natural_language_patterns = [
            r'^(help|status|info|list|add|register|approve|reject)',
            r'^(my|team|player|match|payment|expense)',
            r'^(what|how|when|where|who)',
        ]
        
        for pattern in natural_language_patterns:
            if re.match(pattern, message_text.lower()):
                return None, [message_text]
        
        return None, []
    
    async def _handle_natural_language(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        message_text: str, 
        user_context: UserContext
    ) -> Optional[str]:
        """
        Handle natural language queries using the agent system.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            message_text: The natural language message
            user_context: User context
            
        Returns:
            Response message or None
        """
        try:
            # Import here to avoid circular imports
            from agents.simplified_orchestration import SimplifiedOrchestrationPipeline
            
            # Create orchestration pipeline
            pipeline = SimplifiedOrchestrationPipeline()
            
            # Process the natural language query
            result = await pipeline.process_message(
                message_text=message_text,
                user_id=user_context.user_id,
                team_id=user_context.team_id,
                chat_type=user_context.chat_type
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling natural language query: {e}", exc_info=True)
            return "❌ I couldn't understand your request. Please try using a specific command or rephrase your question."
    
    async def _check_permissions(self, command_metadata, user_context: UserContext) -> bool:
        """
        Check if user has permission to execute the command.
        
        Args:
            command_metadata: Command metadata from registry
            user_context: User context
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Map registry permission levels to service permission levels
            permission_mapping = {
                PermissionLevel.PUBLIC: "public",
                PermissionLevel.PLAYER: "player",
                PermissionLevel.LEADERSHIP: "leadership",
                PermissionLevel.ADMIN: "admin",
                PermissionLevel.SYSTEM: "system"
            }
            
            required_permission = permission_mapping.get(command_metadata.permission_level, "public")
            
            # Check user permissions
            has_permission = await self.permission_service.check_user_permission(
                user_id=user_context.user_id,
                team_id=user_context.team_id,
                required_permission=required_permission,
                chat_type=user_context.chat_type
            )
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Error checking permissions: {e}", exc_info=True)
            return False
    
    async def _execute_command(
        self, 
        command_metadata, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        user_context: UserContext, 
        args: list[str]
    ) -> str:
        """
        Execute a command using its handler.
        
        Args:
            command_metadata: Command metadata from registry
            update: Telegram update object
            context: Telegram context object
            user_context: User context
            args: Command arguments
            
        Returns:
            Response message
        """
        try:
            # Create command context
            from features.shared.application.commands.types import CommandContext
            from enums import PermissionLevel
            
            cmd_context = CommandContext(
                update=update,
                context=context,
                team_id=user_context.team_id,
                user_id=user_context.user_id,
                message_text=update.message.text,
                permission_level=PermissionLevel(user_context.permission_level),
                additional_data={"args": args}
            )
            
            # Execute the command
            if hasattr(command_metadata.handler, 'execute'):
                # Class-based command handler
                result = await command_metadata.handler.execute(cmd_context)
                return result.message
            else:
                # Function-based command handler
                result = await command_metadata.handler(update, context, *args)
                return str(result) if result else "✅ Command executed successfully."
                
        except Exception as e:
            logger.error(f"Error executing command {command_metadata.name}: {e}", exc_info=True)
            raise
    
    async def get_help_text(self, command_name: str, user_context: UserContext) -> Optional[str]:
        """
        Get help text for a specific command.
        
        Args:
            command_name: Name of the command
            user_context: User context
            
        Returns:
            Help text or None if command not found
        """
        command_metadata = self.registry.get_command(command_name)
        if not command_metadata:
            return None
        
        # Check permissions
        if not await self._check_permissions(command_metadata, user_context):
            return f"❌ You don't have permission to use the {command_name} command."
        
        return self.registry.generate_help_text(command_name)
    
    async def get_feature_help(self, feature: str, user_context: UserContext) -> Optional[str]:
        """
        Get help text for all commands in a feature.
        
        Args:
            feature: Feature name
            user_context: User context
            
        Returns:
            Help text or None if feature not found
        """
        commands = self.registry.get_commands_by_feature(feature)
        if not commands:
            return None
        
        # Filter commands by user permissions
        accessible_commands = []
        for cmd in commands:
            if await self._check_permissions(cmd, user_context):
                accessible_commands.append(cmd)
        
        if not accessible_commands:
            return f"❌ You don't have permission to use any {feature} commands."
        
        # Generate help text for accessible commands
        help_parts = [f"📚 **{feature.replace('_', ' ').title()} Commands**"]
        
        for cmd in sorted(accessible_commands, key=lambda x: x.name):
            help_parts.append(f"\n• `{cmd.name}` - {cmd.description}")
            if cmd.aliases:
                help_parts.append(f"  Aliases: {', '.join(cmd.aliases)}")
        
        return "\n".join(help_parts)
    
    def get_available_commands(self, user_context: UserContext) -> list[str]:
        """
        Get list of available commands for a user.
        
        Args:
            user_context: User context
            
        Returns:
            List of command names
        """
        # This would need to be implemented with proper permission checking
        # For now, return all commands
        return [cmd.name for cmd in self.registry.list_all_commands()]


# Global command dispatcher instance
_command_dispatcher: Optional[CommandDispatcher] = None


def get_command_dispatcher() -> CommandDispatcher:
    """Get the global command dispatcher instance."""
    global _command_dispatcher
    if _command_dispatcher is None:
        _command_dispatcher = CommandDispatcher()
    return _command_dispatcher 