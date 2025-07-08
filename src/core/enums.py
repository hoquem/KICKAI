from enum import Enum

class AgentRole(Enum):
    """
    Defined agent roles in the 7-agent KICKAI system.
    1. MESSAGE_PROCESSOR: Primary user interface and command parsing
    2. TEAM_MANAGER: Strategic coordination and high-level planning
    3. PLAYER_COORDINATOR: Operational player management and registration
    4. FINANCE_MANAGER: Financial tracking and payment management
    5. PERFORMANCE_ANALYST: Performance analysis and tactical insights
    6. LEARNING_AGENT: Continuous learning and system improvement
    7. ONBOARDING_AGENT: Specialized player onboarding and registration
    8. COMMAND_FALLBACK_AGENT: Sophisticated NLP for failed command parsing
    """
    MESSAGE_PROCESSOR = "message_processor"
    TEAM_MANAGER = "team_manager"
    PLAYER_COORDINATOR = "player_coordinator"
    FINANCE_MANAGER = "finance_manager"
    PERFORMANCE_ANALYST = "performance_analyst"
    LEARNING_AGENT = "learning_agent"
    ONBOARDING_AGENT = "onboarding_agent"
    COMMAND_FALLBACK_AGENT = "command_fallback_agent" 