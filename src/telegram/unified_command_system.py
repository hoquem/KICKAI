#!/usr/bin/env python3
"""
Unified Command System for KICKAI Bot

This module implements a clean, maintainable command architecture using:
- Command Pattern: Each command is a separate object
- Strategy Pattern: Different permission strategies
- Chain of Responsibility: Command routing and validation
- Factory Pattern: Command creation
- Observer Pattern: Command logging and monitoring

This replaces the multiple overlapping routing systems with a single, clean architecture.
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class PermissionLevel(Enum):
    """Permission levels for commands."""
    PUBLIC = "public"
    PLAYER = "player"
    LEADERSHIP = "leadership"
    ADMIN = "admin"


class ChatType(Enum):
    """Chat types for context."""
    MAIN = "main"
    LEADERSHIP = "leadership"
    PRIVATE = "private"


@dataclass
class CommandContext:
    """Context for command execution."""
    user_id: str
    chat_id: str
    chat_type: ChatType
    user_role: str
    team_id: str
    message_text: str
    username: Optional[str] = None
    raw_update: Optional[Any] = None


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# PERMISSION STRATEGIES (Strategy Pattern)
# ============================================================================

class PermissionStrategy(ABC):
    """Abstract base class for permission strategies."""
    
    @abstractmethod
    def can_execute(self, context: CommandContext) -> bool:
        """Check if command can be executed in given context."""
        pass
    
    @abstractmethod
    def get_access_denied_message(self, context: CommandContext) -> str:
        """Get access denied message."""
        pass


class PublicPermissionStrategy(PermissionStrategy):
    """Strategy for public commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        return True
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return "❌ This command should be available to everyone. Please contact admin."


class PlayerPermissionStrategy(PermissionStrategy):
    """Strategy for player commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        return context.user_role in ['player', 'admin', 'captain', 'secretary', 'manager', 'treasurer']
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 This command requires player access.
💡 Contact your team admin for access.

Your Role: {context.user_role.title()}"""


class LeadershipPermissionStrategy(PermissionStrategy):
    """Strategy for leadership commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        # CHAT-BASED: Only allow in leadership chat (no role check)
        return context.chat_type == ChatType.LEADERSHIP
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 Leadership commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""


class AdminPermissionStrategy(PermissionStrategy):
    """Strategy for admin commands."""
    
    def can_execute(self, context: CommandContext) -> bool:
        # CHAT-BASED: Only allow in leadership chat (no role check)
        return context.chat_type == ChatType.LEADERSHIP
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        return f"""❌ **Access Denied**

🔒 Admin commands are only available in the leadership chat.
💡 Please use the leadership chat for this function."""


# ============================================================================
# COMMAND INTERFACE (Command Pattern)
# ============================================================================

class Command(ABC):
    """Abstract base class for all commands."""
    
    def __init__(self, name: str, description: str, permission_level: PermissionLevel):
        self.name = name
        self.description = description
        self.permission_level = permission_level
        self._permission_strategy = self._get_permission_strategy()
    
    def _get_permission_strategy(self) -> PermissionStrategy:
        """Get the appropriate permission strategy."""
        strategies = {
            PermissionLevel.PUBLIC: PublicPermissionStrategy(),
            PermissionLevel.PLAYER: PlayerPermissionStrategy(),
            PermissionLevel.LEADERSHIP: LeadershipPermissionStrategy(),
            PermissionLevel.ADMIN: AdminPermissionStrategy(),
        }
        return strategies[self.permission_level]
    
    def can_execute(self, context: CommandContext) -> bool:
        """Check if command can be executed."""
        return self._permission_strategy.can_execute(context)
    
    def get_access_denied_message(self, context: CommandContext) -> str:
        """Get access denied message."""
        return self._permission_strategy.get_access_denied_message(context)
    
    @abstractmethod
    async def execute(self, context: CommandContext) -> CommandResult:
        """Execute the command."""
        pass
    
    def get_help_text(self) -> str:
        """Get help text for this command."""
        return f"`{self.name}` - {self.description}"


# ============================================================================
# CONCRETE COMMANDS
# ============================================================================

class StartCommand(Command):
    """Start command implementation."""
    
    def __init__(self):
        super().__init__("/start", "Start the bot", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            message = f"""🤖 **Welcome to KICKAI Bot!**

