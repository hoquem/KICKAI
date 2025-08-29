# Telegram Integration - Bot API & Commands

## Command Processing Flow
```
User Input → AgenticMessageRouter → NLP Analysis → Agent → Tool → Response
```

**Entry Point:** `kickai/agents/agentic_message_router.py`

## Message Types & Routing
- **Slash Commands:** `/help`, `/ping`, `/addplayer` → Direct agent routing
- **Natural Language:** "update my status" → NLP_PROCESSOR → Intent analysis → Specialist agent  
- **Interactive:** Invite links, status updates

## Chat Types & Permissions
```python
chat_type: str  # "main", "leadership", "private"
```
- **Main Chat:** General commands, player operations
- **Leadership Chat:** Admin operations (`/addplayer`, `/addmember`)
- **Private Chat:** Personal commands (`/myinfo`, `/update`)

## Command Examples
**Leadership Commands (requires leadership chat):**
- `/addplayer "John Smith" "+447123456789"` → TEAM_ADMINISTRATOR
- `/addmember "Staff Member" "+447123456789"` → TEAM_ADMINISTRATOR

**Player Commands (any chat):**
- `/update position goalkeeper` → PLAYER_COORDINATOR
- `/myinfo` → PLAYER_COORDINATOR  
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