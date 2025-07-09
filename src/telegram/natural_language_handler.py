#!/usr/bin/env python3
"""
Sophisticated Natural Language Handler for KICKAI Bot

This module provides intelligent natural language processing using CrewAI agents:
- Advanced LLM-based command fallback processing
- Personalized user experiences
- Learning capabilities
- Context awareness
- Intent recognition
- Multi-modal responses
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from database.models_improved import Player
from database.models_improved import Team
from services.player_service import get_player_service
from services.team_service import get_team_service
from services.match_service import get_match_service
from services.payment_service import get_payment_service
from utils.phone_utils import normalize_phone
from domain.interfaces.player_models import PlayerPosition
from src.core.enums import AgentRole

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents."""
    PLAYER_INFO = "player_info"
    TEAM_STATUS = "team_status"
    MATCH_INFO = "match_info"
    PAYMENT_INFO = "payment_info"
    REGISTRATION = "registration"
    ONBOARDING = "onboarding"
    GENERAL_QUERY = "general_query"
    ADMIN_ACTION = "admin_action"
    PERSONAL_UPDATE = "personal_update"
    COMMAND_FALLBACK = "command_fallback"


@dataclass
class UserContext:
    """User context for personalization."""
    user_id: str
    team_id: str
    role: str
    is_leadership: bool
    chat_type: str
    username: Optional[str] = None
    player: Optional[Player] = None
    team: Optional[Team] = None
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    last_interaction: Optional[datetime] = None


@dataclass
class NLResponse:
    """Natural language response."""
    message: str
    intent: IntentType
    confidence: float
    requires_action: bool = False
    action_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandIntent:
    """Extracted command intent from failed command."""
    command_type: str
    entities: Dict[str, Any]
    confidence: float
    suggested_action: str
    error_reason: str


