# CLAUDE.md - KICKAI Agents Directory

This file provides guidance for working with the KICKAI agents system, which implements a **6-agent CrewAI architecture** with centralized message routing and tool management.

## Architecture Overview

### 6-Agent CrewAI Native Collaboration System
The system uses **6 essential agents** with CrewAI native collaboration patterns:

1. **MESSAGE_PROCESSOR** - Primary orchestrator and communication interface
2. **HELP_ASSISTANT** - Help system and guidance  
3. **PLAYER_COORDINATOR** - Player management and onboarding
4. **TEAM_ADMINISTRATOR** - Team member management
5. **SQUAD_SELECTOR** - Squad selection and availability management
6. **NLP_PROCESSOR** - **Intelligent routing analysis and context understanding** (NEW ROLE)

### Core Components

```
kickai/agents/
├── crew_agents.py                    # 6-agent system definition
├── agentic_message_router.py        # Central message routing (CRITICAL)
├── configurable_agent.py           # Agent base class with CrewAI integration
├── tool_registry.py                # Centralized tool management
├── auto_discovery_tool_registry.py # Automatic tool discovery
├── crew_lifecycle_manager.py       # Crew management and cleanup
├── team_memory.py                   # Agent memory and context
├── [REMOVED] tools_manager.py       # Unnecessary layer - replaced with direct assignment
└── user_flow_agent.py              # User flow and intent detection
```

## Critical Agent Rules (MANDATORY)

### ⚠️ CrewAI Native Methods ONLY
**MEMORY: CrewAI tools receive parameters directly via function signatures.**

```python
# ✅ CORRECT - Native CrewAI parameter passing
@tool("FINAL_HELP_RESPONSE")
def final_help_response(
    chat_type: str,
    telegram_id: str, 
    team_id: str,
    username: str
) -> str:
    """Tool receives parameters directly from agent."""
    return f"Help for {username} in {chat_type}"
```

### Tool Independence (CRITICAL)
- **❌ NEVER**: Tools calling other tools or services directly
- **✅ ALWAYS**: Tools are simple, independent functions
- **✅ ALWAYS**: Parameters passed via Task descriptions to agents
- **✅ ALWAYS**: Tools return simple string responses
- **✅ ALWAYS**: Use `@tool` decorator from `crewai.tools`

### Agent Configuration
```python
# ✅ CORRECT - Native CrewAI agent creation
from crewai import Agent
from kickai.config.llm_config import get_llm_config

agent = Agent(
    role="Player Coordinator",
    goal="Manage player registrations and status updates",
    backstory="Expert in football team player management...",
    tools=[get_player_status, register_new_player],
    llm=get_llm_config(),
    verbose=True
)
```

## Key Files Deep Dive

### 1. crew_agents.py - Core Agent System
**Purpose**: Defines the 6-agent CrewAI system with proper initialization and lifecycle management.

**Key Classes**:
- `TeamManagementSystem` - Main system orchestrator
- `ConfigurationError` - Agent configuration exceptions

**Critical Functions**:
- `initialize_agents()` - Sets up all 6 agents with tools
- `get_agent_by_role()` - Retrieves specific agent by role
- `cleanup_resources()` - Proper resource cleanup

**Usage**:
```python
from kickai.agents.crew_agents import TeamManagementSystem

# Initialize system
system = TeamManagementSystem(team_id="KTI")
agents = system.agents  # Returns dict of 6 agents

# Get specific agent
help_agent = system.get_agent_by_role(AgentRole.HELP_ASSISTANT)
```

### 2. agentic_message_router.py - Central Router (MOST CRITICAL)
**Purpose**: Single source of truth for ALL message routing, now with CrewAI native collaboration patterns.

**NEW ARCHITECTURE**: All requests go through CrewAI Task-based execution via CrewLifecycleManager.

