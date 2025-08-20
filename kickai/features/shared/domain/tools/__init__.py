#!/usr/bin/env python3
"""
Shared domain tools for KICKAI system.

This module provides shared tools used across multiple features.
"""

# Import only the tools that actually exist
from kickai.features.shared.domain.tools.help_tools import *
from kickai.features.shared.domain.tools.onboarding_tools import (
    team_member_guidance,
)
# register_player import removed - /register command no longer supported
from kickai.features.shared.domain.tools.user_tools import (
    get_user_status,
)
from kickai.features.shared.domain.tools.system_tools import (
    ping,
    version,
)
from kickai.features.shared.domain.tools.nlp_tools import (
    advanced_intent_recognition,
    entity_extraction_tool,
    conversation_context_tool,
    semantic_similarity_tool,
    routing_recommendation_tool,
    analyze_update_context,
    validate_routing_permissions,
)
from kickai.features.shared.domain.tools.permission_tools import (
    permission_denied_message,
    command_not_available,
)

__all__ = [
    # Help tools (from help_tools.py)
    "help_response",
    "get_available_commands",
    "get_command_help",
    "get_welcome_message",
    # Onboarding tools
    "team_member_guidance",
    # User tools
    "get_user_status",
    # System tools
    "ping",
    "version",
    # NLP tools (intelligent routing and analysis)
    "advanced_intent_recognition",
    "entity_extraction_tool",
    "conversation_context_tool",
    "semantic_similarity_tool",
    "routing_recommendation_tool",
    "analyze_update_context",
    "validate_routing_permissions",
    # Permission tools
    "permission_denied_message",
    "command_not_available",
]
