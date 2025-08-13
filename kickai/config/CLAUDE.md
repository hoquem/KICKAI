# CLAUDE.md - KICKAI Config Directory

This file provides guidance for working with the KICKAI configuration system, which manages agent configurations, LLM providers, and system-wide settings using YAML-based configuration with template processing.

## Architecture Overview

### Configuration System Components
```
kickai/config/
├── agents.yaml                    # Agent definitions and tool assignments (CRITICAL)
├── command_routing.yaml           # Dynamic command routing configuration (NEW)
├── agents.py                     # YAML configuration manager
├── command_routing_manager.py    # Dynamic command routing system (NEW)
├── config_validator.py          # Configuration validation system (NEW)
├── tasks.yaml                    # Task templates and patterns
├── llm_config.py                # LLM provider configuration  
├── optimized_agent_prompts.py   # Agent prompt optimization
├── prompt_optimizer.py          # Prompt engineering utilities
└── complexity_config.py         # System complexity settings
```

## Core Configuration Files

### 1. command_routing.yaml - Dynamic Command Routing (NEW & CRITICAL)
**Purpose**: Centralized command-to-agent routing configuration that eliminates hardcoded routing logic.

**Key Features (SIMPLIFIED)**:
- **Flexible Command Routing**: Maps commands to agents with flexible slash handling
- **Slash-Agnostic Matching**: Both `/info` and `info` work automatically
- **Context-Aware Routing**: Different behavior based on chat type (main/leadership/private)
- **Agent Constraints**: Performance and permission settings per agent
- **Strict Validation**: Fail-fast validation with no silent failures
- **No Caching**: Simplified for reliability and maintainability

**Complete Configuration Structure**:
```yaml
# Default routing behavior
default_routing:
  default_agent: "message_processor"
  fallback_agent: "message_processor"
  case_sensitive: false
  strip_prefix: true

# Command routing rules - maps commands to specific agents
command_routing:
  help_commands:
    agent: "help_assistant"
    commands: ["/help", "help", "/help@KickAI_bot"]
    description: "All help-related queries and guidance"
    priority: 1

  player_info_commands:
    agent: "player_coordinator"
    commands: ["/info", "/myinfo", "/status", "/approve", "/reject"]
    description: "Player information, status queries, and coordination"
    priority: 2
    # Note: Commands work with or without slash - "/info" matches both "/info" and "info"

  admin_commands:
    agent: "team_administrator"
    commands: ["/addplayer", "/addmember", "/creatematch", "/promote"]
    description: "Team administration and management operations"
    priority: 2

  squad_commands:
    agent: "squad_selector"
    commands: ["/attendance", "/availability", "/squad", "/matches"]
    description: "Squad selection, availability, and match management"
    priority: 2

  basic_commands:
    agent: "message_processor"
    commands: ["/list", "/ping", "/version", "/announce", "/poll"]
    description: "Basic queries, communications, and system information"
    priority: 3

# Pattern matching removed for simplicity - use exact commands only

# Context-based routing modifiers
context_routing:
  chat_type_rules:
    main_chat:
      blocked_commands: ["/addplayer", "/promote", "/demote"]
      redirect_agent: "message_processor"
    leadership_chat:
      blocked_commands: []
    private_chat:
      allowed_agents: ["message_processor", "help_assistant", "player_coordinator"]

# Agent capabilities and constraints
agent_constraints:
  message_processor:
    max_concurrent_requests: 10
    can_handle_fallback: true
  player_coordinator:
    max_concurrent_requests: 8
    requires_context: ["telegram_id", "team_id"]
  team_administrator:
    max_concurrent_requests: 3
    requires_permissions: ["leadership"]
    requires_context: ["telegram_id", "team_id", "chat_type"]

# Performance optimization - caching removed for simplicity
optimization:
  load_balancing:
    enabled: false  # Disabled for current 5-agent system
```

**Usage in Code (Flexible Slash Handling)**:
```python
from kickai.config.command_routing_manager import get_command_routing_manager

# Get routing decision - both work the same way!
routing_manager = get_command_routing_manager()

# With slash
decision1 = routing_manager.route_command("/info", chat_type="main_chat")
print(f"Route /info to: {decision1.agent_role}")

# Without slash - automatically works!
decision2 = routing_manager.route_command("info", chat_type="main_chat")  
print(f"Route info to: {decision2.agent_role}")

# Both return: player_coordinator
```

