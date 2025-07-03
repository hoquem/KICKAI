#!/usr/bin/env python3
"""
Player Commands Implementation

This module implements player-related commands using the Command Pattern.
"""

from src.core.command_pattern import Command, CommandContext, PermissionLevel, ChatType, register_command
# Import will be handled dynamically to avoid circular imports
import logging

logger = logging.getLogger(__name__)


@register_command
class HelpCommand(Command):
    """Help command - shows available commands based on context."""
    
    def __init__(self):
        super().__init__("/help", "Show available commands", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute help command."""
        from src.core.command_pattern import get_command_registry
        registry = get_command_registry()
        return registry.get_help_message(context)


@register_command
class ListPlayersCommand(Command):
    """List all players command."""
    
    def __init__(self):
        super().__init__("/list", "List all players", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute list players command."""
        try:
            from src.telegram.player_registration_handler import get_player_command_handler
            handler = get_player_command_handler()
            return await handler._handle_list_players()
        except Exception as e:
            logger.error(f"Error in list players command: {e}")
            return f"❌ Error listing players: {str(e)}"


@register_command
class MyInfoCommand(Command):
    """Get player info command."""
    
    def __init__(self):
        super().__init__("/myinfo", "Get your player information", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute my info command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_myinfo(context.user_id)
        except Exception as e:
            logger.error(f"Error in my info command: {e}")
            return f"❌ Error getting player info: {str(e)}"


@register_command
class PlayerStatusCommand(Command):
    """Get player status command."""
    
    def __init__(self):
        super().__init__("/status", "Get player status by phone", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute player status command."""
        try:
            # Extract phone from message
            parts = context.message_text.split()
            if len(parts) < 2:
                return "❌ Usage: `/status <phone>`"
            
            phone = parts[1]
            handler = get_player_command_handler()
            return await handler._handle_player_status(f"/status {phone}")
        except Exception as e:
            logger.error(f"Error in player status command: {e}")
            return f"❌ Error getting player status: {str(e)}"


@register_command
class PlayerStatsCommand(Command):
    """Get team statistics command."""
    
    def __init__(self):
        super().__init__("/stats", "Get team statistics", PermissionLevel.PLAYER)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute player stats command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_player_stats()
        except Exception as e:
            logger.error(f"Error in player stats command: {e}")
            return f"❌ Error getting player stats: {str(e)}"


@register_command
class AddPlayerCommand(Command):
    """Add player command - leadership only."""
    
    def __init__(self):
        super().__init__("/add", "Add a new player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute add player command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_add_player(context.message_text, context.user_id)
        except Exception as e:
            logger.error(f"Error in add player command: {e}")
            return f"❌ Error adding player: {str(e)}"


@register_command
class RemovePlayerCommand(Command):
    """Remove player command - leadership only."""
    
    def __init__(self):
        super().__init__("/remove", "Remove a player", PermissionLevel.LEADERSHIP)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute remove player command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_remove_player(context.message_text, context.user_id)
        except Exception as e:
            logger.error(f"Error in remove player command: {e}")
            return f"❌ Error removing player: {str(e)}"


@register_command
class ApprovePlayerCommand(Command):
    """Approve player command - admin only."""
    
    def __init__(self):
        super().__init__("/approve", "Approve a player registration", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute approve player command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_approve_player(context.message_text, context.user_id)
        except Exception as e:
            logger.error(f"Error in approve player command: {e}")
            return f"❌ Error approving player: {str(e)}"


@register_command
class RejectPlayerCommand(Command):
    """Reject player command - admin only."""
    
    def __init__(self):
        super().__init__("/reject", "Reject a player registration", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute reject player command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_reject_player(context.message_text, context.user_id)
        except Exception as e:
            logger.error(f"Error in reject player command: {e}")
            return f"❌ Error rejecting player: {str(e)}"


@register_command
class PendingApprovalsCommand(Command):
    """List pending approvals command - admin only."""
    
    def __init__(self):
        super().__init__("/pending", "List players pending approval", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute pending approvals command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_pending_approvals()
        except Exception as e:
            logger.error(f"Error in pending approvals command: {e}")
            return f"❌ Error getting pending approvals: {str(e)}"


@register_command
class CheckFACommand(Command):
    """Check FA registration command - admin only."""
    
    def __init__(self):
        super().__init__("/checkfa", "Check FA registration status", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute check FA command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_check_fa_registration()
        except Exception as e:
            logger.error(f"Error in check FA command: {e}")
            return f"❌ Error checking FA registration: {str(e)}"


@register_command
class DailyStatusCommand(Command):
    """Generate daily status command - admin only."""
    
    def __init__(self):
        super().__init__("/dailystatus", "Generate daily team status report", PermissionLevel.ADMIN)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute daily status command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_daily_status()
        except Exception as e:
            logger.error(f"Error in daily status command: {e}")
            return f"❌ Error generating daily status: {str(e)}"


@register_command
class StartCommand(Command):
    """Start command - public."""
    
    def __init__(self):
        super().__init__("/start", "Start the bot", PermissionLevel.PUBLIC)
    
    async def execute(self, context: CommandContext) -> str:
        """Execute start command."""
        try:
            handler = get_player_command_handler()
            return await handler._handle_start_command(context.message_text, context.user_id)
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            return f"❌ Error processing start command: {str(e)}" 