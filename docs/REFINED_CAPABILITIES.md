# Refined Capabilities System for KICKAI

## Overview

The Refined Capabilities System provides a hierarchical capability structure that improves the accuracy of the CapabilityBasedRouter by ensuring each capability is distinct, clearly defined, and properly categorized. This system allows broader capabilities to encompass more specific ones, enabling more flexible and accurate agent routing.

## Architecture

### Hierarchical Levels

The system defines 5 hierarchical levels for capabilities:

1. **Foundational** (Level 1): Basic system capabilities
   - Message processing, context management, data retrieval
   - Core system operations and communication

2. **Operational** (Level 2): Day-to-day operations
   - User registration, message composition, record keeping
   - Standard operational tasks

3. **Tactical** (Level 3): Tactical decision making
   - Player onboarding, payment processing, performance data collection
   - Domain-specific tactical operations

4. **Strategic** (Level 4): Strategic planning and coordination
   - Strategic planning, multi-agent coordination, advanced analytics
   - High-level strategic operations

5. **Specialized** (Level 5): Domain-specific expertise
   - Pattern recognition, competitive analysis, personalization
   - Advanced specialized capabilities

### Capability Categories

Capabilities are organized into 10 categories:

- **Communication**: Messaging, announcements, polls
- **Data Management**: Data retrieval, analysis, storage
- **User Interaction**: User management, onboarding
- **Financial**: Payment, budgeting, reporting
- **Performance**: Analysis, metrics, insights
- **Planning**: Strategic, tactical, operational
- **Learning**: Pattern learning, optimization
- **Coordination**: Multi-agent coordination
- **Decision Making**: Decision processes
- **System Operations**: System-level operations

## Key Components

### RefinedCapabilityType Enum

Defines 18 distinct capability types with clear boundaries:

```python
class RefinedCapabilityType(Enum):
    # Foundational Capabilities
    MESSAGE_PROCESSING = "message_processing"
    CONTEXT_MANAGEMENT = "context_management"
    NATURAL_LANGUAGE_UNDERSTANDING = "natural_language_understanding"
    DATA_RETRIEVAL = "data_retrieval"
    ROUTING = "routing"
    
    # Operational Capabilities
    USER_REGISTRATION = "user_registration"
    MESSAGE_COMPOSITION = "message_composition"
    RECORD_KEEPING = "record_keeping"
    
    # Tactical Capabilities
    PLAYER_ONBOARDING = "player_onboarding"
    PAYMENT_PROCESSING = "payment_processing"
    PERFORMANCE_DATA_COLLECTION = "performance_data_collection"
    
    # Strategic Capabilities
    STRATEGIC_PLANNING = "strategic_planning"
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"
    ADVANCED_ANALYTICS = "advanced_analytics"
    
    # Specialized Capabilities
    PATTERN_RECOGNITION = "pattern_recognition"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    PERSONALIZATION = "personalization"
    SYSTEM_OPTIMIZATION = "system_optimization"
```

### CapabilityDefinition

Complete definition of a capability with metadata:

```python
@dataclass
class CapabilityDefinition:
    capability: RefinedCapabilityType
    level: CapabilityLevel
    category: CapabilityCategory
    description: str
    keywords: List[str]
    parent_capabilities: List[RefinedCapabilityType]
    child_capabilities: List[RefinedCapabilityType]
    dependencies: List[RefinedCapabilityType]
```

### AgentCapabilityProfile

Represents an agent's capability profile with hierarchical information:

```python
@dataclass
class AgentCapabilityProfile:
    capability: RefinedCapabilityType
    proficiency_level: float  # 0.0 to 1.0
    is_primary: bool = False
    is_specialized: bool = False
    confidence_level: float = 0.8
```

### HierarchicalCapabilityManager

Manages hierarchical capabilities and their relationships:

```python
class HierarchicalCapabilityManager:
    def get_capability_definition(self, capability: RefinedCapabilityType) -> Optional[CapabilityDefinition]
    def get_agent_capabilities(self, agent_role: AgentRole) -> List[AgentCapabilityProfile]
    def get_capability_hierarchy(self, capability: RefinedCapabilityType) -> Dict[str, List[RefinedCapabilityType]]
    def get_related_capabilities(self, capability: RefinedCapabilityType) -> List[RefinedCapabilityType]
    def find_best_agent_for_capability(self, capability: RefinedCapabilityType) -> Optional[AgentRole]
```

