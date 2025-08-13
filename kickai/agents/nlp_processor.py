#!/usr/bin/env python3
"""
NLP Processor Agent

This module implements a specialized Natural Language Processing agent for the KICKAI system.
It provides advanced intent recognition, entity extraction, and conversation context management
for natural language understanding and routing enhancement.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from functools import lru_cache

from loguru import logger
from crewai.tools import tool

from kickai.agents.configurable_agent import ConfigurableAgent
from kickai.core.enums import AgentRole
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
    
    Attributes:
        team_id: Team identifier for context
        conversation_cache: LRU cache for conversation context (size: 1000)
        intent_cache: Cache for common intent patterns (size: 500)
        
    Example:
        >>> nlp_processor = NLPProcessor("KTI")
        >>> result = await nlp_processor.process_natural_language(message)
    """
    
    def __init__(self, team_id: str):
        """
        Initialize NLP processor agent following KICKAI coding standards.
        
        Args:
            team_id: Team identifier for context and memory
            
        Raises:
            InputInputValidationError: When team_id is invalid
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
            
            # Initialize NLP-specific components with performance optimization
            self.conversation_cache = self._create_conversation_cache()
            self.intent_cache = self._create_intent_cache()
            
            # Initialize intent categories and patterns
            self.intent_categories = self._initialize_intent_categories()
            self.entity_patterns = self._initialize_entity_patterns()
            
            logger.info(f"✅ NLP Processor initialized for team: {team_id}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing NLP Processor: {e}")
            raise AgentInitializationError("NLP_PROCESSOR", f"Initialization failed: {str(e)}")

    def _create_conversation_cache(self):
        """Create LRU cache for conversation context."""
        try:
            # Simple dict for now - can be enhanced with proper LRU implementation
            return {}
        except Exception as e:
            logger.warning(f"⚠️ Error creating conversation cache: {e}")
            return {}

    def _create_intent_cache(self):
        """Create LRU cache for intent patterns."""
        try:
            # Simple dict for now - can be enhanced with proper LRU implementation
            return {}
        except Exception as e:
            logger.warning(f"⚠️ Error creating intent cache: {e}")
            return {}

    def _initialize_intent_categories(self) -> Dict[str, List[str]]:
        """
        Initialize intent categories with football-specific patterns.
        
        Returns:
            Dictionary mapping intent categories to pattern keywords
        """
        try:
            return {
                "get_player_info": [
                    "status", "info", "details", "phone", "position", "registration",
                    "my info", "who am i", "what's my", "show me my"
                ],
                "update_profile": [
                    "update", "change", "modify", "edit", "set my", "new phone",
                    "change position", "update details"
                ],
                "get_team_info": [
                    "team", "players", "list", "show", "who's on", "team members",
                    "all players", "squad", "roster"
                ],
                "get_help": [
                    "help", "assist", "support", "how do", "what can", "commands",
                    "don't know", "confused", "explain"
                ],
                "match_management": [
                    "match", "game", "fixture", "availability", "available",
                    "attend", "playing", "squad selection", "lineup"
                ],
                "team_administration": [
                    "add player", "add member", "promote", "admin", "manage",
                    "create team", "invite", "register"
                ],
                "get_team_stats": [
                    "stats", "statistics", "count", "how many", "numbers",
                    "metrics", "performance"
                ]
            }
        except Exception as e:
            logger.warning(f"⚠️ Error initializing intent categories: {e}")
            return {}

    def _initialize_entity_patterns(self) -> Dict[str, List[str]]:
        """
        Initialize entity extraction patterns for football context.
        
        Returns:
            Dictionary mapping entity types to extraction patterns
        """
        try:
            return {
                "player_positions": [
                    "goalkeeper", "defender", "midfielder", "forward", "striker",
                    "centre-back", "fullback", "winger", "attacking midfielder"
                ],
                "info_types": [
                    "phone", "position", "status", "details", "contact", "role"
                ],
                "time_references": [
                    "today", "tomorrow", "yesterday", "this week", "next week",
                    "last match", "next match", "current", "recent"
                ],
                "availability_status": [
                    "available", "unavailable", "maybe", "injured", "away",
                    "busy", "free", "can play", "cannot play"
                ]
            }
        except Exception as e:
            logger.warning(f"⚠️ Error initializing entity patterns: {e}")
            return {}


@tool("advanced_intent_recognition", result_as_answer=True)
def advanced_intent_recognition(
    telegram_id: int,
    team_id: str, 
    username: str,
    chat_type: str,
    message: str,
    conversation_history: str = "",
    **kwargs
) -> str:
    """
    Advanced intent recognition with conversation awareness and confidence scoring.
    
    Performs sophisticated natural language understanding to classify user intent,
    extract entities, and provide routing recommendations with confidence metrics.
    
    This function follows KICKAI coding standards with single try/except boundary,
    comprehensive input validation, and structured JSON responses.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user  
        chat_type: Chat context (main/leadership/private)
        message: User message to analyze
        conversation_history: Previous conversation context
        **kwargs: Additional context parameters
        
    Returns:
        JSON response string with intent classification results containing:
        - primary_intent: Main identified intent
        - secondary_intents: Additional intents if multi-intent detected
        - confidence: Confidence score (0.0-1.0)
        - entities: Extracted entities with types and values
        - conversation_context: Context from previous turns
        - routing_recommendation: Recommended agent and priority
        - requires_followup: Whether follow-up questions needed
        
    Raises:
        InputInputValidationError: When input validation fails
        AgentExecutionError: When intent recognition fails
        
    Example:
        >>> result = advanced_intent_recognition(123, "KTI", "user", "main", "What's my status?")
        >>> data = json.loads(result)
        >>> data["primary_intent"]
        "get_player_status"
    """
    try:
        # Input validation using utility functions
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        try:
            from kickai.utils.tool_validation import validate_string_input
            validate_string_input(message, "Message", allow_empty=False)
        except ToolValidationError as e:
            return create_json_response("error", message=str(e))
        
        # Log tool execution with performance tracking
        inputs = {
            'team_id': team_id,
            'telegram_id': telegram_id_int,
            'message_length': len(message),
            'has_history': bool(conversation_history)
        }
        log_tool_execution("advanced_intent_recognition", inputs, True)
        
        # Get NLP service from container
        container = get_container()
        # For now, use direct analysis since NLP service will be implemented later
        
        # Perform intent recognition analysis
        intent_result = _analyze_intent_direct(
            message=message,
            context={
                "telegram_id": telegram_id_int,
                "team_id": team_id,
                "username": username,
                "chat_type": chat_type,
                "conversation_history": conversation_history
            }
        )
        
        # Structure comprehensive response following KICKAI standards
        response_data = {
            "primary_intent": intent_result.primary_intent,
            "secondary_intents": intent_result.secondary_intents,
            "confidence": intent_result.confidence,
            "entities": intent_result.entities,
            "conversation_context": intent_result.conversation_context,
            "routing_recommendation": intent_result.routing_recommendation,
            "requires_followup": intent_result.requires_followup,
            "reasoning": intent_result.reasoning
        }
        
        return create_json_response("success", data=response_data)
        
    except Exception as e:
        logger.error(f"❌ Error in advanced_intent_recognition: {e}")
        return create_json_response("error", message="Intent recognition failed")


def _analyze_intent_direct(message: str, context: Dict[str, Any]) -> IntentResult:
    """
    Direct intent analysis implementation for NLP processing.
    
    This function provides immediate intent analysis capabilities while the full
    NLP service infrastructure is being developed.
    
    Args:
        message: User message to analyze
        context: Context information for analysis
        
    Returns:
        IntentResult with comprehensive analysis
        
    Raises:
        InputValidationError: When analysis fails
    """
    try:
        # Normalize message for analysis
        message_lower = message.lower().strip()
        
        # Intent classification with football-specific patterns
        intent_patterns = {
            "get_player_info": [
                "my status", "my info", "who am i", "what's my", "show me my",
                "status", "info", "details", "phone", "position"
            ],
            "update_profile": [
                "update", "change", "modify", "edit", "set my", "new phone",
                "change position"
            ],
            "get_team_info": [
                "team", "players", "list", "show", "who's on", "squad", "roster"
            ],
            "get_help": [
                "help", "assist", "support", "how do", "what can", "commands"
            ],
            "match_management": [
                "match", "game", "fixture", "availability", "available", "attend"
            ],
            "team_administration": [
                "add player", "add member", "promote", "admin", "manage"
            ]
        }
        
        # Find best matching intent
        best_intent = "unknown"
        best_confidence = 0.0
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    confidence = len(pattern) / len(message_lower) * 0.8 + 0.2
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = min(confidence, 1.0)
        
        # Extract entities based on patterns
        entities = _extract_entities_direct(message_lower)
        
        # Generate routing recommendation
        routing_recommendation = _generate_routing_recommendation(best_intent, context)
        
        # Build result
        return IntentResult(
            primary_intent=best_intent,
            confidence=best_confidence,
            entities=entities,
            conversation_context={"previous_message": context.get("conversation_history", "")},
            routing_recommendation=routing_recommendation,
            requires_followup=_requires_followup(best_intent, entities),
            reasoning=f"Pattern matching identified '{best_intent}' with {best_confidence:.2f} confidence",
            original_message=message
        )
        
    except Exception as e:
        logger.error(f"❌ Error in direct intent analysis: {e}")
        return IntentResult(
            primary_intent="unknown",
            confidence=0.0,
            reasoning=f"Analysis failed: {str(e)}",
            original_message=message
        )


def _extract_entities_direct(message_lower: str) -> Dict[str, Any]:
    """
    Direct entity extraction from message text.
    
    Args:
        message_lower: Normalized lowercase message
        
    Returns:
        Dictionary of extracted entities
    """
    try:
        entities = {}
        
        # Extract player positions
        positions = ["goalkeeper", "defender", "midfielder", "forward", "striker"]
        for position in positions:
            if position in message_lower:
                entities["position"] = position
                break
        
        # Extract info types
        info_types = ["phone", "status", "details", "contact", "position"]
        for info_type in info_types:
            if info_type in message_lower:
                entities["info_type"] = info_type
                break
        
        # Extract self-reference indicators
        if any(indicator in message_lower for indicator in ["my", "me", "i am", "myself"]):
            entities["target"] = "self"
        
        return entities
        
    except Exception as e:
        logger.warning(f"⚠️ Error extracting entities: {e}")
        return {}


def _generate_routing_recommendation(intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate routing recommendation based on intent and context.
    
    Args:
        intent: Identified intent
        context: Context information
        
    Returns:
        Dictionary with routing recommendation
    """
    try:
        # Map intents to agents
        intent_to_agent = {
            "get_player_info": "player_coordinator",
            "update_profile": "player_coordinator",
            "get_team_info": "player_coordinator",
            "get_help": "help_assistant",
            "match_management": "squad_selector",
            "team_administration": "team_administrator",
            "unknown": "message_processor"
        }
        
        recommended_agent = intent_to_agent.get(intent, "message_processor")
        
        # Determine priority
        priority = "high" if intent in ["get_help", "team_administration"] else "medium"
        
        return {
            "agent": recommended_agent,
            "priority": priority,
            "confidence": 0.8 if intent != "unknown" else 0.3,
            "reason": f"Intent '{intent}' maps to {recommended_agent}"
        }
        
    except Exception as e:
        logger.warning(f"⚠️ Error generating routing recommendation: {e}")
        return {
            "agent": "message_processor",
            "priority": "medium",
            "confidence": 0.5,
            "reason": "Default routing due to error"
        }


