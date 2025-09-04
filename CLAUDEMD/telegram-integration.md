# Telegram Integration - Bot API & Context-Aware Commands

## Context-Aware Command Processing Flow
```
User Input → Manager LLM → Chat Context Analysis → Specialist Agent → Tool → Response
```

**Entry Point:** `kickai/agents/crew_agents.py` (TeamManagementSystem)

## Revolutionary Context-Aware Routing
**Problem Solved:** `/myinfo` in main chat was incorrectly using member tools instead of player tools

**Solution:** Chat context determines user treatment and tool selection

### Context-Aware Message Routing
- **Slash Commands:** `/help`, `/ping`, `/myinfo` → Manager LLM analyzes context → Routes to appropriate agent
- **Natural Language:** "show my status" → Manager LLM → Context analysis → Specialist agent  
- **Context-Aware Tools:** Different tools used based on chat type

## Chat Context & User Treatment
```python
chat_type: str  # "main", "leadership", "private"
```

### Chat Context Rules
- **Main Chat** → Users are **PLAYERS** → `player_coordinator` + player tools
- **Leadership Chat** → Users are **MEMBERS** → `team_administrator` + member tools  
- **Private Chat** → Users are **PLAYERS** → `player_coordinator` + player tools

## Context-Aware Command Examples

### `/myinfo` Command - Context Determines Routing
**Main Chat:**
- `/myinfo` → `player_coordinator` → `get_player_status_current` → Player game data

**Leadership Chat:**
- `/myinfo` → `team_administrator` → `get_member_status_current` → Admin/member data

**Private Chat:**
- `/myinfo` → `player_coordinator` → `get_player_status_current` → Player game data

### Leadership Commands (requires leadership chat):
- `/addplayer "John Smith" "+447123456789"` → TEAM_ADMINISTRATOR → `create_player`
- `/addmember "Staff Member" "+447123456789"` → TEAM_ADMINISTRATOR → `create_member`

### Player Commands (main/private chat):
- `/update position goalkeeper` → PLAYER_COORDINATOR → `update_player_field`
- `/list` → PLAYER_COORDINATOR → `list_players_active`  
- `/help` → HELP_ASSISTANT

## Response Format
All responses use standardized JSON format:
```python
return create_json_response(ResponseStatus.SUCCESS, 
    message="Operation completed", 
    data={"player_name": "John", "status": "active"})
```

## Bot Integration Files
- `kickai/agents/agentic_message_router.py` - Main router
- `kickai/infrastructure/telegram/` - Telegram API integration
- `tests/mock_telegram/` - Testing interface (localhost:8001)

**Mock Testing:** `PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py`