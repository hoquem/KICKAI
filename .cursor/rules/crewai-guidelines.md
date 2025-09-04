# CrewAI Guidelines for KICKAI Development

**Version**: 3.3 | **CrewAI**: Native Intent-Based Routing | **Architecture**: 5-Agent Clean Tool Naming System

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

| Agent | Primary Role | Key Tools (Clean Naming) | Parameter Patterns |
|-------|--------------|---------------------------|-------------------|
| **MESSAGE_PROCESSOR** | Hierarchical manager & native routing | `check_system_ping`, `check_system_version`, `get_active_players` | Minimal params only |
| **PLAYER_COORDINATOR** | Player operations | `update_player_field`, `get_player_current_info`, `get_status_my` | User context when needed |
| **TEAM_ADMINISTRATOR** | Team management | `add_team_member_simplified`, `update_team_member_information` | Team context + specific params |
| **SQUAD_SELECTOR** | Match management | `mark_player_availability`, `list_team_matches`, `select_match_squad` | Match context + user when needed |
| **HELP_ASSISTANT** | Help & documentation | `show_help_commands`, `show_help_final`, `show_help_usage` | Chat context for help targeting |

## 🔧 CrewAI Tool Development Patterns

### 1. Tool Implementation Standard

**Application Layer Tool with Clean Naming (Clean Architecture):**
```python
# kickai/features/[feature]/application/tools/[feature]_tools.py
from crewai.tools import tool
from kickai.features.[feature].domain.services.[service_name] import [ServiceClass]
from kickai.core.dependency_container import get_container
from kickai.utils.tool_validation import create_tool_response

@tool("[action]_[entity]_[modifier]")
async def [action]_[entity]_[modifier](
    telegram_id: str,  # Only include if tool needs user identity
    team_id: str,      # Only include if tool needs team context
    username: str,     # Only include if tool needs user display name
    chat_type: str,    # Only include if tool behavior depends on chat context
    specific_param: str # Tool-specific parameters as needed
) -> str:
    """
    [Clear tool description following clean naming convention]
    
    Clean naming pattern: [action]_[entity]_[modifier]
    Example: update_player_field, get_status_my, show_help_commands
    
    IMPORTANT: Only include parameters this tool actually uses!
    
    Args:
        telegram_id: User's Telegram ID (string) - only if tool needs user identity
        team_id: Team identifier - only if tool needs team context
        username: User's Telegram username - only if tool needs display name
        chat_type: Type of chat context - only if behavior varies by chat
        specific_param: Tool-specific parameters as required
        
    Returns:
        Plain text formatted response string (not JSON objects)
    """
    try:
        # Validate only the parameters this tool actually uses
        if not telegram_id:  # Only if tool needs this param
            return "❌ User identification required"
        if not team_id:  # Only if tool needs this param
            return "❌ Team identifier required"
        
        # Convert telegram_id to int internally when needed for database
        telegram_id_int = int(telegram_id) if telegram_id else 0
        
        # Delegate to domain service
        service = get_container().get_service([ServiceClass])
        result = await service.[method_name](telegram_id_int, team_id, specific_param)
        
        # Return plain text response
        return f"✅ Operation completed successfully: {result}"
        
    except Exception as e:
        logger.error(f"❌ Error in {[action]_[entity]_[modifier]}: {e}")
        return f"❌ Failed to complete operation: {str(e)}"
```

### 2. Maintainable Docstring Strategy

**Official KICKAI Pattern - Mandatory for All Tools**

All CrewAI tools must follow this **official pattern** from CLAUDE.md:

```python
@tool("tool_name")
async def tool_name(...) -> str:
    """
    [SEMANTIC ACTION] - What business action does this perform?
    
    [BUSINESS CONTEXT] - Why this action matters and its business impact
    
    Use when: [BUSINESS INTENT TRIGGER - when this business need arises]
    Required: [BUSINESS PERMISSIONS/CONDITIONS - what business rules apply]
    
    Returns: [SEMANTIC BUSINESS OUTCOME - what business result is delivered]
    """
```

**Key Principles for Maintainable Docstrings:**
1. **Focus on WHAT (semantics)** not HOW (implementation)
2. **Business intent** over UI commands (/status vs "when status verification needed")
3. **Timeless descriptions** that survive interface changes
4. **Agent-friendly** for intelligent routing decisions

**Examples of Maintainable vs Non-Maintainable:**