### 2. agents.yaml - Agent Configuration (MOST CRITICAL)
**Purpose**: Defines all 5 agents with roles, goals, backstories, and tool assignments using **optimized prompts**.

**Recent Optimization (2025)**: Agent prompts have been streamlined for **57.2% token reduction** while preserving all critical functionality.

**Optimized Structure**:
```yaml
shared_templates:
  shared_backstory: |
    You are a specialized KICKAI football team management agent.
    
    CORE RULES:
    1. NEVER fabricate data - always use tools
    2. ONE targeted tool call per request  
    3. Preserve tool output formatting exactly (including emojis)
    4. Provide clear responses even if tools fail
    
    WORKFLOW: Analyze request → Select specific tool → Execute → Respond with tool output
    
    SUCCESS METRICS: Fast, accurate, tool-based responses with preserved formatting

agents:
  - name: message_processor      # Primary interface agent
  - name: help_assistant        # Help system agent
  - name: player_coordinator    # Player management agent
  - name: team_administrator    # Team administration agent  
  - name: squad_selector        # Squad selection agent
```

**Critical Elements**:
- **Optimized Prompts**: 57.2% reduction in token usage (from ~6,000 to 2,570 chars total)
- **Tool Assignment**: Each agent has specific tools assigned via concise routing rules
- **Entity Types**: Primary and secondary entity type handling
- **Backstory Templates**: Streamlined shared template (433 chars vs. ~1,200 original)

### 2. Command Routing System Components (NEW)

#### 2a. command_routing_manager.py - Dynamic Routing Engine
**Purpose**: Provides runtime command routing based on YAML configuration.

**Key Classes**:
- `CommandRoutingManager` - Main routing engine
- `RoutingDecision` - Routing result with metadata
- `RoutingRule` - Configuration rule representation

**Features (SIMPLIFIED + FLEXIBLE)**:
- **Flexible Command Routing**: Route commands with automatic slash handling
- **User-Friendly Input**: Both `/info` and `info` work automatically
- **Context-Aware Processing**: Different behavior per chat type
- **Fail-Fast Validation**: Ensures routed agents exist and configuration is valid
- **No Silent Failures**: System fails immediately on configuration issues

**Usage Example (Flexible Slash Matching)**:
```python
from kickai.config.command_routing_manager import get_command_routing_manager

# Initialize routing manager (global singleton)
routing_manager = get_command_routing_manager()

# Route commands - both work identically!
decision1 = routing_manager.route_command("/info", chat_type="main_chat")
decision2 = routing_manager.route_command("info", chat_type="main_chat")  # No slash!
decision3 = routing_manager.route_command("INFO", chat_type="main_chat")  # Case insensitive!

# All three return the same result:
# agent_role=AgentRole.PLAYER_COORDINATOR, match_type='exact' or 'flexible'
```

#### 2b. config_validator.py - Configuration Validation System
**Purpose**: Comprehensive validation for all configuration files and cross-file consistency.

**Key Classes**:
- `ConfigValidator` - Main validation engine
- `ValidationResult` - Validation results with errors/warnings
- `ValidationError` - Individual validation issue

**Validation Coverage**:
- **YAML Structure Validation**: Syntax, required fields, data types
- **Agent Reference Validation**: Ensures all referenced agents exist
- **Cross-File Consistency**: Validates consistency between configs
- **Pattern Validation**: Regex pattern syntax checking
- **Context Requirements**: Validates context parameter requirements

**Usage Example**:
```python
from kickai.config.config_validator import validate_configuration, print_validation_results

# Validate all configurations
result = validate_configuration()

# Check results
if result.is_valid:
    print("✅ All configurations valid")
else:
    print_validation_results(result)  # Show detailed errors
```

### 3. agents.py - Agent Configuration Manager
**Purpose**: Loads and processes YAML configurations with template substitution.

**Key Classes**:
- `YAMLAgentConfigurationManager` - Main configuration loader
- `AgentConfig` - Configuration data class

**Features**:
- Template variable substitution
- Performance optimizations with caching
- Configuration validation
- Dynamic context injection

### 4. llm_config.py - LLM Provider Management  
**Purpose**: Manages CrewAI-native LLM configuration for multiple providers.

