#!/usr/bin/env python3
"""
NLP Processor Agent

This module implements a specialized Natural Language Processing agent for the KICKAI system.
It provides advanced intent recognition, entity extraction, and conversation context management
for natural language understanding and routing enhancement.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from functools import lru_cache

from loguru import logger
from crewai.tools import tool

from kickai.agents.configurable_agent import ConfigurableAgent
from kickai.agents.prompts.nlp_prompts import render_prompt, validate_prompt_context
from kickai.core.enums import AgentRole, ResponseStatus
from kickai.core.exceptions import AgentInitializationError, InputValidationError, AgentExecutionError
from kickai.utils.tool_validation import validate_team_id, validate_telegram_id, ToolValidationError
from kickai.utils.tool_helpers import create_json_response
from kickai.utils.tool_validation import log_tool_execution
from kickai.core.dependency_container import get_container


@dataclass
class IntentResult:
    """
    Structured result for intent recognition with comprehensive analysis.
    
    This dataclass encapsulates all aspects of natural language understanding
    including intent classification, entity extraction, and routing recommendations.
    
    Attributes:
        primary_intent: The main identified intent
        secondary_intents: Additional intents if multi-intent detected
        confidence: Confidence score (0.0-1.0)
        entities: Extracted entities with their types and values
        conversation_context: Context from previous conversation turns
        routing_recommendation: Recommended agent and routing priority
        requires_followup: Whether response requires follow-up questions
        reasoning: Explanation of the classification decision
        original_message: Original user message for reference
    """
    primary_intent: str
    secondary_intents: List[str] = field(default_factory=list)
    confidence: float = 0.0
    entities: Dict[str, Any] = field(default_factory=dict)
    conversation_context: Dict[str, Any] = field(default_factory=dict)
    routing_recommendation: Dict[str, Any] = field(default_factory=dict)
    requires_followup: bool = False
    reasoning: str = ""
    original_message: str = ""


class NLPProcessor(ConfigurableAgent):
    """
    Specialized Natural Language Processing agent for KICKAI system.
    
    Provides advanced intent recognition, entity extraction, and conversation
    context management for natural language understanding and routing enhancement.
    
    This agent follows KICKAI coding standards with single try/except boundaries,
    comprehensive type hints, and proper error handling throughout.
    
    The NLP processor uses LLM-powered analysis rather than pattern matching,
    delegating all intent recognition and entity extraction to the CrewAI agent's
    specialized language model.
    
    Attributes:
        team_id: Team identifier for context
        
    Example:
        >>> nlp_processor = NLPProcessor("KTI")
        >>> # Tools are called by the CrewAI agent, not directly
    """
    
    def __init__(self, team_id: str):
        """
        Initialize NLP processor agent following KICKAI coding standards.
        
        Args:
            team_id: Team identifier for context and memory
            
        Raises:
            InputValidationError: When team_id is invalid
            AgentInitializationError: When agent setup fails
            
        Example:
            >>> processor = NLPProcessor("KTI")
        """
        try:
            # Validate inputs using utility functions
            team_id = validate_team_id(team_id)
            
            # Initialize base agent with NLP-specific configuration
            super().__init__(
                agent_role=AgentRole.NLP_PROCESSOR,
                team_id=team_id
            )
            
            # NLP processor uses LLM-powered analysis, not pattern matching
            
            logger.info(f"✅ NLP Processor initialized for team: {team_id}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing NLP Processor: {e}")
            raise AgentInitializationError("NLP_PROCESSOR", f"Initialization failed: {str(e)}")


def _handle_tool_error(tool_name: str, error: Exception, error_type: str = "unexpected") -> str:
    """
    Standardized error handling for all NLP tools.
    
    Args:
        tool_name: Name of the tool for logging
        error: The exception that occurred
        error_type: Type of error for specific handling
        
    Returns:
        JSON error response string
    """
    if isinstance(error, ToolValidationError):
        logger.warning(f"⚠️ Validation error in {tool_name}: {error}")
        return create_json_response(ResponseStatus.ERROR, message=f"Invalid input for {tool_name}: {error}")
    elif isinstance(error, AgentExecutionError):
        logger.error(f"❌ Agent execution error in {tool_name}: {error}")
        return create_json_response(ResponseStatus.ERROR, message=f"Execution failed during {tool_name}: {error}")
    elif isinstance(error, InputValidationError):
        logger.warning(f"⚠️ Input validation error in {tool_name}: {error}")
        return create_json_response(ResponseStatus.ERROR, message=f"Input validation failed for {tool_name}: {error}")
    else:
        logger.error(f"❌ Unexpected error in {tool_name}: {error}", exc_info=True)
        return create_json_response(ResponseStatus.ERROR, message=f"An unexpected internal error occurred during {tool_name}")


async def advanced_intent_recognition_domain(
    telegram_id: int,
    team_id: str, 
    username: str,
    chat_type: str,
    message: str,
    conversation_history: str = "",
    **kwargs
) -> str:
    """
    LLM-powered intent recognition using CrewAI native reasoning.
    
    Uses the specialized NLP LLM to analyze user intent, extract entities,
    and provide intelligent routing recommendations. Uses the centralized
    prompt template system for consistent, maintainable prompts.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user  
        chat_type: Chat context (main/leadership/private)
        message: User message to analyze
        conversation_history: Previous conversation context
        **kwargs: Additional context parameters
        
    Returns:
        JSON response string with LLM-analyzed intent classification
        
    Note:
        This tool uses the prompt template system for consistent,
        type-safe prompt generation with validation.
    """
    try:
        # Input validation using utility functions
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        # Validate message input
        from kickai.utils.tool_validation import validate_string_input
        validate_string_input(message, "Message", allow_empty=False)
        validate_string_input(username, "Username", allow_empty=False)
        validate_string_input(chat_type, "Chat type", allow_empty=False)
        
        # Log tool execution with performance tracking
        inputs = {
            'team_id': team_id,
            'telegram_id': telegram_id_int,
            'message_length': len(message),
            'has_history': bool(conversation_history)
        }
        log_tool_execution("advanced_intent_recognition", inputs, True)
        
        # Prepare context for template rendering
        context = {
            'telegram_id': telegram_id_int,
            'team_id': team_id,
            'username': username,
            'chat_type': chat_type,
            'message': message,
            'conversation_history': conversation_history or "None"
        }
        
        # Validate context before rendering
        if not validate_prompt_context('intent_recognition', context):
            return create_json_response(ResponseStatus.ERROR, message="Invalid context for intent recognition")
        
        # Render prompt using template system
        analysis_prompt = render_prompt('intent_recognition', context)
        
        return create_json_response(ResponseStatus.SUCCESS, data={"analysis_prompt": analysis_prompt})
        
    except Exception as e:
        return _handle_tool_error("advanced_intent_recognition", e)


async def entity_extraction_domain(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    **kwargs
) -> str:
    """
    LLM-powered entity extraction for football team management.
    
    Uses the specialized NLP LLM to extract entities like player names,
    positions, time references, and football-specific information.
    Uses the centralized prompt template system.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context
        message: Message to extract entities from
        **kwargs: Additional parameters
        
    Returns:
        JSON response with LLM-extracted entities
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        from kickai.utils.tool_validation import validate_string_input
        validate_string_input(message, "Message", allow_empty=False)
        validate_string_input(username, "Username", allow_empty=False)
        validate_string_input(chat_type, "Chat type", allow_empty=False)
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("entity_extraction_tool", inputs, True)
        
        # Prepare context for template rendering
        context = {
            'telegram_id': telegram_id_int,
            'team_id': team_id,
            'username': username,
            'chat_type': chat_type,
            'message': message
        }
        
        # Validate and render prompt using template system
        if not validate_prompt_context('entity_extraction', context):
            return create_json_response(ResponseStatus.ERROR, message="Invalid context for entity extraction")
        
        extraction_prompt = render_prompt('entity_extraction', context)
        
        return create_json_response(ResponseStatus.SUCCESS, data={"extraction_prompt": extraction_prompt})
        
    except Exception as e:
        return _handle_tool_error("entity_extraction_tool", e)


