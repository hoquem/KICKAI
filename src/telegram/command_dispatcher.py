#!/usr/bin/env python3
"""
Command Dispatcher for KICKAI Bot

This module provides a clean command dispatching system that integrates
with the existing handlers while providing proper permission checking.
"""

import logging
from typing import Optional, Dict, Any
from src.core.command_pattern import CommandContext, ChatType, PermissionLevel
from src.services.access_control_service import AccessControlService
from src.telegram.telegram_command_handler import get_player_command_handler

logger = logging.getLogger(__name__)


class CommandDispatcher:
    """Main command dispatcher with permission checking."""
    
    def __init__(self):
        self.access_control = AccessControlService()
        self.player_handler = get_player_command_handler()
        
        # Command definitions with permission levels
        self.commands = {
            # Public commands
            "/start": {"permission": PermissionLevel.PUBLIC, "description": "Start the bot"},
            "/help": {"permission": PermissionLevel.PUBLIC, "description": "Show available commands"},
            
            # Player commands
            "/list": {"permission": PermissionLevel.PLAYER, "description": "List all players"},
            "/myinfo": {"permission": PermissionLevel.PLAYER, "description": "Get your player information"},
            "/status": {"permission": PermissionLevel.PLAYER, "description": "Get player status by phone"},
            "/stats": {"permission": PermissionLevel.PLAYER, "description": "Get team statistics"},
            
            # Leadership commands
            "/add": {"permission": PermissionLevel.LEADERSHIP, "description": "Add a new player"},
            "/remove": {"permission": PermissionLevel.LEADERSHIP, "description": "Remove a player"},
            
            # Admin commands
            "/approve": {"permission": PermissionLevel.ADMIN, "description": "Approve a player registration"},
            "/reject": {"permission": PermissionLevel.ADMIN, "description": "Reject a player registration"},
            "/pending": {"permission": PermissionLevel.ADMIN, "description": "List players pending approval"},
            "/checkfa": {"permission": PermissionLevel.ADMIN, "description": "Check FA registration status"},
            "/dailystatus": {"permission": PermissionLevel.ADMIN, "description": "Generate daily team status report"},
        }
    
    def _get_chat_type(self, chat_id: str) -> ChatType:
        """Determine chat type based on chat ID."""
        try:
            # Use the existing AccessControlService methods
            team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # Default team ID
            
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
            # Get user role from team member service
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
    
    def _can_execute_command(self, command: str, context: CommandContext) -> bool:
        """Check if command can be executed in given context."""
        if command not in self.commands:
            return False
        
        permission = self.commands[command]["permission"]
        
        if permission == PermissionLevel.PUBLIC:
            return True
        
        if permission == PermissionLevel.PLAYER:
            return context.user_role in ['player', 'admin', 'captain', 'secretary', 'manager', 'treasurer']
        
        if permission == PermissionLevel.LEADERSHIP:
            return context.chat_type == ChatType.LEADERSHIP and context.user_role in ['admin', 'captain', 'secretary', 'manager', 'treasurer']
        
        if permission == PermissionLevel.ADMIN:
            return context.chat_type == ChatType.LEADERSHIP and context.user_role in ['admin', 'captain']
        
        return False
    
    def _get_help_message(self, context: CommandContext) -> str:
        """Generate help message based on context."""
        if context.chat_type == ChatType.LEADERSHIP:
            title = "🤖 **KICKAI Bot Help (Leadership)**"
        else:
            title = "🤖 **KICKAI Bot Help**"
        
        message = f"{title}\n\n📋 **Available Commands:**\n\n"
        
        # Group commands by permission level
        public_commands = []
        player_commands = []
        leadership_commands = []
        admin_commands = []
        
        for cmd, info in self.commands.items():
            if self._can_execute_command(cmd, context):
                if info["permission"] == PermissionLevel.PUBLIC:
                    public_commands.append((cmd, info["description"]))
                elif info["permission"] == PermissionLevel.PLAYER:
                    player_commands.append((cmd, info["description"]))
                elif info["permission"] == PermissionLevel.LEADERSHIP:
                    leadership_commands.append((cmd, info["description"]))
                elif info["permission"] == PermissionLevel.ADMIN:
                    admin_commands.append((cmd, info["description"]))
        
        if public_commands:
            message += "🌐 **General Commands:**\n"
            for cmd, desc in public_commands:
                message += f"• `{cmd}` - {desc}\n"
            message += "\n"
        
        if player_commands:
            message += "👥 **Player Commands:**\n"
            for cmd, desc in player_commands:
                message += f"• `{cmd}` - {desc}\n"
            message += "\n"
        
        if leadership_commands:
            message += "👑 **Leadership Commands:**\n"
            for cmd, desc in leadership_commands:
                message += f"• `{cmd}` - {desc}\n"
            message += "\n"
        
        if admin_commands:
            message += "🔧 **Admin Commands:**\n"
            for cmd, desc in admin_commands:
                message += f"• `{cmd}` - {desc}\n"
            message += "\n"
        
        message += "💡 **Tips:**\n"
        message += "• You can use natural language or specific commands\n"
        if context.chat_type != ChatType.LEADERSHIP:
            message += "• Admin commands are only available in the leadership chat\n"
        
        return message
    
    async def dispatch_command(self, command: str, user_id: str, chat_id: str, team_id: str, message_text: str) -> str:
        """Dispatch command with proper permission checking."""
        try:
            # Create context
            context = CommandContext(
                user_id=user_id,
                chat_id=chat_id,
                chat_type=self._get_chat_type(chat_id),
                user_role=await self._get_user_role(user_id, team_id),
                team_id=team_id,
                message_text=message_text
            )
            
            # Handle help command specially
            if command == "/help":
                return self._get_help_message(context)
            
            # Check if command exists
            if command not in self.commands:
                return f"❌ Unknown command: `{command}`\n\nType `/help` for available commands."
            
            # Check permissions
            if not self._can_execute_command(command, context):
                return self._get_access_denied_message(command, context)
            
            # Execute command
            return await self._execute_command(command, context)
            
        except Exception as e:
            logger.error(f"Error dispatching command {command}: {e}")
            return f"❌ Error executing command: {str(e)}"
    
    def _get_access_denied_message(self, command: str, context: CommandContext) -> str:
        """Get access denied message."""
        permission = self.commands[command]["permission"]
        
        if context.chat_type != ChatType.LEADERSHIP and permission in [PermissionLevel.LEADERSHIP, PermissionLevel.ADMIN]:
            return f"""❌ **Access Denied**

🔒 This command requires leadership chat access.
💡 Please use the leadership chat for admin functions.

Command: `{command}`
Required: {permission.value.title()} access"""
        
        return f"""❌ **Access Denied**

🔒 You don't have permission to use this command.
💡 Contact your team admin for access.

Command: `{command}`
Required: {permission.value.title()} access
Your Role: {context.user_role.title()}"""
    
    async def _execute_command(self, command: str, context: CommandContext) -> str:
        """Execute the actual command."""
        try:
            if command == "/start":
                return await self.player_handler._handle_start_command(context.message_text, context.user_id)
            elif command == "/list":
                return await self.player_handler._handle_list_players()
            elif command == "/myinfo":
                return await self.player_handler._handle_myinfo(context.user_id)
            elif command == "/status":
                return await self.player_handler._handle_player_status(context.message_text)
            elif command == "/stats":
                return await self.player_handler._handle_player_stats()
            elif command == "/add":
                return await self.player_handler._handle_add_player(context.message_text, context.user_id)
            elif command == "/remove":
                return await self.player_handler._handle_remove_player(context.message_text, context.user_id)
            elif command == "/approve":
                return await self.player_handler._handle_approve_player(context.message_text, context.user_id)
            elif command == "/reject":
                return await self.player_handler._handle_reject_player(context.message_text, context.user_id)
            elif command == "/pending":
                return await self.player_handler._handle_pending_approvals()
            elif command == "/checkfa":
                return await self.player_handler._handle_check_fa_registration()
            elif command == "/dailystatus":
                return await self.player_handler._handle_daily_status()
            else:
                return f"❌ Command not implemented: `{command}`"
                
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return f"❌ Error executing command: {str(e)}"


# Global dispatcher instance
command_dispatcher = CommandDispatcher()


def get_command_dispatcher() -> CommandDispatcher:
    """Get the global command dispatcher."""
    return command_dispatcher 