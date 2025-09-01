# CrewAI Guidelines for KICKAI Development

**Version**: 3.2 | **CrewAI**: Native Intent-Based Routing | **Architecture**: 5-Agent Clean Tool Naming System

This document provides comprehensive CrewAI-specific guidelines for working with KICKAI's native intent-based agent system with clean tool naming convention.

## 🤖 KICKAI Agent System Overview

### 5-Agent Native Intent-Based Architecture

```
🎯 NATIVE CREWAI INTENT-BASED ROUTING
    ↓
🧠 MESSAGE_PROCESSOR (Hierarchical Manager)
├── Native Semantic Understanding
├── CrewAI Intelligence
├── Clean Tool Selection  
└── Agent Delegation
    ↓
👥 SPECIALIST AGENTS (Clean Tool Naming)
├── 🏃 PLAYER_COORDINATOR - Player operations  
├── 👔 TEAM_ADMINISTRATOR - Team management
├── ⚽ SQUAD_SELECTOR - Match & availability
└── 🆘 HELP_ASSISTANT - Help & documentation
```

### Clean Tool Naming Convention

**Pattern**: `[action]_[entity]_[modifier]`

**Examples**:
- `get_status_my` (get_[entity]_[modifier])
- `check_system_ping` (check_[entity]_[modifier])
- `show_help_commands` (show_[entity]_[modifier])
- `update_player_field` ([action]_[entity]_[modifier])
- `add_team_member_simplified` ([action]_[entity]_[modifier])

### Agent Responsibilities

| Agent | Primary Role | Key Tools (Clean Naming) | Chat Types |
|-------|--------------|---------------------------|------------|
| **MESSAGE_PROCESSOR** | Hierarchical manager & native routing | `check_system_ping`, `check_system_version`, `get_active_players` | All |
| **PLAYER_COORDINATOR** | Player operations | `update_player_field`, `get_player_current_info`, `get_status_my` | All |
| **TEAM_ADMINISTRATOR** | Team management | `add_team_member_simplified`, `update_team_member_information` | Leadership |
| **SQUAD_SELECTOR** | Match management | `mark_player_availability`, `list_team_matches`, `select_match_squad` | All |
| **HELP_ASSISTANT** | Help & documentation | `show_help_commands`, `show_help_final`, `show_help_usage` | All |

## 🔧 CrewAI Tool Development Patterns

### 1. Tool Implementation Standard

**Application Layer Tool with Clean Naming (Clean Architecture):**
```python
# kickai/features/[feature]/application/tools/[feature]_tools.py
from crewai.tools import tool
from kickai.features.[feature].domain.services.[service_name] import [ServiceClass]
from kickai.core.dependency_container import get_container
from kickai.utils.tool_validation import create_tool_response

@tool("[action]_[entity]_[modifier]", result_as_answer=True)
async def [action]_[entity]_[modifier](
    telegram_id: int, 
    team_id: str, 
    username: str, 
    chat_type: str, 
    **kwargs
) -> str:
    """
    [Clear tool description following clean naming convention]
    
    Clean naming pattern: [action]_[entity]_[modifier]
    Example: update_player_field, get_status_my, show_help_commands
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier  
        username: User's Telegram username
        chat_type: Type of chat (main, leadership, private)
        **kwargs: Additional tool-specific parameters
        
    Returns:
        JSON formatted response string
    """
    try:
        service = get_container().get_service([ServiceClass])
        result = await service.[method_name](telegram_id, team_id, **kwargs)
        return create_tool_response(True, data=result)
    except Exception as e:
        return create_tool_response(False, f"Error in {[action]_[entity]_[modifier]}: {str(e)}")
```

### 2. CrewAI Best Practice Parameter Handling