**Message Flow (CrewAI Native)**:
```
USER MESSAGE 
    ↓
📱 AgenticMessageRouter (Entry Point)
    ↓
🔄 CrewLifecycleManager.execute_task()
    ↓
🎯 TeamManagementSystem.execute_task()
    ↓
🧠 INTELLIGENT ROUTING: _route_command_to_agent()
    ├── PRIMARY: NLP_PROCESSOR analyzes intent & recommends specialist
    ├── TASK: Task(description=analysis_request, agent=nlp_processor)
    └── FALLBACK: Rule-based routing (only if NLP fails)
    ↓
👤 SELECTED SPECIALIST AGENT executes task via CrewAI Task()
    ↓
📤 COORDINATED RESPONSE via MESSAGE_PROCESSOR
```

**Key Classes**:
- `AgenticMessageRouter` - Main routing class (MODERNIZED with CrewAI native patterns)
- `ResourceManager` - Rate limiting and resource management
- `MessageRouterProtocol` - Interface for testing

**Critical Methods (CrewAI Native)**:
- `route_message()` - Main routing entry point (delegates to CrewLifecycleManager)
- `route_contact_share()` - Contact sharing workflow
- `_execute_crew_task()` - **NEW**: Core CrewAI Task execution
- `_process_message()` - Context creation and task delegation

**NLP_PROCESSOR Integration**:
- All complex routing decisions use NLP_PROCESSOR analysis
- CrewAI Task-based communication between agents
- Intelligent context understanding for optimal agent selection

**Resource Management Features**:
- Rate limiting with exponential backoff
- Circuit breaker pattern for failures
- Memory cleanup and garbage collection
- Concurrent request limiting

**Usage**:
```python
from kickai.agents.agentic_message_router import AgenticMessageRouter
from kickai.core.types import TelegramMessage

router = AgenticMessageRouter(team_id="KTI")
response = await router.route_message(telegram_message)
```

### 3. tool_registry.py - Tool Management
**Purpose**: Centralized registry for all CrewAI tools with validation and discovery.

**Key Classes**:
- `ToolRegistry` - Main registry class
- `ToolMetadata` - Tool metadata and validation
- `EntityTypeToolRegistry` - Entity-specific tool organization

**Features**:
- Automatic tool discovery from features
- Tool validation and conflict detection
- Entity type-based tool organization
- Runtime tool registration

**Usage**:
```python
from kickai.agents.tool_registry import initialize_tool_registry

# Initialize all tools
registry = initialize_tool_registry()

# Get tools for specific agent
player_tools = registry.get_tools_for_entity_type("player")
```

### 4. configurable_agent.py - Agent Base Class
**Purpose**: Base class for all agents with CrewAI integration and configuration management.

**Key Features**:
- YAML configuration integration
- LLM provider abstraction
- Tool assignment validation
- Memory management

**Usage**:
```python
from kickai.agents.configurable_agent import ConfigurableAgent
from kickai.core.enums import AgentRole

agent = ConfigurableAgent(
    role=AgentRole.PLAYER_COORDINATOR,
    team_id="KTI",
    tools=["get_player_status", "register_player"]
)
```

## Agent Tool Assignment

### How Tools Are Assigned
Tools are assigned to agents via the `agents.yaml` configuration:

```yaml
# MESSAGE_PROCESSOR - Communication and basic operations
MESSAGE_PROCESSOR:
  tools:
    - "send_message"
    - "get_user_status"  
    - "get_available_commands"
    - "get_active_players"
    - "get_all_players"
    - "get_my_status"
    - "send_announcement"
    - "send_poll"
    - "ping"
    - "version"
    
# PLAYER_COORDINATOR - Player management and registration
PLAYER_COORDINATOR:  
  tools:
    - "get_my_status"
    - "get_player_status"
    - "get_all_players"  
    - "get_active_players"
    - "approve_player"
    - "register_player"
    - "list_team_members_and_players"
    - "send_message"
```

### Tool Discovery Process
1. **Feature Discovery**: System scans `kickai/features/` for `@tool` decorated functions
2. **Registration**: Tools registered in feature `__init__.py` files
3. **Validation**: Tool signatures and metadata validated
4. **Assignment**: Tools assigned to agents via YAML configuration
5. **Runtime Binding**: Tools bound to agents during initialization

### Tool Validation Notes
**CRITICAL**: The following tools were found to be missing/invalid and have been corrected:

❌ **REMOVED (Not Implemented)**:
- `get_help_content` → Use `FINAL_HELP_RESPONSE` in HELP_ASSISTANT
- `process_general_request` → Use specific tools for specific operations
- `register_new_player` → Use `register_player` (actual implementation)
- `update_player_info` → Handled via `/update` command, not direct tool

✅ **CORRECTED TO ACTUAL TOOLS**:
- MESSAGE_PROCESSOR: Communication and basic operations tools
- PLAYER_COORDINATOR: Player management and registration tools

**Always validate tool existence before adding to agent configurations.**

## Agent-Specific Tool Assignment (ACTUAL IMPLEMENTED TOOLS)

### MESSAGE_PROCESSOR (Communication & Basic Operations)
```yaml
MESSAGE_PROCESSOR:
  tools:
    - send_message              # Direct messaging to users/chats
    - get_user_status          # User status queries (telegram_id, team_id)
    - get_available_commands   # Command help and availability
    - get_active_players       # Player lists (MAIN chat only)
    - get_all_players          # All players list
    - get_my_status           # Self status queries
    - send_announcement       # Team-wide announcements
    - send_poll              # Team voting polls
    - ping                   # System connectivity test
    - version               # Bot version and system info
```

### PLAYER_COORDINATOR (Player Management & Registration)
```yaml
PLAYER_COORDINATOR:
  tools:
    - get_my_status           # Current user's player status
    - get_player_status      # Specific player information
    - get_all_players        # All players in team
    - get_active_players     # Active players only
    - approve_player         # Approve player registrations
    - register_player        # Register new players
    - list_team_members_and_players  # Combined team view
    - send_message          # Communication capability
```

### HELP_ASSISTANT (Help System)
```yaml
HELP_ASSISTANT:
  tools:
    - FINAL_HELP_RESPONSE    # Primary help tool
    - get_available_commands # Command availability
    - get_command_help      # Detailed command help
    - get_welcome_message   # New user onboarding
```

### TEAM_ADMINISTRATOR (Team Management)
```yaml
TEAM_ADMINISTRATOR:
  tools:
    - team_member_registration    # New team member registration
    - get_team_members           # Team member listing
    - get_my_team_member_status  # Current user's team member status
    - add_team_member_role       # Role management
    - remove_team_member_role    # Role removal
    - promote_team_member_to_admin # Admin promotions
    - create_team               # Team creation
    - send_message             # Communication
    - send_announcement       # Team announcements
```

### NLP_PROCESSOR (Intelligent Routing & Analysis) **NEW ROLE**
```yaml
NLP_PROCESSOR:
  tools:
    - advanced_intent_recognition    # Deep intent analysis for routing
    - entity_extraction_tool        # Extract entities from user messages
    - conversation_context_tool     # Build conversation context
    - semantic_similarity_tool      # Semantic analysis for routing
    - routing_recommendation_tool   # Provide agent routing recommendations
    - analyze_update_context       # Context analysis for update commands
    - validate_routing_permissions # Permission validation for routing
```

**PRIMARY ROLE**: The NLP_PROCESSOR is now the **primary routing intelligence** in the system:
- Analyzes user intent using CrewAI Task-based communication
- Recommends optimal specialist agent for each request
- Provides context-aware routing decisions
- Enables intelligent agent collaboration

### SQUAD_SELECTOR (Match & Squad Management)
```yaml
SQUAD_SELECTOR:
  tools:
    - list_matches              # Match listing
    - create_match             # Match creation
    - get_match_details        # Match information
    - mark_availability        # Player availability
    - get_availability         # Availability queries
    - select_squad            # Squad selection
    - get_available_players_for_match # Available players
    - record_attendance       # Attendance tracking
    - get_match_attendance    # Attendance queries
    - get_player_availability_history # Availability history
    - get_player_attendance_history # Attendance history
    - record_match_result     # Match results
    - get_all_players         # Player data
    - get_player_status       # Player information
    - send_message           # Communication
```