class SophisticatedNaturalLanguageHandler:
    """
    Sophisticated natural language handler using CrewAI agents.
    
    This handler uses the CrewAI agent system for all natural language processing,
    providing intelligent, context-aware responses without relying on regex patterns.
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_service = get_player_service(team_id=team_id)
        self.team_service = get_team_service(team_id=team_id)
        self.match_service = get_match_service(team_id=team_id)
        self.payment_service = get_payment_service(team_id=team_id)
        self._user_contexts: Dict[str, UserContext] = {}
        
        # Initialize CrewAI system
        self._initialize_crewai_system()
    
    def _initialize_crewai_system(self):
        """Initialize the CrewAI system for natural language processing."""
        try:
            from agents.crew_agents import TeamManagementSystem
            logger.info(f"[NLH INIT] Entering _initialize_crewai_system for team {self.team_id}")
            logger.info(f"[NLH INIT] About to instantiate TeamManagementSystem for team {self.team_id}")
            # Create the team management system
            self.crewai_system = TeamManagementSystem(self.team_id)
            logger.info(f"[NLH INIT] TeamManagementSystem instance id: {id(self.crewai_system)} for team {self.team_id}")
            logger.info(f"[NLH INIT] CrewAI system initialized for team {self.team_id}")
        except Exception as e:
            logger.error(f"Failed to initialize CrewAI system: {e}")
            self.crewai_system = None
    
    async def process_message(self, message: str, user_id: str, chat_id: str, 
                            user_role: str, is_leadership_chat: bool) -> str:
        """
        Process natural language message using CrewAI agents.
        
        This is the main entry point for all natural language processing.
        It uses the CrewAI agent system to understand intent and generate responses.
        """
        try:
            # Get or create user context
            context = await self._get_user_context(user_id, user_role, is_leadership_chat)
            
            # Update interaction history
            self._update_interaction_history(context, message)
            
            # Check if this is a command fallback scenario
            if self._is_command_fallback_scenario(message):
                return await self._handle_command_fallback_with_agent(message, context)
            
            # Use CrewAI agent for natural language processing
            response = await self._process_with_crewai_agent(message, context)
            
            # Update user preferences based on interaction
            self._update_user_preferences(context, response)
            
            # Cache updated context
            self._user_contexts[user_id] = context
            
            logger.info(f"✅ CrewAI processed message for user {user_id}: {response.intent} (confidence: {response.confidence:.2f})")
            
            return response.message
            
        except Exception as e:
            logger.error(f"Error processing natural language with CrewAI: {e}")
            return self._get_fallback_response(message, user_role)
    
    def _is_command_fallback_scenario(self, message: str) -> bool:
        """Check if this message appears to be a failed command attempt."""
        # Look for patterns that suggest a failed command
        command_indicators = [
            message.startswith('/'),  # Slash command
            any(word in message.lower() for word in ['add', 'register', 'approve', 'list', 'status']),  # Command keywords
            len(message.split()) >= 3,  # Multiple parameters
        ]
        
        return any(command_indicators)
    
    async def _handle_command_fallback_with_agent(self, message: str, context: UserContext) -> str:
        """Handle command fallback using CrewAI CommandFallbackAgent."""
        try:
            if not self.crewai_system:
                return "❌ Command processing is currently unavailable. Please try again later."
            
            # Get the CommandFallbackAgent
            command_fallback_agent = self.crewai_system.get_agent(AgentRole.COMMAND_FALLBACK_AGENT)
            if not command_fallback_agent:
                return "❌ Command processing is currently unavailable. Please try again later."
            
            # Create user context for the agent
            user_context = {
                'user_id': context.user_id,
                'team_id': context.team_id,
                'role': context.role,
                'is_leadership': context.is_leadership,
                'chat_type': context.chat_type,
                'username': context.username,
                'player': context.player
            }
            
            # Process with CommandFallbackAgent
            result = await command_fallback_agent.process_failed_command(
                failed_command=message,
                error_message="Command parsing failed, using natural language processing",
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in command fallback processing: {e}")
            return "🤖 I understand you're trying to use a command, but I'm having trouble processing it. Could you try rephrasing your request in natural language?"
    
    async def _process_with_crewai_agent(self, message: str, context: UserContext) -> NLResponse:
        """Process natural language message using CrewAI MessageProcessorAgent."""
        try:
            if not self.crewai_system:
                return NLResponse(
                    message="❌ Natural language processing is currently unavailable. Please use slash commands.",
                    intent=IntentType.GENERAL_QUERY,
                    confidence=0.0
                )
            
            # Get the MessageProcessorAgent
            message_processor_agent = self.crewai_system.get_agent(AgentRole.MESSAGE_PROCESSOR)
            if not message_processor_agent:
                return NLResponse(
                    message="❌ Natural language processing is currently unavailable. Please use slash commands.",
                    intent=IntentType.GENERAL_QUERY,
                    confidence=0.0
                )
            
            # Create detailed task for the agent
            task_description = f"""
            NATURAL LANGUAGE PROCESSING TASK:
            
            User Message: "{message}"
            User Context: {context.user_id} (Role: {context.role})
            Team: {context.team_id}
            Chat Type: {context.chat_type}
            Is Leadership: {context.is_leadership}
            Previous Interactions: {len(context.interaction_history)}
            Player Registered: {context.player is not None}
            
            Your task is to:
            1. Understand the user's intent and needs
            2. Determine the appropriate action to take
            3. Collaborate with other agents if needed
            4. Provide a helpful, personalized response
            
            Available capabilities:
            - Player information and status queries
            - Team statistics and management
            - Match information and scheduling
            - Payment and financial matters
            - Registration and onboarding
            - Admin actions (leadership only)
            
            Respond with a clear, helpful message that addresses the user's needs.
            Use the available tools and collaborate with other agents as needed.
            """
            
            # Process with agent
            result = await message_processor_agent.process_with_memory(
                task_description=task_description,
                user_id=context.user_id,
                context={
                    'message': message,
                    'user_context': context,
                    'team_id': self.team_id
                }
            )
            
            # Determine intent from agent response
            intent = self._determine_intent_from_agent_response(result, message)
            
            return NLResponse(
                message=result,
                intent=intent,
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"Error processing with CrewAI agent: {e}")
            return NLResponse(
                message="❌ Sorry, I encountered an error processing your request. Please try again.",
                intent=IntentType.GENERAL_QUERY,
                confidence=0.0
            )
    
    def _determine_intent_from_agent_response(self, response: str, original_message: str) -> IntentType:
        """Determine intent from agent response."""
        response_lower = response.lower()
        message_lower = original_message.lower()
        
        # Check for player info patterns
        if any(word in message_lower for word in ['my', 'me', 'registration', 'status', 'player', 'info']):
            return IntentType.PLAYER_INFO
        elif any(word in message_lower for word in ['team', 'players', 'list', 'count', 'statistics']):
            return IntentType.TEAM_STATUS
        elif any(word in message_lower for word in ['match', 'fixture', 'game', 'result']):
            return IntentType.MATCH_INFO
        elif any(word in message_lower for word in ['payment', 'fee', 'money', 'financial']):
            return IntentType.PAYMENT_INFO
        elif any(word in message_lower for word in ['register', 'registration', 'join']):
            return IntentType.REGISTRATION
        elif any(word in message_lower for word in ['admin', 'approve', 'manage']):
            return IntentType.ADMIN_ACTION
        else:
            return IntentType.GENERAL_QUERY
    
    async def _get_user_context(self, user_id: str, user_role: str, is_leadership_chat: bool) -> UserContext:
        """Get or create user context."""
        if user_id in self._user_contexts:
            return self._user_contexts[user_id]
        
        # Create new context
        context = UserContext(
            user_id=user_id,
            team_id=self.team_id,
            role=user_role,
            is_leadership=is_leadership_chat,
            chat_type="leadership" if is_leadership_chat else "main"
        )
        
        # Get player information if available
        try:
            player = await self.player_service.get_player_by_telegram_id(user_id, self.team_id)
            if player:
                context.player = player
        except Exception as e:
            logger.warning(f"Could not get player info for user {user_id}: {e}")
        
        # Get team information
        try:
            team = await self.team_service.get_team(self.team_id)
            if team:
                context.team = team
        except Exception as e:
            logger.warning(f"Could not get team info: {e}")
        
        return context
    
    def _update_interaction_history(self, context: UserContext, message: str):
        """Update interaction history."""
        context.interaction_history.append({
            'timestamp': datetime.now(),
            'message': message,
            'chat_type': context.chat_type
        })
        
        # Keep only last 10 interactions
        if len(context.interaction_history) > 10:
            context.interaction_history = context.interaction_history[-10:]
        
        context.last_interaction = datetime.now()
    
    def _update_user_preferences(self, context: UserContext, response: NLResponse):
        """Update user preferences based on interaction."""
        # Track preferred response types
        if response.intent not in context.preferences:
            context.preferences[response.intent.value] = 0
        context.preferences[response.intent.value] += 1
    
    def _get_fallback_response(self, message: str, user_role: str) -> str:
        """Get fallback response when all else fails."""
        return f"""🤖 <b>How can I help you?</b>

I'm your AI assistant for your team!

<b>I can help with:</b>
• 📋 Player information and status
• 📊 Team statistics and reports  
• ⚽ Match schedules and results
• 💰 Payment information
• 📝 Registration and onboarding
• 🔧 Admin tasks (leadership only)

<b>Just ask me naturally!</b>
Examples:
• "What's my player status?"
• "Show me upcoming matches"
• "How many players do we have?"
• "What payments do I owe?"

<b>Or use slash commands:</b>
• /help - Show all commands
• /status - Your status
• /matches - View matches"""


def get_natural_language_handler(team_id: str) -> SophisticatedNaturalLanguageHandler:
    """Get natural language handler for a team."""
    return SophisticatedNaturalLanguageHandler(team_id) 