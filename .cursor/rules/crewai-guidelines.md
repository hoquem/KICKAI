# CrewAI Guidelines for KICKAI Development

**Version**: 3.1 | **CrewAI**: Native 2025 Patterns | **Architecture**: 6-Agent Collaboration System

This document provides comprehensive CrewAI-specific guidelines for working with KICKAI's intelligent agent system.

## 🤖 KICKAI Agent System Overview

### 6-Agent Native Collaboration Architecture

```
🎯 INTELLIGENT ROUTING SYSTEM
    ↓
🧠 NLP_PROCESSOR (Primary Intelligence)
├── Intent Analysis & Recognition  
├── Context Understanding
├── Specialist Recommendation
└── Routing Optimization
    ↓
👥 SPECIALIST AGENTS
├── 📱 MESSAGE_PROCESSOR - Interface coordination
├── 🏃 PLAYER_COORDINATOR - Player operations  
├── 👔 TEAM_ADMINISTRATOR - Team management
├── ⚽ SQUAD_SELECTOR - Match & availability
└── 🆘 HELP_ASSISTANT - Help & documentation
```

### Agent Responsibilities

| Agent | Primary Role | Key Tools | Chat Types |
|-------|--------------|-----------|------------|
| **NLP_PROCESSOR** | Intent analysis & routing | `advanced_intent_recognition`, `routing_recommendation_tool` | All |
| **MESSAGE_PROCESSOR** | Interface orchestration | `ping`, `version`, `list_active_players` | All |
| **PLAYER_COORDINATOR** | Player operations | `update_player_field`, `get_player_info`, `get_my_status` | All |
| **TEAM_ADMINISTRATOR** | Team management | `add_player`, `add_team_member_simplified` | Leadership |
| **SQUAD_SELECTOR** | Match management | `mark_availability`, `list_matches`, `select_squad` | All |
| **HELP_ASSISTANT** | Help & documentation | `get_contextual_help`, `explain_command` | All |

## 🔧 CrewAI Tool Development Patterns

### 1. Tool Implementation Standard

**Application Layer Tool (Clean Architecture):**
```python
# kickai/features/[feature]/application/tools/[feature]_tools.py
from crewai.tools import tool
from kickai.features.[feature].domain.tools.[tool_name]_domain import [tool_name]_domain

@tool("[tool_name]", result_as_answer=True)
async def [tool_name](telegram_id: int, team_id: str, username: str, chat_type: str, **kwargs) -> str:
    """
    [Tool description for CrewAI agent understanding]
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier  
        username: User's Telegram username
        chat_type: Type of chat (main, leadership, private)
        **kwargs: Additional tool-specific parameters
        
    Returns:
        JSON formatted response string
    """
    return await [tool_name]_domain(telegram_id, team_id, username, chat_type, **kwargs)
```

### 2. Parameter Handling Best Practices

**CrewAI Dictionary Parameter Pattern:**
```python
@tool("update_player_field", result_as_answer=True)
async def update_player_field(params) -> str:
    """Handle CrewAI dictionary parameter passing."""
    try:
        # Extract parameters from CrewAI dictionary
        if isinstance(params, dict):
            telegram_id = params.get('telegram_id')
            team_id = params.get('team_id')
            username = params.get('username')
            chat_type = params.get('chat_type')
            field = params.get('field')
            value = params.get('value')
        else:
            # Handle individual parameters (backward compatibility)
            telegram_id, team_id, username, chat_type, field, value = params
        
        # Type conversion and validation
        telegram_id = int(telegram_id) if isinstance(telegram_id, str) else telegram_id
        
        # Delegate to domain layer
        return await update_player_field_domain(telegram_id, team_id, username, chat_type, field, value)
        
    except Exception as e:
        return create_json_response(ResponseStatus.ERROR, message=f"Parameter handling error: {str(e)}")
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

### 1. NLP-Driven Routing

**Intelligent Routing Flow:**
```python
# Example of how NLP_PROCESSOR analyzes and routes requests
async def analyze_and_route_request(user_message: str, context: dict) -> str:
    """NLP_PROCESSOR analysis and routing recommendation."""
    
    # Step 1: Intent Recognition
    intent_analysis = await advanced_intent_recognition(
        message=user_message,
        **context
    )
    
    # Step 2: Context Analysis
    context_data = await analyze_update_context(
        message=user_message,
        **context
    )
    
    # Step 3: Routing Recommendation
    routing_decision = await routing_recommendation_tool(
        intent_data=intent_analysis,
        **context
    )
    
    return routing_decision
```

### 2. Specialist Agent Delegation

**Task Delegation Pattern:**
```python
# TeamManagementSystem delegation logic
async def execute_task(self, message: TelegramMessage) -> str:
    """Execute task with intelligent routing."""
    
    context = self._create_context(message)
    
    # Primary: NLP-driven routing
    if self.nlp_processor_enabled:
        agent_role = await self._nlp_route_command(message.text, context)
    else:
        # Fallback: Rule-based routing
        agent_role = self._route_command_to_agent(message.text, message.chat_type.value)
    
    # Execute with specialist agent
    specialist_agent = self.agents[agent_role.value]
    result = await specialist_agent.execute_task(message.text, context)
    
    return result
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

**Status**: Production Ready | **Agent System**: 6-Agent Collaboration | **Routing**: NLP-Driven Intelligence