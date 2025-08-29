# Agentic Design - 6-Agent CrewAI System

## Agent Architecture
**CrewAI native collaboration with NLP routing**

1. **MESSAGE_PROCESSOR** - Primary interface (`/ping`, `/version`, `/list`)
2. **NLP_PROCESSOR** - **Intelligent routing** via intent analysis
3. **PLAYER_COORDINATOR** - Player ops (`/info`, `/myinfo`, `/status`)
4. **TEAM_ADMINISTRATOR** - Team mgmt (`/addmember`, `/addplayer`) 
5. **SQUAD_SELECTOR** - Match/availability management
6. **HELP_ASSISTANT** - Help system (`/help`, command discovery)

## Collaboration Flow
```
User Input → MESSAGE_PROCESSOR → NLP_PROCESSOR → Specialist → Response
```

## Routing Pattern
MESSAGE_PROCESSOR collaborates with NLP_PROCESSOR for intelligent agent selection:

```yaml
routing:
  primary: "message_processor" 
  pattern: "nlp_analysis_routing"
  tools: ["advanced_intent_recognition", "routing_recommendation_tool"]
```

## Tool Assignment
```yaml
MESSAGE_PROCESSOR:
  tools: [ping, version, get_my_status, advanced_intent_recognition, routing_recommendation_tool]

NLP_PROCESSOR:  
  tools: [analyze_update_context, validate_routing_permissions, advanced_intent_recognition, routing_recommendation_tool]

PLAYER_COORDINATOR:
  tools: [update_player_field, get_player_info, get_my_status, check_player_exists]

TEAM_ADMINISTRATOR:
  tools: [add_player, add_team_member_simplified, get_team_members]

SQUAD_SELECTOR:
  tools: [mark_availability, list_matches, select_squad, get_attendance]

HELP_ASSISTANT:
  tools: [get_contextual_help, explain_command, list_available_commands]
```

## Key Architecture Files
**Core:**
- `kickai/agents/agentic_message_router.py` - Entry router
- `kickai/agents/crew_agents.py` - 6-agent system
- `kickai/config/agents.yaml` - Agent definitions
- `kickai/core/dependency_container.py` - DI system

**Clean Architecture (✅ Complete Migration):**
- Application: `features/*/application/tools/` - @tool decorators
- Domain: `features/*/domain/services/` - Pure business logic
- Infrastructure: `features/*/infrastructure/` - Database/external

## Tool Pattern
```python
# Application layer
@tool("name", result_as_answer=True)  
async def name(...): return await name_domain(...)

# Domain layer (no @tool decorator)
async def name_domain(...):
    service = get_container().get_service(Service)
    return create_json_response(ResponseStatus.SUCCESS, data=result)
```

**Migration Complete:** 62 @tool decorators moved to application layer, zero framework deps in domain