### Tool Validation Summary
**✅ VERIFIED IMPLEMENTED TOOLS**:
- All tools listed above are actually implemented and registered
- Tools are properly decorated with `@tool` decorator
- Tools are registered in the tool registry
- Tools follow CrewAI native parameter passing patterns

**❌ REMOVED NON-EXISTENT TOOLS**:
- `get_help_content` → Use `FINAL_HELP_RESPONSE` in HELP_ASSISTANT
- `process_general_request` → Use specific tools for specific operations
- `register_new_player` → Use `register_player` (actual implementation)
- `update_player_info` → Handled via `/update` command, not direct tool
- `get_registration_link` → Not implemented as a tool
- `process_contact_share` → Not implemented as a tool

## Memory Management

### Team Memory System
```python
from kickai.agents.team_memory import TeamMemory

# Initialize with required team_id (no default)
memory = TeamMemory(team_id="KTI")

# Store conversation using telegram_id
memory.add_conversation(
    telegram_id="123456789", 
    input_text="What's my status?", 
    output_text="Your status is active"
)

# Get memory context using telegram_id
context = memory.get_telegram_memory_context("123456789")

# Store conversation with agent role
memory.store_conversation(
    telegram_id="123456789",
    message="Help me register",
    response="I'll help you register as a player",
    agent_role="player_coordinator"
)
```

### Memory Features
- Telegram ID-based context storage
- Conversation history tracking
- Performance optimization with LRU caching
- Automatic cleanup of stale data
- Required team_id parameter (no default)
- Backward compatibility for legacy user_id methods

## Common Issues & Solutions

### Agent Initialization Issues
```bash
# Issue: Agent configuration not found
# Solution: Check agents.yaml exists and is valid
PYTHONPATH=. python -c "
from kickai.config.agents import get_agent_config
config = get_agent_config('MESSAGE_PROCESSOR')
print('✅ Config loaded')
"
```

### Tool Registration Issues
```bash
# Issue: Tool not found by agent
# Solution: Verify tool registration
PYTHONPATH=. python -c "
from kickai.agents.tool_registry import initialize_tool_registry
registry = initialize_tool_registry()
tools = registry.get_all_tools()
print(f'✅ {len(tools)} tools registered')
"
```

### Router Issues
```bash
# Issue: Message routing failures  
# Solution: Test router initialization
PYTHONPATH=. python -c "
from kickai.agents.agentic_message_router import AgenticMessageRouter
router = AgenticMessageRouter('KTI')
print('✅ Router initialized')
"
```

### CrewAI Integration Issues (NEW ARCHITECTURE)
- **"Tool object is not callable"** → Tool is calling services (forbidden)
- **NLP routing failures** → Check NLP_PROCESSOR tools are available and functional
- **Task creation errors** → Ensure proper Task(description, agent, expected_output) format
- **Agent not responding** → Check tool assignment in agents.yaml
- **Memory leaks** → Use proper cleanup in lifecycle manager
- **Routing loops** → Verify NLP_PROCESSOR recommendations are parsed correctly

## Development Guidelines

### Adding New Agents
1. **Define in agents.yaml** with role, goal, backstory
2. **Add to AgentRole enum** in core/enums.py
3. **Register tools** in agents.yaml tools section
4. **Update crew_agents.py** agent initialization
5. **Test thoroughly** with validation scripts

### Adding New Tools
1. **Create tool function** with `@tool` decorator
2. **Export from feature** `__init__.py`
3. **Assign to agent** in agents.yaml
4. **Test registration** with tool registry validation

### Modifying Router (CrewAI Native Architecture)
1. **NEVER create handler classes** - extend router methods and use CrewAI Tasks
2. **PRESERVE CrewAI patterns** - all routing goes through CrewLifecycleManager
3. **MAINTAIN NLP_PROCESSOR integration** - routing decisions use NLP analysis
4. **MAINTAIN type consistency** - telegram_id as int
5. **TEST extensively** - router is critical path with NLP collaboration
6. **USE Task() patterns** - all agent communication via CrewAI Task objects

## Testing Strategy

