#!/usr/bin/env python3
"""
Telegram Command Handler for KICKAI
Version: 1.3.0-llm-parsing
Deployment: 2024-12-19 17:00 UTC
Handles commands in leadership group and natural language in main team group
DEPLOYMENT VERSION: 2024-12-19-17:00 - LLM Command Parsing Active
"""

import os
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import json

# Monkey patch for httpx proxy issue with Supabase
import httpx
original_init = httpx.Client.__init__
original_async_init = httpx.AsyncClient.__init__

def _patched_client_init(self, *args, **kwargs):
    kwargs.pop('proxy', None)  # Remove proxy argument
    return original_init(self, *args, **kwargs)

def _patched_async_client_init(self, *args, **kwargs):
    kwargs.pop('proxy', None)  # Remove proxy argument
    return original_async_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_client_init
httpx.AsyncClient.__init__ = _patched_async_client_init

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Supabase with error handling
try:
    from supabase import create_client, Client
except ImportError as e:
    logger.error(f"Supabase client not available: {e}")
    raise ImportError("Supabase client not available. Install with: pip install supabase")

# Import configuration
try:
    from config import config
except ImportError as e:
    logger.error(f"Configuration not available: {e}")
    raise ImportError("Configuration not available")

# Version check - this will force Railway to reload
VERSION = "1.3.0-llm-parsing"
DEPLOYMENT_TIME = "2024-12-19 17:00 UTC"

# --- LLM-based Command Parsing ---