**CrewAI Dictionary Parameter Pattern (Standard 2025):**
```python
@tool("update_player_field", result_as_answer=True)
async def update_player_field(params) -> str:
    """Handle CrewAI dictionary parameter passing following 2025 best practices."""
    try:
        # CrewAI 2025: Detect dictionary parameter passing
        if isinstance(params, dict):
            # Extract from CrewAI parameter dictionary
            telegram_id = params.get('telegram_id')
            team_id = params.get('team_id') 
            username = params.get('username')
            chat_type = params.get('chat_type')
            field = params.get('field')
            value = params.get('value')
        else:
            # Fallback: Individual parameters
            telegram_id = params  # First parameter
            # Additional parameters would be handled via **kwargs
        
        # Robust type conversion
        try:
            telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id
        except (ValueError, TypeError):
            return create_tool_response(False, "Invalid telegram_id format")
        
        # Parameter validation
        if not team_id:
            return create_tool_response(False, "team_id is required")
        if not username:
            return create_tool_response(False, "username is required")
            
        # Clean service delegation
        service = get_container().get_service(PlayerService)
        result = await service.update_field(telegram_id, team_id, field, value)
        return create_tool_response(True, data=result)
        
    except Exception as e:
        return create_tool_response(False, f"Error in update_player_field: {str(e)}")
```

### 3. Response Format Standards

**JSON Response Pattern:**
```python
from kickai.utils.json_response import create_json_response, ResponseStatus

# Success response
return create_json_response(
    ResponseStatus.SUCCESS,
    message="Operation completed successfully",
    data={
        "player_name": player.name,
        "updated_field": field,
        "new_value": value
    }
)

# Error response
return create_json_response(
    ResponseStatus.ERROR,
    message="Player not found",
    error_code="PLAYER_NOT_FOUND"
)

# Information response
return create_json_response(
    ResponseStatus.INFO,
    message="Player status retrieved",
    data=player_status
)
```

## 🎯 Agent Collaboration Patterns

### 1. Native CrewAI Intent-Based Routing

**Native Semantic Understanding (No Hardcoded Patterns):**
```python
# MESSAGE_PROCESSOR uses CrewAI's native intelligence for routing
class MessageProcessorAgent:
    def __init__(self):
        self.role = "Primary Interface Manager"
        self.goal = "Route requests using native CrewAI semantic understanding"
        self.backstory = """Expert in understanding user intent and delegating to 
                           appropriate specialists using clean tool naming convention.
                           Uses CrewAI's native intelligence rather than hardcoded patterns."""
        self.process = Process.hierarchical  # Native CrewAI hierarchical process
        
    async def route_request(self, user_message: str, context: dict) -> str:
        """Route using CrewAI's native semantic understanding."""
        
        # CrewAI automatically analyzes intent and selects appropriate agent
        # No explicit NLP tools needed - CrewAI handles this natively
        
        # Clean tool naming makes agent selection clear
        # Example: "check my status" -> get_status_my tool
        # Example: "update my position" -> update_player_field tool
        # Example: "add new player" -> add_team_member_simplified tool
        
        return "CrewAI handles routing via native semantic understanding"
```

### 2. Native CrewAI Hierarchical Process

**Clean Agent Delegation Pattern:**
```python
# TeamManagementSystem using native CrewAI process
class TeamManagementSystem:
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.process = Process.hierarchical  # Native CrewAI process
        self.manager_agent = self._create_message_processor()
        self.specialist_agents = self._create_specialists()
        
    def _create_message_processor(self):
        """Create hierarchical manager with clean tool understanding."""
        return Agent(
            role="Primary Interface Manager",
            goal="Understand user requests and delegate to appropriate specialists",
            backstory="""Expert in understanding user intent using clean tool naming.
                        Delegates to specialists: PLAYER_COORDINATOR for player ops,
                        TEAM_ADMINISTRATOR for team management, SQUAD_SELECTOR for matches,
                        HELP_ASSISTANT for guidance.""",
            tools=[
                check_system_ping,      # Clean: check_[entity]_[modifier]
                check_system_version,   # Clean: check_[entity]_[modifier] 
                get_active_players      # Clean: get_[entity]_[modifier]
            ],
            allow_delegation=True,
            process=Process.hierarchical
        )
        
    async def execute_task(self, message: TelegramMessage) -> str:
        """Execute using native CrewAI hierarchical process."""
        
        # CrewAI's native process handles:
        # 1. Semantic understanding of user request
        # 2. Tool selection based on clean naming
        # 3. Agent delegation to specialists
        # 4. Result aggregation and formatting
        
        crew = Crew(
            agents=[self.manager_agent] + self.specialist_agents,
            tasks=[self._create_task(message)],
            process=Process.hierarchical,
            manager_llm=self.llm_config.main_llm,
            verbose=True
        )
        
        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)
```