def _requires_followup(intent: str, entities: Dict[str, Any]) -> bool:
    """
    Determine if the intent requires follow-up questions.
    
    Args:
        intent: Identified intent
        entities: Extracted entities
        
    Returns:
        True if follow-up questions are needed
    """
    try:
        # Intents that typically require follow-up
        followup_intents = ["update_profile", "team_administration"]
        
        # Check if intent typically needs follow-up
        if intent in followup_intents:
            return True
        
        # Check if entities are incomplete
        if intent == "get_player_info" and not entities.get("info_type"):
            return True
        
        return False
        
    except Exception:
        return False


@tool("entity_extraction_tool", result_as_answer=True)
def entity_extraction_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    **kwargs
) -> str:
    """
    Advanced entity extraction for football team management context.
    
    Extracts relevant entities like player names, positions, time references,
    and other football-specific information from user messages.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context
        message: Message to extract entities from
        **kwargs: Additional parameters
        
    Returns:
        JSON response with extracted entities
        
    Raises:
        InputValidationError: When input validation fails
        AgentExecutionError: When entity extraction fails
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        try:
            from kickai.utils.tool_validation import validate_string_input
            validate_string_input(message, "Message", allow_empty=False)
        except ToolValidationError as e:
            return create_json_response("error", message=str(e))
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("entity_extraction_tool", inputs, True)
        
        # Extract entities
        entities = _extract_entities_direct(message.lower())
        
        return create_json_response("success", data={"entities": entities})
        
    except Exception as e:
        logger.error(f"❌ Error in entity_extraction_tool: {e}")
        return create_json_response("error", message="Entity extraction failed")


@tool("conversation_context_tool", result_as_answer=True) 
def conversation_context_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    **kwargs
) -> str:
    """
    Build and retrieve conversation context for multi-turn conversations.
    
    Manages conversation state and context across multiple message exchanges
    to enable natural, contextual conversations.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context
        **kwargs: Additional parameters
        
    Returns:
        JSON response with conversation context
        
    Raises:
        InputValidationError: When input validation fails
        AgentExecutionError: When context retrieval fails
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("conversation_context_tool", inputs, True)
        
        # For now, return basic context structure
        # TODO: Integrate with TeamMemory for actual conversation tracking
        context = {
            "user_id": telegram_id_int,
            "team_id": team_id,
            "chat_type": chat_type,
            "conversation_turns": 0,
            "last_intent": "unknown",
            "context_entities": {}
        }
        
        return create_json_response("success", data={"context": context})
        
    except Exception as e:
        logger.error(f"❌ Error in conversation_context_tool: {e}")
        return create_json_response("error", message="Context retrieval failed")


