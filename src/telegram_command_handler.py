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

# Monkey patch for httpx proxy issue with Firebase
import httpx
original_request = httpx.Client.request

def patched_request(self, method, url, **kwargs):
    # Remove proxy argument if present (not supported in some environments)
    if 'proxy' in kwargs:
        del kwargs['proxy']
    return original_request(self, method, url, **kwargs)

httpx.Client.request = patched_request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration
try:
    from config import config, ENABLE_INTELLIGENT_ROUTING, ENABLE_LLM_ROUTING
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
        # Dynamic abbreviation memory for this session - starts empty
        self.team_abbreviations = {}
        self.generated_ids = set()
        # Common team name variations mapping
        self.team_variations = {}
    
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
        
        # Store the abbreviation for future use
        self.team_abbreviations[normalized] = abbr
        
        # Also store common variations of this team name
        self._store_team_variations(normalized, abbr)
        
        logger.info(f"Generated abbreviation '{abbr}' for team '{team_name}' (normalized: '{normalized}')")
        return abbr
    
    def _generate_abbreviation(self, normalized: str) -> str:
        """Generate a 3-character abbreviation for a team name."""
        # Remove common suffixes and prefixes
        cleaned = self._clean_team_name(normalized)
        
        # Use initials if multiple words
        words = cleaned.split()
        if len(words) >= 2:
            # Take first letter of each word
            abbr = ''.join(word[0].upper() for word in words if word)
            if len(abbr) >= 2:
                return abbr[:3]  # Limit to 3 characters
        
        # For single words, take first 3 letters
        return cleaned[:3].upper()
    
    def _clean_team_name(self, team_name: str) -> str:
        """Clean team name by removing common suffixes and prefixes."""
        import re
        
        # Remove common football suffixes
        suffixes_to_remove = [
            r'\s+fc\b', r'\s+football\s+club\b', r'\s+united\b', r'\s+city\b',
            r'\s+town\b', r'\s+athletic\b', r'\s+athletics\b', r'\s+rovers\b',
            r'\s+wanderers\b', r'\s+hotspur\b', r'\s+albion\b', r'\s+county\b'
        ]
        
        cleaned = team_name
        for suffix in suffixes_to_remove:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        # Remove common prefixes
        prefixes_to_remove = [
            r'^the\s+', r'^fc\s+', r'^football\s+club\s+'
        ]
        
        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _store_team_variations(self, normalized: str, abbr: str):
        """Store common variations of team names to map to the same abbreviation."""
        # Generate common variations
        variations = []
        
        # Add with/without "FC"
        if not normalized.endswith(' fc'):
            variations.append(f"{normalized} fc")
        else:
            variations.append(normalized.replace(' fc', ''))
        
        # Add with/without "Football Club"
        if 'football club' not in normalized:
            variations.append(f"{normalized} football club")
        else:
            variations.append(normalized.replace(' football club', ''))
        
        # Add with/without "The"
        if not normalized.startswith('the '):
            variations.append(f"the {normalized}")
        else:
            variations.append(normalized.replace('the ', ''))
        
        # Store variations
        for variation in variations:
            if variation != normalized:
                self.team_variations[variation] = normalized
        
        logger.debug(f"Stored variations for '{normalized}': {variations}")
    
    def get_known_teams(self) -> dict:
        """Get all known team abbreviations for debugging/monitoring."""
        return self.team_abbreviations.copy()
    
    def clear_memory(self):
        """Clear all stored abbreviations (useful for testing)."""
        self.team_abbreviations.clear()
        self.team_variations.clear()
        self.generated_ids.clear()
        logger.info("Cleared MatchIDGenerator memory")
    
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
        date_code = self.parse_date_readable(date)
        base_id = f"{home_abbr}{away_abbr}-{date_code}"
        final_id = self._resolve_conflicts(base_id)
        self.generated_ids.add(final_id)
        return final_id
    
    def parse_date_readable(self, date_str: str) -> str:
        """Parse date string and return DDMMM format (e.g., 01JUL)."""
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
                    return parsed_date.strftime('%d%b').upper()
                except ValueError:
                    continue
            
            # If no format works, try to extract day and month from text
            day_match = re.search(r'\b(\d{1,2})\b', cleaned)
            month_match = re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', cleaned, re.IGNORECASE)
            
            if day_match and month_match:
                day = day_match.group(1).zfill(2)
                month = month_match.group(1).upper()[:3]
                return f"{day}{month}"
            
            return '01JAN'  # Default fallback
            
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            return '01JAN'  # Default fallback
    
    def _resolve_conflicts(self, base_id: str) -> str:
        if base_id not in self.generated_ids:
            return base_id
        for i in range(1, 10):
            candidate = f"{base_id}{i}"
            if candidate not in self.generated_ids:
                return candidate