### 3. Context Sharing Between Agents

**Context Management Pattern:**
```python
# Shared context structure for agent collaboration
class AgentContext:
    def __init__(self, telegram_id: int, team_id: str, username: str, chat_type: str):
        self.telegram_id = telegram_id
        self.team_id = team_id
        self.username = username
        self.chat_type = chat_type
        self.timestamp = datetime.utcnow()
        self.session_data = {}
    
    def add_context_data(self, key: str, value: any):
        """Add contextual information for agent sharing."""
        self.session_data[key] = value
    
    def get_context_data(self, key: str, default=None):
        """Retrieve shared context data."""
        return self.session_data.get(key, default)
```

## 📋 CrewAI Prompt Templates

### 1. Tool Creation Prompts

**New Tool Development:**
```
Create a new CrewAI tool for [functionality] following KICKAI standards:

Requirements:
- Application layer: @tool decorator with metadata
- Domain layer: Pure business logic function  
- Parameter handling: Support both individual and dictionary parameters
- Response format: JSON with create_json_response utility
- Error handling: Comprehensive try/catch with specific exceptions
- Testing: Unit tests for domain, integration tests for application

Tool Signature:
@tool("[tool_name]", result_as_answer=True)
async def [tool_name](telegram_id: int, team_id: str, username: str, chat_type: str, [specific_params]) -> str:

Integration:
- Export from feature __init__.py
- Assign to appropriate agent(s)
- Test with mock Telegram UI
```

### 2. Agent Configuration Prompts

**Agent Setup and Configuration:**
```
Configure CrewAI agent [agent_name] for KICKAI system:

Agent Definition (config/agents.yaml):
- role: Clear, specific role description
- goal: Specific objectives and success criteria
- backstory: Context for decision-making
- tools: List of assigned tools
- llm: Configured LLM provider

Tool Assignment:
- Primary tools for core functionality
- Secondary tools for supporting operations
- Shared tools for common operations

Routing Rules:
- Command patterns that route to this agent
- Chat type permissions
- User role requirements
```

### 3. System Integration Prompts

**Multi-Agent System Integration:**
```
Integrate new functionality into KICKAI's 6-agent system:

1. NLP Analysis Integration:
   - Update intent recognition patterns
   - Add new routing rules
   - Test NLP recommendation accuracy

2. Specialist Agent Assignment:
   - Determine primary responsible agent
   - Configure tool assignments
   - Update agent capabilities

3. Cross-Agent Collaboration:
   - Define handoff patterns
   - Share context requirements
   - Coordinate response formatting

4. System Testing:
   - Test routing decisions
   - Verify agent collaboration
   - Validate end-to-end workflows
```

## 🧪 Testing CrewAI Components

### 1. Tool Testing Pattern

**Individual Tool Testing:**
```python
# Test CrewAI tool with mock dependencies
@pytest.mark.asyncio
async def test_crewai_tool_success():
    # Given
    mock_context = {
        'telegram_id': 123456789,
        'team_id': 'TEST',
        'username': 'testuser',
        'chat_type': 'main'
    }
    
    # When
    result = await tool_name(**mock_context)
    
    # Then
    assert result is not None
    response_data = json.loads(result)
    assert response_data['status'] == 'success'
    assert 'data' in response_data

@pytest.mark.asyncio
async def test_crewai_tool_parameter_dictionary():
    # Test dictionary parameter handling
    params_dict = {
        'telegram_id': '123456789',  # String that needs conversion
        'team_id': 'TEST',
        'username': 'testuser',
        'chat_type': 'main',
        'additional_param': 'value'
    }
    
    result = await tool_name(params_dict)
    assert 'Invalid telegram_id format' not in result
```

