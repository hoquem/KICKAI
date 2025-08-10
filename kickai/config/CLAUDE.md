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
- **Rate Limits**: `max_rpm: 800` settings optimized for Groq's 1000 RPM limit
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
- **Rate Limiting**: Thread-safe rate limit handling
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
  max_rpm: 800                  # Optimized for Groq's 1000 RPM limit
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

#### Rate Limiting Rules
```yaml
# Rate Limiting Rules
- Make ONLY the necessary tool call - never explore with multiple tools
- For /info, /myinfo, /status (self): go directly to get_my_status with chat_type parameter
- For specific queries: use the exact tool needed, not general commands
- Avoid redundant tool calls that waste tokens
```

## Tool Assignment Strategy

### Agent-Specific Tool Assignment
```yaml
MESSAGE_PROCESSOR:
  tools:
    - send_message              # Direct messaging
    - get_user_status          # Status queries
    - get_available_commands   # Command help
    - get_active_players       # Player lists (MAIN chat)
    - get_my_status           # Self status
    - send_announcement       # Team announcements
    - send_poll              # Team polls
    - ping                   # System ping
    - version               # Version info

PLAYER_COORDINATOR:
  tools:
    - get_player_status      # Player information
    - register_new_player    # Player registration
    - update_player_info     # Player updates
    - get_registration_link  # Registration links
    - process_contact_share  # Contact processing
```

### Tool Selection Rules
Each agent has specific rules for when to use which tools:
```yaml
# Tool Selection Rules - MANDATORY TOOL USAGE
- /info, /myinfo, /status (self): MUST use get_my_status(telegram_id, team_id, chat_type) - NO exceptions
- /status [player_name]: MUST use get_user_status directly for specific players
- /list commands: MUST use get_active_players (MAIN chat) or list_team_members_and_players (LEADERSHIP chat)
- /ping: MUST use ping tool - returns pong response with timestamp and system status
- /version: MUST use version tool - returns bot version and system information
```

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
    "max_rpm": 6  # Rate limit
}
```

### Rate Limiting Configuration
```python
# Environment variables for rate limiting
AI_RATE_LIMIT_TPM=6000                    # Tokens per minute limit
AI_RATE_LIMIT_RETRY_DELAY=5.0            # Initial retry delay in seconds
AI_RATE_LIMIT_MAX_RETRIES=3              # Maximum retry attempts
AI_RATE_LIMIT_BACKOFF_MULTIPLIER=2.0     # Exponential backoff multiplier
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
  max_rpm: 3
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
3. **Update rate limits** if needed
4. **Test with validation scripts**

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

### Rate Limit Optimization
```yaml
agents:
  - name: message_processor
    max_rpm: 3  # Conservative rate limiting
  - name: help_assistant  
    max_rpm: 3  # Prevent help spam
  - name: player_coordinator
    max_rpm: 5  # Higher for player ops
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
- **Rate limiting**: Prevents abuse and overuse
- **Permission validation**: Chat type and role restrictions
- **Input sanitization**: All user inputs validated

## Development Guidelines

### Configuration Changes
1. **Test locally** with validation scripts
2. **Use Mock Telegram UI** for testing
3. **Validate YAML syntax** before committing
4. **Test all affected agents** thoroughly

### Adding New Configuration
1. **Follow existing patterns** in agents.yaml
2. **Use shared templates** for consistency
3. **Add appropriate validation**
4. **Document configuration options**

### Performance Considerations
1. **Minimize token usage** in backstories
2. **Optimize rate limits** per agent type
3. **Use efficient tool selection rules**
4. **Cache configuration data** appropriately

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

This CLAUDE.md provides comprehensive guidance for working with the KICKAI configuration system. Always refer to this document when modifying agent configurations, adding new tools, or changing system behavior.