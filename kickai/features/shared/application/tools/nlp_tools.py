#!/usr/bin/env python3
"""
NLP Tools - Clean Architecture Application Layer

This module provides CrewAI tools for Natural Language Processing functionality.
These tools serve as the application boundary and delegate to the NLP processor agent.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Optional
from crewai.tools import tool
from loguru import logger

from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response


@tool("advanced_intent_recognition", result_as_answer=True)
def advanced_intent_recognition(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    conversation_history: str = ""
) -> str:
    """
    LLM-powered intent recognition using CrewAI native reasoning.
    
    This tool serves as the application boundary for intent recognition functionality.
    It handles framework concerns and delegates to the NLP processor service.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user  
        chat_type: Chat context (main/leadership/private)
        message: User message to analyze
        conversation_history: Previous conversation context
        
    Returns:
        JSON response string with LLM-analyzed intent classification
    """
    try:
        logger.info(f"🔧 [NLP_INTENT] Processing intent recognition for {username}: {message[:50]}")
        
        # Import the NLP processor domain function dynamically to avoid circular imports
        from kickai.agents.nlp_processor import advanced_intent_recognition_domain as nlp_intent_recognition
        
        # Execute NLP processing (synchronous)
        result = nlp_intent_recognition(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            message=message,
            conversation_history=conversation_history
        )
        
        logger.info(f"✅ [NLP_INTENT] Intent recognition completed for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [NLP_INTENT] Error in intent recognition: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message="Unable to analyze intent. Please try rephrasing your request."
        )


@tool("routing_recommendation_tool", result_as_answer=True)
async def routing_recommendation_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    intent_data: str
) -> str:
    """
    CrewAI-native intelligent routing recommendations using LLM-powered analysis.
    
    This tool provides structured context for the NLP_PROCESSOR agent's LLM to make
    intelligent routing decisions. Follows CrewAI best practices by letting the LLM
    analyze and decide rather than pre-determining outcomes.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        intent_data: Intent analysis data (user message/command)
        
    Returns:
        Structured prompt for LLM analysis and routing decision
    """
    try:
        logger.info(f"🔧 [NLP_ROUTING] Generating LLM routing context for {username}: {intent_data}")
        
        # Import the NLP processor domain function dynamically
        from kickai.agents.nlp_processor import routing_recommendation_domain as nlp_routing_tool
        
        # Execute NLP processing (async) - returns structured prompt for LLM analysis
        routing_context = await nlp_routing_tool(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            intent_data=intent_data
        )
        
        logger.info(f"✅ [NLP_ROUTING] LLM routing context generated for {username}")
        return routing_context
        
    except Exception as e:
        logger.error(f"❌ [NLP_ROUTING] Error in routing context generation: {e}")
        # Return fallback routing context for LLM analysis
        fallback_context = f"""
KICKAI Emergency Routing Analysis

REQUEST: {intent_data}
CHAT TYPE: {chat_type}
USER: {username}

ERROR: {str(e)}

AVAILABLE AGENTS:
• message_processor: General communication and system operations
• help_assistant: Help system and guidance
• player_coordinator: Player management and personal information

EMERGENCY ROUTING DECISION:
Due to system error, analyze this request and route to the most appropriate agent.
For safety, consider message_processor as the fallback option.

RESPONSE FORMAT:
AGENT_RECOMMENDATION: [agent_name]

