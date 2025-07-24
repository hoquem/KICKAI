#!/usr/bin/env python3
"""
Refined Agent Capabilities System for KICKAI

This module provides a hierarchical capability system with:
- Distinct and clearly defined capability types
- Hierarchical structure where broader capabilities encompass specific ones
- Improved accuracy for the CapabilityBasedRouter
- Clear capability relationships and dependencies
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from kickai.core.enums import AgentRole

logger = logging.getLogger(__name__)


class CapabilityLevel(Enum):
    """Hierarchical levels for capabilities."""
    FOUNDATIONAL = "foundational"      # Basic system capabilities
    OPERATIONAL = "operational"        # Day-to-day operations
    TACTICAL = "tactical"             # Tactical decision making
    STRATEGIC = "strategic"           # Strategic planning and coordination
    SPECIALIZED = "specialized"       # Domain-specific expertise


class CapabilityCategory(Enum):
    """Categories for grouping related capabilities."""
    COMMUNICATION = "communication"           # Messaging, announcements, polls
    DATA_MANAGEMENT = "data_management"       # Data retrieval, analysis, storage
    USER_INTERACTION = "user_interaction"     # User management, onboarding
    FINANCIAL = "financial"                   # Payment, budgeting, reporting
    PERFORMANCE = "performance"               # Analysis, metrics, insights
    PLANNING = "planning"                     # Strategic, tactical, operational
    LEARNING = "learning"                     # Pattern learning, optimization
    COORDINATION = "coordination"             # Multi-agent coordination
    DECISION_MAKING = "decision_making"       # Decision processes
    SYSTEM_OPERATIONS = "system_operations"   # System-level operations


class RefinedCapabilityType(Enum):
    """
    Refined capability types with clear definitions and hierarchical relationships.

    Each capability is:
    - Distinct from others
    - Clearly defined
    - Categorized appropriately
    - Assigned a hierarchical level
    """

    # ============================================================================
    # FOUNDATIONAL CAPABILITIES (Level 1)
    # ============================================================================

    # Communication Category
    MESSAGE_PROCESSING = "message_processing"           # Process and route messages
    CONTEXT_MANAGEMENT = "context_management"           # Manage conversation context
    NATURAL_LANGUAGE_UNDERSTANDING = "natural_language_understanding"  # Understand natural language

    # Data Management Category
    DATA_RETRIEVAL = "data_retrieval"                   # Retrieve data from various sources
    DATA_VALIDATION = "data_validation"                 # Validate data integrity
    INFORMATION_STORAGE = "information_storage"         # Store and organize information

    # System Operations Category
    ROUTING = "routing"                                 # Route requests to appropriate handlers
    ERROR_HANDLING = "error_handling"                   # Handle and recover from errors
    SYSTEM_MONITORING = "system_monitoring"             # Monitor system health and performance

    # ============================================================================
    # OPERATIONAL CAPABILITIES (Level 2)
    # ============================================================================

    # User Interaction Category
    USER_REGISTRATION = "user_registration"             # Register new users
    USER_AUTHENTICATION = "user_authentication"         # Authenticate user identity
    USER_PROFILE_MANAGEMENT = "user_profile_management" # Manage user profiles

    # Communication Category
    MESSAGE_COMPOSITION = "message_composition"         # Compose structured messages
    ANNOUNCEMENT_CREATION = "announcement_creation"     # Create team announcements
    POLL_MANAGEMENT = "poll_management"                 # Create and manage polls

    # Data Management Category
    RECORD_KEEPING = "record_keeping"                   # Maintain accurate records
    DATA_QUERYING = "data_querying"                     # Query data with filters
    REPORT_GENERATION = "report_generation"             # Generate basic reports

    # ============================================================================
    # TACTICAL CAPABILITIES (Level 3)
    # ============================================================================

    # User Interaction Category
    PLAYER_ONBOARDING = "player_onboarding"             # Guide players through registration
    PLAYER_STATUS_TRACKING = "player_status_tracking"   # Track player status and eligibility
    PLAYER_APPROVAL_MANAGEMENT = "player_approval_management"  # Manage player approvals

    # Financial Category
    PAYMENT_PROCESSING = "payment_processing"           # Process payments and fees
    PAYMENT_TRACKING = "payment_tracking"               # Track payment status
    FINANCIAL_RECORD_KEEPING = "financial_record_keeping"  # Maintain financial records

    # Performance Category
    PERFORMANCE_DATA_COLLECTION = "performance_data_collection"  # Collect performance data
    BASIC_ANALYTICS = "basic_analytics"                 # Perform basic data analysis
    METRIC_CALCULATION = "metric_calculation"           # Calculate performance metrics

    # Planning Category
    TACTICAL_PLANNING = "tactical_planning"             # Plan tactical operations
    RESOURCE_ALLOCATION = "resource_allocation"         # Allocate resources effectively
    SCHEDULE_MANAGEMENT = "schedule_management"         # Manage schedules and timelines

    # ============================================================================
    # STRATEGIC CAPABILITIES (Level 4)
    # ============================================================================

    # Planning Category
    STRATEGIC_PLANNING = "strategic_planning"           # High-level strategic planning
    LONG_TERM_GOAL_SETTING = "long_term_goal_setting"   # Set long-term objectives
    STRATEGIC_ANALYSIS = "strategic_analysis"           # Analyze strategic implications

    # Coordination Category
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"  # Coordinate multiple agents
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"   # Orchestrate complex workflows
    CROSS_FUNCTIONAL_INTEGRATION = "cross_functional_integration"  # Integrate across functions

    # Decision Making Category
    STRATEGIC_DECISION_MAKING = "strategic_decision_making"  # Make strategic decisions
    RISK_ASSESSMENT = "risk_assessment"                 # Assess risks and opportunities
    OPTION_EVALUATION = "option_evaluation"             # Evaluate different options

    # Performance Category
    ADVANCED_ANALYTICS = "advanced_analytics"           # Perform advanced data analysis
    TREND_ANALYSIS = "trend_analysis"                   # Analyze trends and patterns
    PREDICTIVE_MODELING = "predictive_modeling"         # Build predictive models

    # Financial Category
    FINANCIAL_PLANNING = "financial_planning"           # Plan financial strategies
    BUDGET_MANAGEMENT = "budget_management"             # Manage budgets and forecasts
    FINANCIAL_ANALYSIS = "financial_analysis"           # Analyze financial performance

    # ============================================================================
    # SPECIALIZED CAPABILITIES (Level 5)
    # ============================================================================

    # Learning Category
    PATTERN_RECOGNITION = "pattern_recognition"         # Recognize patterns in data
    MACHINE_LEARNING = "machine_learning"               # Apply machine learning techniques
    ADAPTIVE_OPTIMIZATION = "adaptive_optimization"     # Optimize based on learned patterns

    # Performance Category
    COMPETITIVE_ANALYSIS = "competitive_analysis"       # Analyze competition and opposition
    TACTICAL_INSIGHTS = "tactical_insights"             # Provide tactical insights
    PERFORMANCE_OPTIMIZATION = "performance_optimization"  # Optimize performance strategies

    # User Interaction Category
    PERSONALIZATION = "personalization"                 # Personalize user experiences
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"         # Analyze user behavior patterns
    USER_EXPERIENCE_OPTIMIZATION = "user_experience_optimization"  # Optimize user experience

    # System Operations Category
    SYSTEM_OPTIMIZATION = "system_optimization"         # Optimize system performance
    INTELLIGENT_ROUTING = "intelligent_routing"         # Route requests intelligently
    AUTOMATED_DECISION_MAKING = "automated_decision_making"  # Make automated decisions


@dataclass
class CapabilityDefinition:
    """Complete definition of a capability with metadata."""
    capability: RefinedCapabilityType
    level: CapabilityLevel
    category: CapabilityCategory
    description: str
    keywords: list[str]
    parent_capabilities: list[RefinedCapabilityType] = None
    child_capabilities: list[RefinedCapabilityType] = None
    dependencies: list[RefinedCapabilityType] = None

    def __post_init__(self):
        if self.parent_capabilities is None:
            self.parent_capabilities = []
        if self.child_capabilities is None:
            self.child_capabilities = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class AgentCapabilityProfile:
    """Represents an agent's capability profile with hierarchical information."""
    capability: RefinedCapabilityType
    proficiency_level: float  # 0.0 to 1.0
    is_primary: bool = False
    is_specialized: bool = False
    confidence_level: float = 0.8  # Confidence in proficiency assessment