**Key Features**:
- **Provider Support**: Groq, OpenAI, Google Gemini, Ollama
- **Native Parameters**: Only CrewAI-supported parameters
- **Performance Optimization**: Provider-specific tuning

**Usage**:
```python
from kickai.config.llm_config import get_llm_config

llm = get_llm_config(provider=AIProvider.GROQ)
```

### 5. tasks.yaml - Task Templates
**Purpose**: Provides task templates and patterns for CrewAI task creation.

**Template Structure**:
```yaml
shared_instructions: |
  CRITICAL: Use CrewAI native parameter passing
  Context parameters: team_id, telegram_id, username, chat_type
  
tasks:
  - name: process_general_message
    description: Process and route user messages
    expected_output: Formatted response with tool outputs
```

## Dynamic Routing System Integration

### Integration with TeamManagementSystem
The new command routing system is integrated with the existing `TeamManagementSystem` in `kickai/agents/crew_agents.py`:

```python
class TeamManagementSystem:
    def __init__(self, team_id: str):
        # Initialize routing manager
        try:
            self.routing_manager = CommandRoutingManager()
            logger.info("✅ Dynamic command routing enabled")
        except Exception as e:
            logger.warning(f"Dynamic routing unavailable, using fallback: {e}")
            self.routing_manager = None

    def _route_command_to_agent(
        self, 
        command: str, 
        chat_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentRole:
        """Route command to appropriate agent using dynamic routing."""
        if self.routing_manager:
            try:
                decision = self.routing_manager.route_command(command, chat_type, context)
                return decision.agent_role
            except Exception as e:
                logger.error(f"Dynamic routing failed: {e}")
        
        # Fallback to legacy hardcoded routing if needed
        return self._legacy_route_command(command)
```

### Migration from Hardcoded Routing
**Before (Hardcoded - REMOVED)**:
```python
# OLD - Hardcoded routing logic with fallbacks (REMOVED)
if command in ["/help", "help"]:
    return AgentRole.HELP_ASSISTANT
elif command in ["/info", "/myinfo", "/status"]:
    return AgentRole.PLAYER_COORDINATOR
# ... with silent fallback to MESSAGE_PROCESSOR
```

**After (Configuration-Driven - SIMPLIFIED)**:
```yaml
# NEW - YAML configuration in command_routing.yaml (EXACT MATCHES ONLY)
command_routing:
  help_commands:
    agent: "help_assistant"
    commands: ["/help", "help"]  # Exact commands only
  player_info_commands:
    agent: "player_coordinator" 
    commands: ["/info", "/myinfo", "/status"]  # No patterns
```

**Critical Change**: System now **FAILS FAST** if routing configuration is invalid - no silent fallbacks.

### Benefits of the Simplified + Flexible System
1. **Reliability**: No silent failures - configuration issues cause immediate failure
2. **User-Friendly**: Commands work with or without slash prefix automatically
3. **Maintainability**: Simple exact-match routing with flexible input handling
4. **Predictability**: No caching complexity, deterministic routing
5. **Debuggability**: Clear error messages when configuration is wrong
6. **Context-Awareness**: Different routing based on chat type (preserved)
7. **Validation**: Strict validation prevents configuration errors

### Flexible Command Matching Feature
The system now supports **slash-agnostic command matching**:

**How it works:**
- Configuration defines commands with slashes: `["/info", "/status"]`
- Users can type with or without slashes: `/info` or `info` both work
- Case insensitive: `/INFO`, `Info`, `info` all work
- Context restrictions also work flexibly: blocking `/addplayer` also blocks `addplayer`

**Examples:**
```yaml
# Configuration (define with slashes)
player_info_commands:
  agent: "player_coordinator" 
  commands: ["/info", "/myinfo", "/status"]

# All these user inputs work:
# /info, info, /INFO, INFO, /MyInfo, myinfo, etc.
```

**Implementation:**
- Exact match tried first (fastest path)
- Flexible match tried second (removes slashes, compares)
- Both blocked commands and routing rules use same logic
- No configuration duplication needed

## Agent Configuration Deep Dive

## Prompt Engineering Optimizations (2025)

### Optimization Results Summary
**Achievement**: 57.2% reduction in prompt tokens while preserving all critical functionality.

