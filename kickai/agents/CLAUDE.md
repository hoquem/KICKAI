# CLAUDE.md - KICKAI Agents Directory

This file provides guidance for working with the KICKAI agents system, which implements a **5-agent CrewAI architecture** with centralized message routing and tool management.

## Architecture Overview

### 5-Agent CrewAI System
The system uses **5 essential agents** (simplified from 11 for optimal performance):

1. **MessageProcessorAgent** - Primary interface and command routing
2. **HelpAssistantAgent** - Help system and guidance  
3. **PlayerCoordinatorAgent** - Player management and onboarding
4. **TeamAdministrationAgent** - Team member management
5. **SquadSelectorAgent** - Squad selection and availability management

### Core Components

```
kickai/agents/
├── crew_agents.py                    # 5-agent system definition
├── agentic_message_router.py        # Central message routing (CRITICAL)
├── configurable_agent.py           # Agent base class with CrewAI integration
├── tool_registry.py                # Centralized tool management
├── auto_discovery_tool_registry.py # Automatic tool discovery
├── crew_lifecycle_manager.py       # Crew management and cleanup
├── team_memory.py                   # Agent memory and context
├── tools_manager.py                 # Tool assignment and validation
└── user_flow_agent.py              # User flow and intent detection
```

# ⚠️ CREWAI DEVELOPMENT RULES (MANDATORY) ⚠️

## Before Modifying ANY CrewAI Code

**STOP and check these requirements FIRST:**

### 🔍 Pre-Development Checklist
- [ ] Am I using ONLY native CrewAI patterns?
- [ ] Am I avoiding custom decorators or wrappers?
- [ ] Are my tool parameters simple types (str, int, bool)?
- [ ] Do my tools return strings?
- [ ] Have I checked the main CLAUDE.md CrewAI rules?

### 🚨 Development Decision Tree
When encountering any CrewAI issue:
1. **FIRST**: Check if current approach follows native CrewAI patterns
2. **SECOND**: Review official CrewAI documentation for the correct pattern
3. **THIRD**: Simplify to the most basic CrewAI example that works
4. **ONLY THEN**: If native patterns fail, ask for guidance

### 📝 CrewAI Code Review Checklist
Before completing any CrewAI-related changes:
- ✅ Using `@tool` from `crewai.tools`?
- ✅ Tools have clear docstrings with Args/Returns?
- ✅ All parameters are simple types (str, int, bool, float)?
- ✅ All tools return strings?
- ✅ No custom parameter handling or complex data structures?
- ✅ Following the exact patterns shown in main CLAUDE.md?

**If ANY checkbox is unchecked, STOP and fix before proceeding.**

### 🎯 Agent-Specific Rules
- **Tools**: Must be independent, simple functions with `@tool` decorator
- **Agents**: Use native `Agent` class with simple configuration
- **Tasks**: Use native `Task` class with clear descriptions
- **Crew**: Use native `Crew` orchestration only

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
**Purpose**: Defines the 5-agent CrewAI system with proper initialization and lifecycle management.

**Key Classes**:
- `TeamManagementSystem` - Main system orchestrator
- `ConfigurationError` - Agent configuration exceptions

**Critical Functions**:
- `initialize_agents()` - Sets up all 5 agents with tools
- `get_agent_by_role()` - Retrieves specific agent by role
- `cleanup_resources()` - Proper resource cleanup

**Usage**:
```python
from kickai.agents.crew_agents import TeamManagementSystem

# Initialize system
system = TeamManagementSystem(team_id="KTI")
agents = system.agents  # Returns dict of 5 agents

# Get specific agent
help_agent = system.get_agent_by_role(AgentRole.HELP_ASSISTANT)
```

### 2. agentic_message_router.py - Central Router (MOST CRITICAL)
**Purpose**: Single source of truth for ALL message routing in the system.

**Key Classes**:
- `AgenticMessageRouter` - Main routing class (MODERNIZED)
- `ResourceManager` - Rate limiting and resource management
- `MessageRouterProtocol` - Interface for testing

**Critical Methods**:
- `route_message()` - Main routing entry point
- `route_contact_share()` - Contact sharing workflow
- `_process_with_crewai_system()` - Core CrewAI processing
- `_get_unregistered_user_message()` - Unregistered user handling

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

### CrewAI Integration Issues
- **"Tool object is not callable"** → Tool is calling services (forbidden)
- **Parameter passing errors** → Use structured Task descriptions
- **Agent not responding** → Check tool assignment in agents.yaml
- **Memory leaks** → Use proper cleanup in lifecycle manager

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

### Modifying Router
1. **NEVER create handler classes** - extend router methods
2. **PRESERVE resource management** - don't remove rate limiting
3. **MAINTAIN type consistency** - telegram_id as int
4. **TEST extensively** - router is critical path

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

# Test router
PYTHONPATH=. python -c "
from kickai.agents.agentic_message_router import AgenticMessageRouter
router = AgenticMessageRouter('KTI')
print('✅ Router ready')
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
- **Reduced complexity**: 11 → 5 agents (55% reduction)
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