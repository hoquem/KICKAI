# CLAUDE.md - KICKAI Config Directory

This file provides guidance for working with the KICKAI configuration system, which manages agent configurations, LLM providers, and system-wide settings using YAML-based configuration with template processing.

## Architecture Overview

### Configuration System Components
```
kickai/config/
├── agents.yaml                    # Agent definitions and tool assignments (CRITICAL)
├── agents.py                     # YAML configuration manager
├── tasks.yaml                    # Task templates and patterns
├── llm_config.py                # LLM provider configuration  
├── optimized_agent_prompts.py   # Agent prompt optimization
├── prompt_optimizer.py          # Prompt engineering utilities
└── complexity_config.py         # System complexity settings
```

## Core Configuration Files

### 1. agents.yaml - Agent Configuration (MOST CRITICAL)
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

### 2. agents.py - Configuration Manager
**Purpose**: Loads and processes YAML configurations with template substitution.

**Key Classes**:
- `YAMLAgentConfigurationManager` - Main configuration loader
- `AgentConfig` - Configuration data class

**Features**:
- Template variable substitution
- Performance optimizations with caching
- Configuration validation
- Dynamic context injection

### 3. llm_config.py - LLM Provider Management  
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

### 4. tasks.yaml - Task Templates
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
          approve_player, register_player, list_team_members_and_players, send_message]
  routing: |
    Self queries → get_my_status (current user player info)
    Specific players → get_player_status (individual details)
    Registrations → register_player | Approvals → approve_player
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

### Configuration Loading Issues
```bash
# Issue: YAML syntax error
# Solution: Validate YAML syntax
PYTHONPATH=. python -c "
import yaml
with open('kickai/config/agents.yaml') as f:
    config = yaml.safe_load(f)
print('✅ YAML valid')
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

### Configuration Validation
```bash
# Validate all configuration files
PYTHONPATH=. python scripts/validate_config.py

# Test specific agent configuration
PYTHONPATH=. python -c "
from kickai.config.agents import get_agent_config
from kickai.core.enums import AgentRole

for role in ['MESSAGE_PROCESSOR', 'HELP_ASSISTANT', 'PLAYER_COORDINATOR']:
    config = get_agent_config(role)
    print(f'✅ {role}: {len(config.tools)} tools')
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