async def conversation_context_domain(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    **kwargs
) -> str:
    """
    LLM-powered conversation context analysis.
    
    Uses the NLP LLM to analyze conversation context and provide
    intelligent context-aware responses for multi-turn conversations.
    Uses the centralized prompt template system.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context
        **kwargs: Additional parameters
        
    Returns:
        JSON response with context analysis prompt for LLM
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        from kickai.utils.tool_validation import validate_string_input
        validate_string_input(username, "Username", allow_empty=False)
        validate_string_input(chat_type, "Chat type", allow_empty=False)
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("conversation_context_tool", inputs, True)
        
        # Prepare context for template rendering
        context = {
            'telegram_id': telegram_id_int,
            'team_id': team_id,
            'username': username,
            'chat_type': chat_type
        }
        
        # Validate and render prompt using template system
        if not validate_prompt_context('conversation_context', context):
            return create_json_response(ResponseStatus.ERROR, message="Invalid context for conversation analysis")
        
        context_prompt = render_prompt('conversation_context', context)
        
        return create_json_response(ResponseStatus.SUCCESS, data={"context_prompt": context_prompt})
        
    except Exception as e:
        return _handle_tool_error("conversation_context_tool", e)


async def semantic_similarity_domain(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    reference_commands: str = "",
    **kwargs
) -> str:
    """
    LLM-powered semantic similarity analysis for command suggestions.
    
    Uses the NLP LLM to understand semantic relationships between
    user messages and available commands. Uses the centralized
    prompt template system.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context
        message: User message to analyze
        reference_commands: Commands to compare against (comma-separated)
        **kwargs: Additional parameters
        
    Returns:
        JSON response with LLM-based similarity analysis
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        from kickai.utils.tool_validation import validate_string_input
        validate_string_input(message, "Message", allow_empty=False)
        validate_string_input(username, "Username", allow_empty=False)
        validate_string_input(chat_type, "Chat type", allow_empty=False)
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("semantic_similarity_tool", inputs, True)
        
        # Default commands if none provided
        if not reference_commands:
            reference_commands = "/help,/info,/status,/list,/matches,/availability,/addplayer,/update"
        
        # Prepare context for template rendering
        context = {
            'telegram_id': telegram_id_int,
            'team_id': team_id,
            'username': username,
            'chat_type': chat_type,
            'message': message,
            'reference_commands': reference_commands
        }
        
        # Validate and render prompt using template system
        if not validate_prompt_context('semantic_similarity', context):
            return create_json_response(ResponseStatus.ERROR, message="Invalid context for similarity analysis")
        
        similarity_prompt = render_prompt('semantic_similarity', context)
        
        return create_json_response(ResponseStatus.SUCCESS, data={"similarity_prompt": similarity_prompt})
        
    except Exception as e:
        return _handle_tool_error("semantic_similarity_tool", e)