Analysis:
- Error Encountered: {str(e)}
- Safe Routing: Analyze user intent and route accordingly
- Confidence: [1-10]/10
- Reasoning: [your emergency routing decision]
"""
        return fallback_context


@tool("analyze_update_context", result_as_answer=True)
def analyze_update_context(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str
) -> str:
    """
    LLM-powered update context analysis for intelligent routing.
    
    This tool serves as the application boundary for update context analysis.
    It handles framework concerns and delegates to the NLP processor service.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        message: Update command message to analyze
        
    Returns:
        JSON response with LLM-based update context analysis
    """
    try:
        logger.info(f"🔧 [NLP_UPDATE] Processing update context analysis for {username}")
        
        # Import the NLP processor domain function dynamically
        from kickai.agents.nlp_processor import analyze_update_context_domain as nlp_analyze_update
        
        # Execute NLP processing (synchronous)
        result = nlp_analyze_update(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            message=message
        )
        
        logger.info(f"✅ [NLP_UPDATE] Update context analysis completed for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [NLP_UPDATE] Error in update context analysis: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message="Unable to analyze update context. Please specify the update clearly."
        )


@tool("validate_routing_permissions", result_as_answer=True)
def validate_routing_permissions(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    user_role: str,
    requested_action: str
) -> str:
    """
    LLM-powered permission validation for intelligent routing.
    
    This tool serves as the application boundary for permission validation.
    It handles framework concerns and delegates to the NLP processor service.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        user_role: User's role in the system
        requested_action: Action the user is trying to perform
        
    Returns:
        JSON response with LLM-based permission validation
    """
    try:
        logger.info(f"🔧 [NLP_PERM] Processing permission validation for {username}, action: {requested_action}")
        
        # Import the NLP processor domain function dynamically
        from kickai.agents.nlp_processor import validate_routing_permissions_domain as nlp_validate_permissions
        
        # Execute NLP processing (synchronous)
        result = nlp_validate_permissions(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            user_role=user_role,
            requested_action=requested_action
        )
        
        logger.info(f"✅ [NLP_PERM] Permission validation completed for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [NLP_PERM] Error in permission validation: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message="Unable to validate permissions. Please contact team leadership."
        )


@tool("entity_extraction_tool", result_as_answer=True)
def entity_extraction_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str
) -> str:
    """
    LLM-powered entity extraction for natural language understanding.
    
    This tool serves as the application boundary for entity extraction functionality.
    It handles framework concerns and delegates to the NLP processor service.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        message: Message text to extract entities from
        
    Returns:
        JSON response with LLM-extracted entities and their types
    """
    try:
        logger.info(f"🔧 [NLP_ENTITY] Processing entity extraction for {username}: {message[:50]}")
        
        # Import the NLP processor domain function dynamically to avoid circular imports
        from kickai.agents.nlp_processor import entity_extraction_domain as nlp_entity_extraction
        
        # Execute NLP processing (synchronous)
        result = nlp_entity_extraction(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            message=message
        )
        
        logger.info(f"✅ [NLP_ENTITY] Entity extraction completed for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [NLP_ENTITY] Error in entity extraction: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message="Unable to extract entities from message."
        )


@tool("conversation_context_tool", result_as_answer=True)
def conversation_context_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """
    LLM-powered conversation context analysis for enhanced understanding.
    
    This tool serves as the application boundary for conversation context functionality.
    It handles framework concerns and delegates to the NLP processor service.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        
    Returns:
        JSON response with LLM-analyzed conversation context
    """
    try:
        logger.info(f"🔧 [NLP_CONTEXT] Processing conversation context for {username}")
        
        # Import the NLP processor domain function dynamically to avoid circular imports
        from kickai.agents.nlp_processor import conversation_context_domain as nlp_conversation_context
        
        # Execute NLP processing (synchronous)
        result = nlp_conversation_context(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type
        )
        
        logger.info(f"✅ [NLP_CONTEXT] Conversation context analysis completed for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [NLP_CONTEXT] Error in conversation context analysis: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message="Unable to analyze conversation context."
        )


@tool("semantic_similarity_tool", result_as_answer=True)
def semantic_similarity_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str
) -> str:
    """
    LLM-powered semantic similarity analysis for intelligent routing.
    
    This tool serves as the application boundary for semantic similarity functionality.
    It handles framework concerns and delegates to the NLP processor service.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        message: Message to analyze for semantic similarity
        
    Returns:
        JSON response with LLM-based semantic similarity analysis
    """
    try:
        logger.info(f"🔧 [NLP_SEMANTIC] Processing semantic similarity for {username}: {message[:50]}")
        
        # Import the NLP processor domain function dynamically to avoid circular imports
        from kickai.agents.nlp_processor import semantic_similarity_domain as nlp_semantic_similarity
        
        # Execute NLP processing (synchronous)
        result = nlp_semantic_similarity(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            message=message
        )
        
        logger.info(f"✅ [NLP_SEMANTIC] Semantic similarity analysis completed for {username}")
        return result
        
    except Exception as e:
        logger.error(f"❌ [NLP_SEMANTIC] Error in semantic similarity analysis: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message="Unable to analyze semantic similarity."
        )