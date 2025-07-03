#!/usr/bin/env python3
"""
Simple Agentic Handler for KICKAI
Provides agentic features using LangChain directly, avoiding CrewAI metaclass conflicts.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import LangChain components (avoiding the problematic agents module)
from langchain.tools import BaseTool

# Try to import Google AI with fallback
GOOGLE_AI_AVAILABLE = False
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
    logger.info("✅ google-generativeai imported successfully")
except ImportError:
    logger.warning("⚠️ google-generativeai not available")
    GOOGLE_AI_AVAILABLE = False

# Try to import Ollama with fallback
OLLAMA_AVAILABLE = False
Ollama = None
try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
    logger.info("✅ Ollama imported successfully")
except ImportError:
    logger.warning("⚠️ Ollama not available")
    OLLAMA_AVAILABLE = False

# Import our tools
from src.tools.firebase_tools import PlayerTools, TeamTools, FixtureTools, CommandLoggingTools, BotTools
from src.tools.telegram_tools import (
    SendTelegramMessageTool,
    SendTelegramPollTool,
    SendAvailabilityPollTool,
    SendSquadAnnouncementTool,
    SendPaymentReminderTool,
    SendLeadershipMessageTool
)

# Import Player Registration System
try:
    from src.telegram.player_registration_handler import PlayerRegistrationHandler, PlayerCommandHandler
    PLAYER_REGISTRATION_AVAILABLE = True
    logger.info("✅ Player Registration System imported successfully")
except ImportError as e:
    PLAYER_REGISTRATION_AVAILABLE = False
    logger.warning(f"⚠️ Player Registration System not available: {e}")

# Import OnboardingAgent
try:
    from .crew_agents import OnboardingAgent
    ONBOARDING_AGENT_AVAILABLE = True
    logger.info("✅ OnboardingAgent imported successfully")
except ImportError as e:
    ONBOARDING_AGENT_AVAILABLE = False
    logger.warning(f"⚠️ OnboardingAgent not available: {e}")

# Import configuration
from src.core.config import get_config, AIProvider
config = get_config()

# Import Advanced Memory System
try:
    from src.core.advanced_memory import AdvancedMemorySystem, MemoryType
    ADVANCED_MEMORY_AVAILABLE = True
    logger.info("✅ Advanced Memory System imported successfully")
except ImportError as e:
    ADVANCED_MEMORY_AVAILABLE = False
    logger.warning(f"⚠️ Advanced Memory System not available: {e}")

from src.services.player_service import get_player_service
from src.services.team_service import get_team_service
from src.telegram.player_registration_handler import PlayerRegistrationHandler, PlayerCommandHandler
from src.database.firebase_client import get_firebase_client
from src.services.team_member_service import TeamMemberService
from src.services.access_control_service import AccessControlService

# Import OnboardingHandler
try:
    from src.telegram.onboarding_handler import get_onboarding_workflow
    ONBOARDING_HANDLER_AVAILABLE = True
    logger.info("✅ OnboardingHandler imported successfully")
except ImportError as e:
    ONBOARDING_HANDLER_AVAILABLE = False
    logger.warning(f"⚠️ OnboardingHandler not available: {e}")

class SimpleAgenticHandler:
    """Simple agentic handler using LangChain directly, now using the new service layer."""
    
    def __init__(self, team_id: str):
        """Initialize the SimpleAgenticHandler with dependency injection."""
        self.team_id = team_id
        # Initialize player registration and command handlers
        self.player_registration_handler = PlayerRegistrationHandler(self.team_id)
        self.player_command_handler = PlayerCommandHandler(self.player_registration_handler)
        self.memory_system = None
        self.onboarding_agent = None
        self.team_service = None
        
        # Initialize services with dependency injection
        self.firebase_client = get_firebase_client()
        self.team_member_service = TeamMemberService(self.firebase_client)
        self.access_control_service = AccessControlService()
        
        # Initialize LLM and tools
        self.llm = self._create_llm()
        self.tools = self._create_tools()
        
        # Initialize AI config
        self.ai_config = self._get_ai_config()
        
        logger.info(f"✅ SimpleAgenticHandler initialized for team {team_id}")
        
    def _get_ai_config(self):
        """Get AI configuration from the config system."""
        try:
            return config.ai
        except AttributeError:
            # Fallback to environment variables
            return type('AIConfig', (), {
                'provider': os.getenv('AI_PROVIDER', 'google_gemini'),
                'api_key': os.getenv('GOOGLE_API_KEY', ''),
                'model_name': os.getenv('AI_MODEL_NAME', 'gemini-2.0-flash-001'),
                'temperature': float(os.getenv('AI_TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv('AI_MAX_TOKENS', '1000')),
                'timeout_seconds': int(os.getenv('AI_TIMEOUT', '60'))
            })()
        
    def _create_llm(self):
        """Create LLM instance based on environment."""
        try:
            logger.info(f"[LLM DEBUG] Config object type: {type(config)}")
            logger.info(f"[LLM DEBUG] Config attributes: {dir(config)}")
            try:
                ai_config = config.ai
                logger.info(f"[LLM DEBUG] AI config: {ai_config}")
            except AttributeError as e:
                logger.error(f"[LLM DEBUG] Config has no 'ai' attribute: {e}")
                api_key = os.getenv('GOOGLE_API_KEY')
                model_name = os.getenv('AI_MODEL_NAME', 'gemini-2.0-flash-001')
                provider = os.getenv('AI_PROVIDER', 'google_gemini')
                logger.info(f"[LLM DEBUG] GOOGLE_AI_AVAILABLE={GOOGLE_AI_AVAILABLE}")
                logger.info(f"[LLM DEBUG] api_key={'SET' if api_key else 'MISSING'}")
                logger.info(f"[LLM DEBUG] model_name={model_name}")
                if provider == 'google_gemini' and api_key:
                    if GOOGLE_AI_AVAILABLE and genai is not None:
                        try:
                            # Only use genai if GenerativeModel is available
                            if hasattr(genai, 'GenerativeModel'):
                                # If configure is available, call it
                                if hasattr(genai, 'configure'):
                                    getattr(genai, 'configure')(api_key=api_key)
                                llm = getattr(genai, 'GenerativeModel')(model_name)
                                logger.info("[LLM DEBUG] ✅ Google AI LLM created successfully (fallback)")
                                return llm
                            else:
                                logger.warning("[LLM DEBUG] GenerativeModel not available in google.generativeai")
                                return None
                        except Exception as e:
                            logger.error(f"[LLM DEBUG] Exception during GenerativeModel creation: {e}")
                            return None
                logger.warning("[LLM DEBUG] Using fallback response system")
                return None
            logger.info(f"[LLM DEBUG] Creating LLM with provider: {ai_config.provider}")
            if ai_config.provider == AIProvider.GOOGLE_GEMINI:
                if GOOGLE_AI_AVAILABLE and genai is not None:
                    api_key = ai_config.api_key or os.getenv('GOOGLE_API_KEY')
                    model_name = ai_config.model_name or 'gemini-2.0-flash-001'
                    logger.info(f"[LLM DEBUG] GOOGLE_AI_AVAILABLE={GOOGLE_AI_AVAILABLE}")
                    logger.info(f"[LLM DEBUG] api_key={'SET' if api_key else 'MISSING'}")
                    logger.info(f"[LLM DEBUG] model_name={model_name}")
                    if not api_key or not model_name:
                        logger.error("[LLM DEBUG] Google AI API key or model name missing.")
                        return None
                    try:
                        if hasattr(genai, 'GenerativeModel'):
                            if hasattr(genai, 'configure'):
                                getattr(genai, 'configure')(api_key=api_key)
                            llm = getattr(genai, 'GenerativeModel')(model_name)
                            logger.info("[LLM DEBUG] ✅ Google AI LLM created successfully")
                            return llm
                        else:
                            logger.warning("[LLM DEBUG] GenerativeModel not available in google.generativeai")
                            return None
                    except Exception as e:
                        logger.error(f"[LLM DEBUG] Exception during GenerativeModel creation: {e}")
                        return None
                else:
                    logger.warning("[LLM DEBUG] Google AI packages not available, using fallback")
                    return None
            elif ai_config.provider == AIProvider.OPENAI:
                logger.warning("[LLM DEBUG] OpenAI provider not fully implemented, using fallback")
                return None
            else:
                try:
                    if OLLAMA_AVAILABLE and Ollama is not None:
                        llm = Ollama(
                            model=ai_config.model_name,
                            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
                        )
                        logger.info("[LLM DEBUG] ✅ Ollama LLM created successfully")
                        return llm
                    else:
                        logger.warning("[LLM DEBUG] Ollama packages not available, using fallback")
                        return None
                except ImportError:
                    logger.warning("[LLM DEBUG] Ollama packages not available, using fallback")
                    return None
        except Exception as e:
            logger.error(f"[LLM DEBUG] Error creating LLM: {e}")
            logger.info("[LLM DEBUG] Using fallback response system")
            return None
    
    def _create_tools(self) -> List[BaseTool]:
        """Create tools for the agent."""
        try:
            tools = []
            if self.team_id:
                tools = [
                    PlayerTools(self.team_id),
                    TeamTools(self.team_id),
                    FixtureTools(self.team_id),
                    CommandLoggingTools(self.team_id),
                    BotTools(self.team_id),
                    SendTelegramMessageTool(self.team_id),
                    SendTelegramPollTool(self.team_id),
                    SendAvailabilityPollTool(self.team_id),
                    SendSquadAnnouncementTool(self.team_id),
                    SendPaymentReminderTool(self.team_id),
                    SendLeadershipMessageTool(self.team_id)
                ]
            logger.info(f"✅ Created {len(tools)} tools for team {self.team_id}")
            return tools
            
        except Exception as e:
            logger.error(f"Error creating tools: {e}")
            raise
    
    async def process_message(self, message: str, user_id: str = "", chat_id: str = "", user_role: str = "", is_leadership_chat: bool = False) -> str:
        """Process a message using the agentic system."""
        try:
            logger.info(f"Processing message: {message[:100]}...")
            
            # Store conversation memory if Advanced Memory System is available
            if self.memory_system and user_id and chat_id:
                try:
                    self.memory_system.store_memory(
                        content={
                            'message': message,
                            'user_id': user_id,
                            'chat_id': chat_id,
                            'user_role': user_role,
                            'is_leadership_chat': is_leadership_chat
                        },
                        memory_type=MemoryType.EPISODIC,
                        user_id=user_id,
                        chat_id=chat_id,
                        importance=0.7,
                        tags=['conversation', 'user_input']
                    )
                except Exception as e:
                    logger.warning(f"Failed to store conversation memory: {e}")
            
            # Log the command
            if user_id and chat_id:
                logging_tool = CommandLoggingTools(self.team_id)
                logging_tool._run(
                    'log_command',
                    chat_id=chat_id,
                    user_id=user_id,
                    command=message,
                    success=True
                )
            
            # Get conversation context if available
            conversation_context_list = []
            if self.memory_system and user_id:
                try:
                    conversation_context_list = self.memory_system.get_conversation_context(user_id, chat_id, limit=5) or []
                except Exception as e:
                    logger.warning(f"Failed to retrieve conversation context: {e}")
            
            # Ensure all parameters are correct types
            chat_id_str = chat_id or ""
            user_id_str = user_id or ""
            user_role_str = user_role or ""
            response = await self._route_command(
                message,
                user_id_str,
                chat_id_str,
                user_role_str,
                bool(is_leadership_chat),
                conversation_context_list
            )
            
            # Store response memory
            if self.memory_system and user_id and chat_id:
                try:
                    self.memory_system.store_memory(
                        content={
                            'response': response,
                            'original_message': message,
                            'user_id': user_id,
                            'chat_id': chat_id
                        },
                        memory_type=MemoryType.EPISODIC,
                        user_id=user_id,
                        chat_id=chat_id,
                        importance=0.6,
                        tags=['conversation', 'bot_response']
                    )
                except Exception as e:
                    logger.warning(f"Failed to store response memory: {e}")
            
            logger.info(f"Response: {response[:100]}...")
            
            # Learn from interaction if Advanced Memory System is available
            if self.memory_system and user_id:
                self._learn_from_interaction(message, response, user_id, user_role)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
            # Log the error
            if user_id and chat_id:
                try:
                    logging_tool = CommandLoggingTools(self.team_id)
                    logging_tool._run(
                        'log_command',
                        chat_id=chat_id,
                        user_id=user_id,
                        command=message,
                        success=False,
                        error_message=str(e)
                    )
                except:
                    pass
            
            return f"Sorry, I encountered an error processing your request: {str(e)}"
    
    async def _route_command(self, message: str, user_id: str = "", chat_id: str = "", user_role: str = "", is_leadership_chat: bool = False, conversation_context: list = None) -> str:
        """Route commands to appropriate tools based on keywords (async) with proper access control."""
        message_lower = message.lower()
        
        # Ensure all string parameters
        telegram_id = user_id or ""
        chat_id = chat_id or ""
        user_role = user_role or ""
        if conversation_context is None:
            conversation_context = []
        
        # Handle slash commands with proper access control
        if message.startswith('/'):
            logger.info(f"[ROUTING DEBUG] Processing slash command: {message}")
            # Check access control for admin commands
            if telegram_id and chat_id:
                has_access = await self.access_control_service.check_access(message, chat_id, telegram_id, self.team_id)
                if not has_access:
                    return self.access_control_service.get_access_denied_message(message, chat_id, self.team_id)
            
            # Player Registration System slash commands
            if self.player_command_handler:
                logger.info(f"[ROUTING DEBUG] player_command_handler available, checking command patterns")
                if message.startswith('/add '):
                    logger.info(f"[ROUTING DEBUG] Routing /add command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message.startswith('/remove '):
                    logger.info(f"[ROUTING DEBUG] Routing /remove command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message == '/list':
                    logger.info(f"[ROUTING DEBUG] Routing /list command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message.startswith('/status '):
                    logger.info(f"[ROUTING DEBUG] Routing /status command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message == '/stats':
                    logger.info(f"[ROUTING DEBUG] Routing /stats command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message.startswith('/invite '):
                    logger.info(f"[ROUTING DEBUG] Routing /invite command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message == '/myinfo':
                    logger.info(f"[ROUTING DEBUG] Routing /myinfo command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message.startswith('/approve '):
                    logger.info(f"[ROUTING DEBUG] Routing /approve command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message.startswith('/reject '):
                    logger.info(f"[ROUTING DEBUG] Routing /reject command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message == '/pending':
                    logger.info(f"[ROUTING DEBUG] Routing /pending command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message == '/checkfa':
                    logger.info(f"[ROUTING DEBUG] Routing /checkfa command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message == '/dailystatus':
                    logger.info(f"[ROUTING DEBUG] Routing /dailystatus command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                elif message in ['/help', '/start']:
                    logger.info(f"[ROUTING DEBUG] Routing /help or /start command to player_command_handler")
                    return await self.player_command_handler.handle_command(message, user_id)
                else:
                    logger.info(f"[ROUTING DEBUG] Slash command not matched: {message}")
            else:
                logger.warning(f"[ROUTING DEBUG] player_command_handler is None - this is the problem!")
        
        # Check access control using the new service (for non-slash commands)
        if telegram_id and chat_id:
            has_access = await self.access_control_service.check_access(message, chat_id, telegram_id, self.team_id)
            if not has_access:
                return self.access_control_service.get_access_denied_message(message, chat_id, self.team_id)
        
        # Check for onboarding responses (from players)
        if self.onboarding_agent and user_role != 'admin':
            onboarding_keywords = ['confirm', 'update', 'help', 'emergency', 'dob', 'position', 'name', 'phone', 'complete', 'done', 'no']
            if any(keyword in message_lower for keyword in onboarding_keywords):
                pass
        
        # Check for onboarding responses using new onboarding handler
        if ONBOARDING_HANDLER_AVAILABLE and user_role != 'admin':
            onboarding_keywords = ['yes', 'no', 'confirm', 'update', 'help', 'emergency', 'dob', 'position', 'name', 'phone', 'complete', 'done', 'skip', 'ready']
            if any(keyword in message_lower for keyword in onboarding_keywords):
                try:
                    onboarding_workflow = get_onboarding_workflow(self.team_id)
                    success, response = await onboarding_workflow.process_response(user_id, message)
                    if success:
                        return response
                    else:
                        # If onboarding response failed, continue with normal processing
                        logger.info(f"Onboarding response failed: {response}")
                except Exception as e:
                    logger.error(f"Error processing onboarding response: {e}")
                    # Continue with normal processing
        
        # Player Registration System commands (Phase 1) - natural language
        if self.player_command_handler:
            if any(word in message_lower for word in ['add player', 'remove player', 'list players', 'player status', 'player stats']):
                return await self.player_command_handler.handle_command(message_lower, user_id)
        
        # Legacy player management (fallback) - now with access control
        if any(word in message_lower for word in ['add player', 'new player', 'create player']):
            return self._handle_add_player(message)
        elif any(word in message_lower for word in ['list players', 'show players', 'all players']):
            # Read-only command - allowed in all chats
            player_tool = PlayerTools(self.team_id)
            return player_tool._run('get_all_players')
        elif any(word in message_lower for word in ['player', 'players']) and 'phone' in message_lower:
            # Read-only command - allowed in all chats
            return self._handle_get_player(message)
        
        # Fixture management - with access control
        elif any(word in message_lower for word in ['new match', 'create match', 'schedule match', 'add fixture']):
            return self._handle_add_fixture(message)
        elif any(word in message_lower for word in ['list matches', 'show matches', 'fixtures', 'games']):
            # Read-only command - allowed in all chats
            fixture_tool = FixtureTools(self.team_id)
            return fixture_tool._run('get_all_fixtures')
        
        # Team management (admin only)
        elif any(word in message_lower for word in ['team info', 'team information']):
            team_tool = TeamTools(self.team_id)
            return team_tool._run('get_team_info')
        elif any(word in message_lower for word in ['update team', 'change team name']):
            return self._handle_update_team(message)
        
        # Bot management (admin only)
        elif any(word in message_lower for word in ['bot config', 'bot configuration']):
            bot_tool = BotTools(self.team_id)
            return bot_tool._run('get_bot_config')
        
        # Messaging
        elif any(word in message_lower for word in ['send message', 'notify team', 'announce']):
            return self._handle_send_message(message)
        
        # Help and status
        elif any(word in message_lower for word in ['help', 'what can you do']):
            return self._get_help_message(user_role, is_leadership_chat)
        elif any(word in message_lower for word in ['status', 'system status']):
            return await self._get_status_message()
        
        # Default: try to use LLM to understand the request
        else:
            logger.info(f"[ROUTING DEBUG] Command fell through to LLM handler: {message}")
            return self._use_llm_for_understanding(message)
    
    def _handle_add_player(self, message: str) -> str:
        """Handle adding a new player."""
        if not self.player_command_handler:
            return "Player command handler not available."
        # Simple parsing - in production, use more sophisticated NLP
        try:
            # Extract name and phone from message
            # This is a simplified version - you'd want better parsing
            if 'phone' in message.lower():
                parts = message.split('phone')
                name_part = parts[0].replace('add player', '').replace('new player', '').replace('create player', '').strip()
                phone_part = parts[1].strip()
                
                # Clean up the name and phone
                name = name_part.replace('with', '').replace('phone', '').strip()
                phone = phone_part.strip()
                
                player_tool = PlayerTools(self.team_id)
                return player_tool._run('add_player', name=name, phone_number=phone)
            else:
                return "Please provide both name and phone number. Example: 'Add player John Doe with phone 123456789'"
        except Exception as e:
            return f"Error adding player: {str(e)}"
    
    def _handle_get_player(self, message: str) -> str:
        """Handle getting player information."""
        if not self.player_command_handler:
            return "Player command handler not available."
        try:
            # Extract phone number from message
            if 'phone' in message.lower():
                phone_part = message.split('phone')[1].strip()
                phone = phone_part.strip()
                
                player_tool = PlayerTools(self.team_id)
                return player_tool._run('get_player', phone_number=phone)
            else:
                return "Please provide a phone number to search for a player."
        except Exception as e:
            return f"Error getting player: {str(e)}"
    
    def _handle_add_fixture(self, message: str) -> str:
        """Handle adding a new fixture."""
        if not self.team_service:
            return "Team service not available."
        try:
            # This is a simplified version - you'd want better parsing
            fixture_tool = FixtureTools(self.team_id)
            
            # Extract basic info (this is simplified)
            if 'against' in message.lower():
                opponent_part = message.split('against')[1].split('on')[0].strip()
                opponent = opponent_part.strip()
                
                # Default values for now
                match_date = "2024-07-01"
                kickoff_time = "14:00"
                venue = "Home"
                competition = "League"
                notes = ""
                created_by = "system"
                
                return fixture_tool._run('add_fixture', 
                                       opponent=opponent, 
                                       match_date=match_date, 
                                       kickoff_time=kickoff_time, 
                                       venue=venue, 
                                       competition=competition, 
                                       notes=notes, 
                                       created_by=created_by)
            else:
                return "Please specify the opponent. Example: 'Create a match against Arsenal on July 1st at 2pm'"
        except Exception as e:
            return f"Error adding fixture: {str(e)}"
    
    def _handle_send_message(self, message: str) -> str:
        """Handle sending a message to the team."""
        if not self.tools:
            return "Messaging tools not available."
        try:
            # Extract the message content
            if ':' in message:
                content = message.split(':', 1)[1].strip()
            else:
                content = message.replace('send message', '').replace('to the team', '').strip()
            
            if content:
                message_tool = SendTelegramMessageTool(self.team_id)
                return message_tool._run(content)
            else:
                return "Please provide a message to send. Example: 'Send a message to the team: Training is at 7pm tonight!'"
        except Exception as e:
            return f"Error sending message: {str(e)}"
    
    def _get_help_message(self, user_role: str = None, is_leadership_chat: bool = False) -> str:
        """Get help message based on user role and chat type."""
        if not self.player_command_handler:
            return "Player command handler not available."
        if user_role == 'admin' or is_leadership_chat:
            return """🤖 **KICKAI Bot Help (Admin)**

