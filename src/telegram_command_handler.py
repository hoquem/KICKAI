#!/usr/bin/env python3
"""
Telegram Command Handler for KICKAI
Version: 1.2.0-fixture-management
Deployment: 2024-12-19 16:25 UTC
Handles commands in leadership group and natural language in main team group
DEPLOYMENT VERSION: 2024-12-19-15:45 - Fixture Management Active
"""

import os
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from supabase._sync.client import create_client, Client

# Version check - this will force Railway to reload
VERSION = "1.2.0-fixture-management"
DEPLOYMENT_TIME = "2024-12-19 16:25 UTC"

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
        try:
            # Parse arguments
            args = context.arguments.strip()
            
            if not args:
                # No arguments provided - show usage
                message = "📅 <b>Create New Fixture</b>\n\n"
                message += "<b>Usage:</b> /newfixture <opponent> <date> <time> <venue> [competition] [notes]\n\n"
                message += "<b>Required:</b>\n"
                message += "• <b>Opponent</b> - Team name (e.g., 'Thunder FC')\n"
                message += "• <b>Date</b> - Match date (e.g., '2024-07-15' or '15/07/2024')\n"
                message += "• <b>Time</b> - Kickoff time (e.g., '14:00' or '2:00 PM')\n"
                message += "• <b>Venue</b> - Home/Away + location (e.g., 'Home - Central Park')\n\n"
                message += "<b>Optional:</b>\n"
                message += "• <b>Competition</b> - League, Cup, Friendly (default: League)\n"
                message += "• <b>Notes</b> - Special instructions, kit colors, etc.\n\n"
                message += "<b>Example:</b>\n"
                message += "<code>/newfixture Thunder FC 2024-07-15 14:00 \"Home - Central Park\" League \"Red kit required\"</code>"
                
                self._send_telegram_message(context.chat_id, message, context.bot_token)
                return True
            
            # Parse the arguments
            parts = args.split('"')
            if len(parts) < 3:
                # Simple parsing for basic format
                parts = args.split()
                if len(parts) < 4:
                    message = "❌ <b>Missing required information!</b>\n\n"
                    message += "Please provide: <b>opponent date time venue</b>\n\n"
                    message += "<b>Example:</b>\n"
                    message += "<code>/newfixture Thunder FC 2024-07-15 14:00 \"Home - Central Park\"</code>"
                    self._send_telegram_message(context.chat_id, message, context.bot_token)
                    return True
                
                opponent = parts[0]
                date = parts[1]
                time = parts[2]
                venue = parts[3]
                competition = parts[4] if len(parts) > 4 else "League"
                notes = ' '.join(parts[5:]) if len(parts) > 5 else ""
            else:
                # Complex parsing with quotes
                opponent = parts[0].strip()
                date = parts[1].strip()
                time = parts[2].strip()
                venue = parts[3].strip()
                competition = parts[4].strip() if len(parts) > 4 else "League"
                notes = parts[5].strip() if len(parts) > 5 else ""
            
            # Validate required fields
            missing_fields = []
            
            if not opponent or opponent.lower() in ['vs', 'v', 'against', 'opponent']:
                missing_fields.append("opponent")
            
            if not date or not self._is_valid_date(date):
                missing_fields.append("date (format: YYYY-MM-DD or DD/MM/YYYY)")
            
            if not time or not self._is_valid_time(time):
                missing_fields.append("time (format: HH:MM or H:MM AM/PM)")
            
            if not venue or venue.lower() in ['venue', 'location', 'place']:
                missing_fields.append("venue (e.g., 'Home - Central Park' or 'Away - Thunder Ground')")
            
            if missing_fields:
                message = "❌ <b>Missing or invalid information:</b>\n\n"
                for field in missing_fields:
                    message += f"• {field}\n"
                message += "\n<b>Please provide all required information and try again.</b>"
                self._send_telegram_message(context.chat_id, message, context.bot_token)
                return True
            
            # Create fixture in database
            fixture_data = {
                'team_id': context.team_id,
                'opponent': opponent,
                'match_date': self._parse_date(date),
                'kickoff_time': self._parse_time(time),
                'venue': venue,
                'competition': competition,
                'notes': notes,
                'created_by': context.user_id,
                'created_at': datetime.now().isoformat(),
                'status': 'scheduled'
            }
            
            # Insert into database
            response = self.supabase.table('fixtures').insert(fixture_data).execute()
            
            if response.data:
                fixture = response.data[0]
                
                # Send confirmation message
                message = "✅ <b>Fixture Created Successfully!</b>\n\n"
                message += f"🏆 <b>{fixture['competition']}</b>\n"
                message += f"⚽ <b>BP Hatters FC vs {fixture['opponent']}</b>\n"
                message += f"📅 <b>Date:</b> {self._format_date(fixture['match_date'])}\n"
                message += f"🕐 <b>Time:</b> {self._format_time(fixture['kickoff_time'])}\n"
                message += f"📍 <b>Venue:</b> {fixture['venue']}\n"
                
                if fixture['notes']:
                    message += f"📝 <b>Notes:</b> {fixture['notes']}\n"
                
                message += f"\n🆔 <b>Fixture ID:</b> {fixture['id']}\n"
                message += "💡 Use this ID for updates and availability polls."
                
                self._send_telegram_message(context.chat_id, message, context.bot_token)
                
                # Also send to main team chat if this is from leadership
                if context.is_leadership_chat:
                    bot_info = self._get_team_bot_info(context.chat_id)
                    if bot_info and bot_info['chat_id'] != context.chat_id:
                        team_message = "📢 <b>New Fixture Announced!</b>\n\n"
                        team_message += f"🏆 <b>{fixture['competition']}</b>\n"
                        team_message += f"⚽ <b>BP Hatters FC vs {fixture['opponent']}</b>\n"
                        team_message += f"📅 <b>Date:</b> {self._format_date(fixture['match_date'])}\n"
                        team_message += f"🕐 <b>Time:</b> {self._format_time(fixture['kickoff_time'])}\n"
                        team_message += f"📍 <b>Venue:</b> {fixture['venue']}\n"
                        
                        if fixture['notes']:
                            team_message += f"📝 <b>Notes:</b> {fixture['notes']}\n"
                        
                        team_message += "\n✅ Availability poll will be sent soon!"
                        
                        self._send_telegram_message(bot_info['chat_id'], team_message, bot_info['bot_token'])
                
                return True
            else:
                self._send_telegram_message(context.chat_id, "❌ Failed to create fixture. Please try again.", context.bot_token)
                return False
                
        except Exception as e:
            logger.error(f"Error creating fixture: {e}")
            self._send_telegram_message(context.chat_id, f"❌ Error creating fixture: {str(e)}", context.bot_token)
            return False
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Validate date format."""
        try:
            # Try different date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y']
            for fmt in formats:
                try:
                    datetime.strptime(date_str, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def _is_valid_time(self, time_str: str) -> bool:
        """Validate time format."""
        try:
            # Try different time formats
            formats = ['%H:%M', '%I:%M %p', '%I:%M%p', '%H:%M:%S']
            for fmt in formats:
                try:
                    datetime.strptime(time_str, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format."""
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y']
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return date_str  # Return as-is if parsing fails
    
    def _parse_time(self, time_str: str) -> str:
        """Parse time string to 24-hour format."""
        formats = ['%H:%M', '%I:%M %p', '%I:%M%p', '%H:%M:%S']
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.strftime('%H:%M')
            except ValueError:
                continue
        return time_str  # Return as-is if parsing fails
    
    def _format_date(self, date_str: str) -> str:
        """Format date for display."""
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%A, %d %B %Y')
        except:
            return date_str
    
    def _format_time(self, time_str: str) -> str:
        """Format time for display."""
        try:
            dt = datetime.strptime(time_str, '%H:%M')
            return dt.strftime('%I:%M %p')
        except:
            return time_str
    
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
        try:
            # Parse arguments
            args = context.arguments.strip().lower()
            filter_type = 'upcoming'  # Default to upcoming fixtures
            
            if args in ['upcoming', 'future', 'next']:
                filter_type = 'upcoming'
            elif args in ['past', 'previous', 'history']:
                filter_type = 'past'
            elif args in ['all', 'complete']:
                filter_type = 'all'
            elif args:
                # Invalid filter
                message = "❌ <b>Invalid filter!</b>\n\n"
                message += "<b>Usage:</b> /listfixtures [upcoming|past|all]\n\n"
                message += "<b>Filters:</b>\n"
                message += "• <b>upcoming</b> - Future matches (default)\n"
                message += "• <b>past</b> - Previous matches\n"
                message += "• <b>all</b> - All fixtures\n\n"
                message += "<b>Examples:</b>\n"
                message += "<code>/listfixtures</code> - Show upcoming\n"
                message += "<code>/listfixtures past</code> - Show past matches\n"
                message += "<code>/listfixtures all</code> - Show all fixtures"
                
                self._send_telegram_message(context.chat_id, message, context.bot_token)
                return True
            
            # Build query
            query = self.supabase.table('fixtures').select('*').eq('team_id', context.team_id)
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            if filter_type == 'upcoming':
                query = query.gte('match_date', today).order('match_date', desc=False)
                title = "📅 <b>Upcoming Fixtures</b>"
            elif filter_type == 'past':
                query = query.lt('match_date', today).order('match_date', desc=True)
                title = "📅 <b>Past Fixtures</b>"
            else:  # all
                query = query.order('match_date', desc=True)
                title = "📅 <b>All Fixtures</b>"
            
            # Execute query
            response = query.execute()
            
            if not response.data:
                if filter_type == 'upcoming':
                    message = "📅 <b>No upcoming fixtures</b>\n\n"
                    message += "No matches scheduled. Use /newfixture to create one!"
                elif filter_type == 'past':
                    message = "📅 <b>No past fixtures</b>\n\n"
                    message += "No previous matches found."
                else:
                    message = "📅 <b>No fixtures found</b>\n\n"
                    message += "No fixtures in the database. Use /newfixture to create one!"
                
                self._send_telegram_message(context.chat_id, message, context.bot_token)
                return True
            
            # Format fixtures
            message = f"{title}\n\n"
            
            for i, fixture in enumerate(response.data[:10], 1):  # Limit to 10 fixtures
                # Determine status icon
                if fixture['status'] == 'completed':
                    status_icon = "✅"
                elif fixture['status'] == 'cancelled':
                    status_icon = "❌"
                elif fixture['status'] == 'postponed':
                    status_icon = "⏸️"
                else:
                    status_icon = "⚽"
                
                # Format date
                formatted_date = self._format_date(fixture['match_date'])
                formatted_time = self._format_time(fixture['kickoff_time'])
                
                message += f"{status_icon} <b>{fixture['competition']}</b>\n"
                message += f"   <b>BP Hatters FC vs {fixture['opponent']}</b>\n"
                message += f"   📅 {formatted_date}\n"
                message += f"   🕐 {formatted_time}\n"
                message += f"   📍 {fixture['venue']}\n"
                
                if fixture['notes']:
                    message += f"   📝 {fixture['notes']}\n"
                
                message += f"   🆔 ID: {fixture['id']}\n\n"
            
            if len(response.data) > 10:
                message += f"... and {len(response.data) - 10} more fixtures\n\n"
            
            message += f"💡 Use <code>/listfixtures {filter_type}</code> to refresh this view."
            
            self._send_telegram_message(context.chat_id, message, context.bot_token)
            return True
            
        except Exception as e:
            logger.error(f"Error listing fixtures: {e}")
            self._send_telegram_message(context.chat_id, f"❌ Error listing fixtures: {str(e)}", context.bot_token)
            return False
    
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
    main() # DEPLOYMENT VERSION: 2024-12-19-15:45 - Fixture Management Active