| Agent | Tools | Characters | Previous Est. | Optimization |
|-------|-------|------------|---------------|--------------|
| MESSAGE_PROCESSOR | 10 | 506 | ~1,200 | ~58% reduction |
| HELP_ASSISTANT | 4 | 415 | ~1,200 | ~65% reduction |
| PLAYER_COORDINATOR | 8 | 520 | ~1,200 | ~57% reduction |
| TEAM_ADMINISTRATOR | 9 | 536 | ~1,200 | ~55% reduction |
| SQUAD_SELECTOR | 15 | 593 | ~1,200 | ~51% reduction |

**Benefits**:
- **Cost Reduction**: ~57% lower API costs due to reduced token usage
- **Faster Responses**: Smaller prompts process faster
- **Preserved Functionality**: All anti-hallucination measures intact
- **Better Maintainability**: Cleaner, more focused prompts

### Optimized Agent Definition Pattern
Each agent follows this streamlined YAML pattern:
```yaml
- name: agent_name
  role: >                       # Single-line role description
    Agent Role Title
  goal: >                       # Multi-line goal description
    Primary objectives and
    responsibilities
  backstory: |                  # OPTIMIZED backstory (57% smaller)
    Brief agent description and purpose.
    
    TOOL ROUTING:
    command → tool_name (context)
    specific_action → specific_tool (parameters)
    
    PRIORITY: Key success factors and constraints
    
  tools:                        # Assigned tools list
    - tool_name_1
    - tool_name_2
  primary_entity_type: "type"   # Primary entity focus
  entity_types: ["type1"]       # Supported entity types
```

### Optimized Shared Template System
```yaml
shared_templates:
  shared_backstory: |
    You are a specialized KICKAI football team management agent.
    
    CORE RULES:
    1. NEVER fabricate data - always use tools
    2. ONE targeted tool call per request  
    3. Preserve tool output formatting exactly (including emojis)
    4. Provide clear responses even if tools fail
    
    WORKFLOW: Analyze request → Select specific tool → Execute → Respond with tool output
    
    SUCCESS METRICS: Fast, accurate, tool-based responses with preserved formatting
```

**Optimization Impact**: 
- **Reduced from ~1,200 to 433 characters (64% reduction)**
- **Preserved all critical anti-hallucination measures**
- **Maintained tool governance and error handling**
- **Streamlined workflow for clarity**

**Template Variables**: Use `{variable_name}` for substitution in agent definitions.

### Critical Configuration Rules

#### Data Integrity Rules (MANDATORY)
```yaml
# Rules - CRITICAL DATA INTEGRITY
- NEVER fabricate or invent data - MUST use appropriate tools for ALL data requests
- If you do not call a tool, you CANNOT provide data - return "No tool was called, cannot provide data"
- Use complete tool outputs without ANY modification - preserve ALL formatting, emojis, and visual elements
- PRESERVE ALL EMOJIS AND VISUAL FORMATTING from tool outputs - do not strip or modify them
- MANDATORY: For /list commands, MUST call the appropriate tool - NEVER return made-up data
```

#### Token Usage Optimization
```yaml
# Workflow - MINIMIZE TOKEN USAGE
1. Analyze user request and context
2. Select ONE appropriate tool based on request type (no exploratory calls)
3. Execute tool with provided parameters
4. Use complete tool output as response basis
5. Format response clearly with appropriate indicators
```

#### Optimization Rules
```yaml
# Optimization Rules
- Make ONLY the necessary tool call - never explore with multiple tools
- For /info, /myinfo, /status (self): go directly to get_my_status with chat_type parameter
- For specific queries: use the exact tool needed, not general commands
- Avoid redundant tool calls that waste tokens
```

## Tool Assignment Strategy (Optimized 2025)

### Agent-Specific Tool Assignment (Streamlined Routing)
```yaml
MESSAGE_PROCESSOR:
  tools: [send_message, get_user_status, get_available_commands, get_active_players, 
          get_my_status, send_announcement, send_poll, ping, version]
  routing: |
    /info|/myinfo|/status → get_my_status(telegram_id, team_id, chat_type)
    /status [name] → get_user_status(name)
    /list → get_active_players (MAIN) | list_team_members_and_players (LEADERSHIP)
    /ping → ping | /version → version
    Communications → send_message | send_announcement | send_poll

PLAYER_COORDINATOR:
  tools: [get_my_status, get_player_status, get_all_players, get_active_players,
          approve_player, list_team_members_and_players, send_message]
  routing: |
    Self queries → get_my_status (current user player info)
    Specific players → get_player_status (individual details)
    Approvals → approve_player | Player registration via /addplayer command
```

