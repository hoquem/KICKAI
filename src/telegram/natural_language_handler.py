#!/usr/bin/env python3
"""
Natural Language Handler for KICKAI Bot

This module provides intelligent natural language processing with:
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

from src.utils.llm_intent import extract_intent
from src.services.player_service import get_player_service
from src.services.team_service import get_team_service
from src.services.match_service import get_match_service
from src.services.payment_service import get_payment_service
from src.database.models_improved import Player, Team
from src.core.improved_config_system import get_improved_config

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


class NaturalLanguageHandler:
    """
    Advanced natural language handler with personalization and learning capabilities.
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_service = get_player_service()
        self.team_service = get_team_service()
        self.match_service = get_match_service()
        self.payment_service = get_payment_service()
        self.config_manager = get_improved_config()
        
        # User context cache for personalization
        self._user_contexts: Dict[str, UserContext] = {}
        
        logger.info(f"✅ NaturalLanguageHandler initialized for team {team_id}")
    
    async def process_message(self, message: str, user_id: str, chat_id: str, 
                            user_role: str, is_leadership_chat: bool) -> str:
        """
        Process natural language message with personalization.
        
        Args:
            message: User's natural language message
            user_id: Telegram user ID
            chat_id: Chat ID
            user_role: User's role in the team
            is_leadership_chat: Whether this is a leadership chat
            
        Returns:
            Personalized response message
        """
        try:
            # Get or create user context
            context = await self._get_user_context(user_id, user_role, is_leadership_chat)
            
            # Update interaction history
            self._update_interaction_history(context, message)
            
            # Extract intent and entities
            intent_result = await self._extract_intent_and_entities(message, context)
            
            # Generate personalized response
            response = await self._generate_response(message, intent_result, context)
            
            # Update user preferences based on interaction
            self._update_user_preferences(context, intent_result, response)
            
            # Cache updated context
            self._user_contexts[user_id] = context
            
            logger.info(f"✅ NL processed for user {user_id}: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
            
            return response.message
            
        except Exception as e:
            logger.error(f"Error processing natural language: {e}")
            return self._get_fallback_response(message, user_role)
    
    async def _get_user_context(self, user_id: str, user_role: str, is_leadership_chat: bool) -> UserContext:
        """Get or create user context for personalization."""
        if user_id in self._user_contexts:
            context = self._user_contexts[user_id]
            context.last_interaction = datetime.now()
            return context
        
        # Create new context
        context = UserContext(
            user_id=user_id,
            team_id=self.team_id,
            role=user_role,
            is_leadership=is_leadership_chat,
            chat_type="leadership" if is_leadership_chat else "main",
            last_interaction=datetime.now()
        )
        
        # Load user data
        try:
            context.player = await self.player_service.get_player_by_telegram_id(user_id, self.team_id)
            context.team = await self.team_service.get_team(self.team_id)
        except Exception as e:
            logger.warning(f"Could not load user data for {user_id}: {e}")
        
        return context
    
    async def _extract_intent_and_entities(self, message: str, context: UserContext) -> Dict[str, Any]:
        """Extract intent and entities from message."""
        try:
            # Use LLM intent extraction with context
            llm_context = f"""
            User: {context.user_id} (Role: {context.role})
            Team: {context.team_id}
            Chat: {context.chat_type}
            Previous interactions: {len(context.interaction_history)}
            Available actions: player_info, team_status, match_info, payment_info, registration, admin_actions
            """
            
            result = extract_intent(message, context=llm_context)
            
            # Map to our intent types
            intent_mapping = {
                "player_info": IntentType.PLAYER_INFO,
                "team_status": IntentType.TEAM_STATUS,
                "match_info": IntentType.MATCH_INFO,
                "payment_info": IntentType.PAYMENT_INFO,
                "registration": IntentType.REGISTRATION,
                "onboarding": IntentType.ONBOARDING,
                "admin_action": IntentType.ADMIN_ACTION,
                "personal_update": IntentType.PERSONAL_UPDATE,
                "general_query": IntentType.GENERAL_QUERY
            }
            
            intent = intent_mapping.get(result.get('intent', 'general_query'), IntentType.GENERAL_QUERY)
            confidence = result.get('confidence', 0.5)
            entities = result.get('entities', {})
            
            return {
                'intent': intent,
                'confidence': confidence,
                'entities': entities,
                'raw_result': result
            }
            
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return {
                'intent': IntentType.GENERAL_QUERY,
                'confidence': 0.3,
                'entities': {},
                'raw_result': {}
            }
    
    async def _generate_response(self, message: str, intent_result: Dict[str, Any], 
                               context: UserContext) -> NLResponse:
        """Generate personalized response based on intent and context."""
        intent = intent_result['intent']
        confidence = intent_result['confidence']
        entities = intent_result['entities']
        
        # Route to appropriate handler based on intent
        if intent == IntentType.PLAYER_INFO:
            return await self._handle_player_info(message, entities, context)
        elif intent == IntentType.TEAM_STATUS:
            return await self._handle_team_status(message, entities, context)
        elif intent == IntentType.MATCH_INFO:
            return await self._handle_match_info(message, entities, context)
        elif intent == IntentType.PAYMENT_INFO:
            return await self._handle_payment_info(message, entities, context)
        elif intent == IntentType.REGISTRATION:
            return await self._handle_registration(message, entities, context)
        elif intent == IntentType.ADMIN_ACTION:
            return await self._handle_admin_action(message, entities, context)
        elif intent == IntentType.PERSONAL_UPDATE:
            return await self._handle_personal_update(message, entities, context)
        else:
            return await self._handle_general_query(message, entities, context)
    
    async def _handle_player_info(self, message: str, entities: Dict[str, Any], 
                                 context: UserContext) -> NLResponse:
        """Handle player information requests."""
        try:
            if context.player:
                # User asking about themselves
                player = context.player
                response = f"""👤 <b>Your Player Information</b>

📋 <b>Name:</b> {player.name.upper()}
🆔 <b>Player ID:</b> {player.player_id.upper()}
📱 <b>Phone:</b> {player.phone}
⚽ <b>Position:</b> {player.position.value if hasattr(player.position, 'value') else player.position}
🏆 <b>FA Registered:</b> {'Yes' if player.is_fa_registered() else 'No'}
📊 <b>Status:</b> {player.get_display_status()}
⏰ <b>Last Activity:</b> {player.last_activity.strftime('%d/%m/%Y') if player.last_activity else 'N/A'}"""
                
                return NLResponse(
                    message=response,
                    intent=IntentType.PLAYER_INFO,
                    confidence=0.9
                )
            else:
                # User not registered as player
                return NLResponse(
                    message="❌ You're not registered as a player yet. Please contact your team admin to get registered.",
                    intent=IntentType.PLAYER_INFO,
                    confidence=0.8
                )
                
        except Exception as e:
            logger.error(f"Error handling player info: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't retrieve your player information. Please try again.",
                intent=IntentType.PLAYER_INFO,
                confidence=0.5
            )
    
    async def _handle_team_status(self, message: str, entities: Dict[str, Any], 
                                 context: UserContext) -> NLResponse:
        """Handle team status requests."""
        try:
            if not context.is_leadership:
                return NLResponse(
                    message="❌ Team status information is only available in the leadership chat.",
                    intent=IntentType.TEAM_STATUS,
                    confidence=0.8
                )
            
            # Get team statistics
            players = await self.player_service.get_team_players(self.team_id)
            active_players = [p for p in players if p.is_active()]
            pending_players = [p for p in players if p.is_pending_approval()]
            
            response = f"""📊 <b>Team Status Overview</b>

👥 <b>Total Players:</b> {len(players)}
✅ <b>Active Players:</b> {len(active_players)}
⏳ <b>Pending Players:</b> {len(pending_players)}
🏆 <b>FA Registered:</b> {len([p for p in players if p.is_fa_registered()])}

💡 <b>Quick Actions:</b>
• /list - View all players
• /status - Detailed status report
• /daily_status - Daily summary"""
            
            return NLResponse(
                message=response,
                intent=IntentType.TEAM_STATUS,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Error handling team status: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't retrieve team status. Please try again.",
                intent=IntentType.TEAM_STATUS,
                confidence=0.5
            )
    
    async def _handle_match_info(self, message: str, entities: Dict[str, Any], 
                                context: UserContext) -> NLResponse:
        """Handle match information requests."""
        try:
            # Get upcoming matches
            matches = await self.match_service.list_matches(self.team_id)
            upcoming_matches = [m for m in matches if m.status.value == 'scheduled'][:3]
            
            if upcoming_matches:
                response = "📅 <b>Upcoming Matches</b>\n\n"
                for match in upcoming_matches:
                    response += f"""⚽ <b>{match.opponent}</b>
📅 {match.date.strftime('%d/%m/%Y') if match.date else 'TBD'}
📍 {match.location or 'TBD'}
🏆 {match.competition or 'Friendly'}\n\n"""
            else:
                response = "📅 No upcoming matches scheduled."
            
            response += "\n💡 <b>Quick Actions:</b>\n• /matches - View all matches\n• /create_match - Schedule new match"
            
            return NLResponse(
                message=response,
                intent=IntentType.MATCH_INFO,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Error handling match info: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't retrieve match information. Please try again.",
                intent=IntentType.MATCH_INFO,
                confidence=0.5
            )
    
    async def _handle_payment_info(self, message: str, entities: Dict[str, Any], 
                                  context: UserContext) -> NLResponse:
        """Handle payment information requests."""
        try:
            if not context.player:
                return NLResponse(
                    message="❌ You need to be registered as a player to view payment information.",
                    intent=IntentType.PAYMENT_INFO,
                    confidence=0.8
                )
            
            # Get payment information
            payments = await self.payment_service.get_player_payments(context.player.id)
            pending_payments = [p for p in payments if p.status.value == 'pending']
            paid_payments = [p for p in payments if p.status.value == 'paid']
            
            response = f"""💰 <b>Your Payment Information</b>

📊 <b>Summary:</b>
• Total Payments: {len(payments)}
• Pending: {len(pending_payments)}
• Paid: {len(paid_payments)}

💡 <b>Quick Actions:</b>
• /payments - View all payments
• /payment_status - Check specific payment
• /financial_dashboard - Full financial overview"""
            
            return NLResponse(
                message=response,
                intent=IntentType.PAYMENT_INFO,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Error handling payment info: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't retrieve payment information. Please try again.",
                intent=IntentType.PAYMENT_INFO,
                confidence=0.5
            )
    
    async def _handle_registration(self, message: str, entities: Dict[str, Any], 
                                  context: UserContext) -> NLResponse:
        """Handle registration requests."""
        try:
            if context.player:
                return NLResponse(
                    message="✅ You're already registered as a player!",
                    intent=IntentType.REGISTRATION,
                    confidence=0.9
                )
            
            response = """📝 <b>Player Registration</b>

To register as a player, please contact your team admin or use the following command:

/register [name] [phone] [position]

<b>Example:</b>
/register John Smith 07123456789 midfielder

<b>Available Positions:</b>
• goalkeeper
• defender  
• midfielder
• forward
• striker
• utility"""
            
            return NLResponse(
                message=response,
                intent=IntentType.REGISTRATION,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Error handling registration: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't process your registration request. Please try again.",
                intent=IntentType.REGISTRATION,
                confidence=0.5
            )
    
    async def _handle_admin_action(self, message: str, entities: Dict[str, Any], 
                                  context: UserContext) -> NLResponse:
        """Handle admin action requests."""
        try:
            if not context.is_leadership:
                return NLResponse(
                    message="❌ Admin actions are only available in the leadership chat.",
                    intent=IntentType.ADMIN_ACTION,
                    confidence=0.8
                )
            
            response = """🔧 <b>Admin Actions Available</b>

<b>Player Management:</b>
• /add [name] [phone] [position] - Add new player
• /remove [phone] - Remove player
• /approve [player_id] - Approve player
• /reject [player_id] - Reject player

<b>Team Management:</b>
• /list - View all players
• /status - Team status
• /daily_status - Daily report

<b>Match Management:</b>
• /create_match - Schedule match
• /matches - View matches
• /record_result - Record match result

<b>Financial Management:</b>
• /create_payment - Create payment request
• /payments - View payments
• /financial_dashboard - Financial overview"""
            
            return NLResponse(
                message=response,
                intent=IntentType.ADMIN_ACTION,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Error handling admin action: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't process your admin request. Please try again.",
                intent=IntentType.ADMIN_ACTION,
                confidence=0.5
            )
    
    async def _handle_personal_update(self, message: str, entities: Dict[str, Any], 
                                     context: UserContext) -> NLResponse:
        """Handle personal update requests."""
        try:
            if not context.player:
                return NLResponse(
                    message="❌ You need to be registered as a player to update your information.",
                    intent=IntentType.PERSONAL_UPDATE,
                    confidence=0.8
                )
            
            response = """📝 <b>Personal Information Update</b>

You can update your information using natural language or commands:

<b>Examples:</b>
• "Update my phone number to 07123456789"
• "Change my position to midfielder"
• "Update my emergency contact"

<b>Or use commands:</b>
• /update_phone [new_number]
• /update_position [new_position]
• /update_emergency_contact [contact]"""
            
            return NLResponse(
                message=response,
                intent=IntentType.PERSONAL_UPDATE,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Error handling personal update: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't process your update request. Please try again.",
                intent=IntentType.PERSONAL_UPDATE,
                confidence=0.5
            )
    
    async def _handle_general_query(self, message: str, entities: Dict[str, Any], 
                                   context: UserContext) -> NLResponse:
        """Handle general queries."""
        try:
            response = f"""🤖 <b>How can I help you?</b>

I'm your AI assistant for {context.team.name if context.team else 'your team'}!

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
            
            return NLResponse(
                message=response,
                intent=IntentType.GENERAL_QUERY,
                confidence=0.7
            )
            
        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return NLResponse(
                message="❌ Sorry, I couldn't understand your request. Please try again or use /help for available commands.",
                intent=IntentType.GENERAL_QUERY,
                confidence=0.3
            )
    
    def _update_interaction_history(self, context: UserContext, message: str):
        """Update user's interaction history for personalization."""
        context.interaction_history.append({
            'timestamp': datetime.now(),
            'message': message,
            'chat_type': context.chat_type
        })
        
        # Keep only last 50 interactions
        if len(context.interaction_history) > 50:
            context.interaction_history = context.interaction_history[-50:]
    
    def _update_user_preferences(self, context: UserContext, intent_result: Dict[str, Any], 
                                response: NLResponse):
        """Update user preferences based on interaction."""
        intent = intent_result['intent']
        
        # Track preferred topics
        if 'preferred_topics' not in context.preferences:
            context.preferences['preferred_topics'] = {}
        
        topic = intent.value
        context.preferences['preferred_topics'][topic] = context.preferences['preferred_topics'].get(topic, 0) + 1
    
    def _get_fallback_response(self, message: str, user_role: str) -> str:
        """Get fallback response when processing fails."""
        return f"""🤖 <b>I'm here to help!</b>

I'm your AI assistant for team management. I can help with:

<b>For Players:</b>
• Check your status and information
• View upcoming matches
• Check payment information
• Update your details

<b>For Leadership:</b>
• Manage team members
• Schedule matches
• Handle payments
• Generate reports

<b>Try asking me:</b>
• "What's my player status?"
• "Show me upcoming matches"
• "How many players do we have?"

Or use /help to see all available commands!"""


# Global instance
_nl_handler: Optional[NaturalLanguageHandler] = None


def get_natural_language_handler(team_id: str) -> NaturalLanguageHandler:
    """Get the global natural language handler."""
    global _nl_handler
    if _nl_handler is None or _nl_handler.team_id != team_id:
        _nl_handler = NaturalLanguageHandler(team_id)
    return _nl_handler 