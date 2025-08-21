# Agentic Design - CrewAI Native Collaboration System

## 6-Agent CrewAI Native Collaboration System
**CrewAI native agent-to-agent collaboration with intelligent routing**

1. **MESSAGE_PROCESSOR** - Primary interface with intelligent coordination (`/ping`, `/version`, `/list`)
2. **HELP_ASSISTANT** - Specialized help system and user guidance (`/help`, command discovery)  
3. **PLAYER_COORDINATOR** - Player management and operations (`/info`, `/myinfo`, `/status`)
4. **TEAM_ADMINISTRATOR** - Team member management (`/addmember`, `/addplayer`)
5. **SQUAD_SELECTOR** - Match management, availability, and squad selection
6. **NLP_PROCESSOR** - Intelligent routing and context analysis agent

## CrewAI Native Collaboration Flow
```
User Input → MESSAGE_PROCESSOR → NLP_PROCESSOR Analysis → Specialist Agent → Coordinated Response
```

**Key:** CrewAI native agent-to-agent collaboration patterns with intelligent routing.

## Intelligent Agent Routing
All messages route to MESSAGE_PROCESSOR which collaborates with NLP_PROCESSOR for intelligent routing:

```yaml
# CrewAI Native Collaboration Configuration
collaboration_routing:
  primary_agent: "message_processor"  # All requests start here
  collaboration_pattern: "primary_with_nlp_routing"
  intelligent_routing: true  # Handled by agents, not configuration
```

**Key:** MESSAGE_PROCESSOR uses NLP_PROCESSOR for context-aware agent selection.

## Agent Tool Assignment
```yaml
# Example from agents.yaml - Enhanced with NLP Collaboration
MESSAGE_PROCESSOR:
  tools:
    # Direct operation tools
    - ping, version, get_my_status
    # NLP collaboration tools for intelligent routing
    - advanced_intent_recognition
    - routing_recommendation_tool
    - analyze_update_context
    - validate_routing_permissions

NLP_PROCESSOR:  
  tools:
    # Intelligent routing analysis tools
    - analyze_update_context       # Update command analysis
    - validate_routing_permissions # Permission validation
    - advanced_intent_recognition  # Intent classification
    - routing_recommendation_tool  # Agent selection
```

## Key Files & Their Purposes
- `kickai/agents/agentic_message_router.py` - **Central router** with CrewAI collaboration
- `kickai/agents/crew_agents.py` - 6-agent CrewAI native collaboration system
- `kickai/config/agents.yaml` - Agent definitions with intelligent routing capabilities
- `kickai/config/tasks.yaml` - CrewAI task templates for multi-agent coordination
- `kickai/config/command_routing.yaml` - Simplified collaboration configuration
- `kickai/core/dependency_container.py` - Service container and DI system

## Architecture Modernization (2025)
- **CrewAI Native Collaboration:** Agent-to-agent collaboration using CrewAI best practices
- **Intelligent Routing:** NLP_PROCESSOR provides context-aware agent selection
- **Multi-Agent Patterns:** Sequential, parallel, and hierarchical collaboration workflows
- **Native Async:** All tools use `async def` with CrewAI native support
- **Clean Architecture:** Feature-first structure with domain-driven design
- **Type Safety:** Consistent `telegram_id` as `int` throughout system