### Optimized Tool Selection Rules
Consolidated routing format for maximum clarity:
```yaml
TOOL ROUTING FORMAT:
command|alternative → tool_name (context/parameters)
action_type → specific_tool (detailed_usage)

EXAMPLES:
/info|/myinfo|/status → get_my_status(telegram_id, team_id, chat_type)
/list → get_active_players (MAIN) | list_team_members_and_players (LEADERSHIP)
Communications → send_message | send_announcement | send_poll
```

**Optimization Benefits**:
- **Symbolic notation** reduces verbosity by ~60%
- **Pattern-based routing** improves readability  
- **Consolidated rules** eliminate redundancy
- **Preserved functionality** maintains all routing logic

## LLM Configuration

### Provider Configuration
```python
# Supported providers
AIProvider.GROQ        # Primary for local development
AIProvider.OPENAI      # Production option
AIProvider.GEMINI      # Alternative provider
AIProvider.OLLAMA      # Local models

# Configuration per provider
GROQ_CONFIG = {
    "model": "llama3.1-8b-instant",
    "temperature": 0.1,
    "max_tokens": 800,
}
```

### API Configuration
```python
# The system now relies on CrewAI's native retry and backoff mechanisms
# No custom rate limiting configuration is needed
```

### CrewAI Native LLM Setup
```python
from crewai import LLM
from kickai.config.llm_config import get_llm_config

# ✅ CORRECT - Native CrewAI LLM configuration
llm = get_llm_config()  # Returns properly configured LLM instance

# Agent creation with native LLM
agent = Agent(
    role="Player Coordinator",
    goal="Manage player registrations",
    backstory="Expert in player management...",
    tools=[get_player_status],
    llm=llm,  # Use configured LLM
    verbose=True
)
```

## Configuration Management

### Loading Configurations
```python
from kickai.config.agents import get_agent_config, get_enabled_agent_configs

# Get specific agent configuration
config = get_agent_config("MESSAGE_PROCESSOR")

# Get all enabled agent configurations  
all_configs = get_enabled_agent_configs()
```

### Template Processing
```python
from kickai.config.agents import YAMLAgentConfigurationManager

manager = YAMLAgentConfigurationManager()
processed_config = manager.process_template_variables(config, context_vars)
```

### Dynamic Configuration
```python
# Runtime configuration updates
config_manager = YAMLAgentConfigurationManager()
config_manager.update_agent_tools("PLAYER_COORDINATOR", new_tools)
```

## Common Configuration Patterns

### Adding New Agent
1. **Define in agents.yaml**:
```yaml
- name: new_agent
  role: >
    New Agent Role
  goal: >
    Agent objectives
  backstory: |
    # Role
    Agent description...
    
    # Tool Selection Rules
    - Specific tool usage rules
  tools:
    - assigned_tool_1
    - assigned_tool_2
```

2. **Add to AgentRole enum**:
```python
class AgentRole(str, Enum):
    NEW_AGENT = "new_agent"
```

3. **Update crew initialization** in `crew_agents.py`

### Adding New Tools to Agent
1. **Update agents.yaml**:
```yaml
EXISTING_AGENT:
  tools:
    - existing_tool
    - new_tool_name  # Add new tool
```

2. **Ensure tool is registered** in feature `__init__.py`
3. **Update tool selection rules** in agent backstory

### Modifying Agent Behavior
1. **Update backstory rules** in agents.yaml
2. **Modify tool selection logic**
3. **Test with validation scripts**

## Performance Configuration

### Token Optimization Settings
```yaml
# Shared backstory optimizations
shared_backstory: |
  # Workflow - MINIMIZE TOKEN USAGE
  1. Analyze user request and context
  2. Select ONE appropriate tool based on request type (no exploratory calls)
  3. Execute tool with provided parameters
  4. Use complete tool output as response basis
  5. Format response clearly with appropriate indicators
```

### Agent Optimization
```yaml
agents:
  - name: message_processor
    temperature: 0.1  # Lower for consistency
  - name: help_assistant  
    temperature: 0.2  # Slightly higher for help responses
  - name: player_coordinator
    temperature: 0.1  # Precise for player operations
```

