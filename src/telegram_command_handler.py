#!/usr/bin/env python3
"""
Telegram Command Handler for KICKAI
Handles commands in leadership group and natural language in main team group
"""

import os
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import requests
from supabase import create_client, Client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CommandContext:
    """Context for command execution."""
    team_id: str
    chat_id: str
    user_id: str
    username: str
    user_role: str
    is_leadership_chat: bool
    command: str
    arguments: str
    message_text: str
    bot_token: str

class TelegramCommandHandler:
    """Handles Telegram commands and natural language processing."""
    
    def __init__(self):
        self.supabase = self._get_supabase_client()
        
        # Command definitions with roles and descriptions
        self.commands = {
            # Fixture Management
            '/newfixture': {
                'roles': ['admin', 'secretary'],
                'description': 'Create a new fixture',
                'usage': '/newfixture <opponent> <date> <time> <venue>',
                'handler': self._handle_new_fixture
            },
            '/deletefixture': {
                'roles': ['admin', 'secretary'],
                'description': 'Delete a fixture',
                'usage': '/deletefixture <fixture_id>',
                'handler': self._handle_delete_fixture
            },
            '/updatefixture': {
                'roles': ['admin', 'secretary'],
                'description': 'Update fixture details',
                'usage': '/updatefixture <fixture_id> <field> <value>',
                'handler': self._handle_update_fixture
            },
            '/listfixtures': {
                'roles': ['admin', 'secretary', 'manager'],
                'description': 'List all fixtures',
                'usage': '/listfixtures [upcoming|past|all]',
                'handler': self._handle_list_fixtures
            },
            
            # Availability Management
            '/sendavailability': {
                'roles': ['admin', 'secretary', 'manager'],
                'description': 'Send availability poll',
                'usage': '/sendavailability <fixture_id>',
                'handler': self._handle_send_availability
            },
            '/checkavailability': {
                'roles': ['admin', 'secretary', 'manager'],
                'description': 'Check availability status',
                'usage': '/checkavailability <fixture_id>',
                'handler': self._handle_check_availability
            },
            
            # Squad Management
            '/selectsquad': {
                'roles': ['admin', 'manager'],
                'description': 'Select squad for fixture',
                'usage': '/selectsquad <fixture_id> <player1,player2,...>',
                'handler': self._handle_select_squad
            },
            '/announcesquad': {
                'roles': ['admin', 'secretary', 'manager'],
                'description': 'Announce squad to team',
                'usage': '/announcesquad <fixture_id>',
                'handler': self._handle_announce_squad
            },
            
            # Payment Management
            '/createpayment': {
                'roles': ['admin', 'treasurer'],
                'description': 'Create payment link',
                'usage': '/createpayment <fixture_id> <amount>',
                'handler': self._handle_create_payment
            },
            '/sendpayment': {
                'roles': ['admin', 'treasurer'],
                'description': 'Send payment reminder',
                'usage': '/sendpayment <fixture_id>',
                'handler': self._handle_send_payment
            },
            '/checkpayments': {
                'roles': ['admin', 'treasurer'],
                'description': 'Check payment status',
                'usage': '/checkpayments <fixture_id>',
                'handler': self._handle_check_payments
            },
            
            # Team Management
            '/addmember': {
                'roles': ['admin'],
                'description': 'Add team member',
                'usage': '/addmember <name> <phone> <role>',
                'handler': self._handle_add_member
            },
            '/removemember': {
                'roles': ['admin'],
                'description': 'Remove team member',
                'usage': '/removemember <member_id>',
                'handler': self._handle_remove_member
            },
            '/updaterole': {
                'roles': ['admin'],
                'description': 'Update member role',
                'usage': '/updaterole <member_id> <new_role>',
                'handler': self._handle_update_role
            },
            '/listmembers': {
                'roles': ['admin', 'secretary', 'manager'],
                'description': 'List team members',
                'usage': '/listmembers [role]',
                'handler': self._handle_list_members
            },
            
            # Help and Status
            '/help': {
                'roles': ['all'],
                'description': 'Show available commands',
                'usage': '/help [command]',
                'handler': self._handle_help
            },
            '/status': {
                'roles': ['all'],
                'description': 'Show team status',
                'usage': '/status',
                'handler': self._handle_status
            }
        }
    
    def _get_supabase_client(self) -> Client:
        """Get Supabase client."""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("Missing Supabase environment variables")
        
        return create_client(url, key)
    
    def _get_team_bot_info(self, chat_id: str) -> Optional[Dict]:
        """Get team bot information for a chat ID."""
        try:
            # Check if this is a main team chat or leadership chat
            response = self.supabase.table('team_bots').select('*').or_(f'chat_id.eq.{chat_id},leadership_chat_id.eq.{chat_id}').execute()
            
            if response.data:
                bot_info = response.data[0]
                is_leadership = str(bot_info.get('leadership_chat_id')) == str(chat_id)
                return {
                    'team_id': bot_info['team_id'],
                    'bot_token': bot_info['bot_token'],
                    'chat_id': bot_info['chat_id'],
                    'leadership_chat_id': bot_info.get('leadership_chat_id'),
                    'is_leadership_chat': is_leadership
                }
            return None
        except Exception as e:
            logger.error(f"Error getting team bot info: {e}")
            return None
    
    def _get_user_role(self, team_id: str, user_id: str) -> str:
        """Get user role in the team."""
        try:
            response = self.supabase.table('team_members').select('role').eq('team_id', team_id).eq('telegram_user_id', user_id).execute()
            
            if response.data:
                return response.data[0]['role']
            return 'player'  # Default role
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return 'player'
    
    def _log_command(self, context: CommandContext, success: bool, error_message: str = None):
        """Log command execution."""
        try:
            self.supabase.table('command_logs').insert({
                'team_id': context.team_id,
                'chat_id': context.chat_id,
                'user_id': context.user_id,
                'username': context.username,
                'command': context.command,
                'arguments': context.arguments,
                'success': success,
                'error_message': error_message,
                'executed_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error logging command: {e}")
    
    def _send_telegram_message(self, chat_id: str, message: str, bot_token: str, parse_mode: str = 'HTML'):
        """Send message to Telegram chat."""
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return None
    
    def process_message(self, update: Dict) -> bool:
        """Process incoming Telegram message."""
        try:
            message = update.get('message', {})
            chat_id = str(message.get('chat', {}).get('id'))
            user_id = str(message.get('from', {}).get('id'))
            username = message.get('from', {}).get('username', 'Unknown')
            text = message.get('text', '').strip()
            
            # Get team bot info
            bot_info = self._get_team_bot_info(chat_id)
            if not bot_info:
                logger.warning(f"No team found for chat ID: {chat_id}")
                return False
            
            # Get user role
            user_role = self._get_user_role(bot_info['team_id'], user_id)
            
            # Create context
            context = CommandContext(
                team_id=bot_info['team_id'],
                chat_id=chat_id,
                user_id=user_id,
                username=username,
                user_role=user_role,
                is_leadership_chat=bot_info['is_leadership_chat'],
                command='',
                arguments='',
                message_text=text,
                bot_token=bot_info['bot_token']
            )
            
            # Check if this is a command
            if text.startswith('/'):
                return self._handle_command(context)
            else:
                return self._handle_natural_language(context)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    def _handle_command(self, context: CommandContext) -> bool:
        """Handle command messages."""
        try:
            # Parse command
            parts = context.message_text.split(' ', 1)
            command = parts[0].lower()
            arguments = parts[1] if len(parts) > 1 else ''
            
            context.command = command
            context.arguments = arguments

            # Strictly enforce: in main group, everyone is a player
            if not context.is_leadership_chat:
                original_role = context.user_role
                context.user_role = 'player'
                if original_role != 'player':
                    logger.info(f"User {context.username} ({original_role}) treated as 'player' in main group for command {command}")

            # Check if command exists
            if command not in self.commands:
                self._send_telegram_message(context.chat_id, f"❌ Unknown command: {command}\nUse /help to see available commands.", context.bot_token)
                self._log_command(context, False, f"Unknown command: {command}")
                return False
            
            # Check if user has permission
            command_info = self.commands[command]
            if 'all' not in command_info['roles'] and context.user_role not in command_info['roles']:
                self._send_telegram_message(context.chat_id, f"❌ You don't have permission to use {command}", context.bot_token)
                self._log_command(context, False, f"Insufficient permissions: {context.user_role}")
                return False
            
            # Check if command is allowed in this chat type
            if context.is_leadership_chat and command not in ['/help', '/status']:
                # Commands are only allowed in leadership chat
                pass
            elif not context.is_leadership_chat:
                # Only help and status in main team chat
                if command not in ['/help', '/status']:
                    self._send_telegram_message(context.chat_id, f"❌ Command {command} is only available in the leadership group. Even if you are an admin, admin commands must be used in the leadership group only.", context.bot_token)
                    self._log_command(context, False, f"Admin command attempt in main group by {context.username}")
                    return False
            
            # Execute command
            try:
                result = command_info['handler'](context)
                self._log_command(context, True)
                return result
            except Exception as e:
                error_msg = f"Error executing {command}: {str(e)}"
                self._send_telegram_message(context.chat_id, f"❌ {error_msg}", context.bot_token)
                self._log_command(context, False, error_msg)
                return False
                
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            return False
    
    def _handle_natural_language(self, context: CommandContext) -> bool:
        """Handle natural language messages."""
        try:
            # Only process natural language in main team chat
            if context.is_leadership_chat:
                return False
            
            # Simple keyword matching for now
            # Later this can be enhanced with AI/NLP
            text = context.message_text.lower()
            
            if any(word in text for word in ['availability', 'available', 'can play', 'in for']):
                return self._handle_natural_availability(context)
            elif any(word in text for word in ['payment', 'paid', 'money', 'fee']):
                return self._handle_natural_payment(context)
            elif any(word in text for word in ['squad', 'team', 'lineup']):
                return self._handle_natural_squad(context)
            elif any(word in text for word in ['fixture', 'match', 'game']):
                return self._handle_natural_fixture(context)
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling natural language: {e}")
            return False
    
    # Command handlers
    def _handle_new_fixture(self, context: CommandContext) -> bool:
        """Handle /newfixture command."""
        # Implementation for creating new fixture
        self._send_telegram_message(context.chat_id, "🏆 New fixture creation - Coming soon!", context.bot_token)
        return True
    
    def _handle_delete_fixture(self, context: CommandContext) -> bool:
        """Handle /deletefixture command."""
        self._send_telegram_message(context.chat_id, "🗑️ Fixture deletion - Coming soon!", context.bot_token)
        return True
    
    def _handle_update_fixture(self, context: CommandContext) -> bool:
        """Handle /updatefixture command."""
        self._send_telegram_message(context.chat_id, "✏️ Fixture update - Coming soon!", context.bot_token)
        return True
    
    def _handle_list_fixtures(self, context: CommandContext) -> bool:
        """Handle /listfixtures command."""
        self._send_telegram_message(context.chat_id, "📅 Fixture list - Coming soon!", context.bot_token)
        return True
    
    def _handle_send_availability(self, context: CommandContext) -> bool:
        """Handle /sendavailability command."""
        self._send_telegram_message(context.chat_id, "📊 Availability poll - Coming soon!", context.bot_token)
        return True
    
    def _handle_check_availability(self, context: CommandContext) -> bool:
        """Handle /checkavailability command."""
        self._send_telegram_message(context.chat_id, "👥 Availability status - Coming soon!", context.bot_token)
        return True
    
    def _handle_select_squad(self, context: CommandContext) -> bool:
        """Handle /selectsquad command."""
        self._send_telegram_message(context.chat_id, "⚽ Squad selection - Coming soon!", context.bot_token)
        return True
    
    def _handle_announce_squad(self, context: CommandContext) -> bool:
        """Handle /announcesquad command."""
        self._send_telegram_message(context.chat_id, "📢 Squad announcement - Coming soon!", context.bot_token)
        return True
    
    def _handle_create_payment(self, context: CommandContext) -> bool:
        """Handle /createpayment command."""
        self._send_telegram_message(context.chat_id, "💳 Payment link creation - Coming soon!", context.bot_token)
        return True
    
    def _handle_send_payment(self, context: CommandContext) -> bool:
        """Handle /sendpayment command."""
        self._send_telegram_message(context.chat_id, "💰 Payment reminder - Coming soon!", context.bot_token)
        return True
    
    def _handle_check_payments(self, context: CommandContext) -> bool:
        """Handle /checkpayments command."""
        self._send_telegram_message(context.chat_id, "📊 Payment status - Coming soon!", context.bot_token)
        return True
    
    def _handle_add_member(self, context: CommandContext) -> bool:
        """Handle /addmember command."""
        self._send_telegram_message(context.chat_id, "👤 Add member - Coming soon!", context.bot_token)
        return True
    
    def _handle_remove_member(self, context: CommandContext) -> bool:
        """Handle /removemember command."""
        self._send_telegram_message(context.chat_id, "🚫 Remove member - Coming soon!", context.bot_token)
        return True
    
    def _handle_update_role(self, context: CommandContext) -> bool:
        """Handle /updaterole command."""
        self._send_telegram_message(context.chat_id, "🔄 Update role - Coming soon!", context.bot_token)
        return True
    
    def _handle_list_members(self, context: CommandContext) -> bool:
        """Handle /listmembers command."""
        self._send_telegram_message(context.chat_id, "👥 Member list - Coming soon!", context.bot_token)
        return True
    
    def _handle_help(self, context: CommandContext) -> bool:
        """Handle /help command."""
        if context.arguments:
            # Show help for specific command
            command = context.arguments.lower()
            if command in self.commands:
                cmd_info = self.commands[command]
                message = f"📖 Help for {command}:\n"
                message += f"Description: {cmd_info['description']}\n"
                message += f"Usage: {cmd_info['usage']}\n"
                message += f"Roles: {', '.join(cmd_info['roles'])}"
            else:
                message = f"❌ Unknown command: {command}"
        else:
            # Show general help
            if context.is_leadership_chat:
                message = "🤖 <b>Leadership Commands</b>\n\n"
                for cmd, info in self.commands.items():
                    if 'all' in info['roles'] or context.user_role in info['roles']:
                        message += f"{cmd} - {info['description']}\n"
            else:
                message = "🤖 <b>Team Commands</b>\n\n"
                message += "In the main team group, you can use natural language:\n"
                message += "• \"I'm available for Sunday's match\"\n"
                message += "• \"I've paid my match fee\"\n"
                message += "• \"What's the squad for next week?\"\n\n"
                message += "Commands: /help, /status"
        
        self._send_telegram_message(context.chat_id, message, context.bot_token)
        return True
    
    def _handle_status(self, context: CommandContext) -> bool:
        """Handle /status command."""
        message = f"📊 <b>Team Status</b>\n\n"
        message += f"Role: {context.user_role.title()}\n"
        message += f"Chat: {'Leadership' if context.is_leadership_chat else 'Main Team'}\n"
        message += "Status: System Active ✅"
        
        self._send_telegram_message(context.chat_id, message, context.bot_token)
        return True
    
    # Natural language handlers
    def _handle_natural_availability(self, context: CommandContext) -> bool:
        """Handle natural language availability messages."""
        self._send_telegram_message(context.chat_id, "✅ Availability noted! Management will be notified.", context.bot_token)
        return True
    
    def _handle_natural_payment(self, context: CommandContext) -> bool:
        """Handle natural language payment messages."""
        self._send_telegram_message(context.chat_id, "💰 Payment noted! Management will be notified.", context.bot_token)
        return True
    
    def _handle_natural_squad(self, context: CommandContext) -> bool:
        """Handle natural language squad queries."""
        self._send_telegram_message(context.chat_id, "⚽ Squad information will be announced by management.", context.bot_token)
        return True
    
    def _handle_natural_fixture(self, context: CommandContext) -> bool:
        """Handle natural language fixture queries."""
        self._send_telegram_message(context.chat_id, "📅 Fixture information will be announced by management.", context.bot_token)
        return True

def main():
    """Test the command handler."""
    handler = TelegramCommandHandler()
    print("🤖 KICKAI Telegram Command Handler")
    print("=" * 40)
    print("✅ Command handler initialized")
    print("📋 Available commands:")
    for cmd, info in handler.commands.items():
        print(f"  {cmd:<15} - {info['description']}")

if __name__ == "__main__":
    main() 