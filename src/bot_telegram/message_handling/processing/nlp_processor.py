"""
Natural Language Processor

This module provides natural language processing logic.
"""

import logging
from typing import Optional
from core.context_manager import UserContext
from agents.crew_agents import TeamManagementSystem

logger = logging.getLogger(__name__)


class NaturalLanguageProcessor:
    """Handles natural language processing."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.agent_system = self._initialize_agent_system()
    
    def _initialize_agent_system(self) -> TeamManagementSystem:
        """Initialize the agent system for NLP processing."""
        try:
            return TeamManagementSystem(self.team_id)
        except Exception as e:
            logger.error(f"Error initializing agent system for team {self.team_id}: {e}")
            raise
    
    async def process_natural_language(self, message_text: str, user_context: UserContext) -> str:
        """Process natural language using the agent system."""
        try:
            # Create execution context
            execution_context = {
                'user_id': user_context.user_id,
                'team_id': user_context.team_id,
                'chat_id': user_context.chat_id,
                'is_leadership_chat': user_context.is_leadership_chat,
                'username': user_context.username
            }
            
            # Execute the task using the agent system
            result = await self.agent_system.execute_task(message_text, execution_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing natural language: {e}")
            return f"❌ I couldn't process your request: {str(e)}"
    
    async def get_help_for_query(self, query: str, user_context: UserContext) -> str:
        """Get help information for a natural language query."""
        try:
            # Try to identify what the user is asking for help with
            help_query = f"Help with: {query}"
            execution_context = {
                'user_id': user_context.user_id,
                'team_id': user_context.team_id,
                'chat_id': user_context.chat_id,
                'is_leadership_chat': user_context.is_leadership_chat,
                'username': user_context.username,
                'help_request': True
            }
            
            result = await self.agent_system.execute_task(help_query, execution_context)
            return result
            
        except Exception as e:
            logger.error(f"Error getting help for query: {e}")
            return "❌ I couldn't provide help for your query. Please try rephrasing or use /help for general assistance."
    
    def is_help_request(self, message_text: str) -> bool:
        """Check if a message is a help request."""
        help_keywords = ['help', 'how', 'what', 'where', 'when', 'why', 'guide', 'assist', 'support']
        message_lower = message_text.lower()
        
        return any(keyword in message_lower for keyword in help_keywords)
    
    def is_status_request(self, message_text: str) -> bool:
        """Check if a message is a status request."""
        status_keywords = ['status', 'info', 'myinfo', 'check', 'list', 'show', 'display']
        message_lower = message_text.lower()
        
        return any(keyword in message_lower for keyword in status_keywords)
    
    def is_registration_request(self, message_text: str) -> bool:
        """Check if a message is a registration request."""
        registration_keywords = ['register', 'signup', 'join', 'add me', 'onboard']
        message_lower = message_text.lower()
        
        return any(keyword in message_lower for keyword in registration_keywords) 