👋 Hello! I'm your AI-powered football team management assistant.

💡 **What I can help you with:**
• Player registration and management
• Match scheduling and coordination
• Team statistics and analytics
• Communication and notifications

📋 **Quick Start:**
• Type `/help` to see all available commands
• Use natural language: "Create a match against Arsenal on July 1st"
• Ask questions: "What's our next match?"

🔗 **Team:** {context.team_id}

Ready to get started! 🏆"""
            
            return CommandResult(success=True, message=message)
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            return CommandResult(success=False, message="❌ Error starting bot", error=str(e))


class HelpCommand(Command):
    """Help command implementation."""
    
    def __init__(self, command_registry: 'CommandRegistry'):
        super().__init__("/help", "Show available commands", PermissionLevel.PUBLIC)
        self.command_registry = command_registry
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # CHAT-BASED PERMISSIONS: Show commands based on chat type only
            all_commands = self.command_registry.get_all_commands()
            
            if context.chat_type == ChatType.LEADERSHIP:
                # Leadership chat: Show ALL commands (public, player, leadership, admin)
                public_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PUBLIC]
                player_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PLAYER]
                leadership_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.LEADERSHIP]
                admin_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.ADMIN]
            else:
                # Main chat: Show only public and player commands
                public_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PUBLIC]
                player_commands = [cmd for cmd in all_commands if cmd.permission_level == PermissionLevel.PLAYER]
                leadership_commands = []
                admin_commands = []
            
            # Build help message
            if context.chat_type == ChatType.LEADERSHIP:
                title = "🤖 **KICKAI Bot Help (Leadership)**"
            else:
                title = "🤖 **KICKAI Bot Help**"
            
            message = f"{title}\n\n📋 **Available Commands:**\n\n"
            
            if public_commands:
                message += "🌐 **General Commands:**\n"
                for cmd in public_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            if player_commands:
                message += "👥 **Player Commands:**\n"
                for cmd in player_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            if leadership_commands:
                message += "👑 **Leadership Commands:**\n"
                for cmd in leadership_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            if admin_commands:
                message += "🔧 **Admin Commands:**\n"
                for cmd in admin_commands:
                    message += f"• {cmd.get_help_text()}\n"
                message += "\n"
            
            message += "💡 **Tips:**\n"
            message += "• You can use natural language or specific commands\n"
            if context.chat_type != ChatType.LEADERSHIP:
                message += "• Admin commands are only available in the leadership chat\n"
            
            return CommandResult(success=True, message=message)
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            return CommandResult(success=False, message="❌ Error displaying help", error=str(e))


class ListPlayersCommand(Command):
    """List players command implementation."""
    
    def __init__(self):
        super().__init__("/list", "List all players", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            # Import here to avoid circular imports
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_list_players()
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in list players command: {e}")
            return CommandResult(success=False, message="❌ Error listing players", error=str(e))


class MyInfoCommand(Command):
    """My info command implementation."""
    
    def __init__(self):
        super().__init__("/myinfo", "Get your player information", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_myinfo(context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in myinfo command: {e}")
            return CommandResult(success=False, message="❌ Error getting player info", error=str(e))


class RegisterCommand(Command):
    """Register command implementation."""
    
    def __init__(self):
        super().__init__("/register", "Register as a new player", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.services.team_member_service import TeamMemberService
            from src.database.firebase_client import get_firebase_client
            
            firebase_client = get_firebase_client()
            team_service = TeamMemberService(firebase_client)
            
            # Check if user is already registered
            existing_member = await team_service.get_team_member_by_telegram_id(context.user_id, context.team_id)
            if existing_member:
                return CommandResult(
                    success=False,
                    message="❌ You are already registered as a team member."
                )
            
            # Return information about how to register
            return CommandResult(
                success=True,
                message="""📝 **Player Registration**

To register as a new player, you need an invitation from a team admin.

**How to register:**
1. Ask a team admin to add you to the team
2. The admin will generate an invitation link for you
3. Click the invitation link to join the team
4. Complete your profile information

**Alternative:**
If you have a player ID, use:
`/start [player_id]`