## Agent Capability Matrix

Each agent has a carefully defined set of capabilities across different levels:

### Message Processor
- **Foundational**: Message processing (0.95), Context management (0.90), Natural language understanding (0.90)
- **Operational**: Message composition (0.85)
- **System Operations**: Routing (0.85)

### Team Manager
- **Strategic**: Strategic planning (0.95), Multi-agent coordination (0.90)
- **Decision Making**: Strategic decision making (0.85)
- **Coordination**: Workflow orchestration (0.90), Resource allocation (0.85)

### Player Coordinator
- **Tactical**: Player onboarding (0.95), Player status tracking (0.90), Player approval management (0.85)
- **Operational**: User registration (0.90), Record keeping (0.85)

### Finance Manager
- **Tactical**: Payment processing (0.95), Payment tracking (0.90), Financial record keeping (0.85)
- **Financial**: Budget management (0.90), Financial analysis (0.85)

### Performance Analyst
- **Strategic**: Advanced analytics (0.95), Trend analysis (0.90)
- **Tactical**: Performance data collection (0.85)
- **Performance**: Metric calculation (0.90), Predictive modeling (0.85)

### Learning Agent
- **Specialized**: Pattern recognition (0.95), Machine learning (0.90), Adaptive optimization (0.85)
- **Learning**: Behavioral analysis (0.90), System optimization (0.85)

### Onboarding Agent
- **Tactical**: Player onboarding (0.95)
- **Operational**: User registration (0.90), Message composition (0.85)
- **User Interaction**: User profile management (0.90), Data validation (0.85)

### Command Fallback Agent
- **Foundational**: Natural language understanding (0.95), Message processing (0.90), Context management (0.85)
- **Specialized**: Intelligent routing (0.90), Error handling (0.85)

## Hierarchical Relationships

### Parent-Child Relationships

The system defines clear parent-child relationships:

- **MESSAGE_PROCESSING** → **MESSAGE_COMPOSITION**
- **DATA_RETRIEVAL** → **RECORD_KEEPING**
- **USER_REGISTRATION** → **PLAYER_ONBOARDING**

### Relationship Strength Calculation

The CapabilityBasedRouter calculates relationship strength:

- **Direct parent-child**: 0.8 (Strong relationship)
- **Parent to child**: 0.6 (Moderate relationship)
- **Siblings**: 0.4 (Weak relationship)
- **Dependencies**: 0.3 (Dependency relationship)
- **Same category**: 0.2 (Category relationship)
- **No relationship**: 0.0

## Enhanced CapabilityBasedRouter

The router now uses hierarchical capabilities for improved accuracy:

### Scoring Algorithm

1. **Exact Match** (70% weight): Direct capability match
2. **Hierarchical Match** (50% weight): Related capability match
3. **Primary Bonus** (10%): Bonus for primary capabilities
4. **Specialized Bonus** (5%): Bonus for specialized capabilities
5. **Load Balancing** (10%): Prefer less loaded agents

### Hierarchical Matching

```python
def _calculate_hierarchical_match_score(self, agent_capabilities: List, required_capability: CapabilityType) -> float:
    """Calculate score based on hierarchical capability relationships."""
    # Convert to refined capability type
    # Check related capabilities
    # Calculate relationship strength
    # Return best score
```

## Benefits

### 1. Distinct Capability Definitions
- Each capability has a clear, unique purpose
- No overlap or ambiguity between capabilities
- Well-defined boundaries and responsibilities

### 2. Hierarchical Structure
- Broader capabilities encompass specific ones
- Clear parent-child relationships
- Logical progression from foundational to specialized

### 3. Improved Routing Accuracy
- More precise agent selection
- Better handling of related capabilities
- Reduced routing errors and fallbacks

### 4. Flexible Agent Assignment
- Agents can handle related capabilities
- Graceful degradation when exact matches aren't available
- Intelligent fallback to related capabilities

### 5. Scalable Architecture
- Easy to add new capabilities
- Clear categorization and organization
- Maintainable capability definitions

## Usage Examples

### Basic Capability Lookup