**Available Commands:**

**Player Registration (Slash Commands):**
- `/add &lt;name&gt; &lt;phone&gt; &lt;position&gt;` - Add a new player
- `/remove &lt;phone&gt;` - Remove a player
- `/list` - List all players
- `/status &lt;phone&gt;` - Get player status
- `/stats` - Get team statistics
- `/invite &lt;phone&gt;` - Generate invite link
- `/invite <phone_or_player_id>` - Generate invitation message
- `/myinfo` - Get your player information
- `/approve <player_id>` - Approve a player
- `/reject <player_id> [reason]` - Reject a player
- `/pending` - List players pending approval

**Player Registration (Natural Language):**
- "add player John Smith 07123456789 striker"
- "remove player 07123456789"
- "list players"
- "player status 07123456789"
- "player stats"

**Fixture Management:**
- "Create a match against Arsenal on July 1st at 2pm"
- "List all fixtures"
- "Show upcoming matches"

**Team Management:**
- "Show team info"
- "Update team name to BP Hatters United"

**Bot Management:**
- "Show bot configuration"

**Messaging:**
- "Send a message to the team: Training is at 7pm tonight!"

**General:**
- "Status" - Show system status
- "Help" - Show this help message

💡 You can use natural language or slash commands!"""
        else:
            return """🤖 **KICKAI Bot Help**