### Model-Specific Tuning
```python
# Optimized for llama3.1:8b-instruct-q4_k_m
LLAMA_OPTIMIZATION = {
    "temperature": 0.1,      # Lower for consistency
    "max_tokens": 800,       # Balanced for responses
    "top_p": 0.9,           # Focused responses
    "frequency_penalty": 0.0 # No repetition penalty
}
```

## Common Issues & Solutions

### Dynamic Routing Issues (SIMPLIFIED SYSTEM)
```bash
# Issue: System fails to start due to routing configuration
# Solution: Check configuration syntax and completeness - NO FALLBACKS
PYTHONPATH=. python -c "
from kickai.config.command_routing_manager import get_command_routing_manager
try:
    routing_manager = get_command_routing_manager()
    print('✅ Routing manager initialized')
    stats = routing_manager.get_routing_statistics()
    print(f'Rules loaded: {stats[\"routing_rules_count\"]}')
except Exception as e:
    print(f'❌ SYSTEM WILL NOT START: {e}')
    print('Fix configuration - no silent fallbacks available')
"

# Issue: Commands not routing correctly
# Solution: Test flexible command matching
PYTHONPATH=. python -c "
from kickai.config.command_routing_manager import get_command_routing_manager
routing_manager = get_command_routing_manager()

# Test both slash and non-slash versions
test_commands = ['/info', 'info', '/INFO', 'Info']
for cmd in test_commands:
    decision = routing_manager.route_command(cmd)
    print(f'{cmd:6} → {decision.agent_role.value:18} ({decision.match_type})')
# All should route to same agent with 'exact' or 'flexible' match type
"

# Issue: Configuration validation errors
# Solution: System enforces strict validation - fix all errors
PYTHONPATH=. python -c "
from kickai.config.config_validator import validate_configuration
result = validate_configuration()
if not result.is_valid:
    print('❌ CONFIGURATION INVALID - SYSTEM WILL NOT START')
    for error in result.errors:
        print(f'   {error.file_path}: {error.message}')
else:
    print('✅ Configuration valid')
"
```

### Configuration Validation Issues
```bash
# Issue: Invalid agent reference in routing config
# Solution: Validate agent names match AgentRole enum
PYTHONPATH=. python -c "
from kickai.config.config_validator import validate_configuration
from kickai.core.enums import AgentRole

result = validate_configuration()
if not result.is_valid:
    for error in result.errors:
        if 'Invalid agent' in error.message:
            print(f'❌ {error.message}')
            
print('Valid agents:', [role.value.lower() for role in AgentRole])
"

# Issue: Context validation failures
# Solution: Check required context parameters
PYTHONPATH=. python -c "
from kickai.config.command_routing_manager import get_command_routing_manager
routing_manager = get_command_routing_manager()

# Test with missing context
decision = routing_manager.route_command('/addplayer', context={'telegram_id': 123})
print(f'Context valid: {decision.context_valid}')

# Test with complete context  
decision = routing_manager.route_command('/addplayer', context={'telegram_id': 123, 'team_id': 'KTI', 'chat_type': 'leadership'})
print(f'Context valid: {decision.context_valid}')
"
```

### Integration Issues
```bash
# Issue: TeamManagementSystem not using dynamic routing
# Solution: Check routing manager initialization in crew_agents.py
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
team_system = TeamManagementSystem('TEST')

if hasattr(team_system, 'routing_manager') and team_system.routing_manager:
    print('✅ Dynamic routing active')
else:
    print('❌ Dynamic routing not initialized, check crew_agents.py')
"

# Issue: /register command still referenced
# Solution: All /register references have been removed, replaced with /addplayer
PYTHONPATH=. python -c "
import os
from pathlib import Path

# Search for any remaining /register references
project_root = Path('kickai')
register_files = []

for file_path in project_root.rglob('*.py'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '/register' in content.lower():
                register_files.append(str(file_path))
    except:
        continue

if register_files:
    print('❌ /register references still found in:')
    for file in register_files:
        print(f'   {file}')
else:
    print('✅ All /register references removed')
"
```

### Configuration Loading Issues
```bash
# Issue: YAML syntax error
# Solution: Validate YAML syntax
PYTHONPATH=. python -c "
import yaml
with open('kickai/config/agents.yaml') as f:
    config = yaml.safe_load(f)
print('✅ agents.yaml valid')

with open('kickai/config/command_routing.yaml') as f:
    config = yaml.safe_load(f)
print('✅ command_routing.yaml valid')
"
```

