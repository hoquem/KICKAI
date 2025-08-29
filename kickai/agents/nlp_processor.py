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


# REMOVED: classify_user_intent function - using native CrewAI routing now
# This function used hardcoded keyword matching which goes against CrewAI best practices


async def routing_recommendation_domain(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    intent_data: str,
    **kwargs
) -> str:
    """
    Provides context analysis for MESSAGE_PROCESSOR's native CrewAI routing decisions.
    
    NO HARDCODED ROUTING PATTERNS - this tool provides analysis only.
    The actual routing decision is made by MESSAGE_PROCESSOR's LLM intelligence.
    
    Args:
        telegram_id: User ID for context
        team_id: Team identifier for context
        username: Username for context 
        chat_type: Chat context (main/leadership/private)
        intent_data: The user's request/message to analyze
        **kwargs: Additional parameters
        
    Returns:
        JSON response with request analysis (NOT routing decision)
    """
    try:
        # Minimal validation with defaults
        user_id = telegram_id if isinstance(telegram_id, int) and telegram_id > 0 else 0
        team = team_id if team_id and isinstance(team_id, str) else "UNKNOWN"
        user = username if username and isinstance(username, str) else "unknown_user"
        chat = chat_type if chat_type and isinstance(chat_type, str) else "main"
        request = intent_data if intent_data and isinstance(intent_data, str) else "No request provided"
        
        logger.info(f"🧠 [NLP_DOMAIN] Providing analysis for: '{request[:30]}...'")
        
        # Log execution with minimal overhead
        log_tool_execution("routing_recommendation_domain", 
                         {'team_id': team, 'request_length': len(request)}, True)
        
        # Provide pure analysis without routing decision
        analysis = {
            "request": request,
            "context": {
                "user": user,
                "chat_type": chat,
                "team_id": team
            },
            "analysis_note": "Use your LLM intelligence to understand intent and route appropriately",
            "guidance": "Consider the user's actual intent, not keywords. Route to specialist agents when appropriate."
        }
        
        logger.info(f"🎯 [NLP_DOMAIN] Analysis provided for: '{request[:30]}...'")
        
        # Return analysis in format that encourages LLM-based decisions
        return create_json_response(ResponseStatus.SUCCESS, data=analysis)
        
    except Exception as e:
        logger.error(f"❌ [NLP_DOMAIN] Error in routing analysis: {e}")
        return create_json_response(
            ResponseStatus.ERROR, 
            message=f"Analysis failed: {str(e)}"
        )


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