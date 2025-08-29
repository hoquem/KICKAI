#!/usr/bin/env python3
"""
NLP Tools - Clean Architecture Application Layer [DEPRECATED]

DEPRECATED: These NLP tools are no longer needed after migration to native CrewAI routing.
The MESSAGE_PROCESSOR agent now handles intent understanding natively using CrewAI's LLM intelligence.

This module provided CrewAI tools for Natural Language Processing functionality.
All framework dependencies (@tool decorators, container access) are confined to this layer.
"""

from typing import Optional
from crewai.tools import tool
from loguru import logger

from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response


@tool("advanced_intent_recognition", result_as_answer=True)
async def advanced_intent_recognition(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    conversation_history: str = ""
) -> str:
    """
    Intent recognition and routing analysis using intent-based classification.
    
    This tool analyzes user messages and returns concrete agent routing decisions
    with intent classification and confidence scores.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user  
        chat_type: Chat context (main/leadership/private)
        message: User message to analyze
        conversation_history: Previous conversation context (optional)
        
    Returns:
        JSON response with routing decision: {"agent": "name", "confidence": 0.9, "intent": "type", "reasoning": "explanation"}
    """
    try:
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            message = params.get('message', '')
            conversation_history = params.get('conversation_history', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
            
        if not message or not isinstance(message, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid message is required"
            )
        
        logger.info(f"🔧 [NLP_INTENT] Processing intent recognition for {username}: {message[:50]}")
        
        # Import the actual routing decision function
        from kickai.agents.nlp_processor import routing_recommendation_domain
        
        # Execute NLP routing analysis (async) - use message as intent_data
        result = await routing_recommendation_domain(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            intent_data=message
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
    CrewAI-native intelligent routing recommendations using intent-based analysis.
    
    This tool analyzes user requests and returns concrete agent routing decisions
    in JSON format for the NLP_PROCESSOR agent.
    
    Args:
        telegram_id: Telegram ID of the requesting user  
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context (main/leadership/private)
        intent_data: The user's request to analyze (REQUIRED)
        
    Returns:
        JSON response with routing decision: {"agent": "name", "confidence": 0.9, "intent": "type", "reasoning": "explanation"}
    """
    try:
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            intent_data = params.get('intent_data', '') or params.get('message', '') or params.get('message_text', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
            
        if not intent_data or not isinstance(intent_data, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid intent_data is required"
            )
        
        logger.info(f"🔧 [NLP_ROUTING] Analyzing request: '{intent_data[:50]}...' from {username} (ID: {telegram_id}) in {chat_type}")
        
        # Import the actual routing decision function
        from kickai.agents.nlp_processor import routing_recommendation_domain
        
        # Call the domain function that returns proper JSON routing decisions
        result = await routing_recommendation_domain(
            telegram_id=telegram_id,
            team_id=team_id,
            username=username,
            chat_type=chat_type,
            intent_data=intent_data
        )
        
        logger.info(f"✅ [NLP_ROUTING] Routing decision completed for '{intent_data[:30]}...'")
        return result
        
    except Exception as e:
        logger.error(f"❌ [NLP_ROUTING] Error generating routing prompt: {e}")
        return create_json_response(
            ResponseStatus.ERROR,
            message="Unable to analyze routing request. Please try rephrasing your request."
        )


@tool("analyze_update_context", result_as_answer=True)
async def analyze_update_context(
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
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            message = params.get('message', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
            
        if not message or not isinstance(message, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid message is required"
            )
        
        logger.info(f"🔧 [NLP_UPDATE] Processing update context analysis for {username}")
        
        # Import the NLP processor domain function dynamically
        from kickai.agents.nlp_processor import analyze_update_context_domain as nlp_analyze_update
        
        # Execute NLP processing (async)
        result = await nlp_analyze_update(
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
async def validate_routing_permissions(
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
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            user_role = params.get('user_role', '')
            requested_action = params.get('requested_action', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
            
        if not user_role or not isinstance(user_role, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid user_role is required"
            )
            
        if not requested_action or not isinstance(requested_action, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid requested_action is required"
            )
        
        logger.info(f"🔧 [NLP_PERM] Processing permission validation for {username}, action: {requested_action}")
        
        # Import the NLP processor domain function dynamically
        from kickai.agents.nlp_processor import validate_routing_permissions_domain as nlp_validate_permissions
        
        # Execute NLP processing (async)
        result = await nlp_validate_permissions(
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
async def entity_extraction_tool(
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
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            message = params.get('message', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
            
        if not message or not isinstance(message, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid message is required"
            )
        
        logger.info(f"🔧 [NLP_ENTITY] Processing entity extraction for {username}: {message[:50]}")
        
        # Import the NLP processor domain function dynamically to avoid circular imports
        from kickai.agents.nlp_processor import entity_extraction_domain as nlp_entity_extraction
        
        # Execute NLP processing (async)
        result = await nlp_entity_extraction(
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
async def conversation_context_tool(
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
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
        
        logger.info(f"🔧 [NLP_CONTEXT] Processing conversation context for {username}")
        
        # Import the NLP processor domain function dynamically to avoid circular imports
        from kickai.agents.nlp_processor import conversation_context_domain as nlp_conversation_context
        
        # Execute NLP processing (async)
        result = await nlp_conversation_context(
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
async def semantic_similarity_tool(
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
        # Handle CrewAI parameter dictionary passing (CrewAI best practice)
        if isinstance(telegram_id, dict):
            params = telegram_id
            telegram_id = params.get('telegram_id', 0)
            team_id = params.get('team_id', '')
            username = params.get('username', '')
            chat_type = params.get('chat_type', '')
            message = params.get('message', '')
            
            # Type conversion with robust error handling
            if isinstance(telegram_id, str):
                try:
                    telegram_id = int(telegram_id)
                except (ValueError, TypeError):
                    return create_json_response(
                        ResponseStatus.ERROR, 
                        message="Invalid telegram_id format"
                    )
        
        # Comprehensive parameter validation (CrewAI best practice)
        if not telegram_id or telegram_id <= 0:
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid telegram_id is required"
            )
        
        if not team_id or not isinstance(team_id, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid team_id is required"
            )
            
        if not username or not isinstance(username, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid username is required"
            )
            
        if not chat_type or not isinstance(chat_type, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid chat_type is required"
            )
            
        if not message or not isinstance(message, str):
            return create_json_response(
                ResponseStatus.ERROR, 
                message="Valid message is required"
            )
        
        logger.info(f"🔧 [NLP_SEMANTIC] Processing semantic similarity for {username}: {message[:50]}")
        
        # Import the NLP processor domain function dynamically to avoid circular imports
        from kickai.agents.nlp_processor import semantic_similarity_domain as nlp_semantic_similarity
        
        # Execute NLP processing (async)
        result = await nlp_semantic_similarity(
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