async def routing_recommendation_domain(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    intent_data: str,
    **kwargs
) -> str:
    """
    CrewAI-native intelligent routing recommendations using LLM-powered analysis.
    
    Provides structured context for the NLP_PROCESSOR agent's LLM to make intelligent
    routing decisions based on user intent, context, and available agent capabilities.
    This follows CrewAI best practices by letting the LLM make the decisions.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        intent_data: Intent analysis data (user message/command)
        **kwargs: Additional parameters
        
    Returns:
        Structured prompt for LLM analysis and routing decision
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        from kickai.utils.tool_validation import validate_string_input
        validate_string_input(intent_data, "Intent data", allow_empty=False)
        validate_string_input(username, "Username", allow_empty=False)
        validate_string_input(chat_type, "Chat type", allow_empty=False)
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int, 'intent_data': intent_data[:50]}
        log_tool_execution("routing_recommendation_tool", inputs, True)
        
        # Extract command and message components for context
        message = intent_data.strip()
        command = None
        if message.startswith('/'):
            command_parts = message.split()
            command = command_parts[0] if command_parts else message
        
        # Prepare comprehensive routing context for LLM analysis
        routing_context = {
            'user_request': intent_data,
            'extracted_command': command,
            'chat_context': chat_type,
            'user_info': {
                'username': username,
                'telegram_id': telegram_id_int,
                'team_id': team_id
            },
            'available_agents': {
                'help_assistant': {
                    'description': 'Help system and guidance for users',
                    'capabilities': ['command help', 'system guidance', 'user onboarding'],
                    'best_for': 'questions, help requests, guidance needs'
                },
                'player_coordinator': {
                    'description': 'Player management and personal information',
                    'capabilities': ['player status', 'personal info updates', 'player coordination'],
                    'best_for': 'personal player operations, status queries, individual updates'
                },
                'team_administrator': {
                    'description': 'Team member management and administration',
                    'capabilities': ['team member management', 'administrative tasks', 'team operations'],
                    'best_for': 'administrative operations, team member management, leadership tasks'
                },
                'squad_selector': {
                    'description': 'Squad selection and match management',
                    'capabilities': ['match operations', 'squad selection', 'availability tracking'],
                    'best_for': 'match-related tasks, squad operations, availability management'
                },
                'message_processor': {
                    'description': 'General communication and system operations',
                    'capabilities': ['general messaging', 'system info', 'basic operations'],
                    'best_for': 'general queries, system information, basic communication'
                }
            },
            'context_factors': {
                'chat_type_analysis': {
                    'main': 'General team communication - typically player-focused operations',
                    'leadership': 'Administrative context - typically management operations',
                    'private': 'Personal queries - typically individual assistance'
                },
                'current_chat_context': chat_type,
                'routing_patterns': {
                    '/update_patterns': {
                        'main_chat': 'Usually personal player information updates',
                        'leadership_chat': 'Usually administrative team member updates',
                        'private_chat': 'Personal assistance and individual updates'
                    }
                }
            },
            'decision_framework': {
                'primary_factors': [
                    'User intent and request type',
                    'Chat context and permissions', 
                    'Agent specialization match',
                    'Historical routing patterns'
                ],
                'confidence_guidelines': {
                    'high_confidence_9_10': 'Clear command match with agent specialization',
                    'medium_confidence_7_8': 'Good intent match with some context consideration',
                    'low_confidence_5_6': 'Unclear intent requiring safe fallback routing'
                }
            }
        }
        
        # Generate structured prompt for LLM routing analysis
        routing_prompt = f"""
