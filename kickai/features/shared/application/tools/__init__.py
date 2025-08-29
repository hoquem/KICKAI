"""Shared Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for shared/common features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools
from .help_tools import (
    help_response, 
    FINAL_HELP_RESPONSE,
    get_command_help,
    get_welcome_message,
    get_available_commands
)
from .system_tools import ping, version
from .user_tools import get_user_status
from .permission_tools import permission_denied_message, command_not_available
from .nlp_tools import (
    advanced_intent_recognition,
    routing_recommendation_tool,
    analyze_update_context,
    validate_routing_permissions,
    entity_extraction_tool,
    conversation_context_tool,
    semantic_similarity_tool
)

# Export all tools for agent registration
_all_ = [
    "help_response",
    "FINAL_HELP_RESPONSE",
    "get_command_help",
    "get_welcome_message",
    "get_available_commands",
    "ping",
    "version",
    "get_user_status",
    "permission_denied_message",
    "command_not_available",
    "advanced_intent_recognition",
    "routing_recommendation_tool",
    "analyze_update_context",
    "validate_routing_permissions",
    "entity_extraction_tool",
    "conversation_context_tool",
    "semantic_similarity_tool"
]