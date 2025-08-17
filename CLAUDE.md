# KICKAI Development Guide

AI-powered football team management system built with a **6-agent CrewAI architecture** and clean architecture principles.

**Version:** 3.1 | **Status:** Production Ready | **Python:** 3.11+ (MANDATORY)  
**Deployment:** Railway (Production) | **Local Dev:** Groq | **Test UI:** http://localhost:8001

## Quick Start

### Prerequisites
```bash
# 1. Python 3.11+ (MANDATORY)
python3.11 check_python_version.py
source venv311/bin/activate

# 2. Environment variables
AI_PROVIDER=groq
KICKAI_INVITE_SECRET_KEY=test-invite-secret-key-for-testing-only
FIREBASE_PROJECT_ID=<project_name>
FIREBASE_CREDENTIALS_FILE=credentials/<filename>.json

# 3. Always use PYTHONPATH
PYTHONPATH=. python run_bot_local.py
```

### Essential Commands
```bash
# Development
make dev                           # Start development server
./start_bot_safe.sh               # Safe startup (kills existing processes)
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py  # Mock UI (http://localhost:8001)

# Testing
make test                          # All tests
make test-unit                     # Unit tests only
PYTHONPATH=. python -m pytest tests/unit/test_file.py::test_function -v  # Specific test

# Code Quality
make lint                          # All linting and formatting
ruff check kickai/ && ruff format kickai/ && mypy kickai/  # Individual tools

# Validation
PYTHONPATH=. python scripts/run_health_checks.py
```

## System Architecture

### 6-Agent CrewAI System
1. **MessageProcessorAgent** - Primary interface and routing
2. **HelpAssistantAgent** - Help system and guidance  
3. **PlayerCoordinatorAgent** - Player management
4. **TeamAdministrationAgent** - Team member management
5. **SquadSelectorAgent** - Squad selection and availability
6. **NLPProcessorAgent** - Natural language processing and understanding

### Processing Flow
```
User Input → AgenticMessageRouter → CrewAI Agent → Tool Execution → Response
```

### Project Structure
```
kickai/
├── features/           # Domain features (player_registration, team_administration, etc.)
├── agents/            # 6-agent CrewAI system
├── core/              # Core utilities and DI container
└── database/          # Firebase/Firestore integration
```

### Feature Architecture
```
kickai/features/<feature_name>/
├── application/commands/     # @command decorators
├── domain/
│   ├── tools/               # @tool decorators (async)
│   ├── services/            # Business logic (async)
│   └── entities/            # Domain models
└── infrastructure/          # Repositories, external APIs
```

## CrewAI Tool Development (MANDATORY)

### Standard Tool Pattern
```python
from crewai.tools import tool
from loguru import logger
from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response

@tool("tool_name", result_as_answer=True)
async def tool_name(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    # ... tool-specific parameters
) -> str:
    """Tool description."""
    try:
        # 1. Get services from container
        container = get_container()
        service = container.get_service(ServiceClass)
        
        # 2. Direct async service calls
        result = await service.async_method(...)
        
        # 3. Return standardized response
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"❌ Error in tool_name: {e}")
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### Implementation Requirements
- **Always**: Use `async def` for tool functions
- **Always**: Use `ResponseStatus` enum for status values
- **Always**: Call services with `await` directly
- **Always**: Return JSON string responses
- **Never**: Use `asyncio.run()` in tools
- **Never**: Access database directly from tools
- **Never**: Create sync wrapper methods

### Anti-Patterns to Avoid
```python
# ❌ NEVER use asyncio.run() in tools
@tool("bad_tool")
def bad_tool(...):
    return asyncio.run(async_function(...))  # Causes event loop conflicts

# ❌ NEVER bypass services in tools
@tool("bad_tool")
async def bad_tool(...):
    database = container.get_database()  # Use services instead
    await database.query_documents(...)

# ❌ NEVER use string status values
create_json_response("success", ...)  # Use ResponseStatus.SUCCESS
```

## Service Architecture

### Clean Architecture Flow
```
Tool (async) → Service (async) → Repository (async) → Database (async)
     ↓              ↓                ↓                    ↓
ResponseStatus  Domain Logic    Domain Models       Firestore
   Enum          & Rules        (Team, Player)       Client
```

### Service Layer Pattern
```python
class TeamService:
    """Services use async methods only - no sync wrappers."""
    
    async def get_team(self, *, team_id: str) -> Optional[Team]:
        """Returns domain model, not raw database document."""
        return await self.repository.get_team_by_id(team_id)
    
    async def create_player(self, player: Player) -> Player:
        """Business logic in service, not in tool."""
        return await self.repository.create(player)
```

### Repository Pattern
```python
class FirebaseTeamRepository(TeamRepositoryInterface):
    """Repositories handle database operations and model conversion."""
    
    async def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """Get from Firestore, return domain model."""
        doc = await self.db.get_document("kickai_teams", team_id)
        return Team.from_dict(doc) if doc else None
    
    async def create(self, team: Team) -> Team:
        """Save domain model to Firestore."""
        await self.db.set_document("kickai_teams", team.id, team.to_dict())
        return team
```

## Development Best Practices

### Code Standards
```python
# ✅ Use enums instead of magic strings
from kickai.core.enums import ChatType, UserStatus, ResponseStatus
if chat_type.lower() != ChatType.LEADERSHIP.value:
    raise AuthorizationError("Leadership required")

