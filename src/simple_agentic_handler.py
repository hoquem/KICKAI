#!/usr/bin/env python3
"""
Simple Agentic Handler for KICKAI
Provides agentic features using LangChain directly, avoiding CrewAI metaclass conflicts.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

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

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config, ENABLE_ADVANCED_MEMORY

# Import Advanced Memory System
if ENABLE_ADVANCED_MEMORY:
    try:
        from src.advanced_memory import AdvancedMemorySystem, MemoryType
        ADVANCED_MEMORY_AVAILABLE = True
        logger.info("✅ Advanced Memory System imported successfully")
    except ImportError as e:
        ADVANCED_MEMORY_AVAILABLE = False
        logger.warning(f"⚠️ Advanced Memory System not available: {e}")
else:
    ADVANCED_MEMORY_AVAILABLE = False

class SimpleAgenticHandler:
    """Simple agentic handler using LangChain directly."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.llm = self._create_llm()
        self.tools = self._create_tools()
        
        # Initialize Advanced Memory System if available
        self.memory_system = None
        if ADVANCED_MEMORY_AVAILABLE and ENABLE_ADVANCED_MEMORY:
            try:
                memory_config = {
                    'max_short_term_items': 100,
                    'max_long_term_items': 500,
                    'max_episodic_items': 200,
                    'max_semantic_items': 100,
                    'pattern_learning_enabled': True
                }
                self.memory_system = AdvancedMemorySystem(memory_config)
                logger.info("✅ Advanced Memory System initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Advanced Memory System: {e}")
                self.memory_system = None
        
    def _create_llm(self):
        """Create LLM instance based on environment."""
        try:
            ai_config = config.ai_config
            logger.info(f"Creating LLM with provider: {ai_config['provider']}")
            
            if ai_config['provider'] == 'google':
                if GOOGLE_AI_AVAILABLE:
                    api_key = ai_config.get('api_key') or os.getenv('GOOGLE_API_KEY')
                    model_name = ai_config.get('model') or 'gemini-pro'
                    if not api_key or not model_name:
                        logger.error("Google AI API key or model name missing.")
                        return None
                    genai.configure(api_key=api_key)
                    llm = genai.GenerativeModel(model_name)
                    logger.info("✅ Google AI LLM created successfully")
                    return llm
                else:
                    logger.warning("⚠️ Google AI packages not available, using fallback")
                    return None
                
            else:
                # Use Ollama for local development
                try:
                    if OLLAMA_AVAILABLE:
                        llm = Ollama(
                            model=ai_config['model'],
                            base_url=ai_config['base_url']
                        )
                        logger.info("✅ Ollama LLM created successfully")
                        return llm
                    else:
                        logger.warning("⚠️ Ollama packages not available, using fallback")
                        return None
                except ImportError:
                    logger.warning("⚠️ Ollama packages not available, using fallback")
                    return None
            
        except Exception as e:
            logger.error(f"Error creating LLM: {e}")
            logger.info("⚠️ Using fallback response system")
            return None
    
    def _create_tools(self) -> List[BaseTool]:
        """Create tools for the agent."""
        try:
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
    
    def process_message(self, message: str, user_id: str = None, chat_id: str = None, user_role: str = None, is_leadership_chat: bool = False) -> str:
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
            conversation_context = []
            if self.memory_system and user_id:
                try:
                    conversation_context = self.memory_system.get_conversation_context(user_id, chat_id, limit=5)
                except Exception as e:
                    logger.warning(f"Failed to retrieve conversation context: {e}")
            
            # Simple command routing based on keywords
            response = self._route_command(message, user_role, is_leadership_chat, conversation_context)
            
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
    
    def _route_command(self, message: str, user_role: str = None, is_leadership_chat: bool = False, conversation_context: List = None) -> str:
        """Route commands to appropriate tools based on keywords."""
        message_lower = message.lower()
        
        # Player management
        if any(word in message_lower for word in ['add player', 'new player', 'create player']):
            return self._handle_add_player(message)
        elif any(word in message_lower for word in ['list players', 'show players', 'all players']):
            player_tool = PlayerTools(self.team_id)
            return player_tool._run('get_all_players')
        elif any(word in message_lower for word in ['player', 'players']) and 'phone' in message_lower:
            return self._handle_get_player(message)
        
        # Fixture management
        elif any(word in message_lower for word in ['new match', 'create match', 'schedule match', 'add fixture']):
            return self._handle_add_fixture(message)
        elif any(word in message_lower for word in ['list matches', 'show matches', 'fixtures', 'games']):
            fixture_tool = FixtureTools(self.team_id)
            return fixture_tool._run('get_all_fixtures')
        
        # Team management (admin only)
        elif any(word in message_lower for word in ['team info', 'team information']):
            team_tool = TeamTools(self.team_id)
            return team_tool._run('get_team_info')
        elif any(word in message_lower for word in ['update team', 'change team name']) and (user_role == 'admin' or is_leadership_chat):
            return self._handle_update_team(message)
        
        # Bot management (admin only)
        elif any(word in message_lower for word in ['bot config', 'bot configuration']) and (user_role == 'admin' or is_leadership_chat):
            bot_tool = BotTools(self.team_id)
            return bot_tool._run('get_bot_config')
        
        # Messaging
        elif any(word in message_lower for word in ['send message', 'notify team', 'announce']):
            return self._handle_send_message(message)
        
        # Help and status
        elif any(word in message_lower for word in ['help', 'what can you do']):
            return self._get_help_message(user_role, is_leadership_chat)
        elif any(word in message_lower for word in ['status', 'system status']):
            return self._get_status_message()
        
        # Default: try to use LLM to understand the request
        else:
            return self._use_llm_for_understanding(message)
    
    def _handle_add_player(self, message: str) -> str:
        """Handle adding a new player."""
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
        if user_role == 'admin' or is_leadership_chat:
            return """🤖 **KICKAI Bot Help (Admin)**

**Available Commands:**

**Player Management:**
- "Add player John Doe with phone 123456789"
- "List all players"
- "Show player with phone 123456789"

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
    
    def _get_status_message(self) -> str:
        """Get status message."""
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

        status_message += """

Ready to help with team management! 🏆"""
        return status_message
    
    def _use_llm_for_understanding(self, message: str) -> str:
        """Use LLM to understand and respond to complex requests."""
        try:
            # Check if LLM is available
            if self.llm is None:
                return f"I'm not sure how to help with that request. Try asking for 'help' to see what I can do. (AI features are currently unavailable)"
            
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
            print(f"\n🤖 Testing: {message}")
            response = handler.process_message(message)
            print(f"📝 Response: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}") 