**Need help?**
Contact a team admin in the leadership chat for assistance."""
            )
        except Exception as e:
            logger.error(f"Error in register command: {e}")
            return CommandResult(
                success=False,
                message="❌ Error processing registration request."
            )


class AddPlayerCommand(Command):
    """Add player command implementation."""
    
    def __init__(self):
        super().__init__("/add", "Add a new player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_add_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in add player command: {e}")
            return CommandResult(success=False, message="❌ Error adding player", error=str(e))


class RemovePlayerCommand(Command):
    """Remove player command implementation."""
    
    def __init__(self):
        super().__init__("/remove", "Remove a player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_remove_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in remove player command: {e}")
            return CommandResult(success=False, message="❌ Error removing player", error=str(e))


class ApprovePlayerCommand(Command):
    """Approve player command implementation."""
    
    def __init__(self):
        super().__init__("/approve", "Approve a player registration", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_approve_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in approve player command: {e}")
            return CommandResult(success=False, message="❌ Error approving player", error=str(e))


class RejectPlayerCommand(Command):
    """Reject player command implementation."""
    
    def __init__(self):
        super().__init__("/reject", "Reject a player registration", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_reject_player(context.message_text, context.user_id)
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in reject player command: {e}")
            return CommandResult(success=False, message="❌ Error rejecting player", error=str(e))


class PendingApprovalsCommand(Command):
    """Pending approvals command implementation."""
    
    def __init__(self):
        super().__init__("/pending", "List players pending approval", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_pending_approvals()
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in pending approvals command: {e}")
            return CommandResult(success=False, message="❌ Error listing pending approvals", error=str(e))


class CheckFACommand(Command):
    """Check FA registration command implementation."""
    
    def __init__(self):
        super().__init__("/checkfa", "Check FA registration status", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_check_fa_registration()
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in check FA command: {e}")
            return CommandResult(success=False, message="❌ Error checking FA registration", error=str(e))


class DailyStatusCommand(Command):
    """Daily status command implementation."""
    
    def __init__(self):
        super().__init__("/dailystatus", "Generate daily team status report", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> CommandResult:
        try:
            from src.telegram.telegram_command_handler import get_player_command_handler
            handler = get_player_command_handler()
            
            result = await handler._handle_daily_status()
            return CommandResult(success=True, message=result)
        except Exception as e:
            logger.error(f"Error in daily status command: {e}")
            return CommandResult(success=False, message="❌ Error generating daily status", error=str(e))


# ============================================================================
# COMMAND REGISTRY (Factory Pattern)
# ============================================================================

class CommandRegistry:
    """Registry for all available commands."""
    
    def __init__(self):
        self._commands: Dict[str, Command] = {}
        self._help_command: Optional[HelpCommand] = None
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register all default commands."""
        # Create help command first (it needs reference to registry)
        self._help_command = HelpCommand(self)
        
        # Register all commands
        commands = [
            StartCommand(),
            self._help_command,
            ListPlayersCommand(),
            MyInfoCommand(),
            RegisterCommand(),
            AddPlayerCommand(),
            RemovePlayerCommand(),
            ApprovePlayerCommand(),
            RejectPlayerCommand(),
            PendingApprovalsCommand(),
            CheckFACommand(),
            DailyStatusCommand(),
        ]
        
        for command in commands:
            self.register_command(command)
    
    def register_command(self, command: Command):
        """Register a command."""
        self._commands[command.name] = command
        logger.info(f"Registered command: {command.name}")
    
    def get_command(self, name: str) -> Optional[Command]:
        """Get a command by name."""
        return self._commands.get(name)
    
    def get_all_commands(self) -> List[Command]:
        """Get all registered commands."""
        return list(self._commands.values())
    
    def get_available_commands(self, context: CommandContext) -> List[Command]:
        """Get all commands available for the given context."""
        return [cmd for cmd in self._commands.values() if cmd.can_execute(context)]


# ============================================================================
# COMMAND PROCESSOR (Chain of Responsibility Pattern)
# ============================================================================