### Agent Tool Assignment Issues
```bash
# Issue: Tool not found for agent
# Solution: Verify tool registration and assignment
PYTHONPATH=. python -c "
from kickai.config.agents import get_agent_config
config = get_agent_config('MESSAGE_PROCESSOR')
print(f'Tools: {config.tools}')
"
```

### Template Processing Issues
```bash
# Issue: Template variable not substituted
# Solution: Check variable availability and syntax
PYTHONPATH=. python -c "
from kickai.config.agents import YAMLAgentConfigurationManager
manager = YAMLAgentConfigurationManager()
print('✅ Template manager ready')
"
```

### LLM Configuration Issues
```bash
# Issue: Provider configuration error
# Solution: Validate LLM config
PYTHONPATH=. python -c "
from kickai.config.llm_config import get_llm_config
llm = get_llm_config()
print('✅ LLM config valid')
"
```

## Security Considerations

### Configuration Security
- **No secrets in YAML**: Use environment variables
- **Validate inputs**: Template variables are sanitized
- **Access control**: Configuration loading requires proper permissions
- **Audit trail**: Configuration changes should be logged

### Agent Security
- **Tool restrictions**: Agents can only use assigned tools
- **Permission validation**: Chat type and role restrictions
- **Input sanitization**: All user inputs validated

## Development Guidelines (Updated for Optimizations)

### Configuration Changes
1. **Maintain optimization gains**: Preserve 57% token reduction achieved
2. **Test locally** with validation scripts to ensure character count stays low
3. **Use Mock Telegram UI** for testing agent behavior with streamlined prompts
4. **Validate YAML syntax** and measure prompt token usage before committing

### Adding New Configuration
1. **Follow optimized patterns** in agents.yaml - use concise TOOL ROUTING format
2. **Use streamlined shared template** for consistency (433 chars max)
3. **Preserve anti-hallucination rules** while keeping prompts concise
4. **Document configuration options** with optimization impact notes

### Performance Considerations (2025 Optimizations)
1. **Token efficiency**: Target <600 characters per agent backstory
2. **Tool routing**: Use symbolic notation (`→` format) for clarity
3. **Shared templates**: Keep shared_backstory under 450 characters
4. **Monitor optimization**: Track prompt size to prevent regression

### Optimization Validation
```bash
# Test prompt efficiency
PYTHONPATH=. python -c "
from kickai.config.agents import YAMLAgentConfigurationManager
manager = YAMLAgentConfigurationManager()
context = {'team_id': 'TEST', 'current_date': '2025-01-01'}

total_chars = 0
for role in ['MESSAGE_PROCESSOR', 'HELP_ASSISTANT', 'PLAYER_COORDINATOR', 'TEAM_ADMINISTRATOR', 'SQUAD_SELECTOR']:
    config = manager.get_agent_config(role, context)
    chars = len(config.backstory)
    total_chars += chars
    if chars > 600:
        print(f'⚠️  {role}: {chars} chars (exceeds 600 target)')
    else:
        print(f'✅ {role}: {chars} chars')

print(f'📊 Total: {total_chars} chars (target: <3000)')
"
```

## Testing Configuration

### Configuration System Testing
```bash
# Run comprehensive configuration system tests
PYTHONPATH=. python scripts/test_configuration_system.py

# This tests:
# - Configuration loading
# - Command routing accuracy
# - Context-aware routing
# - Configuration validation
# - Integration with crew agents
# - Performance metrics
```

### Configuration Validation
```bash
# Validate all configuration files
PYTHONPATH=. python -c "
from kickai.config.config_validator import validate_configuration, print_validation_results
result = validate_configuration()
print_validation_results(result)
"

# Validate specific configuration
PYTHONPATH=. python -c "
from kickai.config.config_validator import ConfigValidator
validator = ConfigValidator()
result = validator.validate_specific_file('routing')
print(f'Routing config valid: {result.is_valid}')
"

# Test command routing
PYTHONPATH=. python -c "
from kickai.config.command_routing_manager import get_command_routing_manager
from kickai.core.enums import AgentRole

routing_manager = get_command_routing_manager()

# Test specific commands
test_commands = ['/help', '/info', '/addplayer', '/attendance']
for cmd in test_commands:
    decision = routing_manager.route_command(cmd)
    print(f'{cmd:12} → {decision.agent_role.value:18} ({decision.match_type})')
"

# Test agent configuration
PYTHONPATH=. python -c "
from kickai.config.agents import get_agent_config
from kickai.core.enums import AgentRole

for role in ['MESSAGE_PROCESSOR', 'HELP_ASSISTANT', 'PLAYER_COORDINATOR']:
    config = get_agent_config(role)
    print(f'✅ {role}: {len(config.tools)} tools')
"
```