### 2. Agent Integration Testing

**Agent Behavior Testing:**
```python
# Test agent task execution
@pytest.mark.asyncio
async def test_agent_task_execution():
    # Given
    agent = PlayerCoordinatorAgent()
    test_message = TelegramMessage(
        telegram_id=123456789,
        text="/update position goalkeeper",
        team_id="TEST",
        chat_type=ChatType.MAIN,
        username="testuser"
    )
    
    # When
    result = await agent.execute_task("/update position goalkeeper", context)
    
    # Then
    assert result is not None
    assert "position" in result.lower()
    assert "goalkeeper" in result.lower()
```

### 3. System-Wide Testing

**Multi-Agent System Testing:**
```python
# Test complete agent system workflow
@pytest.mark.asyncio
async def test_intelligent_routing_system():
    # Given
    system = TeamManagementSystem("TEST")
    message = TelegramMessage(
        telegram_id=123456789,
        text="I need to update my availability",
        team_id="TEST",
        chat_type=ChatType.MAIN,
        username="testuser"
    )
    
    # When
    result = await system.execute_task(message)
    
    # Then
    assert result is not None
    # Should route to SQUAD_SELECTOR for availability updates
    # Should use NLP analysis for intent recognition
    # Should provide appropriate response
```

## 🔍 Debugging CrewAI Issues

### Common Issues and Solutions

**1. Tool Not Found Error:**
```python
# Problem: Tool not discovered by CrewAI
# Solution: Check tool export and registration
from kickai.features.[feature] import [tool_name]  # Verify export
from kickai.agents.tool_registry import initialize_tool_registry
registry = initialize_tool_registry()
print(f"Tool found: {'tool_name' in registry.get_all_tools()}")
```

**2. Parameter Passing Issues:**
```python
# Problem: CrewAI passing parameters incorrectly
# Solution: Implement robust parameter handling
def handle_crewai_params(params):
    """Handle both individual and dictionary parameters."""
    if isinstance(params, dict):
        return extract_from_dict(params)
    elif isinstance(params, (list, tuple)):
        return extract_from_sequence(params)
    else:
        return handle_single_parameter(params)
```

**3. Async Execution Problems:**
```python
# Problem: CrewAI not properly awaiting async tools
# Solution: Ensure proper async def and await patterns
@tool("async_tool", result_as_answer=True)
async def async_tool(params) -> str:  # Must be async def
    """Ensure CrewAI can properly await this tool."""
    result = await some_async_operation()  # Proper await
    return json.dumps(result)  # Return serializable result
```

### Debugging Commands

**System Health Checks:**
```bash
# Validate tool registry
PYTHONPATH=. python -c "
from kickai.agents.tool_registry import initialize_tool_registry
registry = initialize_tool_registry()
print(f'✅ Tools loaded: {len(registry.get_all_tools())}')
"

# Test agent system
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('TEST')
print('✅ Agent system initialized successfully')
"

# Validate configuration
PYTHONPATH=. python scripts/run_health_checks.py
```

## 📈 Performance Optimization

### CrewAI Performance Best Practices

**1. Tool Efficiency:**
- Minimize tool execution time
- Use caching for expensive operations
- Implement proper error handling to avoid retries

**2. Agent Optimization:**
- Configure appropriate LLM models per agent
- Optimize prompt templates for conciseness
- Use tool result caching where appropriate

**3. System Scalability:**
- Monitor agent resource usage
- Implement proper logging and metrics
- Use async patterns throughout

---

**Status**: Production Ready | **Agent System**: 5-Agent Clean Naming | **Routing**: Native CrewAI Intent-Based | **Tools**: 75+ with Clean Convention