### Agent System Testing
```bash
# Test agent initialization
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('KTI')
print(f'✅ {len(system.agents)} agents initialized')
"

# Test tool registry
PYTHONPATH=. python -c "
from kickai.agents.tool_registry import initialize_tool_registry
registry = initialize_tool_registry()
print(f'✅ Tool registry with {len(registry.get_all_tools())} tools')
"

# Test router with CrewAI native patterns
PYTHONPATH=. python -c "
from kickai.agents.agentic_message_router import AgenticMessageRouter
router = AgenticMessageRouter('KTI')
print('✅ Router ready with CrewAI integration')
"

# Test NLP_PROCESSOR routing intelligence
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('KTI')
if AgentRole.NLP_PROCESSOR in system.agents:
    print('✅ NLP_PROCESSOR routing intelligence available')
else:
    print('❌ NLP_PROCESSOR not initialized - routing will use fallback')
"
```

### Mock Testing
```bash
# Use Mock Telegram UI for agent testing
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001
```

## Performance Optimizations

### Agent Efficiency
- **Reduced complexity**: 11 → 6 agents (45% reduction)
- **Token optimization**: Minimal prompt design
- **Memory management**: Automatic cleanup and LRU caching
- **Rate limiting**: Prevents API overload

### Resource Management
- **Circuit breakers**: Prevent cascade failures  
- **Request limiting**: Maximum concurrent requests
- **Cleanup intervals**: Regular memory cleanup
- **Weak references**: Prevent memory leaks

## Integration with Main System

### Dependency Container
```python
from kickai.core.dependency_container import get_dependency_container

container = get_dependency_container()
router = container.get_agentic_message_router()
```

### Command Integration
Commands delegate to agents through the router:
```python
from kickai.core.decorators import command

@command("help")
async def help_command(context):
    router = get_dependency_container().get_agentic_message_router()
    return await router.route_message(context.message)
```

## Security Considerations

### Agent Security
- **Tool isolation**: Tools cannot call each other
- **Permission validation**: Role-based access control
- **Input sanitization**: All inputs validated
- **Resource limits**: Rate limiting and timeouts

### Memory Security
- **Context isolation**: User contexts are isolated
- **Data cleanup**: Automatic cleanup of sensitive data
- **Access control**: Memory access via proper interfaces

## Legacy Migration Notes

### Removed Components (DO NOT USE)
- `kickai/agents/handlers/` - **REMOVED** (functionality moved to router)
- `kickai/agents/context/` - **REMOVED** (logic moved to router)
- `kickai/core/factories/agent_system_factory.py` - **REMOVED**

### Migration Mapping
- `UnregisteredUserHandler` → `AgenticMessageRouter._get_unregistered_user_message()`
- `ContactShareHandler` → `AgenticMessageRouter.route_contact_share()`
- `RegisteredUserHandler` → `AgenticMessageRouter._process_with_crewai_system()`
- `ContextBuilder` → Logic moved directly into router methods

## Quick Validation

### System Health Check
```bash
# Complete agent system validation
PYTHONPATH=. python scripts/validate_agent_system.py

# Individual component validation
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
from kickai.agents.tool_registry import initialize_tool_registry
from kickai.agents.agentic_message_router import AgenticMessageRouter

system = TeamManagementSystem('KTI')
registry = initialize_tool_registry()
router = AgenticMessageRouter('KTI')

print(f'✅ Agents: {len(system.agents)}')
print(f'✅ Tools: {len(registry.get_all_tools())}')
print('✅ Router: Ready')
"
```

### Tool Validation Check
```bash
# Validate specific tools exist in registry
PYTHONPATH=. python -c "
from kickai.agents.tool_registry import initialize_tool_registry

registry = initialize_tool_registry()
all_tools = registry.get_tool_names()

# Check for specific tools
tools_to_check = ['get_player_status', 'register_player', 'get_my_status']
for tool in tools_to_check:
    if tool in all_tools:
        print(f'✅ {tool} - EXISTS')
    else:
        print(f'❌ {tool} - MISSING')

print(f'\\nTotal tools available: {len(all_tools)}')
"
```

This CLAUDE.md provides comprehensive guidance for working with the KICKAI agents system. Always refer to this document when modifying agents, tools, or routing logic.