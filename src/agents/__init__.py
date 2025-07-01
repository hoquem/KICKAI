"""
KICKAI Agents Package

This package contains all agent-related functionality for the KICKAI system.
"""

from .crew_agents import (
    create_llm,
    create_agents_for_team,
    create_crew_for_team,
    OnboardingAgent,
    get_messaging_tools,
    CREWAI_SYSTEM_PROMPT
)

from .capabilities import (
    AgentCapability,
    AgentCapabilityMatrix,
    CapabilityType,
    get_agent_capabilities,
    get_agents_with_capability,
    get_capability_matrix_summary,
    get_best_agent_for_capability
)

from .handlers import (
    SimpleAgenticHandler,
    create_simple_agentic_handler
)

from .intelligent_system import (
    ImprovedAgenticSystem,
    AgentCommunicationProtocol,
    AgentPerformanceMonitor
)

from .routing import (
    IntelligentAgentRouter,
    StandaloneIntelligentRouter,
    RoutingDecision,
    RequestContext
)

__all__ = [
    # CrewAI Agents
    'create_llm',
    'create_agents_for_team', 
    'create_crew_for_team',
    'OnboardingAgent',
    'get_messaging_tools',
    'CREWAI_SYSTEM_PROMPT',
    
    # Capabilities
    'AgentCapability',
    'AgentCapabilityMatrix',
    'CapabilityType',
    'get_agent_capabilities',
    'get_agents_with_capability',
    'get_capability_matrix_summary',
    'get_best_agent_for_capability',
    
    # Handlers
    'SimpleAgenticHandler',
    'create_simple_agentic_handler',
    
    # Intelligent System
    'ImprovedAgenticSystem',
    'AgentCommunicationProtocol',
    'AgentPerformanceMonitor',
    
    # Routing
    'IntelligentAgentRouter',
    'StandaloneIntelligentRouter',
    'RoutingDecision',
    'RequestContext'
] 