```python
# ❌ Non-maintainable - specific examples that become outdated
"""
Get player information for the current user.

USE THIS FOR:
- /myinfo command in player context
- "my status", "my information" queries
- When user asks "what's my info?"

DO NOT USE FOR:
- Looking up other players by name/ID
- Use get_player_by_identifier for those cases
"""

# ✅ Maintainable - semantic intent that stays relevant
"""
Get requesting user's player information.

This tool retrieves the current user's own player data including status,
position, and team membership. Use when the user wants to see their
own information, not when looking up other players.

Use when: Player needs status verification
Required: Active player registration
Returns: Personal player status summary
```

### 3. CrewAI Direct Parameter Passing (Current Standard)

**Direct Parameter Pattern - Tools Only Include What They Need:**
```python
# Example 1: Tool that NEEDS user context
@tool("update_player_field")
async def update_player_field(
    telegram_id: str,  # NEEDED - identifies which player to update
    team_id: str,      # NEEDED - scopes to correct team
    field: str,        # NEEDED - what field to update
    value: str         # NEEDED - new value
    # Note: username and chat_type NOT included - tool doesn't need them
) -> str:
    """Update a player field - only includes parameters it actually uses."""
    try:
        # Validate required parameters
        if not telegram_id:
            return "❌ Player identification required"
        if not team_id:
            return "❌ Team identifier required"
        if not field or not value:
            return "❌ Field name and value are required"
        
        # Convert types internally when needed
        telegram_id_int = int(telegram_id)
        
        # Delegate to service
        service = get_container().get_service(PlayerService)
        result = await service.update_field(telegram_id_int, team_id, field, value)
        
        return f"✅ Player {field} updated successfully to: {value}"
        
    except Exception as e:
        logger.error(f"❌ Error updating player field: {e}")
        return f"❌ Failed to update player field: {str(e)}"

# Example 2: Tool that DOESN'T need user context
@tool("send_team_announcement")
async def send_team_announcement(
    team_id: str,    # NEEDED - which team to send to
    message: str     # NEEDED - what to send
    # Note: No telegram_id, username, chat_type - tool doesn't need user context
) -> str:
    """Send announcement to team - minimal parameters."""
    try:
        if not team_id or not message:
            return "❌ Team ID and message are required"
        
        service = get_container().get_service(CommunicationService)
        result = await service.send_announcement(team_id, message)
        
        return f"✅ Announcement sent to team {team_id}"
        
    except Exception as e:
        return f"❌ Failed to send announcement: {str(e)}"
```

### 4. Response Format Standards

**Plain Text Response Pattern (CrewAI Best Practice):**
```python
# Success response with formatting
return f"""✅ **Player Updated Successfully**

👤 Player: {player.name}
🔄 Field: {field}
💾 New Value: {value}
📅 Updated: {datetime.now().strftime('%H:%M')}"""

# Error response - clear and actionable
return "❌ Player not found. Please check the player ID and team."

# Information response with structure
return f"""📊 **Player Status: {player.name}**

🆔 ID: {player.player_id}
📊 Status: {player.status}
⚽ Position: {player.position}
📞 Phone: {player.phone_number}

✅ Information retrieved successfully"""

# List response with clear formatting
players_text = "📋 **Active Players** (3 total)\n\n"
for i, player in enumerate(players, 1):
    players_text += f"{i}. ⚽ {player.name} ({player.position})\n"
return players_text
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
    def __init__(self, telegram_id: str, team_id: str, username: str, chat_type: str):
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

Tool Signature (Only Include Parameters Tool Actually Uses):
@tool("[tool_name]")
async def [tool_name](
    telegram_id: str,    # Only if tool needs user identity
    team_id: str,        # Only if tool needs team context  
    [specific_params]: str  # Tool-specific parameters as needed
) -> str:

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
    # Test with only parameters the tool actually needs
    result = await tool_name(
        telegram_id="123456789",  # String type for LLM compatibility
        team_id="TEST",
        specific_param="test_value"
        # Note: Only include params this specific tool uses
    )
    
    # Then
    assert result is not None
    assert isinstance(result, str)  # Tools return plain text
    assert "✅" in result  # Success indicator in plain text
    assert "error" not in result.lower()  # No error in successful response

@pytest.mark.asyncio
async def test_crewai_tool_type_conversion():
    # Test string to int conversion for telegram_id
    result = await tool_name(
        telegram_id="123456789",  # String input
        team_id="TEST"
        # Only parameters this tool actually needs
    )
    
    # Should handle string->int conversion internally
    assert result is not None
    assert "✅" in result or result.startswith("✅")
    assert "Invalid telegram_id format" not in result
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
        telegram_id="123456789",  # String type for consistency
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
        telegram_id="123456789",  # String type for consistency
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

**Status**: Production Ready | **Agent System**: 5-Agent Clean Naming | **Routing**: Native CrewAI Intent-Based | **Tools**: 75+ with Clean Convention | **Docstrings**: Maintainable Semantic Focus