KICKAI Intelligent Routing Analysis

REQUEST ANALYSIS:
User Request: "{intent_data}"
Command: {command or 'No specific command'}
Chat Type: {chat_type}
User: {username} (ID: {telegram_id_int})

AVAILABLE AGENTS:
{_format_agent_capabilities(routing_context['available_agents'])}

CONTEXT CONSIDERATIONS:
- Chat Type: {chat_type} ({routing_context['context_factors']['chat_type_analysis'].get(chat_type, 'Unknown context')})
- User Intent: Analyze the user's actual intent from their message
- Agent Specialization: Match intent to agent capabilities
- Context Appropriateness: Consider chat type and permissions

ROUTING DECISION FRAMEWORK:
1. Analyze the user's primary intent
2. Consider the chat context and any permission implications
3. Match intent to the most specialized agent
4. Provide confidence level (1-10) based on match quality
5. Include reasoning for the routing decision

SPECIAL ROUTING PATTERNS:
- /update commands: Context-sensitive routing
  * Main chat: Usually player-focused (player_coordinator)
  * Leadership chat: Usually admin-focused (team_administrator)
  * Private chat: Usually personal assistance (player_coordinator)

RESPONSE FORMAT:
Provide your routing recommendation as JSON:

{{
  "agent": "agent_name",
  "confidence": 0.9,
  "intent": "primary_intent_classification",
  "reasoning": "Brief explanation for the routing decision"
}}
"""
        
        logger.info(f"🧠 [NLP_ROUTING] Generated LLM routing context for '{intent_data[:30]}...' in {chat_type} chat")
        
        return routing_prompt
        
    except Exception as e:
        return _handle_tool_error("routing_recommendation_tool", e)


def _format_agent_capabilities(agents_dict: dict) -> str:
    """Format agent capabilities for LLM consumption."""
    formatted = []
    for agent_name, agent_info in agents_dict.items():
        capabilities = ", ".join(agent_info['capabilities'])
        formatted.append(f"• {agent_name}: {agent_info['description']}")
        formatted.append(f"  Capabilities: {capabilities}")
        formatted.append(f"  Best for: {agent_info['best_for']}")
        formatted.append("")
    return "\n".join(formatted)


async def analyze_update_context_domain(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    **kwargs
) -> str:
    """
    LLM-powered update context analysis for intelligent routing.
    
    Uses the NLP LLM to determine whether update commands should target
    player records or team member records. Uses the centralized
    prompt template system.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        message: Update command message to analyze
        **kwargs: Additional parameters
        
    Returns:
        JSON response with LLM-based update context analysis
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        from kickai.utils.tool_validation import validate_string_input
        validate_string_input(message, "Message", allow_empty=False)
        validate_string_input(username, "Username", allow_empty=False)
        validate_string_input(chat_type, "Chat type", allow_empty=False)
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int, 'chat_type': chat_type}
        log_tool_execution("analyze_update_context", inputs, True)
        
        # Prepare context for template rendering
        context = {
            'telegram_id': telegram_id_int,
            'team_id': team_id,
            'username': username,
            'chat_type': chat_type,
            'message': message
        }
        
        # Validate and render prompt using template system
        if not validate_prompt_context('update_context', context):
            return create_json_response(ResponseStatus.ERROR, message="Invalid context for update analysis")
        
        update_prompt = render_prompt('update_context', context)
        
        return create_json_response(ResponseStatus.SUCCESS, data={"update_prompt": update_prompt})
        
    except Exception as e:
        return _handle_tool_error("analyze_update_context", e)