# ✅ Always validate service availability
container = get_container()
team_service = container.get_service(TeamService)
if not team_service:
    raise ServiceNotAvailableError("Team service not available")

# ✅ Use domain services, not direct database access
team = await team_service.get_team(team_id=team_id)
if not team:
    raise TeamNotFoundError(f"Team not found: {team_id}")

# ✅ Simple exception handling
try:
    result = await service.method()
    return create_json_response(ResponseStatus.SUCCESS, data=result)
except Exception as e:
    logger.error(f"❌ Error: {e}")
    return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### Import Standards
```python
# ✅ Use absolute imports
from kickai.features.player_registration.domain.tools.player_tools import get_status

# ❌ Never use relative imports
from .domain.tools.player_tools import get_status

# ✅ Standard imports (no fallbacks)
from loguru import logger
from crewai.tools import tool
from kickai.core.enums import ChatType, ResponseStatus
from kickai.utils.tool_helpers import create_json_response
```

## Testing

### Test Organization
- `tests/unit/` - Component tests
- `tests/integration/` - Service tests
- `tests/e2e/` - Workflow tests
- `tests/mock_telegram/` - UI testing

### Tool Testing Pattern
```python
from unittest.mock import AsyncMock, patch

async def test_tool_with_mocks():
    with patch('kickai.core.dependency_container.get_container') as mock_container:
        mock_service = AsyncMock()
        mock_container.return_value.get_service.return_value = mock_service
        
        result = await add_player(
            telegram_id=123456789, team_id="KTI", username="test",
            chat_type="leadership", player_name="John", phone_number="+447123456789"
        )
        
        mock_service.create_player.assert_called_once()
        assert "success" in result

# Test error handling
async def test_tool_error_handling():
    result = await add_player(telegram_id=None, ...)  # Invalid
    
    import json
    response = json.loads(result)
    assert response["status"] == "error"
    assert "telegram_id" in response["message"].lower()
```

### Mock Telegram Testing
```bash
# Start Mock Telegram UI (recommended for testing)
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001
```

**Benefits**:
- Liverpool FC themed interface for professional testing
- No real Telegram API calls needed during development
- Complete command testing including slash commands and natural language
- Real-time agent responses and system monitoring

## Development Workflow

### Adding New Features
1. Create feature in `kickai/features/` following clean architecture
2. Add async tools with `@tool` decorator
3. Register commands with `@command` decorator  
4. Update agent tool assignments in `agents.yaml`
5. Add tests (unit, integration, E2E)

### Adding New Tools
1. Create async tool function with `@tool` decorator
2. Export from feature's `__init__.py`
3. Add to agent configuration in `agents.yaml`
4. Use services for business logic

## Common Issues & Solutions

### Tool Issues
- **Tool not executing** → Check registration in feature `__init__.py`
- **Import errors** → Use `PYTHONPATH=.` when running
- **Enum errors** → Use `.value` for enum comparisons (`ChatType.LEADERSHIP.value`)
- **Service not available** → Check dependency container initialization

### Development Issues  
- **Python version errors** → Must use Python 3.11+ with `venv311`
- **Process conflicts** → Use `./start_bot_safe.sh`
- **Module not found** → Ensure `PYTHONPATH=.` is set
- **Firebase auth** → Check credentials file path

### Type Issues
- **telegram_id errors** → Must be `int` (not string)
- **Response format** → Use `ResponseStatus` enum

## System Health Check

```bash
# Complete system validation
PYTHONPATH=. python scripts/run_health_checks.py

# Container initialization
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test_key python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('✅ Container OK')
"

# Agent system
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('KTI')
print(f'✅ {len(system.agents)} agents loaded')
"
```

## Key Architecture Files

### Essential Files
- `kickai/agents/crew_agents.py` - 6-agent system
- `kickai/agents/agentic_message_router.py` - Message routing
- `kickai/core/dependency_container.py` - Service container
- `kickai/config/agents.yaml` - Agent configuration

### System Modernization (2025)
- **Unified Router**: `AgenticMessageRouter` handles all message routing (removed legacy handlers)
- **Native Async**: All tools use `async def` with CrewAI native support (removed sync wrappers)
- **Type Safety**: Consistent `telegram_id` as `int` throughout system
- **Memory Management**: Proper cleanup and resource management

## Legacy Migration Notes

### For Developers Working on Old Code
If you encounter references to deleted components:

1. **Handler Classes** → Methods in `AgenticMessageRouter`
   - `UnregisteredUserHandler` → `_get_unregistered_user_message()`
   - `ContactShareHandler` → `route_contact_share()`
   - `RegisteredUserHandler` → `_process_with_crewai_system()`

2. **Context Classes** → Direct logic in router
   - `ContextBuilder` → Logic moved to router methods
   - `AgentContext` → Use `tests/agents/test_context.py` for tests

3. **Factory Classes** → Use dependency container
   - `AgentSystemFactory` → Removed, use `dependency_container.py`

### System Benefits
- **-500+ lines** of duplicate code eliminated
- **Single source of truth** for message routing
- **Consistent type handling** (telegram_id as int)
- **Better error handling** with circuit breakers
- **Improved testability** with unified routing

## Performance Characteristics
- **Response Time**: < 2 seconds for most operations
- **Async Efficiency**: Native async execution throughout the stack
- **Error Recovery**: Graceful degradation with clear error messages
- **Resource Usage**: Efficient async I/O without thread pool overhead