match_id_generator = MatchIDGenerator()

# --- Agent-Based Message Processing ---

class AgentBasedMessageHandler:
    """Agent-based message handler using CrewAI for intelligent message processing."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.crew = None
        self.agents = {}
        self.conversation_memory = {}  # Store conversation context per chat
        self.intelligent_router = None  # Add intelligent router
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize CrewAI agents for message processing."""
        try:
            from src.agents import create_llm, create_agents_for_team, create_crew_for_team
            
            # Create LLM
            llm = create_llm()
            
            # Create agents for this team
            agents = create_agents_for_team(llm, self.team_id)
            (
                message_processor,      # Primary interface
                team_manager,           # Strategic coordination
                player_coordinator,     # Operational management
                match_analyst,          # Tactical analysis
                communication_specialist, # Broadcast management
                finance_manager,        # Financial management
                squad_selection_specialist, # Squad selection
                analytics_specialist    # Performance analytics
            ) = agents
            
            # Store agents in a dictionary for easy access
            self.agents = {
                'message_processor': message_processor,
                'team_manager': team_manager,
                'player_coordinator': player_coordinator,
                'match_analyst': match_analyst,
                'communication_specialist': communication_specialist,
                'finance_manager': finance_manager,
                'squad_selection_specialist': squad_selection_specialist,
                'analytics_specialist': analytics_specialist
            }
            
            # Create crew for complex multi-agent tasks
            self.crew = create_crew_for_team(agents)
            
            # Initialize LLM-powered routing if enabled
            if ENABLE_LLM_ROUTING:
                try:
                    from src.intelligent_router_standalone import StandaloneIntelligentRouter
                    self.intelligent_router = StandaloneIntelligentRouter(self.agents, llm)
                    logger.info(f"✅ LLM-powered routing initialized for team {self.team_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize LLM-powered router: {e}")
                    self.intelligent_router = None
            # Otherwise, fall back to intelligent routing if enabled
            elif ENABLE_INTELLIGENT_ROUTING:
                try:
                    from src.intelligent_router_standalone import StandaloneIntelligentRouter
                    self.intelligent_router = StandaloneIntelligentRouter(self.agents, llm)
                    logger.info(f"✅ Intelligent router initialized for team {self.team_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize intelligent router: {e}")
                    self.intelligent_router = None
            logger.info(f"✅ Agent-based message handler initialized for team {self.team_id}")
            logger.info(f"📊 Loaded {len(self.agents)} agents: {list(self.agents.keys())}")
            logger.info(f"🧠 Routing: {'✅ LLM-powered' if ENABLE_LLM_ROUTING and self.intelligent_router else ('✅ Intelligent' if ENABLE_INTELLIGENT_ROUTING and self.intelligent_router else '❌ Disabled')}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {e}")
            raise
    
    async def process_message(self, message_text: str, user_id: str, username: str, chat_id: str) -> str:
        """
        Process incoming message using CrewAI agents.
        
        Returns:
            str: Response message to send back to user
        """
        try:
            # Get conversation context
            context_key = f"{chat_id}_{user_id}"
            conversation_context = self.conversation_memory.get(context_key, "")
            
            # Determine if this is a follow-up question
            is_followup = len(conversation_context) > 0
            
            if is_followup:
                # Handle as follow-up question
                response = await self._handle_followup(message_text, conversation_context, user_id, username, chat_id)
            else:
                # Handle as new request
                response = await self._handle_new_request(message_text, user_id, username, chat_id)
            
            # Update conversation memory
            self.conversation_memory[context_key] = f"{conversation_context}\nUser: {message_text}\nBot: {response}"
            
            # Limit memory size to prevent memory bloat
            if len(self.conversation_memory[context_key]) > 2000:
                self.conversation_memory[context_key] = self.conversation_memory[context_key][-1000:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error in agent-based message processing: {e}")
            return f"❌ Sorry, I encountered an error processing your message: {str(e)}"
    
    async def _handle_new_request(self, message_text: str, user_id: str, username: str, chat_id: str) -> str:
        """Handle a new request using intelligent agent routing."""
        try:
            # Use LLM-powered routing if enabled and available
            if ENABLE_LLM_ROUTING and self.intelligent_router:
                return await self._handle_with_intelligent_routing(message_text, user_id, username, chat_id)
            # Otherwise, use intelligent routing if enabled and available
            elif ENABLE_INTELLIGENT_ROUTING and self.intelligent_router:
                return await self._handle_with_intelligent_routing(message_text, user_id, username, chat_id)
            # Otherwise, fall back to legacy routing
            else:
                return await self._handle_with_legacy_routing(message_text, user_id, username, chat_id)
                
        except Exception as e:
            logger.error(f"Error handling new request: {e}")
            return f"❌ Error processing your request: {str(e)}"
    
    async def _handle_with_intelligent_routing(self, message_text: str, user_id: str, username: str, chat_id: str) -> str:
        """Handle request using intelligent routing."""
        try:
            from src.intelligent_router_standalone import RequestContext
            
            # Create request context
            context_key = f"{chat_id}_{user_id}"
            conversation_history = []
            if context_key in self.conversation_memory:
                # Convert conversation memory to history format
                conversation_history = [{"role": "user", "content": self.conversation_memory[context_key]}]
            
            request_context = RequestContext(
                user_id=user_id,
                team_id=self.team_id,
                message=message_text,
                conversation_history=conversation_history,
                user_preferences={},  # Could be enhanced with user preference learning
                team_patterns={}      # Could be enhanced with team pattern analysis
            )
            
            # Get routing decision
            routing_decision = await self.intelligent_router.route_request(message_text, request_context)
            
            logger.info(f"🧠 Intelligent routing decision: {routing_decision.selected_agents} (confidence: {routing_decision.confidence_score:.2f})")
            
            # Execute with selected agents
            if len(routing_decision.selected_agents) == 1:
                # Single agent execution
                agent_name = routing_decision.selected_agents[0]
                agent = self.agents.get(agent_name)
                if agent:
                    return await self._execute_single_agent(agent, message_text, routing_decision)
                else:
                    logger.error(f"Agent {agent_name} not found")
                    return await self._handle_with_legacy_routing(message_text, user_id, username, chat_id)
            
            else:
                # Multi-agent execution using crew
                return await self._execute_multi_agent(routing_decision.selected_agents, message_text, routing_decision)
                
        except Exception as e:
            logger.error(f"Error in intelligent routing: {e}")
            # Fallback to legacy routing
            return await self._handle_with_legacy_routing(message_text, user_id, username, chat_id)
    
    async def _handle_with_legacy_routing(self, message_text: str, user_id: str, username: str, chat_id: str) -> str:
        """Handle request using legacy routing (original implementation)."""
        try:
            # First, use the message processor to understand the request
            message_processor = self.agents['message_processor']
            
            # Create a task for the message processor to interpret the request
            from src.tasks import MessageProcessingTasks
            message_tasks = MessageProcessingTasks()
            task = message_tasks.interpret_message_task(message_processor)
            
            # Format the task description with actual values
            task.description = task.description.format(
                message_text=message_text,
                username=username,
                chat_id=chat_id
            )
            
            # Execute the task
            result = await self._execute_task(task)
            
            # If the message processor determines it needs multiple agents, use the crew
            if self._requires_multi_agent_coordination(message_text):
                return await self._handle_complex_request(message_text, user_id, username, chat_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in legacy routing: {e}")
            return f"❌ Error processing your request: {str(e)}"
    
    async def _execute_single_agent(self, agent: Any, message_text: str, routing_decision) -> str:
        """Execute request with a single agent."""
        try:
            # Create a simple task for the agent
            from src.tasks import MessageProcessingTasks
            message_tasks = MessageProcessingTasks()
            task = message_tasks.interpret_message_task(agent)
            
            # Update task description with routing context
            task.description = f"""
            {task.description}
            
            Routing Context:
            - Selected for: {agent.role}
            - Required capabilities: {routing_decision.required_capabilities}
            - Complexity: {routing_decision.complexity_score}
            - Reasoning: {routing_decision.reasoning}
            """
            
            result = await self._execute_task(task)
            return result
            
        except Exception as e:
            logger.error(f"Error executing single agent: {e}")
            raise
    
    async def _execute_multi_agent(self, selected_agents: List[str], message_text: str, routing_decision) -> str:
        """Execute request with multiple agents using crew."""
        try:
            # Create tasks for each selected agent
            tasks = []
            for agent_name in selected_agents:
                agent = self.agents.get(agent_name)
                if agent:
                    from src.tasks import MessageProcessingTasks
                    message_tasks = MessageProcessingTasks()
                    task = message_tasks.interpret_message_task(agent)
                    
                    # Customize task for this agent
                    task.description = f"""
                    As {agent.role}, contribute to handling: {message_text}
                    
                    Routing Context:
                    - Required capabilities: {routing_decision.required_capabilities}
                    - Complexity: {routing_decision.complexity_score}
                    - Reasoning: {routing_decision.reasoning}
                    
                    Focus on your area of expertise and provide your perspective.
                    """
                    
                    tasks.append(task)
            
            if not tasks:
                raise ValueError("No valid tasks created")
            
            # Execute with crew
            if self.crew and len(tasks) > 1:
                # Use crew for coordination
                self.crew.tasks = tasks
                result = await self.crew.kickoff()
                return str(result)
            else:
                # Execute tasks sequentially
                results = []
                for task in tasks:
                    result = await self._execute_task(task)
                    results.append(result)
                
                # Combine results
                if len(results) == 1:
                    return results[0]
                else:
                    return "\n\n".join([f"From {task.agent.role}: {result}" for task, result in zip(tasks, results)])
                    
        except Exception as e:
            logger.error(f"Error executing multi-agent: {e}")
            raise
    
    async def _handle_followup(self, message_text: str, conversation_context: str, user_id: str, username: str, chat_id: str) -> str:
        """Handle a follow-up question maintaining conversation context."""
        try:
            from src.tasks import MessageProcessingTasks
            
            # Create the follow-up task
            message_tasks = MessageProcessingTasks()
            task = message_tasks.handle_followup_task(self.agents['message_processor'])
            
            # Format the task description with actual values
            task.description = task.description.format(
                followup_message=message_text,
                conversation_context=conversation_context
            )
            
            # Execute the task
            result = await self._execute_task(task)
            return result
            
        except Exception as e:
            logger.error(f"Error handling follow-up: {e}")
            return f"❌ Error processing your follow-up: {str(e)}"
    
    async def _handle_complex_request(self, message_text: str, user_id: str, username: str, chat_id: str) -> str:
        """Handle complex requests that require multiple agents using the crew."""
        try:
            from src.tasks import MessageProcessingTasks
            
            # Create the complex request task
            message_tasks = MessageProcessingTasks()
            task = message_tasks.route_complex_request_task(self.agents['message_processor'])
            
            # Format the task description with actual values
            task.description = task.description.format(
                complex_request=message_text
            )
            
            # Use the crew for complex multi-agent coordination
            result = await self._execute_crew_task(task)
            return result
            
        except Exception as e:
            logger.error(f"Error handling complex request: {e}")
            return f"❌ Error processing your complex request: {str(e)}"
    
    def _requires_multi_agent_coordination(self, message_text: str) -> bool:
        """Determine if a message requires coordination between multiple agents."""
        complex_keywords = [
            'plan', 'coordinate', 'organize', 'manage', 'analyze', 'report',
            'squad selection', 'team selection', 'financial', 'payment',
            'performance analysis', 'tactical', 'strategy', 'coordination'
        ]
        
        message_lower = message_text.lower()
        return any(keyword in message_lower for keyword in complex_keywords)
    
    async def _execute_task(self, task) -> str:
        """Execute a CrewAI task and return the result."""
        try:
            # Execute the task directly with the assigned agent
            result = await task.execute()
            
            # Extract the final answer from the result
            if hasattr(result, 'output'):
                return result.output
            elif isinstance(result, str):
                return result
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            raise
    
    async def _execute_crew_task(self, task) -> str:
        """Execute a task using the crew for multi-agent coordination."""
        try:
            # Use the crew to execute the task with multiple agents
            result = await self.crew.kickoff([task])
            
            # Extract the final answer from the result
            if hasattr(result, 'output'):
                return result.output
            elif isinstance(result, str):
                return result
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error executing crew task: {e}")
            raise
    
    def clear_conversation_memory(self, chat_id: str, user_id: str):
        """Clear conversation memory for a specific user in a chat."""
        context_key = f"{chat_id}_{user_id}"
        if context_key in self.conversation_memory:
            del self.conversation_memory[context_key]
            logger.info(f"Cleared conversation memory for {context_key}")
    
    def get_conversation_stats(self) -> dict:
        """Get statistics about conversation memory usage."""
        return {
            'total_conversations': len(self.conversation_memory),
            'memory_size': sum(len(context) for context in self.conversation_memory.values()),
            'active_chats': len(set(key.split('_')[0] for key in self.conversation_memory.keys())),
            'agents_loaded': len(self.agents),
            'agent_types': list(self.agents.keys())
        }
    
    def get_agent_info(self) -> dict:
        """Get information about loaded agents."""
        agent_info = {}
        for name, agent in self.agents.items():
            agent_info[name] = {
                'role': agent.role,
                'goal': agent.goal,
                'tools_count': len(agent.tools) if hasattr(agent, 'tools') else 0,
                'can_delegate': agent.allow_delegation if hasattr(agent, 'allow_delegation') else False
            }
        return agent_info

# --- Helper Functions ---

def is_admin_command(command: str) -> bool:
    """Check if a command requires admin privileges."""
    admin_commands = {
        'newmatch', 'add_player', 'update_player', 'deactivate_player',
        'update_team_info', 'send_telegram_message', 'create_poll',
        'send_payment_reminder', 'analyze_performance', 'plan_squad'
    }
    return command in admin_commands

def is_leadership_chat(chat_id: str, team_id: str) -> bool:
    """Check if the current chat is a leadership chat."""
    try:
        from src.tools.firebase_tools import get_firebase_client
        
        db = get_firebase_client()
        bots_ref = db.collection('team_bots')
        query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
        docs = list(query.stream())
        
        if docs:
            bot_data = docs[0].to_dict()
            leadership_chat_id = bot_data.get('leadership_chat_id')
            return leadership_chat_id and str(chat_id) == str(leadership_chat_id)
        
        return False
    except Exception as e:
        logger.error(f"Error checking leadership chat: {e}")
        return False

async def newmatch_command(update, context, params: Dict[str, Any]):
    """Handle newmatch command with LLM-parsed parameters."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    if not update.effective_user:
        return
    user_id = update.effective_user.id
    username = update.effective_user.username or 'Unknown'
    
    # Get team ID
    team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
    
    # Check if this is an admin command and enforce leadership chat requirement
    if is_admin_command('newmatch') and not is_leadership_chat(str(chat_id), team_id):
        message = "❌ **Access Denied**\n\n"
        message += "🔒 Admin commands can only be executed from the leadership chat\\.\n"
        message += "💡 Please use the leadership chat to create matches\\."
        
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='MarkdownV2')
        return
    
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
    message = f"✅ **Match Created Successfully\\!**\n\n"
    message += f"🏆 **{competition}**\n"
    message += f"⚽ **BP Hatters FC vs {opponent}**\n"
    message += f"📅 **Date:** {date}\n"
    message += f"🕐 **Time:** {time}\n"
    message += f"📍 **Venue:** {venue}\n"
    
    if notes:
        message += f"📝 **Notes:** {notes}\n"
    
    message += f"\n🆔 **Match ID:** `{match_id}`\n"
    message += "💡 Use this ID for updates and availability polls\\."
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='MarkdownV2')

async def listmatches_command(update, context, params: Dict[str, Any]):
    """Handle listmatches command."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    filter_type = params.get('filter', 'upcoming')
    
    # TODO: Add Firebase integration to fetch actual matches
    message = f"📅 **Matches \\({filter_type}\\)**\n\n"
    message += "This feature is coming soon with LLM parsing\\!\n"
    message += f"Filter: {filter_type}"
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='MarkdownV2')

async def help_command(update, context, params: Dict[str, Any]):
    """Handle help command with role-based permissions."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    if not update.effective_user:
        return
    user_id = update.effective_user.id
    
    # Get team ID (using the default team for now)
    team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
    
    try:
        # Import the necessary functions
        from src.tools.telegram_tools import get_user_role_in_team, get_team_bot_credentials_dual
        from src.tools.firebase_tools import get_firebase_client
        
        # Get user role
        user_role = get_user_role_in_team(team_id, str(user_id))
        
        # Determine if this is a leadership chat
        db = get_firebase_client()
        bots_ref = db.collection('team_bots')
        query = bots_ref.where('team_id', '==', team_id).where('is_active', '==', True)
        docs = list(query.stream())
        
        is_leadership_chat = False
        if docs:
            bot_data = docs[0].to_dict()
            leadership_chat_id = bot_data.get('leadership_chat_id')
            if leadership_chat_id and str(chat_id) == str(leadership_chat_id):
                is_leadership_chat = True
        
        # Build help message based on chat type (not user role for main chat)
        message = "🤖 **KICKAI Bot Help**\n\n"
        
        if is_leadership_chat:
            # Leadership chat - show commands based on user role
            message += f"👑 **Leadership Chat** \\- User Role: {user_role.title()}\n\n"
            
            if user_role in ['admin', 'captain']:
                message += "📅 **Match Management:**\n"
                message += "• \"Create a match against Arsenal on July 1st at 2pm\"\n"
                message += "• \"List all fixtures\"\n"
                message += "• \"Show upcoming matches\"\n\n"
                
                message += "👥 **Player Management:**\n"
                message += "• \"Add player John Doe with phone 123456789\"\n"
                message += "• \"List all players\"\n"
                message += "• \"Show player with phone 123456789\"\n"
                message += "• \"Update player John's phone to 987654321\"\n\n"
                
                message += "🏆 **Team Management:**\n"
                message += "• \"Show team info\"\n"
                message += "• \"Update team name to BP Hatters United\"\n\n"
                
                message += "📢 **Communication:**\n"
                message += "• \"Send a message to the team: Training is at 7pm tonight\\!\"\n"
                message += "• \"Create a poll: Who's available for Saturday's match\\?\"\n\n"
                
                message += "💰 **Financial Management:**\n"
                message += "• \"Send payment reminder for match fees\"\n"
                message += "• \"Track player payments\"\n\n"
                
                message += "📊 **Analytics & Planning:**\n"
                message += "• \"Analyze our team performance\"\n"
                message += "• \"Plan squad selection for next match\"\n"
                message += "• \"Generate match report\"\n\n"
                
            else:
                # Other leadership roles (secretary, manager, treasurer)
                message += "📅 **Match Management:**\n"
                message += "• \"List all fixtures\"\n"
                message += "• \"Show upcoming matches\"\n\n"
                
                message += "👥 **Player Management:**\n"
                message += "• \"List all players\"\n"
                message += "• \"Show player with phone 123456789\"\n\n"
                
                message += "🏆 **Team Management:**\n"
                message += "• \"Show team info\"\n\n"
                
                message += "📢 **Communication:**\n"
                message += "• \"Send a message to the team: Training is at 7pm tonight\\!\"\n\n"
                
        else:
            # Main group chat - show only non-admin commands regardless of user role
            message += f"👥 **Main Group Chat** \\- User Role: {user_role.title()}\n\n"
            message += "💡 **Note:** Admin commands are only available in the leadership chat\\.\n\n"
            
            # Show only basic commands for all users in main chat
            message += "📅 **Match Information:**\n"
            message += "• \"List all fixtures\"\n"
            message += "• \"Show upcoming matches\"\n"
            message += "• \"What games do we have coming up\\?\"\n\n"
            
            message += "👥 **Player Information:**\n"
            message += "• \"List all players\"\n"
            message += "• \"Show player with phone 123456789\"\n\n"
            
            message += "🏆 **Team Information:**\n"
            message += "• \"Show team info\"\n\n"
        
        # Common commands for all users
        message += "📊 **General:**\n"
        message += "• \"Status\" \\- Show system status\n"
        message += "• \"Help\" \\- Show this help message\n\n"
        
        message += "💡 **Tips:**\n"
        message += "• You can use natural language or specific commands\n"
        message += "• Try asking questions like \"What matches do we have\\?\"\n"
        if user_role in ['admin', 'captain'] and not is_leadership_chat:
            message += "• Use the leadership chat for admin management features\n"
        
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='MarkdownV2')
        
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        # Fallback to basic help if there's an error
        fallback_message = "🤖 <b>KICKAI Bot Help</b>\n\n"
        fallback_message += "📅 <b>Basic Commands:</b>\n"
        fallback_message += "• \"List all fixtures\"\n"
        fallback_message += "• \"Show team info\"\n"
        fallback_message += "• \"Status\" - Show system status\n"
        fallback_message += "• \"Help\" - Show this help message\n\n"
        fallback_message += "💡 You can use natural language or specific commands!"
        
        await context.bot.send_message(chat_id=chat_id, text=fallback_message, parse_mode='MarkdownV2')

async def status_command(update, context, params: Dict[str, Any]):
    """Handle status command."""
    if not update.effective_chat:
        return
    chat_id = update.effective_chat.id
    
    if not update.effective_user:
        return
    user = update.effective_user
    
    message = f"📊 **Bot Status**\n\n"
    message += f"👤 **User:** {user.first_name} (@{user.username or 'No username'})\n"
    message += f"🆔 **User ID:** {user.id}\n"
    message += f"💬 **Chat ID:** {chat_id}\n"
    message += f"🤖 **Framework:** LLM Command Parsing ✅\n"
    message += f"📅 **Version:** 1.3.0-llm-parsing\n"
    message += f"🟢 **Status:** Active"
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='MarkdownV2')

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
                    parse_mode='MarkdownV2'
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
                    parse_mode='MarkdownV2'
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
                    parse_mode='MarkdownV2'
                )
            return
        
        # Check admin command restrictions
        team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
        if is_admin_command(command) and not is_leadership_chat(str(update.effective_chat.id), team_id):
            message = "❌ **Access Denied**\n\n"
            message += "🔒 Admin commands can only be executed from the leadership chat\\.\n"
            message += "💡 Please use the leadership chat for admin management features."
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode='MarkdownV2'
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
                parse_mode='MarkdownV2'
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

def main():
    """Test the command handler."""
    print("🤖 KICKAI Telegram Command Handler (LLM Parsing)")
    print("=" * 50)
    print("✅ Command handler initialized")
    print(" Available commands:")
    for cmd, handler in COMMAND_HANDLERS.items():
        print(f"  {cmd}")
    print("\n💡 Natural language parsing enabled!")
    print("   Try: \"Create a match against Arsenal on July 1st at 2pm\"")

if __name__ == "__main__":
    main()

# Add this new function after the AgentBasedMessageHandler class

async def agent_based_command_handler(update, context):
    """Agent-based command handler that replaces the LLM parser."""
    try:
        # Get the message text
        message = update.message
        if not message or not message.text:
            return
        
        text = message.text.strip()
        if not text:
            return
        
        # Get user and chat information
        if not update.effective_chat:
            return
        chat_id = update.effective_chat.id
        
        if not update.effective_user:
            return
        user_id = update.effective_user.id
        username = update.effective_user.username or 'Unknown'
        
        # Initialize agent-based message handler
        # Use the default team ID for now (can be made configurable later)
        team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
        
        try:
            handler = AgentBasedMessageHandler(team_id)
        except Exception as e:
            logger.error(f"Failed to initialize agent handler: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ <b>System Error:</b> Agent system is currently unavailable. Please try again later.",
                parse_mode='MarkdownV2'
            )
            return
        
        # Process the message using agents
        logger.info(f"Processing message with agents: {text}")
        response = await handler.process_message(text, str(user_id), username, str(chat_id))
        
        # Send the response
        await context.bot.send_message(
            chat_id=chat_id,
            text=response,
            parse_mode='MarkdownV2'
        )
        
        # Log successful processing
        logger.info(f"Agent-based message processed successfully for user {username}")
        
    except Exception as e:
        logger.error(f"Error in agent_based_command_handler: {e}")
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ <b>Error:</b> {str(e)}",
                parse_mode='MarkdownV2'
            )

# Add this function to register the agent-based handler
def register_agent_based_commands(app):
    """Register agent-based command handlers with the Application."""
    try:
        from telegram.ext import MessageHandler, filters
        
        # Add a message handler that processes all text messages with agents
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent_based_command_handler))
        
        # Also handle slash commands for backward compatibility
        app.add_handler(MessageHandler(filters.COMMAND, agent_based_command_handler))
        
        print("✅ Agent-based command processing registered successfully")
        print("🤖 Using 8-agent CrewAI system for message processing")
        print("💡 Natural language processing with agent collaboration enabled!")
        
    except Exception as e:
        print(f"❌ Failed to register agent-based commands: {e}")
        raise

from src.simple_agentic_handler import SimpleAgenticHandler
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

def register_langchain_agentic_handler(app):
    """Register a message handler that uses SimpleAgenticHandler for agentic processing."""
    # Dictionary to cache handlers per team
    agentic_handlers = {}

    async def langchain_agentic_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Extract chat and user info
        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user
        chat_id = str(chat.id)
        user_id = str(user.id)
        username = user.username or user.full_name or "Unknown"
        message_text = message.text or ""

        # For now, use a fixed team_id (can be improved to map chat_id to team_id)
        team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'

        # Get user role and check if it's a leadership chat
        try:
            from src.tools.firebase_tools import get_user_role, is_leadership_chat
            user_role = get_user_role(team_id, user_id)
            is_leadership = is_leadership_chat(chat_id, team_id)
        except Exception as e:
            logger.error(f"Error getting user role or chat type: {e}")
            user_role = 'member'  # Default to member
            is_leadership = False

        # Get or create the handler for this team
        if team_id not in agentic_handlers:
            agentic_handlers[team_id] = SimpleAgenticHandler(team_id)
        handler = agentic_handlers[team_id]

        # Process the message with role and chat type information
        response = handler.process_message(
            message_text, 
            user_id=user_id, 
            chat_id=chat_id, 
            user_role=user_role, 
            is_leadership_chat=is_leadership
        )

        # Reply to the user
        await message.reply_text(response)

    # Register the handler for all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, langchain_agentic_message_handler))