class CommandProcessor:
    """Main command processor using Chain of Responsibility pattern."""
    
    def __init__(self, command_registry: CommandRegistry):
        self.command_registry = command_registry
        self._setup_chain()
    
    def _setup_chain(self):
        """Set up the processing chain."""
        # Import here to avoid circular imports
        from src.services.access_control_service import AccessControlService
        self.access_control = AccessControlService()
    
    def _get_chat_type(self, chat_id: str, team_id: str) -> ChatType:
        """Determine chat type based on chat ID."""
        try:
            if self.access_control.is_leadership_chat(chat_id, team_id):
                return ChatType.LEADERSHIP
            elif self.access_control.is_main_chat(chat_id, team_id):
                return ChatType.MAIN
            else:
                # Try to detect by chat name as fallback
                if self.access_control._is_leadership_chat_by_name(chat_id):
                    return ChatType.LEADERSHIP
                else:
                    return ChatType.MAIN  # Default to main chat
        except Exception as e:
            logger.error(f"Error determining chat type: {e}")
            return ChatType.MAIN  # Default to main chat
    
    async def _get_user_role(self, user_id: str, team_id: str) -> str:
        """Get user role for permission checking."""
        try:
            from src.services.team_member_service import TeamMemberService
            from src.database.firebase_client import get_firebase_client
            firebase_client = get_firebase_client()
            team_service = TeamMemberService(firebase_client)
            member = await team_service.get_team_member_by_telegram_id(user_id, team_id)
            if member and member.roles:
                return member.roles[0]  # Return first role
            return 'player'
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return 'player'  # Default to player
    
    async def process_command(self, command_name: str, user_id: str, chat_id: str, 
                            team_id: str, message_text: str, username: str = None, 
                            raw_update: Any = None) -> CommandResult:
        """Process a command through the chain."""
        try:
            # Step 1: Create context
            context = CommandContext(
                user_id=user_id,
                chat_id=chat_id,
                chat_type=self._get_chat_type(chat_id, team_id),
                user_role=await self._get_user_role(user_id, team_id),
                team_id=team_id,
                message_text=message_text,
                username=username,
                raw_update=raw_update
            )
            
            # Step 2: Get command
            command = self.command_registry.get_command(command_name)
            if not command:
                return CommandResult(
                    success=False,
                    message=f"❌ Unknown command: `{command_name}`\n\nType `/help` for available commands."
                )
            
            # Step 3: Check permissions
            if not command.can_execute(context):
                return CommandResult(
                    success=False,
                    message=command.get_access_denied_message(context)
                )
            
            # Step 4: Execute command
            result = await command.execute(context)
            
            # Step 5: Log command execution
            self._log_command_execution(context, command, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing command {command_name}: {e}")
            return CommandResult(
                success=False,
                message=f"❌ Error executing command: {str(e)}",
                error=str(e)
            )
    
    def _log_command_execution(self, context: CommandContext, command: Command, result: CommandResult):
        """Log command execution for monitoring."""
        logger.info(
            f"Command executed: {command.name} by {context.user_id} in {context.chat_id} "
            f"(role: {context.user_role}, chat: {context.chat_type.value}) - "
            f"Success: {result.success}"
        )


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Global command registry
_command_registry: Optional[CommandRegistry] = None
_command_processor: Optional[CommandProcessor] = None


def get_command_registry() -> CommandRegistry:
    """Get the global command registry."""
    global _command_registry
    if _command_registry is None:
        _command_registry = CommandRegistry()
    return _command_registry


def get_command_processor() -> CommandProcessor:
    """Get the global command processor."""
    global _command_processor
    if _command_processor is None:
        registry = get_command_registry()
        _command_processor = CommandProcessor(registry)
    return _command_processor


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def process_command(command_name: str, user_id: str, chat_id: str, 
                         team_id: str, message_text: str, username: str = None, 
                         raw_update: Any = None) -> CommandResult:
    """Convenience function to process a command."""
    processor = get_command_processor()
    return await processor.process_command(
        command_name, user_id, chat_id, team_id, message_text, username, raw_update
    )


def is_slash_command(message: str) -> bool:
    """Check if message is a slash command."""
    return message.startswith('/')


def extract_command_name(message: str) -> Optional[str]:
    """Extract command name from message."""
    if not is_slash_command(message):
        return None
    
    # Split by space and take first part
    parts = message.split()
    if not parts:
        return None
    
    return parts[0].lower() 