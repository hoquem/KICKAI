# Configuration Directory

This directory contains centralized configuration files for the KICKAI system.

## Files

### `agents.py`
Unified agent configuration that centralizes all agent roles, backstories, and tool mappings in a single location.

**Features:**
- **Agent Definitions**: Complete agent definitions including roles, goals, and backstories
- **Capability Matrix**: Defines what each agent can do with proficiency levels
- **Tool Mappings**: Specifies which tools each agent has access to
- **Default Configurations**: Standard settings for each agent type
- **Utility Functions**: Helper functions for agent selection and configuration

**Key Classes:**
- `AgentConfiguration`: Main configuration management class
- `AgentDefinition`: Complete agent definition with role, goal, and backstory
- `AgentCapability`: Represents an agent capability with proficiency level
- `AgentConfig`: Configuration for individual agents
- `CapabilityType`: Enum defining all available capability types

**Usage Examples:**
```python
from config.agents import (
    get_agent_definition,
    get_agent_capabilities,
    get_agent_tools,
    find_best_agent_for_capabilities,
    AgentRole,
    CapabilityType
)

# Get agent definition
definition = get_agent_definition(AgentRole.PLAYER_COORDINATOR)

# Get agent capabilities
capabilities = get_agent_capabilities(AgentRole.PLAYER_COORDINATOR)

# Get agent tools
tools = get_agent_tools(AgentRole.PLAYER_COORDINATOR)

# Find best agent for specific capabilities
best_agent = find_best_agent_for_capabilities([
    CapabilityType.PLAYER_MANAGEMENT,
    CapabilityType.DATA_RETRIEVAL
])
```

### `bot_config.example.json`
**⚠️ DEPRECATED**: Example bot configuration file for reference only.

**IMPORTANT**: Bot configuration is now stored in Firestore (teams collection). Each team entity contains bot configuration fields:
- `bot_id`: Bot identifier
- `bot_token`: Telegram bot token
- `main_chat_id`: Main chat ID
- `leadership_chat_id`: Leadership chat ID

The JSON configuration files are no longer used by the system and exist only for documentation purposes.

## Configuration Architecture

### Bot Configuration (Firestore)
- **Primary Source**: Teams collection in Firestore
- **Fields**: `bot_id`, `bot_token`, `main_chat_id`, `leadership_chat_id`  
- **Management**: Via `TeamService.set_bot_config()` method
- **Loading**: Via `MultiBotManager.load_bot_configurations()`

### Agent Configuration (YAML)
1. **Single Source of Truth**: All agent properties are defined in one place
2. **Reduced Code Duplication**: Eliminates scattered agent definitions  
3. **Easy Maintenance**: Changes to agent properties only need to be made in one location
4. **Consistent Structure**: All agents follow the same configuration pattern
5. **Dynamic Tool Assignment**: Tools are assigned based on configuration rather than hardcoded
6. **Standardized Parameters**: All tools use consistent parameter order (telegram_id, team_id, username, chat_type)

## Agent Roles

The system supports 8 specialized agents:

1. **Message Processor**: User interface and command parsing
2. **Team Manager**: Strategic coordination and planning
3. **Player Coordinator**: Player management and registration
4. **Finance Manager**: Financial tracking and payments
5. **Performance Analyst**: Performance analysis and insights
6. **Learning Agent**: Continuous learning and optimization
7. **Onboarding Agent**: Player onboarding and registration
8. **Command Fallback Agent**: Handles unrecognized commands

## Capability Types

Agents are defined by their capabilities:

- **Intent Analysis**: Understanding user intent
- **Context Management**: Managing conversation context
- **Routing**: Routing requests to appropriate agents
- **Strategic Planning**: High-level strategic planning
- **Coordination**: Coordinating multiple agents
- **Decision Making**: Making strategic decisions
- **Player Management**: Managing player operations
- **Financial Management**: Managing financial operations
- **Data Retrieval**: Retrieving data from various sources
- **Natural Language Understanding**: Understanding natural language
- **Operational Tasks**: Handling day-to-day operations
- **High Level Operations**: Handling high-level operations

## Tool Mappings

Each agent has access to specific tools based on their role:

- **Player Tools**: GetAllPlayersTool, GetPlayerByIdTool, GetPendingApprovalsTool, etc.
- **Communication Tools**: SendMessageTool, SendPollTool, SendAnnouncementTool
- **Logging Tools**: LogCommandTool, LogEventTool

## Configuration Override

The system supports configuration overrides through the config manager:

```python
# Override specific agent settings
agent_configs = {
    'player_coordinator': {
        'enabled': True,
        'max_iterations': 8,
        'verbose': True
    }
}
```

## Migration Guide

When adding new agents or modifying existing ones:

1. Update `AgentConfiguration.AGENT_DEFINITIONS` with new agent definitions
2. Add capabilities to `AgentConfiguration.CAPABILITY_MATRIX`
3. Define tool mappings in `AgentConfiguration.TOOL_MAPPINGS`
4. Set default configuration in `AgentConfiguration.DEFAULT_CONFIGS`
5. Update the agent class in `src/agents/crew_agents.py` to use the unified configuration

This ensures all agent properties are centrally managed and consistent across the system. 