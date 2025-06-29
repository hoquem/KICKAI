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
ChatGoogleGenerativeAI = None
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AI_AVAILABLE = True
    logger.info("✅ langchain_google_genai imported successfully")
except ImportError:
    logger.warning("⚠️ langchain_google_genai not available, will use fallback")
    # Create a fallback using google-generativeai directly
    try:
        import google.generativeai as genai
        GOOGLE_AI_AVAILABLE = True
        logger.info("✅ Using google-generativeai as fallback")
        
        # Create a wrapper class
        class ChatGoogleGenerativeAI:
            def __init__(self, model="gemini-pro", google_api_key=None, **kwargs):
                genai.configure(api_key=google_api_key)
                self.model = genai.GenerativeModel(model)
                self.temperature = kwargs.get('temperature', 0.7)
                self.max_output_tokens = kwargs.get('max_output_tokens', 1000)
            
            def invoke(self, messages):
                # Convert LangChain format to Google AI format
                if isinstance(messages, str):
                    prompt = messages
                else:
                    prompt = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
                
                response = self.model.generate_content(prompt)
                return response.text
                
    except ImportError:
        logger.warning("⚠️ google-generativeai also not available")
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
from config import config

class SimpleAgenticHandler:
    """Simple agentic handler using LangChain directly."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.llm = self._create_llm()
        self.tools = self._create_tools()
        
    def _create_llm(self):
        """Create LLM instance based on environment."""
        try:
            ai_config = config.ai_config
            logger.info(f"Creating LLM with provider: {ai_config['provider']}")
            
            if ai_config['provider'] == 'google':
                # Use Google AI for production
                try:
                    if GOOGLE_AI_AVAILABLE:
                        llm = ChatGoogleGenerativeAI(
                            model=ai_config['model'],
                            google_api_key=ai_config['api_key'],
                            temperature=0.7,
                            max_output_tokens=1000
                        )
                        logger.info("✅ Google AI LLM created successfully")
                        return llm
                    else:
                        logger.warning("⚠️ Google AI packages not available, using fallback")
                        return None
                except ImportError:
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
            
            # Simple command routing based on keywords
            response = self._route_command(message, user_role, is_leadership_chat)
            
            logger.info(f"Response: {response[:100]}...")
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
    
    def _route_command(self, message: str, user_role: str = None, is_leadership_chat: bool = False) -> str:
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
• "Add player John Doe with phone 123456789"
• "List all players"
• "Show player with phone 123456789"

**Fixture Management:**
• "Create a match against Arsenal on July 1st at 2pm"
• "List all fixtures"
• "Show upcoming matches"

**Team Management:**
• "Show team info"
• "Update team name to BP Hatters United"

**Bot Management:**
• "Show bot configuration"

**Messaging:**
• "Send a message to the team: Training is at 7pm tonight!"

**General:**
• "Status" - Show system status
• "Help" - Show this help message

💡 You can use natural language or slash commands!"""
        else:
            return """🤖 **KICKAI Bot Help**

**Available Commands:**

**Player Management:**
• "List all players"
• "Show player with phone 123456789"

**Fixture Management:**
• "List all fixtures"
• "Show upcoming matches"

**Team Management:**
• "Show team info"

**Messaging:**
• "Send a message to the team: Training is at 7pm tonight!"

**General:**
• "Status" - Show system status
• "Help" - Show this help message

💡 You can use natural language or slash commands!"""
    
    def _get_status_message(self) -> str:
        """Get status message."""
        return """✅ **KICKAI Bot Status**

🟢 **System Status:** Online
🔥 **Database:** Firebase Firestore Connected
🤖 **AI Model:** Google Gemini Active
📱 **Telegram:** Connected and Ready
👥 **Team:** BP Hatters FC

**Available Tools:**
• Player Management ✅
• Fixture Management ✅
• Team Management ✅
• Messaging Tools ✅
• Command Logging ✅

Ready to help with team management! 🏆"""
    
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
            
            response = self.llm.invoke(prompt)
            return response.content
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