"""
LLM Intent Extraction Utility

This module provides intent extraction functionality for natural language processing
in the KICKAI system.
"""

import re
from typing import Any

from loguru import logger


def extract_intent(message: str, context: str = "") -> dict[str, Any]:
    """
    Extract intent and entities from a natural language message.


        message: The input message to analyze
        context: Additional context about the conversation


    :return: Dictionary containing 'intent' and 'entities' keys
    :rtype: str  # TODO: Fix type
    """
    try:
        # Convert to lowercase for easier matching
        message_lower = message.lower().strip()

        # Define intent patterns
        intent_patterns = {
            "get_player_info": [
                # Pattern for "What's my registration status?" and similar queries
                r"\b(what|show|tell|get|my|me)\b.*\b(phone|number|position|role|id|player|info|information|status|fa|registration)\b",
                r"\b(phone|number|position|role|id|player|info|information|status|fa|registration)\b.*\b(what|is|my|me)\b",
                r"\b(am|i|are|you|is|my)\b.*\b(fa|registered|eligible|active|pending)\b",
                r"\b(my|me)\b.*\b(phone|number|position|role|id|info|information)\b",
                # Additional patterns for registration status queries
                r"\b(what|how)\b.*\b(registration|status)\b",
                r"\b(registration|status)\b.*\b(what|how)\b",
                r"\b(my|me)\b.*\b(registration|status)\b",
                r"\b(registration|status)\b.*\b(my|me)\b",
            ],
            "get_help": [
                r"\b(help|how|what)\b.*\b(you|commands|available)\b",
                r"\b(how|do|what|should|does)\b",
                r"\b(help|me|assist|support)\b",
            ],
            "update_profile": [
                r"\b(update|change|modify|edit)\b.*\b(phone|number|position|role|info|information|profile)\b",
                r"\b(my|me)\b.*\b(phone|number|position|role|info|information)\b.*\b(is|are)\b",
                r"\b(change|update|modify)\b.*\b(my|me)\b",
            ],
            "get_team_info": [
                r"\b(team|players|members|list|show)\b.*\b(all|everyone|everybody)\b",
                r"\b(how|many|count|total)\b.*\b(players|members|team)\b",
                r"\b(show|list|get)\b.*\b(team|players|members)\b",
            ],
            "filter_players": [
                r"\b(players|members)\b.*\b(position|role|fa|registered|eligible|active|pending)\b",
                r"\b(show|list|get)\b.*\b(goalkeeper|defender|midfielder|forward|striker|utility)\b",
                r"\b(goalkeeper|defender|midfielder|forward|striker|utility)\b.*\b(players|members)\b",
            ],
            "get_team_stats": [
                r"\b(stats|statistics|numbers|count|total)\b",
                r"\b(how|many|much)\b.*\b(players|members|active|pending|registered)\b",
                r"\b(team|overall|summary)\b.*\b(stats|statistics|info|information)\b",
            ],
        }

        # Check each intent pattern
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    # Extract entities based on intent
                    entities = extract_entities(message_lower, intent)
                    return {"intent": intent, "entities": entities, "confidence": 0.8}

        # Default to unknown intent
        return {"intent": "unknown", "entities": {}, "confidence": 0.0}

    except Exception as e:
        logger.error(f"Error extracting intent: {e}")
        return {"intent": "unknown", "entities": {}, "confidence": 0.0}


def extract_entities(message: str, intent: str) -> dict[str, Any]:
    """
    Extract entities from the message based on the detected intent.


        message: The input message
        intent: The detected intent


    :return: Dictionary of extracted entities
    :rtype: str  # TODO: Fix type
    """
    entities = {}

    try:
        if intent == "get_player_info":
            # Extract specific info type requested
            if re.search(r"\b(phone|number)\b", message):
                entities["info_type"] = "phone"
            elif re.search(r"\b(position|role)\b", message):
                entities["info_type"] = "position"
            elif re.search(r"\b(id|player.?id)\b", message):
                entities["info_type"] = "id"
            elif re.search(r"\b(fa|registration|registered)\b", message):
                entities["info_type"] = "fa_status"
            elif re.search(r"\b(status|onboarding)\b", message):
                entities["info_type"] = "status"
            else:
                entities["info_type"] = "all"

        elif intent == "update_profile":
            # Extract what needs to be updated
            if re.search(r"\b(phone|number)\b", message):
                entities["update_type"] = "phone"
            elif re.search(r"\b(position|role)\b", message):
                entities["update_type"] = "position"
            elif re.search(r"\b(emergency|contact)\b", message):
                entities["update_type"] = "emergency_contact"
            elif re.search(r"\b(dob|birth|date)\b", message):
                entities["update_type"] = "date_of_birth"
            else:
                entities["update_type"] = "general"

        elif intent == "filter_players":
            # Extract position filter
            positions = ["goalkeeper", "defender", "midfielder", "forward", "striker", "utility"]
            for pos in positions:
                if pos in message:
                    entities["position"] = pos
                    break

            # Extract status filter
            if re.search(r"\b(Union[fa, registered])\b", message):
                entities["fa_status"] = "registered"
            elif re.search(r"\b(eligible)\b", message):
                entities["fa_status"] = "eligible"
            elif re.search(r"\b(active)\b", message):
                entities["status"] = "active"
            elif re.search(r"\b(pending)\b", message):
                entities["status"] = "pending"

    except Exception as e:
        logger.error(f"Error extracting entities: {e}")

    return entities


def extract_intent_sync(message: str, context: str = "") -> dict[str, Any]:
    """
    Synchronous version of extract_intent for backward compatibility.


        message: The input message to analyze
        context: Additional context about the conversation


    :return: Dictionary containing 'intent' and 'entities' keys
    :rtype: str  # TODO: Fix type
    """
    return extract_intent(message, context)


class LLMIntent:
    """LLM-based intent extraction using CrewAI agents."""

    def __init__(self, team_id: str | None = None):
        self.team_id = team_id
        logger.info(f"🤖 LLMIntent initialized for team: {team_id}")

    async def extract_intent(self, message: str, context: str = "") -> dict[str, Any]:
        """
        Extract intent using LLM-based approach.


            message: The input message to analyze
            context: Additional context about the conversation


    :return: Dictionary containing 'intent' and 'entities' keys
    :rtype: str  # TODO: Fix type
        """
        try:
            # Use the existing regex-based intent extraction as fallback
            # In the future, this can be replaced with actual LLM-based extraction
            return extract_intent(message, context)
        except Exception as e:
            logger.error(f"Error in LLM intent extraction: {e}")
            return {"intent": "unknown", "entities": {}, "confidence": 0.0}
