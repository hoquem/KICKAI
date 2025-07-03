"""
Access Control Service for KICKAI

This service handles access control based on chat type and user roles
with dependency injection and clean architecture principles.
"""

import logging
import os
import re
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass
import requests

from src.services.team_member_service import TeamMemberService
from src.core.exceptions import AccessDeniedError
from src.core.bot_config_manager import get_bot_config_manager

logger = logging.getLogger(__name__)


@dataclass
class AccessControlConfig:
    """Configuration for AccessControlService."""
    # These will be overridden by team-specific bot configuration
    main_chat_id: str = ""  # Will be loaded from bot config
    leadership_chat_id: str = ""  # Will be loaded from bot config
    admin_commands: Optional[set] = None
    read_only_commands: Optional[set] = None
    
    def __post_init__(self):
        if self.admin_commands is None:
            self.admin_commands = {
                'add', 'add player', 'new player', 'create player', 'remove', 'remove player', 'update player', 'deactivate player',
                'new match', 'create match', 'schedule match', 'add fixture', 'update fixture', 'delete fixture',
                'send message to team', 'create poll', 'send payment reminder', 'update team', 'change team name',
                'invite', 'approve', 'reject', 'pending'
            }
        
        if self.read_only_commands is None:
            self.read_only_commands = {
                'list', 'list players', 'show players', 'all players', 'get player', 'player info',
                'list matches', 'show matches', 'fixtures', 'games', 'team info', 'team information',
                'help', 'start', 'status', 'system status', 'stats', 'myinfo'
            }