@tool("semantic_similarity_tool", result_as_answer=True)
def semantic_similarity_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    message: str,
    reference_commands: str = "",
    **kwargs
) -> str:
    """
    Calculate semantic similarity between user message and known commands/patterns.
    
    This tool helps identify the most similar commands or patterns to a user's
    natural language input, enabling intelligent command suggestions and routing.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context
        message: User message to analyze
        reference_commands: Commands to compare against (comma-separated)
        **kwargs: Additional parameters
        
    Returns:
        JSON response with similarity scores and recommendations
        
    Raises:
        InputValidationError: When input validation fails
        AgentExecutionError: When similarity calculation fails
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        try:
            from kickai.utils.tool_validation import validate_string_input
            validate_string_input(message, "Message", allow_empty=False)
        except ToolValidationError as e:
            return create_json_response("error", message=str(e))
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("semantic_similarity_tool", inputs, True)
        
        # Calculate similarity scores with known commands
        similarity_results = _calculate_semantic_similarity(message, reference_commands)
        
        return create_json_response("success", data={"similarity_results": similarity_results})
        
    except Exception as e:
        logger.error(f"❌ Error in semantic_similarity_tool: {e}")
        return create_json_response("error", message="Semantic similarity calculation failed")


def _calculate_semantic_similarity(message: str, reference_commands: str) -> Dict[str, Any]:
    """
    Calculate semantic similarity using simple text matching techniques.
    
    Args:
        message: User message to analyze
        reference_commands: Reference commands to compare against
        
    Returns:
        Dictionary with similarity results
    """
    try:
        message_lower = message.lower().strip()
        
        # Default command patterns if none provided
        if not reference_commands:
            reference_commands = "/help,/info,/status,/list,/matches,/availability"
        
        commands = [cmd.strip() for cmd in reference_commands.split(",")]
        similarities = []
        
        for command in commands:
            command_lower = command.lower().strip()
            
            # Simple similarity based on word overlap
            message_words = set(message_lower.split())
            command_words = set(command_lower.replace("/", "").split())
            
            if command_words and message_words:
                overlap = len(message_words.intersection(command_words))
                total_words = len(message_words.union(command_words))
                similarity = overlap / total_words if total_words > 0 else 0.0
            else:
                similarity = 0.0
            
            # Direct substring matching bonus
            if command_lower.replace("/", "") in message_lower:
                similarity += 0.3
            
            similarities.append({
                "command": command,
                "similarity": min(similarity, 1.0),
                "match_type": "direct" if similarity > 0.5 else "partial"
            })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return {
            "top_matches": similarities[:3],
            "best_match": similarities[0] if similarities else None,
            "has_good_match": similarities[0]["similarity"] > 0.4 if similarities else False
        }
        
    except Exception as e:
        logger.warning(f"⚠️ Error calculating semantic similarity: {e}")
        return {
            "top_matches": [],
            "best_match": None,
            "has_good_match": False
        }


@tool("routing_recommendation_tool", result_as_answer=True)
def routing_recommendation_tool(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    intent_data: str,
    **kwargs
) -> str:
    """
    Generate intelligent routing recommendations based on intent analysis.
    
    This tool provides routing recommendations by analyzing intent data,
    user context, and system state to determine the optimal agent for handling
    the user's request.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team identifier for context
        username: Username of the requesting user
        chat_type: Chat context
        intent_data: JSON string with intent analysis results
        **kwargs: Additional parameters
        
    Returns:
        JSON response with routing recommendations
        
    Raises:
        InputValidationError: When input validation fails
        AgentExecutionError: When routing recommendation fails
    """
    try:
        # Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        try:
            from kickai.utils.tool_validation import validate_string_input
            validate_string_input(intent_data, "Intent data", allow_empty=False)
        except ToolValidationError as e:
            return create_json_response("error", message=str(e))
        
        # Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("routing_recommendation_tool", inputs, True)
        
        # Parse intent data
        try:
            intent_info = json.loads(intent_data)
        except json.JSONDecodeError:
            intent_info = {"primary_intent": "unknown", "confidence": 0.0}
        
        # Generate routing recommendation
        routing_recommendation = _generate_enhanced_routing_recommendation(
            intent_info, chat_type, telegram_id_int, team_id
        )
        
        return create_json_response("success", data={"routing_recommendation": routing_recommendation})
        
    except Exception as e:
        logger.error(f"❌ Error in routing_recommendation_tool: {e}")
        return create_json_response("error", message="Routing recommendation failed")


def _generate_enhanced_routing_recommendation(
    intent_info: Dict[str, Any], 
    chat_type: str, 
    telegram_id: int, 
    team_id: str
) -> Dict[str, Any]:
    """
    Generate enhanced routing recommendation with context awareness.
    
    Args:
        intent_info: Intent analysis information
        chat_type: Type of chat context
        telegram_id: User's Telegram ID
        team_id: Team identifier
        
    Returns:
        Dictionary with enhanced routing recommendation
    """
    try:
        primary_intent = intent_info.get("primary_intent", "unknown")
        confidence = intent_info.get("confidence", 0.0)
        
        # Enhanced intent to agent mapping
        intent_to_agent = {
            "get_player_info": "player_coordinator",
            "update_profile": "player_coordinator", 
            "get_team_info": "player_coordinator",
            "get_help": "help_assistant",
            "match_management": "squad_selector",
            "team_administration": "team_administrator",
            "unknown": "message_processor"
        }
        
        # Context-based routing adjustments
        recommended_agent = intent_to_agent.get(primary_intent, "message_processor")
        
        # Adjust routing based on chat type
        if chat_type == "leadership" and primary_intent in ["team_administration", "match_management"]:
            priority = "high"
        elif chat_type == "main" and primary_intent == "get_help":
            priority = "high"
        else:
            priority = "medium"
        
        # Calculate routing confidence
        routing_confidence = confidence * 0.8 + 0.2  # Base confidence adjustment
        
        # Check if agent is available (simplified check for now)
        agent_available = True  # TODO: Implement actual agent availability check
        
        recommendation = {
            "agent": recommended_agent,
            "priority": priority,
            "confidence": routing_confidence,
            "reason": f"Intent '{primary_intent}' with {confidence:.2f} confidence",
            "agent_available": agent_available,
            "fallback_agent": "message_processor",
            "estimated_response_time": "< 2 seconds",
            "context_factors": {
                "chat_type": chat_type,
                "intent_confidence": confidence,
                "has_entities": bool(intent_info.get("entities"))
            }
        }
        
        return recommendation
        
    except Exception as e:
        logger.warning(f"⚠️ Error generating enhanced routing recommendation: {e}")
        return {
            "agent": "message_processor",
            "priority": "medium",
            "confidence": 0.5,
            "reason": "Default routing due to error",
            "agent_available": True,
            "fallback_agent": "message_processor"
        }