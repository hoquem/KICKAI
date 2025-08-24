#!/usr/bin/env python3
"""
NLP Tools for KICKAI System

This module provides Natural Language Processing tools for intelligent routing,
intent recognition, and context analysis. These tools are used by the NLP_PROCESSOR
agent to enable intelligent agent selection and routing decisions.
"""

# Import NLP tools from the agent implementation
from kickai.agents.nlp_processor import (
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