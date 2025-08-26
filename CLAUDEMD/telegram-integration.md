# Telegram Integration - Bot API & Messaging

## Telegram Bot Architecture
KICKAI integrates with Telegram through a multi-layered approach:

- **Bot Integration Layer**: `kickai/infrastructure/telegram/`
- **Message Router**: `kickai/agents/agentic_message_router.py`
- **Command Processing**: Feature-based command handlers
- **Response Formatting**: Standardized message templates

## Command System (Clean Architecture Integration)
Commands are processed through the agentic message router and routed to appropriate agents using Clean Architecture patterns:

```python
# Clean Architecture Command Flow
User Input ("/addplayer John +447123456789") 
→ MESSAGE_PROCESSOR (Application Layer)
→ NLP_PROCESSOR (intent analysis) 
→ TEAM_ADMINISTRATOR (calls application tools)
→ Application Tool (get_container())
→ Domain Service (pure business logic)
→ Repository Interface → Infrastructure Implementation
→ Formatted Response
```

### Tool Discovery and Execution
```python
# Application Layer Tool (kickai/features/*/application/tools/)
@tool("add_team_member_simplified", result_as_answer=True)  
async def add_team_member_simplified(telegram_id: int, team_id: str, username: str, chat_type: str, ...):
    container = get_container()  # ✅ Dependency injection at boundary
    service = container.get_service(TeamMemberManagementService)
    result = await service.add_team_member(...)  # ✅ Pure business logic call
    return create_json_response(ResponseStatus.SUCCESS, data=result)
```

## Telegram-Specific Features

### Message Types
- **Slash Commands**: `/help`, `/ping`, `/addplayer`, etc.
- **Natural Language**: Intelligent routing via NLP_PROCESSOR
- **Interactive Elements**: Invite links, status updates
- **Notifications**: Admin alerts, system messages

### Chat Type Handling
```python
chat_type: str  # "main", "leadership", "private"
```
- **Main Chat**: General team communication
- **Leadership Chat**: Admin-only operations (`/addplayer`, `/addmember`)
- **Private Chat**: Individual user interactions

### Permission System
Role-based access control integrated with Telegram chat membership:
- **PUBLIC**: Basic access
- **PLAYER**: Registered team members
- **LEADERSHIP**: Admin operations
- **ADMIN**: System administration
- **SYSTEM**: Internal operations

## Bot Configuration
```bash
# Environment variables for Telegram integration
TELEGRAM_BOT_TOKEN=<bot_token>
TELEGRAM_ADMIN_USER_ID=<admin_id>
KICKAI_INVITE_SECRET_KEY=<invite_secret>
```

## Key Integration Files

### Core Integration
- `kickai/infrastructure/telegram/telegram_bot_service.py` - Main bot service
- `kickai/features/communication/` - Message handling and formatting
- `kickai/agents/agentic_message_router.py` - Central message routing
- `kickai/config/command_routing.yaml` - Command-to-agent mapping

### Clean Architecture Structure
- `kickai/features/*/application/tools/` - **CrewAI tools** (Telegram command endpoints)
- `kickai/features/*/domain/services/` - **Business logic** (chat-agnostic operations)
- `kickai/features/*/infrastructure/` - **External integrations** (Telegram API, Firebase)

### Tool-to-Service Pattern
```python
# Telegram integration follows Clean Architecture boundaries:
Telegram Message → Application Tool → Domain Service → Repository Interface → Infrastructure
```