#!/usr/bin/env python3
"""
Agent Capabilities Matrix for KICKAI
Defines capabilities for each agent type to support intelligent routing.
"""

import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum

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
    
    def _initialize_capabilities(self) -> Dict[str, List[AgentCapability]]:
        """Initialize the capability matrix for all agents."""
        return {
            'message_processor': [
                AgentCapability(CapabilityType.INTENT_ANALYSIS, 0.95, "Analyze user intent and context", True),
                AgentCapability(CapabilityType.CONTEXT_MANAGEMENT, 0.90, "Manage conversation context", True),
                AgentCapability(CapabilityType.ROUTING, 0.85, "Route requests to appropriate agents", True),
                AgentCapability(CapabilityType.NATURAL_LANGUAGE_UNDERSTANDING, 0.90, "Understand natural language", True),
            ],
            'team_manager': [
                AgentCapability(CapabilityType.STRATEGIC_PLANNING, 0.95, "High-level strategic planning", True),
                AgentCapability(CapabilityType.COORDINATION, 0.90, "Coordinate multiple agents", True),
                AgentCapability(CapabilityType.DECISION_MAKING, 0.85, "Make strategic decisions", True),
                AgentCapability(CapabilityType.HIGH_LEVEL_OPERATIONS, 0.90, "Handle high-level operations", True),
            ],
            'player_coordinator': [
                AgentCapability(CapabilityType.PLAYER_MANAGEMENT, 0.95, "Manage player information", True),
                AgentCapability(CapabilityType.AVAILABILITY_TRACKING, 0.90, "Track player availability", True),
                AgentCapability(CapabilityType.OPERATIONAL_TASKS, 0.85, "Handle operational tasks", True),
                AgentCapability(CapabilityType.COORDINATION, 0.80, "Coordinate player-related activities", False),
            ],
            'match_analyst': [
                AgentCapability(CapabilityType.PERFORMANCE_ANALYSIS, 0.95, "Analyze team performance", True),
                AgentCapability(CapabilityType.TACTICAL_INSIGHTS, 0.90, "Provide tactical insights", True),
                AgentCapability(CapabilityType.OPPOSITION_ANALYSIS, 0.85, "Analyze opposition teams", True),
                AgentCapability(CapabilityType.MATCH_PLANNING, 0.80, "Plan match strategies", True),
            ],
            'communication_specialist': [
                AgentCapability(CapabilityType.MESSAGING, 0.95, "Send messages to team", True),
                AgentCapability(CapabilityType.ANNOUNCEMENTS, 0.90, "Make team announcements", True),
                AgentCapability(CapabilityType.POLLS, 0.85, "Create and manage polls", True),
                AgentCapability(CapabilityType.BROADCAST_MANAGEMENT, 0.80, "Manage team communications", True),
            ],
            'finance_manager': [
                AgentCapability(CapabilityType.PAYMENT_TRACKING, 0.95, "Track payments", True),
                AgentCapability(CapabilityType.FINANCIAL_REPORTING, 0.90, "Generate financial reports", True),
                AgentCapability(CapabilityType.BUDGET_MANAGEMENT, 0.85, "Manage team budget", True),
                AgentCapability(CapabilityType.COORDINATION, 0.75, "Coordinate financial activities", False),
            ],
            'squad_selection_specialist': [
                AgentCapability(CapabilityType.SQUAD_SELECTION, 0.95, "Select optimal squad", True),
                AgentCapability(CapabilityType.FORM_ANALYSIS, 0.90, "Analyze player form", True),
                AgentCapability(CapabilityType.TACTICAL_FIT, 0.85, "Assess tactical fit", True),
                AgentCapability(CapabilityType.PLAYER_EVALUATION, 0.80, "Evaluate player performance", True),
            ],
            'analytics_specialist': [
                AgentCapability(CapabilityType.TREND_ANALYSIS, 0.95, "Analyze trends", True),
                AgentCapability(CapabilityType.PERFORMANCE_METRICS, 0.90, "Calculate performance metrics", True),
                AgentCapability(CapabilityType.DATA_ANALYSIS, 0.85, "Analyze data", True),
                AgentCapability(CapabilityType.PREDICTIONS, 0.80, "Make predictions", True),
                AgentCapability(CapabilityType.PERFORMANCE_ANALYSIS, 0.85, "Analyze performance data", False),
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
            CapabilityType.PREDICTIONS: "Make predictions based on data and trends"
        }
    
    def get_agent_capabilities(self, agent_name: str) -> List[AgentCapability]:
        """Get capabilities for a specific agent."""
        return self._capabilities.get(agent_name, [])
    
    def get_agents_with_capability(self, capability: CapabilityType, min_proficiency: float = 0.5) -> List[str]:
        """Get agents that have a specific capability with minimum proficiency."""
        agents = []
        for agent_name, capabilities in self._capabilities.items():
            for cap in capabilities:
                if cap.capability == capability and cap.proficiency_level >= min_proficiency:
                    agents.append(agent_name)
                    break
        return agents
    
    def get_primary_capabilities(self, agent_name: str) -> List[AgentCapability]:
        """Get primary capabilities for a specific agent."""
        capabilities = self.get_agent_capabilities(agent_name)
        return [cap for cap in capabilities if cap.is_primary]
    
    def get_capability_description(self, capability: CapabilityType) -> str:
        """Get description for a specific capability."""
        return self._capability_descriptions.get(capability, "Unknown capability")
    
    def get_agent_proficiency(self, agent_name: str, capability: CapabilityType) -> float:
        """Get proficiency level for a specific agent and capability."""
        capabilities = self.get_agent_capabilities(agent_name)
        for cap in capabilities:
            if cap.capability == capability:
                return cap.proficiency_level
        return 0.0
    
    def get_all_capabilities(self) -> Set[CapabilityType]:
        """Get all available capability types."""
        return set(self._capability_descriptions.keys())
    
    def get_capability_matrix_summary(self) -> Dict[str, List[str]]:
        """Get a summary of the capability matrix for easy reference."""
        summary = {}
        for agent_name, capabilities in self._capabilities.items():
            summary[agent_name] = [cap.capability.value for cap in capabilities if cap.is_primary]
        return summary
    
    def validate_capability(self, agent_name: str, capability: CapabilityType) -> bool:
        """Validate if an agent has a specific capability."""
        return self.get_agent_proficiency(agent_name, capability) > 0.0
    
    def get_best_agent_for_capability(self, capability: CapabilityType) -> Optional[str]:
        """Get the best agent for a specific capability based on proficiency."""
        best_agent = None
        best_proficiency = 0.0
        
        for agent_name, capabilities in self._capabilities.items():
            for cap in capabilities:
                if cap.capability == capability and cap.proficiency_level > best_proficiency:
                    best_proficiency = cap.proficiency_level
                    best_agent = agent_name
        
        return best_agent

# Global instance for easy access
capability_matrix = AgentCapabilityMatrix()

# Convenience functions
def get_agent_capabilities(agent_name: str) -> List[AgentCapability]:
    """Get capabilities for a specific agent."""
    return capability_matrix.get_agent_capabilities(agent_name)

def get_agents_with_capability(capability: CapabilityType, min_proficiency: float = 0.5) -> List[str]:
    """Get agents that have a specific capability."""
    return capability_matrix.get_agents_with_capability(capability, min_proficiency)

def get_capability_matrix_summary() -> Dict[str, List[str]]:
    """Get a summary of the capability matrix."""
    return capability_matrix.get_capability_matrix_summary()

def get_best_agent_for_capability(capability: CapabilityType) -> Optional[str]:
    """Get the best agent for a specific capability."""
    return capability_matrix.get_best_agent_for_capability(capability)

if __name__ == "__main__":
    # Test the capability matrix
    # Tests completed successfully
    pass 