**Available Commands:**

**Player Management:**
- `/list` - List all players
- `/myinfo` - Get your player information
- "List all players"
- "Show player with phone 123456789"

**Fixture Management:**
- "List all fixtures"
- "Show upcoming matches"

**Team Management:**
- "Show team info"

**Messaging:**
- "Send a message to the team: Training is at 7pm tonight!"

**General:**
- "Status" - Show system status
- "Help" - Show this help message

💡 You can use natural language or slash commands!"""
    
    async def _get_status_message(self) -> str:
        """Get status message (async)."""
        status_message = """✅ **KICKAI Bot Status**

🟢 **System Status:** Online
🔥 **Database:** Firebase Firestore Connected
🤖 **AI Model:** Google Gemini Active
📱 **Telegram:** Connected and Ready
👥 **Team:** BP Hatters FC

**Available Tools:**
- Player Management ✅
- Fixture Management ✅
- Team Management ✅
- Messaging Tools ✅
- Command Logging ✅"""

        # Add Advanced Memory System status if available
        if self.memory_system:
            memory_stats = self.memory_system.get_memory_stats()
            status_message += f"""
🧠 **Advanced Memory System:** Active
- Short-term: {memory_stats['short_term_count']} items
- Long-term: {memory_stats['long_term_count']} items
- Episodic: {memory_stats['episodic_count']} items
- Semantic: {memory_stats['semantic_count']} items
- User Preferences: {memory_stats['user_preferences_count']} items
- Patterns: {memory_stats['patterns_count']} items"""
        
        # Add Player Registration System status if available
        if self.player_registration_handler:
            player_stats = await self.player_registration_handler.get_player_stats()
            status_message += f"""
