#!/usr/bin/env python3
"""
NLP Tools for KICKAI System [DEPRECATED]

DEPRECATED: These NLP tools are no longer needed after migration to native CrewAI routing.
The MESSAGE_PROCESSOR agent now handles routing and intent recognition natively.

This module provided Natural Language Processing tools for intelligent routing,
intent recognition, and context analysis. These tools were used by the NLP_PROCESSOR
agent (now removed) to enable intelligent agent selection and routing decisions.
"""

# Import NLP tools from the application layer
from kickai.features.shared.application.tools.nlp_tools import (
    advanced_intent_recognition,
    entity_extraction_tool,
    conversation_context_tool,
    semantic_similarity_tool,
    routing_recommendation_tool,
    analyze_update_context,
    validate_routing_permissions,
)

__all__ = [
    "advanced_intent_recognition",
    "entity_extraction_tool", 
    "conversation_context_tool",
    "semantic_similarity_tool",
    "routing_recommendation_tool",
    "analyze_update_context",
    "validate_routing_permissions",
]