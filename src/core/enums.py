from enum import Enum

"""
Core enums for the KICKAI system.

Defined agent roles in the 8-agent KICKAI system.
"""

class AgentRole(Enum):
    """Agent roles in the 8-agent system."""
    MESSAGE_PROCESSOR = "message_processor"
    TEAM_MANAGER = "team_manager"
    PLAYER_COORDINATOR = "player_coordinator"
    FINANCE_MANAGER = "finance_manager"
    PERFORMANCE_ANALYST = "performance_analyst"
    LEARNING_AGENT = "learning_agent"
    ONBOARDING_AGENT = "onboarding_agent"
    COMMAND_FALLBACK_AGENT = "command_fallback_agent"

class AIProvider(Enum):
    """AI provider types."""
    GOOGLE_GEMINI = "google_gemini"
    OLLAMA = "ollama" 