class AccessControlService:
    """Service for managing access control in Telegram chats."""
    
    def __init__(self):
        from src.database.firebase_client import get_firebase_client
        firebase_client = get_firebase_client()
        self.team_member_service = TeamMemberService(firebase_client)
        
        # Initialize command sets from AccessControlConfig
        config = AccessControlConfig()
        self.admin_commands: Set[str] = config.admin_commands or set()
        self.read_only_commands: Set[str] = config.read_only_commands or set()
        self._bot_token: Optional[str] = None
    
    def _get_bot_token(self) -> str:
        """Get bot token from environment or bot config manager."""
        if not self._bot_token:
            self._bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        return self._bot_token
    
    def _get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat information from Telegram Bot API."""
        try:
            bot_token = self._get_bot_token()
            if not bot_token:
                logger.warning("Bot token not available for chat info lookup")
                return None
            
            url = f"https://api.telegram.org/bot{bot_token}/getChat"
            response = requests.post(url, json={'chat_id': chat_id}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data['result']
                else:
                    logger.warning(f"Telegram API error getting chat info: {data.get('description')}")
            else:
                logger.warning(f"HTTP error getting chat info: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting chat info for {chat_id}: {e}")
        
        return None
    
    def _is_leadership_chat_by_name(self, chat_id: str) -> bool:
        """Check if chat is leadership chat based on chat name containing 'leadership'."""
        try:
            chat_info = self._get_chat_info(chat_id)
            if chat_info:
                chat_title = chat_info.get('title', '').lower()
                chat_type = chat_info.get('type', '')
                
                # Only check group/supergroup chats
                if chat_type in ['group', 'supergroup']:
                    return 'leadership' in chat_title
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking leadership chat by name: {e}")
            return False
    
    def _auto_detect_chat_type(self, chat_id: str, team_id: str) -> str:
        """Auto-detect if chat is main or leadership based on name and configuration."""
        try:
            # First check if it matches configured chat IDs
            manager = get_bot_config_manager()
            bot_config = manager.get_bot_config(team_id)
            
            if bot_config:
                if str(chat_id) == str(bot_config.main_chat_id):
                    return 'main'
                elif str(chat_id) == str(bot_config.leadership_chat_id):
                    return 'leadership'
            
            # If not configured, try to detect by chat name
            if self._is_leadership_chat_by_name(chat_id):
                logger.info(f"Auto-detected leadership chat by name: {chat_id}")
                return 'leadership'
            
            # Default to main chat
            return 'main'
            
        except Exception as e:
            logger.error(f"Error auto-detecting chat type: {e}")
            return 'main'
    
    def _get_bot_config(self, team_id: str):
        """Get bot configuration for a team."""
        try:
            manager = get_bot_config_manager()
            return manager.get_bot_config(team_id)
        except Exception as e:
            logger.error(f"Failed to get bot config for team {team_id}: {e}")
            return None
    
    def is_leadership_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if the current chat is a leadership chat for the team."""
        bot_config = self._get_bot_config(team_id)
        if not bot_config:
            return False
        return str(chat_id) == str(bot_config.leadership_chat_id)
    
    def is_main_chat(self, chat_id: str, team_id: str) -> bool:
        """Check if the current chat is the main chat for the team."""
        bot_config = self._get_bot_config(team_id)
        if not bot_config:
            return False
        return str(chat_id) == str(bot_config.main_chat_id)
    
    def is_admin_command(self, command: str) -> bool:
        """Check if a command requires admin privileges."""
        command_lower = command.lower()
        return any(admin_cmd in command_lower for admin_cmd in self.admin_commands)
    
    def is_read_only_command(self, command: str) -> bool:
        """Check if a command is read-only."""
        command_lower = command.lower()
        return any(read_cmd in command_lower for read_cmd in self.read_only_commands)
    
    async def check_access(self, command: str, chat_id: str, telegram_id: str, team_id: str) -> bool:
        """
        Check if user has access to execute the command.
        
        Returns:
            True if access is granted, False otherwise
        """
        try:
            # Auto-detect chat type based on name and configuration
            chat_type = self._auto_detect_chat_type(chat_id, team_id)
            is_leadership = (chat_type == 'leadership')
            
            logger.info(f"[DEBUG] Auto-detected chat type: {chat_type} for chat {chat_id}")
            
            # Read-only commands are allowed in all chats
            if self.is_read_only_command(command):
                return True
            
            # Admin commands require leadership chat
            if self.is_admin_command(command):
                if not is_leadership:
                    logger.warning(f"❌ Access denied: Admin command '{command}' attempted in non-leadership chat {chat_id}")
                    return False
                
                # In leadership chat, check if user has any leadership role
                member = await self.team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)
                if not member:
                    logger.warning(f"❌ Access denied: User {telegram_id} not found in team {team_id}")
                    return False
                
                if not member.has_any_leadership_role():
                    logger.warning(f"❌ Access denied: User {telegram_id} has no leadership role")
                    return False
                
                return True
            
            # Unknown commands are allowed in leadership chat, denied in main chat
            if is_leadership:
                return True
            else:
                logger.warning(f"❌ Access denied: Unknown command '{command}' attempted in main chat")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking access for command '{command}': {e}")
            return False
    
    async def get_user_permissions(self, telegram_id: str, team_id: str) -> Dict[str, Any]:
        """Get user permissions and role information."""
        try:
            member = await self.team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)
            if not member:
                return {
                    'has_access': False,
                    'roles': [],
                    'is_player': False,
                    'is_leadership': False,
                    'error': 'User not found in team'
                }
            
            return {
                'has_access': True,
                'roles': member.roles,
                'is_player': member.is_player(),
                'is_leadership': member.has_any_leadership_role(),
                'chat_access': member.chat_access,
                'user_id': member.user_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user permissions for {telegram_id}: {e}")
            return {
                'has_access': False,
                'roles': [],
                'is_player': False,
                'is_leadership': False,
                'error': str(e)
            }
    
    def get_access_denied_message(self, command: str, chat_id: str, team_id: str) -> str:
        """Get a user-friendly access denied message."""
        chat_type = self._auto_detect_chat_type(chat_id, team_id)
        is_leadership = (chat_type == 'leadership')
        
        if self.is_admin_command(command) and not is_leadership:
            return (
                "❌ **Access Denied**\n\n"
                "🔒 Admin commands can only be executed from the leadership chat.\n"
                "💡 Please use the leadership chat for team management functions."
            )
        else:
            return (
                "❌ **Access Denied**\n\n"
                "🔒 This command is not available in this chat.\n"
                "💡 Please use the appropriate chat for this function."
            )
    
    async def validate_team_member_roles(self, telegram_id: str, team_id: str) -> List[str]:
        """Validate that a team member has appropriate roles and return any issues."""
        try:
            member = await self.team_member_service.get_team_member_by_telegram_id(telegram_id, team_id)
            if not member:
                return ["User not found in team"]
            
            return await self.team_member_service.validate_member_roles(member)
            
        except Exception as e:
            logger.error(f"❌ Error validating roles for {telegram_id}: {e}")
            return [f"Error validating roles: {str(e)}"]
    
    def get_available_commands(self, chat_id: str, team_id: str, is_leadership: bool = False) -> Dict[str, List[str]]:
        """Get available commands based on chat type and user role."""
        if self.is_leadership_chat(chat_id, team_id) and is_leadership:
            return {
                'admin_commands': list(self.admin_commands),
                'read_only_commands': list(self.read_only_commands),
                'all_commands': list(self.admin_commands | self.read_only_commands)
            }
        else:
            return {
                'read_only_commands': list(self.read_only_commands),
                'all_commands': list(self.read_only_commands)
            } 