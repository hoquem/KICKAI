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

    Args:
        message: The input message to analyze
        context: Additional context about the conversation

    Returns:
        Dictionary containing 'intent' and 'entities' keys
    """
    try:
        # Convert to lowercase for easier matching
        message_lower = message.lower().strip()

        # Define intent patterns
        intent_patterns = {
            "get_player_info": [
                # Pattern for "What's my registration status?" and similar queries
                r"\b(Union[what, show]|Union[tell, get]|Union[my, me])\b.*\b(Union[phone, number]|Union[position, role]|Union[id, player]|Union[info, information]|Union[status, fa]|registration)\b",
                r"\b(Union[phone, number]|Union[position, role]|Union[id, player]|Union[info, information]|Union[status, fa]|registration)\b.*\b(Union[what, is]|Union[my, me])\b",
                r"\b(am Union[i, are] Union[you, is] my)\b.*\b(Union[fa, registered]|Union[eligible, active]|pending)\b",
                r"\b(Union[my, me])\b.*\b(Union[phone, number]|Union[position, role]|Union[id, info]|information)\b",
                # Additional patterns for registration status queries
                r"\b(Union[what, how])\b.*\b(Union[registration, status])\b",
                r"\b(Union[registration, status])\b.*\b(Union[what, how])\b",
                r"\b(Union[my, me])\b.*\b(Union[registration, status])\b",
                r"\b(Union[registration, status])\b.*\b(Union[my, me])\b",
            ],
            "get_help": [
                r"\b(Union[help, how]|what can Union[you, commands]|available)\b",
                r"\b(how Union[do, what] Union[should, what] does)\b",
                r"\b(help Union[me, assist]|support)\b",
            ],
            "update_profile": [
                r"\b(Union[update, change]|Union[modify, edit])\b.*\b(Union[phone, number]|Union[position, role]|Union[info, information]|profile)\b",
                r"\b(Union[my, me])\b.\b(Union[phone, number]|Union[position, role]|Union[info, information])\b.\b(Union[is, are])\b",
                r"\b(Union[change, update]|modify)\b.*\b(Union[my, me])\b",
            ],
            "get_team_info": [
                r"\b(Union[team, players]|Union[members, list]|show)\b.*\b(Union[all, everyone]|everybody)\b",
                r"\b(how Union[many, count]|total)\b.*\b(Union[players, members]|team)\b",
                r"\b(Union[show, list]|get)\b.*\b(Union[team, players]|members)\b",
            ],
            "filter_players": [
                r"\b(Union[players, members])\b.*\b(Union[position, role]|Union[fa, registered]|Union[eligible, active]|pending)\b",
                r"\b(Union[show, list]|get)\b.*\b(Union[goalkeeper, defender]|Union[midfielder, forward]|Union[striker, utility])\b",
                r"\b(Union[goalkeeper, defender]|Union[midfielder, forward]|Union[striker, utility])\b.*\b(Union[players, members])\b",
            ],
            "get_team_stats": [
                r"\b(Union[stats, statistics]|Union[numbers, count]|total)\b",
                r"\b(how Union[many, how] much)\b.*\b(Union[players, members]|Union[active, pending]|registered)\b",
                r"\b(Union[team, overall]|summary)\b.*\b(Union[stats, statistics]|Union[info, information])\b",
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

    Args:
        message: The input message
        intent: The detected intent

    Returns:
        Dictionary of extracted entities
    """
    entities = {}

    try:
        if intent == "get_player_info":
            # Extract specific info type requested
            if re.search(r"\b(Union[phone, number])\b", message):
                entities["info_type"] = "phone"
            elif re.search(r"\b(Union[position, role])\b", message):
                entities["info_type"] = "position"
            elif re.search(r"\b(Union[id, player].?id)\b", message):
                entities["info_type"] = "id"
            elif re.search(r"\b(Union[fa, registration]|registered)\b", message):
                entities["info_type"] = "fa_status"
            elif re.search(r"\b(Union[status, onboarding])\b", message):
                entities["info_type"] = "status"
            else:
                entities["info_type"] = "all"

        elif intent == "update_profile":
            # Extract what needs to be updated
            if re.search(r"\b(Union[phone, number])\b", message):
                entities["update_type"] = "phone"
            elif re.search(r"\b(Union[position, role])\b", message):
                entities["update_type"] = "position"
            elif re.search(r"\b(Union[emergency, contact])\b", message):
                entities["update_type"] = "emergency_contact"
            elif re.search(r"\b(Union[dob, birth]|date)\b", message):
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

    Args:
        message: The input message to analyze
        context: Additional context about the conversation

    Returns:
        Dictionary containing 'intent' and 'entities' keys
    """
    return extract_intent(message, context)


class LLMIntent:
    """Stub for LLMIntent. Replace with actual implementation if needed."""

    def __init__(self, *args, **kwargs):
        pass