class HierarchicalCapabilityManager:
    """Manages hierarchical capabilities and their relationships."""

    def __init__(self):
        self._capability_definitions = self._initialize_capability_definitions()
        self._hierarchical_relationships = self._build_hierarchical_relationships()
        self._capability_matrix = self._initialize_capability_matrix()
        logger.info("[HierarchicalCapabilityManager] Initialized with hierarchical capability system")

    def _initialize_capability_definitions(self) -> dict[RefinedCapabilityType, CapabilityDefinition]:
        """Initialize all capability definitions with hierarchical information."""
        definitions = {}

        # FOUNDATIONAL CAPABILITIES
        definitions[RefinedCapabilityType.MESSAGE_PROCESSING] = CapabilityDefinition(
            capability=RefinedCapabilityType.MESSAGE_PROCESSING,
            level=CapabilityLevel.FOUNDATIONAL,
            category=CapabilityCategory.COMMUNICATION,
            description="Process and route messages between users and agents",
            keywords=["message", "process", "route", "communication"]
        )

        definitions[RefinedCapabilityType.CONTEXT_MANAGEMENT] = CapabilityDefinition(
            capability=RefinedCapabilityType.CONTEXT_MANAGEMENT,
            level=CapabilityLevel.FOUNDATIONAL,
            category=CapabilityCategory.COMMUNICATION,
            description="Manage conversation context and maintain conversation history",
            keywords=["context", "conversation", "history", "memory"]
        )

        definitions[RefinedCapabilityType.NATURAL_LANGUAGE_UNDERSTANDING] = CapabilityDefinition(
            capability=RefinedCapabilityType.NATURAL_LANGUAGE_UNDERSTANDING,
            level=CapabilityLevel.FOUNDATIONAL,
            category=CapabilityCategory.COMMUNICATION,
            description="Understand and interpret natural language input",
            keywords=["language", "understand", "interpret", "nlp"]
        )

        definitions[RefinedCapabilityType.DATA_RETRIEVAL] = CapabilityDefinition(
            capability=RefinedCapabilityType.DATA_RETRIEVAL,
            level=CapabilityLevel.FOUNDATIONAL,
            category=CapabilityCategory.DATA_MANAGEMENT,
            description="Retrieve data from various sources and databases",
            keywords=["data", "retrieve", "fetch", "query"]
        )

        definitions[RefinedCapabilityType.ROUTING] = CapabilityDefinition(
            capability=RefinedCapabilityType.ROUTING,
            level=CapabilityLevel.FOUNDATIONAL,
            category=CapabilityCategory.SYSTEM_OPERATIONS,
            description="Route requests to appropriate handlers and agents",
            keywords=["route", "direct", "forward", "dispatch"]
        )

        # OPERATIONAL CAPABILITIES
        definitions[RefinedCapabilityType.USER_REGISTRATION] = CapabilityDefinition(
            capability=RefinedCapabilityType.USER_REGISTRATION,
            level=CapabilityLevel.OPERATIONAL,
            category=CapabilityCategory.USER_INTERACTION,
            description="Register new users and create user accounts",
            keywords=["register", "user", "account", "signup"],
            dependencies=[RefinedCapabilityType.DATA_VALIDATION, RefinedCapabilityType.INFORMATION_STORAGE]
        )

        definitions[RefinedCapabilityType.MESSAGE_COMPOSITION] = CapabilityDefinition(
            capability=RefinedCapabilityType.MESSAGE_COMPOSITION,
            level=CapabilityLevel.OPERATIONAL,
            category=CapabilityCategory.COMMUNICATION,
            description="Compose structured and formatted messages",
            keywords=["compose", "format", "structure", "message"],
            dependencies=[RefinedCapabilityType.MESSAGE_PROCESSING]
        )

        definitions[RefinedCapabilityType.RECORD_KEEPING] = CapabilityDefinition(
            capability=RefinedCapabilityType.RECORD_KEEPING,
            level=CapabilityLevel.OPERATIONAL,
            category=CapabilityCategory.DATA_MANAGEMENT,
            description="Maintain accurate and organized records",
            keywords=["record", "maintain", "organize", "track"],
            dependencies=[RefinedCapabilityType.DATA_RETRIEVAL, RefinedCapabilityType.INFORMATION_STORAGE]
        )

        # TACTICAL CAPABILITIES
        definitions[RefinedCapabilityType.PLAYER_ONBOARDING] = CapabilityDefinition(
            capability=RefinedCapabilityType.PLAYER_ONBOARDING,
            level=CapabilityLevel.TACTICAL,
            category=CapabilityCategory.USER_INTERACTION,
            description="Guide players through the complete onboarding process",
            keywords=["onboard", "player", "guide", "process"],
            dependencies=[RefinedCapabilityType.USER_REGISTRATION, RefinedCapabilityType.MESSAGE_COMPOSITION]
        )

        definitions[RefinedCapabilityType.PAYMENT_PROCESSING] = CapabilityDefinition(
            capability=RefinedCapabilityType.PAYMENT_PROCESSING,
            level=CapabilityLevel.TACTICAL,
            category=CapabilityCategory.FINANCIAL,
            description="Process payments and handle financial transactions",
            keywords=["payment", "process", "transaction", "financial"],
            dependencies=[RefinedCapabilityType.DATA_VALIDATION, RefinedCapabilityType.FINANCIAL_RECORD_KEEPING]
        )

        definitions[RefinedCapabilityType.PERFORMANCE_DATA_COLLECTION] = CapabilityDefinition(
            capability=RefinedCapabilityType.PERFORMANCE_DATA_COLLECTION,
            level=CapabilityLevel.TACTICAL,
            category=CapabilityCategory.PERFORMANCE,
            description="Collect and organize performance-related data",
            keywords=["performance", "collect", "data", "metrics"],
            dependencies=[RefinedCapabilityType.DATA_RETRIEVAL, RefinedCapabilityType.RECORD_KEEPING]
        )

        # STRATEGIC CAPABILITIES
        definitions[RefinedCapabilityType.STRATEGIC_PLANNING] = CapabilityDefinition(
            capability=RefinedCapabilityType.STRATEGIC_PLANNING,
            level=CapabilityLevel.STRATEGIC,
            category=CapabilityCategory.PLANNING,
            description="Create high-level strategic plans and objectives",
            keywords=["strategic", "plan", "objective", "high-level"],
            dependencies=[RefinedCapabilityType.STRATEGIC_ANALYSIS, RefinedCapabilityType.LONG_TERM_GOAL_SETTING]
        )

        definitions[RefinedCapabilityType.MULTI_AGENT_COORDINATION] = CapabilityDefinition(
            capability=RefinedCapabilityType.MULTI_AGENT_COORDINATION,
            level=CapabilityLevel.STRATEGIC,
            category=CapabilityCategory.COORDINATION,
            description="Coordinate activities between multiple agents",
            keywords=["coordinate", "multi-agent", "collaboration", "orchestration"],
            dependencies=[RefinedCapabilityType.WORKFLOW_ORCHESTRATION]
        )

        definitions[RefinedCapabilityType.ADVANCED_ANALYTICS] = CapabilityDefinition(
            capability=RefinedCapabilityType.ADVANCED_ANALYTICS,
            level=CapabilityLevel.STRATEGIC,
            category=CapabilityCategory.PERFORMANCE,
            description="Perform advanced data analysis and insights generation",
            keywords=["analytics", "advanced", "analysis", "insights"],
            dependencies=[RefinedCapabilityType.BASIC_ANALYTICS, RefinedCapabilityType.TREND_ANALYSIS]
        )

        # SPECIALIZED CAPABILITIES
        definitions[RefinedCapabilityType.PATTERN_RECOGNITION] = CapabilityDefinition(
            capability=RefinedCapabilityType.PATTERN_RECOGNITION,
            level=CapabilityLevel.SPECIALIZED,
            category=CapabilityCategory.LEARNING,
            description="Recognize patterns in data and user behavior",
            keywords=["pattern", "recognize", "learn", "behavior"],
            dependencies=[RefinedCapabilityType.ADVANCED_ANALYTICS, RefinedCapabilityType.BEHAVIORAL_ANALYSIS]
        )

        definitions[RefinedCapabilityType.COMPETITIVE_ANALYSIS] = CapabilityDefinition(
            capability=RefinedCapabilityType.COMPETITIVE_ANALYSIS,
            level=CapabilityLevel.SPECIALIZED,
            category=CapabilityCategory.PERFORMANCE,
            description="Analyze competition and provide competitive insights",
            keywords=["competitive", "opposition", "analysis", "insights"],
            dependencies=[RefinedCapabilityType.ADVANCED_ANALYTICS, RefinedCapabilityType.TACTICAL_INSIGHTS]
        )

        definitions[RefinedCapabilityType.PERSONALIZATION] = CapabilityDefinition(
            capability=RefinedCapabilityType.PERSONALIZATION,
            level=CapabilityLevel.SPECIALIZED,
            category=CapabilityCategory.USER_INTERACTION,
            description="Personalize user experiences based on preferences and behavior",
            keywords=["personalize", "user", "experience", "preferences"],
            dependencies=[RefinedCapabilityType.BEHAVIORAL_ANALYSIS, RefinedCapabilityType.USER_EXPERIENCE_OPTIMIZATION]
        )

        definitions[RefinedCapabilityType.SYSTEM_OPTIMIZATION] = CapabilityDefinition(
            capability=RefinedCapabilityType.SYSTEM_OPTIMIZATION,
            level=CapabilityLevel.SPECIALIZED,
            category=CapabilityCategory.SYSTEM_OPERATIONS,
            description="Optimize system performance and route requests intelligently",
            keywords=["optimize", "system", "performance", "routing"],
            dependencies=[RefinedCapabilityType.INTELLIGENT_ROUTING, RefinedCapabilityType.AUTOMATED_DECISION_MAKING]
        )

        return definitions

    def _build_hierarchical_relationships(self) -> dict[RefinedCapabilityType, dict[str, list[RefinedCapabilityType]]]:
        """Build hierarchical relationships between capabilities."""
        relationships = {}

        # Define parent-child relationships
        parent_child_mappings = {
            # Foundational -> Operational
            RefinedCapabilityType.MESSAGE_PROCESSING: [RefinedCapabilityType.MESSAGE_COMPOSITION],
            RefinedCapabilityType.DATA_RETRIEVAL: [RefinedCapabilityType.RECORD_KEEPING],

            # Operational -> Tactical
            RefinedCapabilityType.USER_REGISTRATION: [RefinedCapabilityType.PLAYER_ONBOARDING],
            RefinedCapabilityType.RECORD_KEEPING: [RefinedCapabilityType.FINANCIAL_RECORD_KEEPING],

            # Tactical -> Strategic
            RefinedCapabilityType.PERFORMANCE_DATA_COLLECTION: [RefinedCapabilityType.ADVANCED_ANALYTICS],
            RefinedCapabilityType.TACTICAL_PLANNING: [RefinedCapabilityType.STRATEGIC_PLANNING],

            # Strategic -> Specialized
            RefinedCapabilityType.ADVANCED_ANALYTICS: [RefinedCapabilityType.PATTERN_RECOGNITION],
            RefinedCapabilityType.STRATEGIC_ANALYSIS: [RefinedCapabilityType.COMPETITIVE_ANALYSIS],
        }

        for capability in RefinedCapabilityType:
            relationships[capability] = {
                'parents': [],
                'children': [],
                'siblings': [],
                'dependencies': self._capability_definitions[capability].dependencies if capability in self._capability_definitions else []
            }

        # Build relationships
        for parent, children in parent_child_mappings.items():
            if parent in relationships:
                relationships[parent]['children'] = children
                for child in children:
                    if child in relationships:
                        relationships[child]['parents'].append(parent)

        return relationships

    def _initialize_capability_matrix(self) -> dict[AgentRole, list[AgentCapabilityProfile]]:
        """Initialize the capability matrix for all agents."""
        matrix = {}

        # Message Processor - Foundational and Operational
        matrix[AgentRole.MESSAGE_PROCESSOR] = [
            AgentCapabilityProfile(RefinedCapabilityType.MESSAGE_PROCESSING, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.CONTEXT_MANAGEMENT, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.NATURAL_LANGUAGE_UNDERSTANDING, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.ROUTING, 0.85, False),
            AgentCapabilityProfile(RefinedCapabilityType.MESSAGE_COMPOSITION, 0.85, False),
        ]

        # Team Manager - Strategic and Coordination
        matrix[AgentRole.TEAM_MANAGER] = [
            AgentCapabilityProfile(RefinedCapabilityType.STRATEGIC_PLANNING, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.MULTI_AGENT_COORDINATION, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.STRATEGIC_DECISION_MAKING, 0.85, True),
            AgentCapabilityProfile(RefinedCapabilityType.WORKFLOW_ORCHESTRATION, 0.90, False),
            AgentCapabilityProfile(RefinedCapabilityType.RESOURCE_ALLOCATION, 0.85, False),
        ]

        # Player Coordinator - Tactical and Operational
        matrix[AgentRole.PLAYER_COORDINATOR] = [
            AgentCapabilityProfile(RefinedCapabilityType.PLAYER_ONBOARDING, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.PLAYER_STATUS_TRACKING, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.PLAYER_APPROVAL_MANAGEMENT, 0.85, True),
            AgentCapabilityProfile(RefinedCapabilityType.USER_REGISTRATION, 0.90, False),
            AgentCapabilityProfile(RefinedCapabilityType.RECORD_KEEPING, 0.85, False),
        ]

        # Finance Manager - Tactical and Financial
        matrix[AgentRole.FINANCE_MANAGER] = [
            AgentCapabilityProfile(RefinedCapabilityType.PAYMENT_PROCESSING, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.PAYMENT_TRACKING, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.FINANCIAL_RECORD_KEEPING, 0.85, True),
            AgentCapabilityProfile(RefinedCapabilityType.BUDGET_MANAGEMENT, 0.90, False),
            AgentCapabilityProfile(RefinedCapabilityType.FINANCIAL_ANALYSIS, 0.85, False),
        ]

        # Performance Analyst - Strategic and Performance
        matrix[AgentRole.PERFORMANCE_ANALYST] = [
            AgentCapabilityProfile(RefinedCapabilityType.ADVANCED_ANALYTICS, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.TREND_ANALYSIS, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.PERFORMANCE_DATA_COLLECTION, 0.85, True),
            AgentCapabilityProfile(RefinedCapabilityType.METRIC_CALCULATION, 0.90, False),
            AgentCapabilityProfile(RefinedCapabilityType.PREDICTIVE_MODELING, 0.85, False),
        ]

        # Learning Agent - Specialized and Learning
        matrix[AgentRole.LEARNING_AGENT] = [
            AgentCapabilityProfile(RefinedCapabilityType.PATTERN_RECOGNITION, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.MACHINE_LEARNING, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.ADAPTIVE_OPTIMIZATION, 0.85, True),
            AgentCapabilityProfile(RefinedCapabilityType.BEHAVIORAL_ANALYSIS, 0.90, False),
            AgentCapabilityProfile(RefinedCapabilityType.SYSTEM_OPTIMIZATION, 0.85, False),
        ]

        # Onboarding Agent - Tactical and User Interaction
        matrix[AgentRole.ONBOARDING_AGENT] = [
            AgentCapabilityProfile(RefinedCapabilityType.PLAYER_ONBOARDING, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.USER_REGISTRATION, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.MESSAGE_COMPOSITION, 0.85, True),
            AgentCapabilityProfile(RefinedCapabilityType.USER_PROFILE_MANAGEMENT, 0.90, False),
            AgentCapabilityProfile(RefinedCapabilityType.DATA_VALIDATION, 0.85, False),
        ]

        # Command Fallback Agent - Foundational and Specialized
        matrix[AgentRole.COMMAND_FALLBACK_AGENT] = [
            AgentCapabilityProfile(RefinedCapabilityType.NATURAL_LANGUAGE_UNDERSTANDING, 0.95, True),
            AgentCapabilityProfile(RefinedCapabilityType.INTELLIGENT_ROUTING, 0.90, True),
            AgentCapabilityProfile(RefinedCapabilityType.ERROR_HANDLING, 0.85, True),
            AgentCapabilityProfile(RefinedCapabilityType.MESSAGE_PROCESSING, 0.90, False),
            AgentCapabilityProfile(RefinedCapabilityType.CONTEXT_MANAGEMENT, 0.85, False),
        ]

        return matrix

    def get_capability_definition(self, capability: RefinedCapabilityType) -> CapabilityDefinition | None:
        """Get the definition for a specific capability."""
        return self._capability_definitions.get(capability)

    def get_agent_capabilities(self, agent_role: AgentRole) -> list[AgentCapabilityProfile]:
        """Get all capabilities for a specific agent."""
        return self._capability_matrix.get(agent_role, [])

    def get_agents_with_capability(self, capability: RefinedCapabilityType, min_proficiency: float = 0.5) -> list[AgentRole]:
        """Get all agents that have a specific capability with minimum proficiency."""
        agents = []
        for agent_role, capabilities in self._capability_matrix.items():
            for cap_profile in capabilities:
                if cap_profile.capability == capability and cap_profile.proficiency_level >= min_proficiency:
                    agents.append(agent_role)
                    break
        return agents

    def get_capability_hierarchy(self, capability: RefinedCapabilityType) -> dict[str, list[RefinedCapabilityType]]:
        """Get the hierarchical relationships for a capability."""
        return self._hierarchical_relationships.get(capability, {
            'parents': [],
            'children': [],
            'siblings': [],
            'dependencies': []
        })

    def get_capabilities_by_level(self, level: CapabilityLevel) -> list[RefinedCapabilityType]:
        """Get all capabilities at a specific hierarchical level."""
        return [
            capability for capability, definition in self._capability_definitions.items()
            if definition.level == level
        ]

    def get_capabilities_by_category(self, category: CapabilityCategory) -> list[RefinedCapabilityType]:
        """Get all capabilities in a specific category."""
        return [
            capability for capability, definition in self._capability_definitions.items()
            if definition.category == category
        ]

    def find_best_agent_for_capability(self, capability: RefinedCapabilityType) -> AgentRole | None:
        """Find the best agent for a specific capability."""
        best_agent = None
        best_proficiency = 0.0

        for agent_role, capabilities in self._capability_matrix.items():
            for cap_profile in capabilities:
                if cap_profile.capability == capability and cap_profile.proficiency_level > best_proficiency:
                    best_proficiency = cap_profile.proficiency_level
                    best_agent = agent_role

        return best_agent if best_proficiency > 0.0 else None

    def get_agent_proficiency(self, agent_role: AgentRole, capability: RefinedCapabilityType) -> float:
        """Get proficiency level for a specific agent and capability."""
        capabilities = self.get_agent_capabilities(agent_role)
        for cap_profile in capabilities:
            if cap_profile.capability == capability:
                return cap_profile.proficiency_level
        return 0.0

    def get_related_capabilities(self, capability: RefinedCapabilityType) -> list[RefinedCapabilityType]:
        """Get capabilities related to the given capability (parents, children, siblings)."""
        hierarchy = self.get_capability_hierarchy(capability)
        related = set()
        related.update(hierarchy['parents'])
        related.update(hierarchy['children'])
        related.update(hierarchy['siblings'])
        related.update(hierarchy['dependencies'])
        return list(related)

    def get_capability_summary(self) -> dict[str, Any]:
        """Get a comprehensive summary of the capability system."""
        summary = {
            'total_capabilities': len(self._capability_definitions),
            'capabilities_by_level': {},
            'capabilities_by_category': {},
            'agent_capability_counts': {}
        }

        # Count by level
        for level in CapabilityLevel:
            summary['capabilities_by_level'][level.value] = len(self.get_capabilities_by_level(level))

        # Count by category
        for category in CapabilityCategory:
            summary['capabilities_by_category'][category.value] = len(self.get_capabilities_by_category(category))

        # Count by agent
        for agent_role, capabilities in self._capability_matrix.items():
            summary['agent_capability_counts'][agent_role.value] = len(capabilities)

        return summary


# Global instance for easy access
_hierarchical_capability_manager = HierarchicalCapabilityManager()

def get_hierarchical_capability_manager() -> HierarchicalCapabilityManager:
    """Get the global hierarchical capability manager instance."""
    return _hierarchical_capability_manager

def get_agent_capabilities(agent_role: AgentRole) -> list[AgentCapabilityProfile]:
    """Get capabilities for a specific agent."""
    return _hierarchical_capability_manager.get_agent_capabilities(agent_role)

def get_agents_with_capability(capability: RefinedCapabilityType, min_proficiency: float = 0.5) -> list[AgentRole]:
    """Get all agents that have a specific capability."""
    return _hierarchical_capability_manager.get_agents_with_capability(capability, min_proficiency)

def find_best_agent_for_capability(capability: RefinedCapabilityType) -> AgentRole | None:
    """Find the best agent for a specific capability."""
    return _hierarchical_capability_manager.find_best_agent_for_capability(capability)

def get_capability_definition(capability: RefinedCapabilityType) -> CapabilityDefinition | None:
    """Get the definition for a specific capability."""
    return _hierarchical_capability_manager.get_capability_definition(capability)