async def validate_routing_permissions_domain(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    user_role: str,
    requested_action: str,
    **kwargs
) -> str:
    """
    LLM-powered permission validation for intelligent routing.
    
    Uses the NLP LLM to analyze permissions and context to determine
    if routing decisions respect security and access control requirements.
    Uses the centralized prompt template system.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        user_role: User's role in the system
        requested_action: Action the user is trying to perform
        **kwargs: Additional parameters
        
    Returns:
        JSON response with LLM-based permission validation
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        from kickai.utils.tool_validation import validate_string_input
        validate_string_input(requested_action, "Requested action", allow_empty=False)
        validate_string_input(username, "Username", allow_empty=False)
        validate_string_input(chat_type, "Chat type", allow_empty=False)
        validate_string_input(user_role, "User role", allow_empty=False)
        
        # Log tool execution
        inputs = {
            'team_id': team_id, 
            'telegram_id': telegram_id_int, 
            'chat_type': chat_type,
            'requested_action': requested_action
        }
        log_tool_execution("validate_routing_permissions", inputs, True)
        
        # Prepare context for template rendering
        context = {
            'telegram_id': telegram_id_int,
            'team_id': team_id,
            'username': username,
            'chat_type': chat_type,
            'user_role': user_role,
            'requested_action': requested_action
        }
        
        # Validate and render prompt using template system
        if not validate_prompt_context('permission_validation', context):
            return create_json_response(ResponseStatus.ERROR, message="Invalid context for permission validation")
        
        permission_prompt = render_prompt('permission_validation', context)
        
        return create_json_response(ResponseStatus.SUCCESS, data={"permission_prompt": permission_prompt})
        
    except Exception as e:
        return _handle_tool_error("validate_routing_permissions", e)