```python
from src.agents.refined_capabilities import get_hierarchical_capability_manager

manager = get_hierarchical_capability_manager()

# Get capability definition
definition = manager.get_capability_definition(RefinedCapabilityType.PLAYER_ONBOARDING)
print(f"Level: {definition.level.value}")
print(f"Category: {definition.category.value}")
print(f"Description: {definition.description}")

# Get agent capabilities
capabilities = manager.get_agent_capabilities(AgentRole.PLAYER_COORDINATOR)
for cap_profile in capabilities:
    print(f"{cap_profile.capability.value}: {cap_profile.proficiency_level:.2f}")
```

### Hierarchical Relationship Analysis

```python
# Get hierarchical relationships
hierarchy = manager.get_capability_hierarchy(RefinedCapabilityType.PLAYER_ONBOARDING)
print(f"Parents: {[cap.value for cap in hierarchy['parents']]}")
print(f"Children: {[cap.value for cap in hierarchy['children']]}")
print(f"Dependencies: {[cap.value for cap in hierarchy['dependencies']]}")

# Get related capabilities
related = manager.get_related_capabilities(RefinedCapabilityType.PLAYER_ONBOARDING)
for cap in related:
    print(f"Related: {cap.value}")
```

### Agent Selection

```python
# Find best agent for a capability
best_agent = manager.find_best_agent_for_capability(RefinedCapabilityType.PAYMENT_PROCESSING)
print(f"Best agent for payment processing: {best_agent.value}")

# Get all agents with a capability
agents = manager.get_agents_with_capability(RefinedCapabilityType.DATA_RETRIEVAL)
for agent in agents:
    print(f"Agent with data retrieval: {agent.value}")
```

### Router Integration

```python
from src.agents.intelligent_system import CapabilityBasedRouter, Subtask

router = CapabilityBasedRouter()

# Create subtask with refined capabilities
subtask = Subtask(
    task_id="test_task",
    description="Register new player",
    agent_role=AgentRole.PLAYER_COORDINATOR,
    capabilities_required=[RefinedCapabilityType.PLAYER_ONBOARDING],
    parameters={},
    user_id="user123",
    team_id="KAI"
)

# Calculate agent scores with hierarchical matching
for role in AgentRole:
    score = router._calculate_agent_score(role, subtask)
    if score > 0:
        print(f"{role.value}: {score:.3f}")
```

## Migration Guide

### From Old Capability System

1. **Update Imports**:
   ```python
   # Old
   from src.agents.capabilities import CapabilityType
   
   # New
   from src.agents.refined_capabilities import RefinedCapabilityType
   ```

2. **Update Capability References**:
   ```python
   # Old
   CapabilityType.PLAYER_MANAGEMENT
   
   # New
   RefinedCapabilityType.PLAYER_ONBOARDING
   ```

3. **Update Router Usage**:
   ```python
   # The router automatically uses hierarchical capabilities
   router = CapabilityBasedRouter()  # No changes needed
   ```

### Backward Compatibility

The system maintains backward compatibility:
- Old capability types are still supported
- Existing router methods work unchanged
- Gradual migration is possible

## Future Enhancements

### Planned Improvements

1. **Dynamic Capability Learning**
   - Learn new capabilities from agent interactions
   - Adapt capability definitions based on usage patterns

2. **Advanced Relationship Modeling**
   - Weighted relationship strengths
   - Context-dependent relationships
   - Temporal relationship evolution

3. **Capability Performance Tracking**
   - Track capability success rates
   - Optimize capability assignments
   - Performance-based capability refinement

4. **Multi-Dimensional Capabilities**
   - Support for capability combinations
   - Complex capability dependencies
   - Capability interaction modeling

## Conclusion

The Refined Capabilities System provides a robust foundation for intelligent agent routing in the KICKAI system. By implementing hierarchical capabilities with clear definitions and relationships, the system achieves:

- **Improved Accuracy**: More precise agent selection
- **Better Flexibility**: Graceful handling of related capabilities
- **Enhanced Maintainability**: Clear, organized capability structure
- **Scalable Architecture**: Easy to extend and modify

This system ensures that the CapabilityBasedRouter can make intelligent decisions about agent assignment, leading to better system performance and user experience. 