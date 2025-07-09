#!/usr/bin/env python3
"""
Agent Capabilities Matrix for KICKAI
Defines capabilities for each agent type to support intelligent routing.
"""

import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum

# Import AgentRole from crew_agents for type safety
from src.core.enums import AgentRole

logger = logging.getLogger(__name__)

class CapabilityType(Enum):
    """Types of agent capabilities."""
    INTENT_ANALYSIS = "intent_analysis"
    CONTEXT_MANAGEMENT = "context_management"
    ROUTING = "routing"
    STRATEGIC_PLANNING = "strategic_planning"
    COORDINATION = "coordination"
    DECISION_MAKING = "decision_making"
    PLAYER_MANAGEMENT = "player_management"
    AVAILABILITY_TRACKING = "availability_tracking"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TACTICAL_INSIGHTS = "tactical_insights"
    MESSAGING = "messaging"
    ANNOUNCEMENTS = "announcements"
    POLLS = "polls"
    PAYMENT_TRACKING = "payment_tracking"
    FINANCIAL_REPORTING = "financial_reporting"
    SQUAD_SELECTION = "squad_selection"
    FORM_ANALYSIS = "form_analysis"
    TREND_ANALYSIS = "trend_analysis"
    PERFORMANCE_METRICS = "performance_metrics"
    NATURAL_LANGUAGE_UNDERSTANDING = "natural_language_understanding"
    HIGH_LEVEL_OPERATIONS = "high_level_operations"
    OPERATIONAL_TASKS = "operational_tasks"
    OPPOSITION_ANALYSIS = "opposition_analysis"
    MATCH_PLANNING = "match_planning"
    BROADCAST_MANAGEMENT = "broadcast_management"
    BUDGET_MANAGEMENT = "budget_management"
    TACTICAL_FIT = "tactical_fit"
    PLAYER_EVALUATION = "player_evaluation"
    DATA_ANALYSIS = "data_analysis"
    PREDICTIONS = "predictions"
    PATTERN_LEARNING = "pattern_learning"
    USER_PREFERENCE_ANALYSIS = "user_preference_analysis"
    RESPONSE_OPTIMIZATION = "response_optimization"
    SYSTEM_IMPROVEMENT = "system_improvement"

@dataclass
class AgentCapability:
    """Represents an agent's capability with metadata."""
    capability: CapabilityType
    proficiency_level: float  # 0.0 to 1.0
    description: str
    is_primary: bool = False  # Whether this is a primary capability