class LLMCommandParser:
    """LLM-based command parser for natural language interpretation."""
    
    def __init__(self):
        self.ai_config = config.ai_config
        self.available_commands = {
            'newmatch': {
                'description': 'Create a new match/fixture',
                'required_params': ['opponent', 'date', 'time', 'venue'],
                'optional_params': ['competition', 'notes'],
                'examples': [
                    'Create a match against Red Lion FC on July 1st at 2pm at home',
                    'New match vs Arsenal on 2025-07-15 19:30 at Emirates Stadium',
                    'Schedule a friendly against Chelsea next Saturday 3pm at Stamford Bridge'
                ]
            },
            'listmatches': {
                'description': 'List matches/fixtures',
                'required_params': [],
                'optional_params': ['filter'],
                'examples': [
                    'Show upcoming matches',
                    'List all matches',
                    'What games do we have coming up?',
                    'Show past matches'
                ]
            },
            'help': {
                'description': 'Show help information',
                'required_params': [],
                'optional_params': [],
                'examples': [
                    'Help',
                    'What can you do?',
                    'Show commands',
                    'How do I use this bot?'
                ]
            },
            'status': {
                'description': 'Show bot status',
                'required_params': [],
                'optional_params': [],
                'examples': [
                    'Status',
                    'Bot status',
                    'Are you working?',
                    'Show system status'
                ]
            }
        }
    
    def parse_command(self, message_text: str) -> Dict[str, Any]:
        """
        Parse natural language message into structured command data.
        
        Returns:
            Dict with keys: command, params, confidence, error
        """
        try:
            # Check if it's already a slash command
            if message_text.startswith('/'):
                return self._parse_slash_command(message_text)
            
            # Use LLM to parse natural language
            return self._parse_natural_language(message_text)
            
        except Exception as e:
            logger.error(f"Error parsing command: {e}")
            return {
                'command': None,
                'params': {},
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _parse_slash_command(self, message_text: str) -> Dict[str, Any]:
        """Parse traditional slash commands."""
        parts = message_text.split(' ', 1)
        command = parts[0][1:]  # Remove the '/'
        arguments = parts[1] if len(parts) > 1 else ""
        
        # Basic parameter extraction for slash commands
        params = {}
        if command == 'newmatch' and arguments:
            # Try to extract parameters from arguments
            try:
                # Split by quotes to handle spaces in team names
                import shlex
                args = shlex.split(arguments)
                if len(args) >= 4:
                    params = {
                        'opponent': args[0],
                        'date': args[1],
                        'time': args[2],
                        'venue': args[3],
                        'competition': args[4] if len(args) > 4 else 'League',
                        'notes': args[5] if len(args) > 5 else ''
                    }
            except:
                # Fallback: treat as single parameter
                params = {'raw_arguments': arguments}
        
        return {
            'command': command,
            'params': params,
            'confidence': 1.0,
            'error': None
        }
    
    def _parse_natural_language(self, message_text: str) -> Dict[str, Any]:
        """Use LLM to parse natural language into structured command."""
        
        # First, try simple command matching for common cases
        simple_match = self._try_simple_command_match(message_text)
        if simple_match:
            return simple_match
        
        # Use LLM to parse natural language
        prompt = self._create_parsing_prompt(message_text)
        llm_response = self._call_llm(prompt)
        return self._parse_llm_response(llm_response, message_text)
    
    def _try_simple_command_match(self, message_text: str) -> Optional[Dict[str, Any]]:
        """Try to match simple command patterns before using LLM."""
        text = message_text.strip().lower()
        
        # Simple command mappings
        simple_commands = {
            'status': 'status',
            'bot status': 'status',
            'system status': 'status',
            'help': 'help',
            'commands': 'help',
            'what can you do': 'help',
            'show help': 'help',
            'matches': 'listmatches',
            'games': 'listmatches',
            'show matches': 'listmatches',
            'list matches': 'listmatches',
            'show games': 'listmatches',
            'list games': 'listmatches'
        }
        
        # Check for exact matches
        if text in simple_commands:
            return {
                'command': simple_commands[text],
                'params': {},
                'confidence': 0.95,
                'error': None
            }
        
        # Check for partial matches (commands that start with the text)
        for pattern, command in simple_commands.items():
            if text.startswith(pattern) or pattern.startswith(text):
                return {
                    'command': command,
                    'params': {},
                    'confidence': 0.9,
                    'error': None
                }
        
        return None
    
    def _create_parsing_prompt(self, message_text: str) -> str:
        """Create a prompt for the LLM to parse the command."""
        
        commands_info = []
        for cmd, info in self.available_commands.items():
            cmd_info = f"Command: {cmd}\n"
            cmd_info += f"Description: {info['description']}\n"
            cmd_info += f"Required parameters: {', '.join(info['required_params'])}\n"
            cmd_info += f"Optional parameters: {', '.join(info['optional_params'])}\n"
            cmd_info += f"Examples: {', '.join(info['examples'])}\n"
            commands_info.append(cmd_info)
        
        prompt = f"""You are a command parser for a football team management bot. Your job is to interpret user messages and extract the intended command and parameters.

Available commands:
{chr(10).join(commands_info)}

User message: "{message_text}"

Please respond with a JSON object in this exact format:
{{
    "command": "command_name_or_null",
    "params": {{
        "param1": "value1",
        "param2": "value2"
    }},
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this command was chosen"
}}

Rules:
1. If the message doesn't match any command, set command to null
2. Extract all relevant parameters from the message
3. For dates, use YYYY-MM-DD format when possible
4. For times, use HH:MM format (24-hour)
5. Confidence should be between 0.0 and 1.0
6. Only respond with valid JSON, no other text
7. Pay special attention to simple commands like "Status", "Help", "Fixtures" - these are valid commands
8. If the message is just a single word that matches a command name, it's likely a valid command

JSON response:"""

        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM with the prompt."""
        
        if self.ai_config['provider'] == 'google':
            return self._call_google_ai(prompt)
        else:  # ollama
            return self._call_ollama(prompt)
    
    def _call_google_ai(self, prompt: str) -> str:
        """Call Google AI (Gemini) API."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.ai_config['api_key'])
            model = genai.GenerativeModel(self.ai_config['model'])
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Google AI error: {e}")
            raise
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        try:
            import requests
            
            url = f"{self.ai_config['base_url']}/api/generate"
            data = {
                "model": self.ai_config['model'],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent parsing
                    "num_predict": 500
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise
    
    def _parse_llm_response(self, llm_response: str, original_message: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        
        try:
            # Clean the response - remove any markdown formatting
            cleaned_response = llm_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned_response)
            
            # Validate the response
            if not isinstance(parsed, dict):
                raise ValueError("Response is not a dictionary")
            
            if 'command' not in parsed:
                raise ValueError("Missing 'command' field")
            
            if 'params' not in parsed:
                parsed['params'] = {}
            
            if 'confidence' not in parsed:
                parsed['confidence'] = 0.5
            
            # Ensure params is a dictionary
            if not isinstance(parsed['params'], dict):
                parsed['params'] = {}
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response: {llm_response}")
            return {
                'command': None,
                'params': {},
                'confidence': 0.0,
                'error': f"Invalid JSON response: {e}"
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {
                'command': None,
                'params': {},
                'confidence': 0.0,
                'error': str(e)
            }

# --- Match ID Generation System ---

class MatchIDGenerator:
    """Generates human-readable match IDs with dynamic, stable team abbreviations."""
    
    def __init__(self):
        # Dynamic abbreviation memory for this session
        self.team_abbreviations = {
            'bp hatters': 'BPH',
            'bp hatters fc': 'BPH',
            'hatters': 'BPH',
        }
        self.generated_ids = set()
    
    def get_team_abbreviation(self, team_name: str) -> str:
        """Get or generate a stable abbreviation for a team name."""
        if not team_name:
            return 'UNK'
        normalized = team_name.lower().strip()
        if normalized in ['unknown team', 'unknown', 'tbd', 'tba']:
            return 'UNK'
        # Check if already known
        if normalized in self.team_abbreviations:
            return self.team_abbreviations[normalized]
        # Generate abbreviation
        abbr = self._generate_abbreviation(normalized)
        self.team_abbreviations[normalized] = abbr
        return abbr
    
    def _generate_abbreviation(self, normalized: str) -> str:
        # Use initials if multiple words
        words = normalized.split()
        if len(words) >= 2:
            # Take first letter of each word
            abbr = ''.join(word[0].upper() for word in words if word)
            if len(abbr) >= 2:
                return abbr[:3]  # Limit to 3 characters
        # For single words, take first 3 letters
        return normalized[:3].upper()
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string and return DDMM format."""
        try:
            # Try to parse various date formats
            from datetime import datetime
            import re
            
            # Remove common words
            cleaned = re.sub(r'\b(against|vs|v|on|at|home|away)\b', '', date_str, flags=re.IGNORECASE).strip()
            
            # Try different date formats
            date_formats = [
                '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
                '%B %d, %Y', '%d %B %Y', '%B %d %Y', '%d %B, %Y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(cleaned, fmt)
                    return parsed_date.strftime('%d%m')
                except ValueError:
                    continue
            
            # If no format works, try to extract day and month from text
            day_match = re.search(r'\b(\d{1,2})\b', cleaned)
            month_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', cleaned, re.IGNORECASE)
            
            if day_match and month_match:
                day = day_match.group(1).zfill(2)
                month_map = {
                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                }
                month = month_map[month_match.group(1).lower()]
                return f"{day}{month}"
            
            return '0101'  # Default fallback
            
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            return '0101'  # Default fallback
    
    def generate_match_id(self, opponent: str, date: str, venue: str = '') -> str:
        home_abbr = 'BPH'
        away_abbr = self.get_team_abbreviation(opponent)
        date_code = self.parse_date(date)
        base_id = f"{home_abbr}v{away_abbr}{date_code}"
        final_id = self._resolve_conflicts(base_id)
        self.generated_ids.add(final_id)
        return final_id
    
    def _resolve_conflicts(self, base_id: str) -> str:
        if base_id not in self.generated_ids:
            return base_id
        for i in range(1, 10):
            candidate = f"{base_id}{i}"
            if candidate not in self.generated_ids:
                return candidate
        import random, string
        while True:
            suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
            candidate = f"{base_id}{suffix}"
            if candidate not in self.generated_ids:
                return candidate

match_id_generator = MatchIDGenerator()

# --- Command Handlers ---

async def newmatch_command(update, context, params: Dict[str, Any]):
    """Handle newmatch command with LLM-parsed parameters."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    if not update.effective_user:
        return
    user_id = update.effective_user.id
    username = update.effective_user.username or 'Unknown'
    
    # Extract parameters
    opponent = params.get('opponent', 'Unknown Team')
    date = params.get('date', 'TBD')
    time = params.get('time', 'TBD')
    venue = params.get('venue', 'TBD')
    competition = params.get('competition', 'League')
    notes = params.get('notes', '')
    
    # Generate human-readable match ID
    match_id = match_id_generator.generate_match_id(opponent, date, venue)
    
    # Create response message
    message = f"✅ <b>Match Created Successfully!</b>\n\n"
    message += f"🏆 <b>{competition}</b>\n"
    message += f"⚽ <b>BP Hatters FC vs {opponent}</b>\n"
    message += f"📅 <b>Date:</b> {date}\n"
    message += f"🕐 <b>Time:</b> {time}\n"
    message += f"📍 <b>Venue:</b> {venue}\n"
    
    if notes:
        message += f"📝 <b>Notes:</b> {notes}\n"
    
    message += f"\n🆔 <b>Match ID:</b> <code>{match_id}</code>\n"
    message += "💡 Use this ID for updates and availability polls."
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

async def listmatches_command(update, context, params: Dict[str, Any]):
    """Handle listmatches command."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    filter_type = params.get('filter', 'upcoming')
    
    # TODO: Add Supabase integration to fetch actual matches
    message = f"📅 <b>Matches ({filter_type})</b>\n\n"
    message += "This feature is coming soon with LLM parsing!\n"
    message += f"Filter: {filter_type}"
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

async def help_command(update, context, params: Dict[str, Any]):
    """Handle help command."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    message = "🤖 <b>KICKAI Bot Commands</b>\n\n"
    message += "📅 <b>Match Management:</b>\n"
    message += "• <code>/newmatch</code> - Create new match\n"
    message += "• <code>/listmatches</code> - List matches\n\n"
    message += "📊 <b>General:</b>\n"
    message += "• <code>/help</code> - Show this help\n"
    message += "• <code>/status</code> - Show bot status\n\n"
    message += "💡 <b>Natural Language Examples:</b>\n"
    message += "• \"Create a match against Red Lion FC on July 1st at 2pm\"\n"
    message += "• \"Show upcoming matches\"\n"
    message += "• \"What games do we have coming up?\"\n"
    message += "• \"Schedule a match vs Arsenal next Saturday\""
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

async def status_command(update, context, params: Dict[str, Any]):
    """Handle status command."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    if not update.effective_user:
        return
    user = update.effective_user
    
    message = f"📊 <b>Bot Status</b>\n\n"
    message += f"👤 <b>User:</b> {user.first_name} (@{user.username or 'No username'})\n"
    message += f"🆔 <b>User ID:</b> {user.id}\n"
    message += f"💬 <b>Chat ID:</b> {chat_id}\n"
    message += f"🤖 <b>Framework:</b> LLM Command Parsing ✅\n"
    message += f"📅 <b>Version:</b> 1.3.0-llm-parsing\n"
    message += f"🟢 <b>Status:</b> Active"
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

# --- Command Handler Mapping ---

COMMAND_HANDLERS = {
    'newmatch': newmatch_command,
    'listmatches': listmatches_command,
    'help': help_command,
    'status': status_command,
}

# --- Main Handler ---

async def llm_command_handler(update, context):
    """Main handler that uses LLM to parse and route commands."""
    try:
        # Get the message text
        message = update.message
        if not message or not message.text:
            return
        
        text = message.text.strip()
        if not text:
            return
        
        # Initialize LLM parser
        parser = LLMCommandParser()
        
        # Parse the command
        parsed = parser.parse_command(text)
        
        if parsed.get('error'):
            logger.error(f"Command parsing error: {parsed['error']}")
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ <b>Error:</b> {parsed['error']}",
                    parse_mode='HTML'
                )
            return
        
        command = parsed.get('command')
        params = parsed.get('params', {})
        confidence = parsed.get('confidence', 0.0)
        
        # Log the parsing result
        logger.info(f"Parsed command: {command} (confidence: {confidence:.2f})")
        logger.info(f"Parameters: {params}")
        
        # If no command found or low confidence
        if not command or confidence < 0.3:
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🤔 I'm not sure what you want me to do. Try saying something like:\n"
                         "• \"Create a match against Red Lion FC on July 1st at 2pm\"\n"
                         "• \"Show upcoming matches\"\n"
                         "• \"Help\"",
                    parse_mode='HTML'
                )
            return
        
        # Get the handler function
        handler_func = COMMAND_HANDLERS.get(command)
        if not handler_func:
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ <b>Unknown command:</b> {command}\n\n"
                         f"💡 Type <code>/help</code> to see available commands.",
                    parse_mode='HTML'
                )
            return
        
        # Call the command handler
        await handler_func(update, context, params)
        
    except Exception as e:
        logger.error(f"Error in llm_command_handler: {e}")
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ <b>Error:</b> {str(e)}",
                parse_mode='HTML'
            )

# --- Register commands with the bot ---

def register_llm_commands(app):
    """Register LLM-based command handlers with the Application."""
    try:
        from telegram.ext import MessageHandler, filters
        
        # Add a message handler that processes all text messages
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, llm_command_handler))
        
        # Also handle slash commands for backward compatibility
        app.add_handler(MessageHandler(filters.COMMAND, llm_command_handler))
        
        print("✅ LLM command parsing registered successfully")
        print("📋 Available commands: newmatch, listmatches, help, status")
        print("💡 Natural language parsing enabled!")
        
    except Exception as e:
        print(f"❌ Failed to register LLM commands: {e}")
        raise

# --- DEPRECATED: Legacy telegram-click code ---
# Keeping for reference but not using anymore

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

def main():
    """Test the command handler."""
    print("🤖 KICKAI Telegram Command Handler (LLM Parsing)")
    print("=" * 50)
    print("✅ Command handler initialized")
    print("📋 Available commands:")
    for cmd, handler in COMMAND_HANDLERS.items():
        print(f"  {cmd}")
    print("\n💡 Natural language parsing enabled!")
    print("   Try: \"Create a match against Arsenal on July 1st at 2pm\"")

if __name__ == "__main__":
    main()