### Routing Performance Testing
```bash
# Test routing performance
PYTHONPATH=. python -c "
import time
from kickai.config.command_routing_manager import get_command_routing_manager

routing_manager = get_command_routing_manager()
commands = ['/help', '/info', '/addplayer', '/list'] * 100

start_time = time.time()
for cmd in commands:
    routing_manager.route_command(cmd)
end_time = time.time()

print(f'Routed {len(commands)} commands in {end_time - start_time:.4f}s')
print(f'Average: {(end_time - start_time) / len(commands) * 1000:.2f}ms per command')

# Check cache effectiveness
stats = routing_manager.get_routing_statistics()
print(f'Cache size: {stats[\"cache_size\"]} entries')
"
```

### Template Testing
```bash
# Test template processing
PYTHONPATH=. python -c "
from kickai.config.agents import YAMLAgentConfigurationManager

manager = YAMLAgentConfigurationManager()
config = manager.get_agent_config('MESSAGE_PROCESSOR')
print(f'✅ Template processed: {config.role}')
"
```

## Integration with System

### Dependency Container Integration
```python
from kickai.core.dependency_container import get_dependency_container

# Configuration manager available in container
container = get_dependency_container()
config_manager = container.get_configuration_manager()
```

### Runtime Configuration Updates
```python
# Hot reload configuration (development only)
config_manager.reload_configuration()
```

## Migration and Upgrades

### Configuration Schema Updates
1. **Backup existing configuration**
2. **Update schema gradually**  
3. **Test with existing agents**
4. **Validate all tool assignments**

### Agent Migration
1. **Update agents.yaml** with new structure
2. **Test agent initialization**
3. **Validate tool assignments**
4. **Run integration tests**

## Quick Validation

### Pre-Development Checklist
```bash
# 1. Validate configuration files
PYTHONPATH=. python -c "
from kickai.config.agents import YAMLAgentConfigurationManager
manager = YAMLAgentConfigurationManager()
print('✅ Configuration loaded')
"

# 2. Test LLM configuration  
PYTHONPATH=. python -c "
from kickai.config.llm_config import get_llm_config
llm = get_llm_config()
print('✅ LLM configured')
"

# 3. Validate agent definitions
PYTHONPATH=. python -c "
from kickai.config.agents import get_enabled_agent_configs
configs = get_enabled_agent_configs()
print(f'✅ {len(configs)} agents configured')
"
```

## Summary of 2025 Optimizations

### Key Achievements
- **57.2% token reduction** across all agent prompts
- **Preserved functionality**: All anti-hallucination measures intact
- **Cost efficiency**: ~57% reduction in API costs
- **Improved maintainability**: Cleaner, more focused prompts
- **Faster processing**: Smaller prompts execute more quickly

### Before vs After Comparison

| Aspect | Before (2024) | After (2025) | Improvement |
|--------|---------------|-------------|-------------|
| Shared Template | ~1,200 chars | 433 chars | 64% reduction |
| Average Agent | ~1,200 chars | 514 chars | 57% reduction |
| Total System | ~6,000 chars | 2,570 chars | 57% reduction |
| Tool Routing | Verbose rules | Symbolic notation | 60% reduction |

### Implementation Philosophy
**"Preserve functionality, optimize efficiency"** - The optimizations maintain all critical:
- Anti-hallucination measures
- Tool governance rules  
- Error handling patterns
- Agent specialization boundaries

While achieving maximum token efficiency through:
- Concise shared templates
- Symbolic tool routing notation
- Streamlined backstory format
- Consolidated rule structures

---

This CLAUDE.md provides comprehensive guidance for working with the **optimized** KICKAI configuration system. Always refer to this document when modifying agent configurations, adding new tools, or changing system behavior while maintaining the 57% efficiency gains achieved.