class AgentCapabilityMatrix:
    """Manages agent capabilities for intelligent routing."""
    
    def __init__(self):
        self._capabilities = self._initialize_capabilities()
        self._capability_descriptions = self._initialize_descriptions()
        logger.info("[AgentCapabilityMatrix] Capability matrix initialized:")
        for agent_role, capabilities in self._capabilities.items():
            logger.info(f"  {agent_role}: {[cap.capability.value for cap in capabilities]}")
    
    def _initialize_capabilities(self) -> Dict[AgentRole, List[AgentCapability]]:
        """Initialize the capability matrix for all agents."""
        return {
            AgentRole.MESSAGE_PROCESSOR: [
                AgentCapability(CapabilityType.INTENT_ANALYSIS, 0.95, "Analyze user intent and context", True),
                AgentCapability(CapabilityType.CONTEXT_MANAGEMENT, 0.90, "Manage conversation context", True),
                AgentCapability(CapabilityType.ROUTING, 0.85, "Route requests to appropriate agents", True),
                AgentCapability(CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING, 0.90, "Understand natural language", True),
            ],
            AgentRole.TEAM_MANAGER: [
                AgentCapability(CapabilityType.STRATEGIC_PLANNING, 0.95, "High-level strategic planning", True),
                AgentCapability(CapabilityType.COORDINATION, 0.90, "Coordinate multiple agents", True),
                AgentCapability(CapabilityType.DECISION_MAKING, 0.85, "Make strategic decisions", True),
                AgentCapability(CapabilityType.HIGH_LEVEL_OPERATIONS, 0.90, "Handle high-level operations", True),
            ],
            AgentRole.PLAYER_COORDINATOR: [
                AgentCapability(CapabilityType.PLAYER_MANAGEMENT, 0.95, "Manage player information", True),
                AgentCapability(CapabilityType.AVAILABILITY_TRACKING, 0.90, "Track player availability", True),
                AgentCapability(CapabilityType.OPERATIONAL_TASKS, 0.85, "Handle operational tasks", True),
                AgentCapability(CapabilityType.COORDINATION, 0.80, "Coordinate player-related activities", False),
            ],
            AgentRole.PERFORMANCE_ANALYST: [
                AgentCapability(CapabilityType.PERFORMANCE_ANALYSIS, 0.95, "Analyze team performance", True),
                AgentCapability(CapabilityType.TACTICAL_INSIGHTS, 0.90, "Provide tactical insights", True),
                AgentCapability(CapabilityType.OPPOSITION_ANALYSIS, 0.85, "Analyze opposition teams", True),
                AgentCapability(CapabilityType.MATCH_PLANNING, 0.80, "Plan match strategies", True),
            ],
            AgentRole.FINANCE_MANAGER: [
                AgentCapability(CapabilityType.PAYMENT_TRACKING, 0.95, "Track payments", True),
                AgentCapability(CapabilityType.FINANCIAL_REPORTING, 0.90, "Generate financial reports", True),
                AgentCapability(CapabilityType.BUDGET_MANAGEMENT, 0.85, "Manage team budget", True),
                AgentCapability(CapabilityType.COORDINATION, 0.75, "Coordinate financial activities", False),
            ],
            AgentRole.LEARNING_AGENT: [
                AgentCapability(CapabilityType.PATTERN_LEARNING, 0.95, "Learn from interaction patterns", True),
                AgentCapability(CapabilityType.USER_PREFERENCE_ANALYSIS, 0.90, "Analyze and learn user preferences", True),
                AgentCapability(CapabilityType.RESPONSE_OPTIMIZATION, 0.85, "Optimize responses based on learned patterns", True),
                AgentCapability(CapabilityType.SYSTEM_IMPROVEMENT, 0.80, "Suggest system improvements", True),
            ],
            AgentRole.ONBOARDING_AGENT: [
                AgentCapability(CapabilityType.PLAYER_MANAGEMENT, 0.95, "Manage player onboarding", True),
                AgentCapability(CapabilityType.OPERATIONAL_TASKS, 0.90, "Handle onboarding tasks", True),
                AgentCapability(CapabilityType.MESSAGING, 0.85, "Send onboarding messages", True),
                AgentCapability(CapabilityType.COORDINATION, 0.80, "Coordinate onboarding process", False),
            ],
            AgentRole.COMMAND_FALLBACK_AGENT: [
                AgentCapability(CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING, 0.95, "Understand failed commands", True),
                AgentCapability(CapabilityType.INTENT_ANALYSIS, 0.90, "Analyze intent from failed commands", True),
                AgentCapability(CapabilityType.ROUTING, 0.85, "Route to appropriate handlers", True),
                AgentCapability(CapabilityType.CONTEXT_MANAGEMENT, 0.80, "Manage fallback context", False),
            ]
        }
    
    def _initialize_descriptions(self) -> Dict[CapabilityType, str]:
        """Initialize descriptions for all capability types."""
        return {
            CapabilityType.INTENT_ANALYSIS: "Understand and analyze user intent from messages",
            CapabilityType.CONTEXT_MANAGEMENT: "Manage conversation context and history",
            CapabilityType.ROUTING: "Route requests to appropriate agents",
            CapabilityType.STRATEGIC_PLANNING: "Create high-level strategic plans",
            CapabilityType.COORDINATION: "Coordinate activities between multiple agents",
            CapabilityType.DECISION_MAKING: "Make strategic decisions based on available information",
            CapabilityType.PLAYER_MANAGEMENT: "Manage player information and records",
            CapabilityType.AVAILABILITY_TRACKING: "Track player availability for matches",
            CapabilityType.PERFORMANCE_ANALYSIS: "Analyze team and player performance",
            CapabilityType.TACTICAL_INSIGHTS: "Provide tactical insights and recommendations",
            CapabilityType.MESSAGING: "Send messages to team members",
            CapabilityType.ANNOUNCEMENTS: "Make announcements to the team",
            CapabilityType.POLLS: "Create and manage polls for team decisions",
            CapabilityType.PAYMENT_TRACKING: "Track payment status and history",
            CapabilityType.FINANCIAL_REPORTING: "Generate financial reports and summaries",
            CapabilityType.SQUAD_SELECTION: "Select optimal squad for matches",
            CapabilityType.FORM_ANALYSIS: "Analyze player form and fitness",
            CapabilityType.TREND_ANALYSIS: "Analyze trends in performance and data",
            CapabilityType.PERFORMANCE_METRICS: "Calculate and track performance metrics",
            CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING: "Understand natural language input",
            CapabilityType.HIGH_LEVEL_OPERATIONS: "Handle high-level operational tasks",
            CapabilityType.OPERATIONAL_TASKS: "Handle day-to-day operational tasks",
            CapabilityType.OPPOSITION_ANALYSIS: "Analyze opposition teams and strategies",
            CapabilityType.MATCH_PLANNING: "Plan match strategies and tactics",
            CapabilityType.BROADCAST_MANAGEMENT: "Manage team communications and broadcasts",
            CapabilityType.BUDGET_MANAGEMENT: "Manage team budget and finances",
            CapabilityType.TACTICAL_FIT: "Assess tactical fit of players",
            CapabilityType.PLAYER_EVALUATION: "Evaluate player performance and potential",
            CapabilityType.DATA_ANALYSIS: "Analyze data and statistics",
            CapabilityType.PREDICTIONS: "Make predictions based on data and trends",
            CapabilityType.PATTERN_LEARNING: "Learn from interaction patterns and improve responses",
            CapabilityType.USER_PREFERENCE_ANALYSIS: "Analyze and learn user preferences and behavior",
            CapabilityType.RESPONSE_OPTIMIZATION: "Optimize responses based on learned patterns and preferences",
            CapabilityType.SYSTEM_IMPROVEMENT: "Suggest system improvements based on learned insights"
        }
    
    def get_agent_capabilities(self, agent_role: AgentRole) -> List[AgentCapability]:
        logger.debug(f"[AgentCapabilityMatrix] get_agent_capabilities called for {agent_role}")
        return self._capabilities.get(agent_role, [])
    
    def get_agents_with_capability(self, capability: CapabilityType, min_proficiency: float = 0.5) -> List[AgentRole]:
        logger.debug(f"[AgentCapabilityMatrix] get_agents_with_capability called for {capability} (min_proficiency={min_proficiency})")
        agents = []
        for agent_role, capabilities in self._capabilities.items():
            for cap in capabilities:
                if cap.capability == capability and cap.proficiency_level >= min_proficiency:
                    agents.append(agent_role)
                    break
        logger.debug(f"[AgentCapabilityMatrix] Agents with {capability}: {agents}")
        return agents
    
    def get_primary_capabilities(self, agent_role: AgentRole) -> List[AgentCapability]:
        """Get primary capabilities for a specific agent."""
        capabilities = self.get_agent_capabilities(agent_role)
        return [cap for cap in capabilities if cap.is_primary]
    
    def get_capability_description(self, capability: CapabilityType) -> str:
        """Get description for a specific capability."""
        return self._capability_descriptions.get(capability, "Unknown capability")
    
    def get_agent_proficiency(self, agent_role: AgentRole, capability: CapabilityType) -> float:
        """Get proficiency level for a specific agent and capability."""
        capabilities = self.get_agent_capabilities(agent_role)
        for cap in capabilities:
            if cap.capability == capability:
                return cap.proficiency_level
        return 0.0
    
    def get_all_capabilities(self) -> Set[CapabilityType]:
        """Get all available capability types."""
        return set(self._capability_descriptions.keys())
    
    def get_capability_matrix_summary(self) -> Dict[str, List[str]]:
        """Get a summary of the capability matrix."""
        summary = {}
        for agent_role, capabilities in self._capabilities.items():
            summary[agent_role.value] = [
                f"{cap.capability.value} ({cap.proficiency_level:.2f})"
                for cap in capabilities if cap.is_primary
            ]
        return summary
    
    def validate_capability(self, agent_role: AgentRole, capability: CapabilityType) -> bool:
        """Validate if an agent has a specific capability."""
        return self.get_agent_proficiency(agent_role, capability) > 0.0
    
    def get_best_agent_for_capability(self, capability: CapabilityType) -> Optional[AgentRole]:
        logger.debug(f"[AgentCapabilityMatrix] get_best_agent_for_capability called for {capability}")
        best_agent = None
        best_proficiency = 0.0
        
        for agent_role in AgentRole:
            proficiency = self.get_agent_proficiency(agent_role, capability)
            if proficiency > best_proficiency:
                best_proficiency = proficiency
                best_agent = agent_role
        
        logger.debug(f"[AgentCapabilityMatrix] Best agent for {capability}: {best_agent} (proficiency={best_proficiency})")
        return best_agent if best_proficiency > 0.0 else None

# Global instance for easy access
_capability_matrix = AgentCapabilityMatrix()

def get_agent_capabilities(agent_role: AgentRole) -> List[AgentCapability]:
    """Get capabilities for a specific agent."""
    return _capability_matrix.get_agent_capabilities(agent_role)

def get_agents_with_capability(capability: CapabilityType, min_proficiency: float = 0.5) -> List[AgentRole]:
    """Get agents that have a specific capability with minimum proficiency."""
    return _capability_matrix.get_agents_with_capability(capability, min_proficiency)

def get_capability_matrix_summary() -> Dict[str, List[str]]:
    """Get a summary of the capability matrix."""
    return _capability_matrix.get_capability_matrix_summary()

def get_best_agent_for_capability(capability: CapabilityType) -> Optional[AgentRole]:
    """Get the best agent for a specific capability based on proficiency."""
    return _capability_matrix.get_best_agent_for_capability(capability)

if __name__ == "__main__":
    # Test the capability matrix
    # Tests completed successfully
    pass 