"""
KICKAI Agents Package

This package contains all agent-related functionality for the KICKAI system.
"""

from src.core.enums import AgentRole

from .crew_agents import (
    AgentFactory,
    TeamManagementSystem,
    ConfigurationManager,
    LLMFactory,
    MessageProcessorAgent,
    TeamManagerAgent,
    PlayerCoordinatorAgent,
    FinanceManagerAgent,
    PerformanceAnalystAgent,
    LearningAgent,
    OnboardingAgent
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

from .intelligent_system import (
    DynamicTaskDecomposer,
    ImprovedAgenticSystem,
    TaskContext,
    CapabilityBasedRouter,
    StandaloneIntelligentRouter,
    RoutingDecision,
    RequestContext,
    SimpleAgenticHandler
)

__all__ = [
    # CrewAI Agents
    'AgentRole',
    'AgentFactory',
    'TeamManagementSystem',
    'ConfigurationManager',
    'LLMFactory',
    'MessageProcessorAgent',
    'TeamManagerAgent',
    'PlayerCoordinatorAgent',
    'FinanceManagerAgent',
    'PerformanceAnalystAgent',
    'LearningAgent',
    'OnboardingAgent',
    
    # Capabilities
    'AgentCapability',
    'AgentCapabilityMatrix',
    'CapabilityType',
    'get_agent_capabilities',
    'get_agents_with_capability',
    'get_capability_matrix_summary',
    'get_best_agent_for_capability',
    
    # Intelligent System
    'DynamicTaskDecomposer',
    'ImprovedAgenticSystem',
    'TaskContext',
    'CapabilityBasedRouter',
    'StandaloneIntelligentRouter',
    'RoutingDecision',
    'RequestContext',
    'SimpleAgenticHandler'
] 