👥 **Player Registration System:** Active
- Total Players: {player_stats['total_players']}
- Active: {player_stats['active_players']}
- Pending: {player_stats['pending_players']}
- FA Registered: {player_stats['fa_registered']}"""

        status_message += """

Ready to help with team management! 🏆"""
        return status_message
    
    def _use_llm_for_understanding(self, message: str) -> str:
        """Use LLM to understand and respond to complex requests."""
        if not self.llm:
            return "LLM is not available."
        try:
            prompt = f"""You are a helpful football team management assistant. A user has sent this message: "{message}"

Available tools and capabilities:
- Player management (add, list, update players)
- Fixture management (create, list matches)
- Team information
- Sending messages to the team
- Command logging

Please provide a helpful response. If the user is asking for something we can do, explain how to do it. If not, politely explain what we can help with.

Response:"""
            
            response = self.llm.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"I'm not sure how to help with that request. Try asking for 'help' to see what I can do. Error: {str(e)}"
    
    def _handle_update_team(self, message: str) -> str:
        """Handle updating team information."""
        try:
            # Extract new team name from message
            if 'to' in message.lower():
                new_name = message.split('to')[1].strip()
                team_tool = TeamTools(self.team_id)
                return team_tool._run('update_team_name', new_name=new_name)
            else:
                return "Please specify the new team name. Example: 'Update team name to BP Hatters United'"
        except Exception as e:
            return f"Error updating team: {str(e)}"
    
    def _learn_from_interaction(self, message: str, response: str, user_id: str, user_role: str = None):
        """Learn from user interaction to improve future responses."""
        if not self.memory_system:
            return
        
        try:
            # Learn user preferences based on interaction patterns
            message_lower = message.lower()
            
            # Communication style preference
            if any(word in message_lower for word in ['please', 'thank you', 'thanks']):
                self.memory_system.learn_user_preference(
                    user_id=user_id,
                    preference_type='communication_style',
                    value='formal',
                    confidence=0.7
                )
            elif any(word in message_lower for word in ['yo', 'hey', 'hi']):
                self.memory_system.learn_user_preference(
                    user_id=user_id,
                    preference_type='communication_style',
                    value='casual',
                    confidence=0.7
                )
            
            # Response length preference
            if len(response) > 200:
                self.memory_system.learn_user_preference(
                    user_id=user_id,
                    preference_type='response_length',
                    value='detailed',
                    confidence=0.6
                )
            elif len(response) < 50:
                self.memory_system.learn_user_preference(
                    user_id=user_id,
                    preference_type='response_length',
                    value='concise',
                    confidence=0.6
                )
            
            # Learn patterns from successful interactions
            if 'successfully' in response.lower() or 'done' in response.lower():
                # Extract key words from message for pattern learning
                key_words = [word for word in message_lower.split() if len(word) > 3]
                if key_words:
                    self.memory_system.learn_pattern(
                        pattern_type='successful_request',
                        trigger_conditions=key_words[:3],  # Use first 3 key words
                        response_pattern=response[:100],  # First 100 chars of response
                        success=True
                    )
            
            # Learn from user role patterns
            if user_role:
                self.memory_system.learn_user_preference(
                    user_id=user_id,
                    preference_type='user_role',
                    value=user_role,
                    confidence=1.0
                )
            
            logger.debug(f"Learned from interaction for user {user_id}")
            
        except Exception as e:
            logger.warning(f"Failed to learn from interaction: {e}")

    async def handle_onboarding_response(self, telegram_user_id: str, response: str) -> str:
        """
        Handle onboarding responses from players (async version)
        """
        try:
            if not self.player_registration_handler:
                return "❌ Player registration system not available"
            # Find player by telegram_user_id
            players_coro = self.player_registration_handler.get_all_players()
            if players_coro is None or not hasattr(players_coro, '__await__'):
                players = []
            else:
                players = await players_coro
                if players is None:
                    players = []
            player = None
            for p in players:
                if getattr(p, 'telegram_id', None) == telegram_user_id:
                    player = p
                    break
            if not player:
                return "❌ Player not found. Please contact leadership if you believe this is an error."
            # Handle the response through the onboarding agent if available
            if self.onboarding_agent:
                # If onboarding_agent.handle_response is async, await it
                result = self.onboarding_agent.handle_response(getattr(player, 'player_id', ""), telegram_user_id or "", response or "")
                if result is not None and hasattr(result, '__await__'):
                    result = await result
                if result is None:
                    return "❌ Error processing onboarding response: No result returned"
                success, message = result
                if success:
                    return f"✅ {message}"
                else:
                    return f"⚠️ {message}"
            else:
                return "❌ Onboarding agent not available"
        except Exception as e:
            logger.error(f"Error handling onboarding response: {e}", exc_info=True)
            return f"❌ Error processing response: {str(e)}"

    async def handle_player_join(self, player_id: str, telegram_user_id: str, telegram_username: str = None) -> str:
        """
        Handle when a player joins via invite link (async version)
        """
        try:
            if not self.player_registration_handler:
                return "❌ Player registration system not available"
            # Update player status to joined
            result_coro = self.player_registration_handler.player_joined_via_invite(player_id or "", telegram_user_id or "", telegram_username or "")
            if result_coro is None or not hasattr(result_coro, '__await__'):
                return "❌ Error processing player join: No result returned"
            result = await result_coro
            if result is None:
                return "❌ Error processing player join: No result returned"
            success, message = result
            if success and self.onboarding_agent:
                return f"✅ {message}\n⚠️ Onboarding started!"
            elif success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"
        except Exception as e:
            logger.error(f"Error handling player join: {e}", exc_info=True)
            return f"❌ Error processing player join: {str(e)}"

    async def handle_onboarding_message(self, message: str, user_id: str, username: str = None, is_leadership_chat: bool = False) -> str:
        """Handle incoming messages and route to appropriate handlers (async everywhere)."""
        try:
            # Check for onboarding responses first (from players)
            if self.onboarding_agent and not is_leadership_chat:
                onboarding_keywords = ['confirm', 'update', 'help', 'emergency', 'dob', 'position', 'name', 'phone', 'complete', 'done', 'no']
                message_lower = message.lower()
                if any(keyword in message_lower for keyword in onboarding_keywords):
                    return await self.handle_onboarding_response(user_id or "", message or "")
            # Check for player join via invite link
            if message.startswith('/join_'):
                player_id = message.replace('/join_', '')
                return await self.handle_player_join(player_id or "", user_id or "", username or "")
            # Handle regular commands and messages
            # Use self if this is the main handler, or self.agentic_handler if that's the correct handler
            handler = getattr(self, 'agentic_handler', self)
            return await handler.process_message(message or "", user_id or "", chat_id="", user_role="", is_leadership_chat=is_leadership_chat)
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return f"❌ Error processing message: {str(e)}"

def create_simple_agentic_handler(team_id: str) -> SimpleAgenticHandler:
    """Factory function to create a simple agentic handler."""
    return SimpleAgenticHandler(team_id)

# Example usage
if __name__ == "__main__":
    # Test the simple agentic handler
    team_id = '0854829d-445c-4138-9fd3-4db562ea46ee'
    
    try:
        handler = create_simple_agentic_handler(team_id)
        
        # Test messages
        test_messages = [
            "List all players",
            "What's our next fixture?",
            "Send a message to the team: Hello everyone!"
        ]
        
        for message in test_messages:
            # Test completed
            response = handler.process_message(message)
            
    except Exception as e:
        # Error occurred during testing
        pass 