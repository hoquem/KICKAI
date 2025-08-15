# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KICKAI is an AI-powered football team management system built with a **5-agent CrewAI architecture** and clean architecture principles. The system processes ALL user interactions through specialized AI agents, ensuring intelligent, context-aware responses.

**Version:** 5.0  
**Status:** Production Ready with Simplified Agentic Architecture  
**Python Version:** 3.11+ (MANDATORY - Will NOT work with Python 3.9)  
**Deployment:** Railway (Production), Local Development with Groq  
**Test UI:** Mock Telegram at http://localhost:8001

## Critical Requirements

### ⚠️ Python 3.11+ MANDATORY (NOT 3.9)
**IMPORTANT**: This project requires Python 3.11+ and will NOT work with Python 3.9. Always verify the Python version before starting work.

```bash
# Always verify Python version first
python3.11 check_python_version.py

# Activate correct virtual environment  
source venv311/bin/activate

# Verify activation
which python  # Should show: /path/to/KICKAI/venv311/bin/python
python --version  # Should show: Python 3.11.x
```

### Essential Environment Variables
```bash
# Always use PYTHONPATH when running
PYTHONPATH=. python run_bot_local.py

# Core configuration
AI_PROVIDER=groq  # primary for local development, groq, gemini, openai, ollama
KICKAI_INVITE_SECRET_KEY=test-invite-secret-key-for-testing-only
FIREBASE_PROJECT_ID=<project name>
FIREBASE_CREDENTIALS_FILE=credentials/<filename>.json

# API configuration
# The system now relies on CrewAI's native retry and backoff mechanisms
```

## Common Development Commands

### Starting Development
```bash
# Standard startup (ALWAYS use this pattern)
source venv311/bin/activate && PYTHONPATH=. python run_bot_local.py

# Safe startup (kills existing processes)
./start_bot_safe.sh

# Mock Telegram UI
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001

```

### Testing
```bash
# Run all tests
make test

# Specific test types
make test-unit          # Unit tests
make test-integration   # Integration tests  
make test-e2e          # E2E tests

# Run specific test
PYTHONPATH=. python -m pytest tests/unit/test_file.py::test_function -v -s

# Run with specific features
PYTHONPATH=. python -m pytest tests/unit/features/player_registration/ -v
PYTHONPATH=. python -m pytest tests/integration/features/ -v

# Run with coverage
PYTHONPATH=. python -m pytest tests/ --cov=kickai --cov-report=html
```

### Code Quality
```bash
make lint  # Run all linting and formatting

# Individual tools (must be in venv311)
source venv311/bin/activate && ruff check kickai/
source venv311/bin/activate && ruff format kickai/
source venv311/bin/activate && mypy kickai/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Architecture Overview

### 5-Agent CrewAI System
The system uses **5 essential agents** (simplified from 11):

1. **MessageProcessorAgent** - Primary interface and command routing
2. **HelpAssistantAgent** - Help system and guidance  
3. **PlayerCoordinatorAgent** - Player management and onboarding
4. **TeamAdministrationAgent** - Team member management
5. **SquadSelectorAgent** - Squad selection and availability

### Unified Processing Pipeline
```
User Input → AgenticMessageRouter → CrewAI System → Agent Selection → Tool Execution → Response

```
- Both slash commands and natural language use the **same pipeline**
- Consistent security and permission checking
- No duplicate logic between input types

### Feature-First Clean Architecture
```
kickai/
├── features/                    # Domain-driven feature modules
│   ├── player_registration/     
│   ├── team_administration/     
│   ├── match_management/        
│   └── shared/                  
├── agents/                      # 5-Agent CrewAI System
│   ├── crew_agents.py          # Agent definitions
│   └── agentic_message_router.py # Central routing (MODERNIZED)
├── core/                        # Core utilities
│   ├── command_registry.py     # Command discovery
│   └── dependency_container.py # DI container
└── database/                    # Firebase/Firestore
```

## Critical System Changes (Recent Updates)

### ✅ **Legacy Component Removal (Completed)**
The following legacy components have been **REMOVED** and functionality consolidated:
- `kickai/agents/handlers/` - All message handlers removed (functionality moved to router)
- `kickai/agents/context/` - Context builder removed (logic moved to router)
- `kickai/core/factories/agent_system_factory.py` - Unused factory removed

### ✅ **AgenticMessageRouter Modernization**
The `AgenticMessageRouter` is now the **single source of truth** for all message routing:
- **Consolidated Logic**: All handler functionality moved to router methods
- **Resource Management**: Circuit breaker patterns and memory management
- **Type Safety**: Consistent `telegram_id` handling as `int` throughout
- **Memory Management**: Proper cleanup and garbage collection

### ✅ **Sync Method Wrapper Cleanup (2025)**
All sync wrapper methods using `asyncio.run()` have been **REMOVED** for CrewAI 2025 compatibility:
- **PlayerService**: Removed 6 `*_sync()` wrapper methods (~100 lines)
- **TeamMemberService**: Removed 6 `*_sync()` wrapper methods (~120 lines)
- **InviteLinkService**: Removed 1 `create_player_invite_link_sync()` method (~35 lines)
- **CrewAgents**: Removed unused sync `execute_task()` function (~5 lines)
- **Total Cleanup**: ~260 lines of obsolete sync wrapper code removed

**Why This Was Necessary**:
- `asyncio.run()` calls within running event loops caused `RuntimeError`
- CrewAI 2025 natively supports async tools without wrapper methods
- Dual sync/async interfaces violated Single Responsibility Principle
- Sync wrappers used inefficient ThreadPoolExecutor workarounds

## Critical CrewAI Rules (MANDATORY) - UPDATED 2025

### 🚨 CRITICAL: CrewAI Tools MUST Be Synchronous!

**IMPORTANT UPDATE (Dec 2024)**: Despite documentation claims, CrewAI 0.159.0 does NOT properly support async tools. Tools MUST be synchronous (`def`, not `async def`). Async tools cause "coroutine was never awaited" errors.

### ✅ **Tool Implementation Pattern (DEFINITIVE)**

All tools MUST be synchronous functions that use our standard bridge utility for async operations.

```python
# ✅ CORRECT - Synchronous tool with async bridge utility
from kickai.utils.async_utils import run_async_in_sync

@tool("add_player", result_as_answer=True)
def add_player(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_name: str,
    phone_number: str
) -> str:
    """Synchronous tool with async bridge pattern."""
    
    async def _async_operations():
        # All async operations encapsulated here
        container = get_container()
        database = container.get_database()
        team_service = container.get_service(TeamService)
        
        # Async database and service calls
        existing = await database.query_documents("kickai_players", filters)
        team = await team_service.get_team(team_id=team_id)
        await database.set_document("kickai_players", player_id, player_data)
        
        return create_json_response("success", data=success_message)
    
    # Bridge to sync using standard utility
    return run_async_in_sync(_async_operations())
```

### ❌ **FORBIDDEN Anti-Patterns**
```python
# ❌ ANTI-PATTERN - Async tool functions (CrewAI can't await them)
@tool("add_player", result_as_answer=True)  
async def add_player(...) -> str:  # WRONG - causes "coroutine was never awaited"
    result = await some_service.method()
    return result

# ❌ ANTI-PATTERN - Using asyncio.run() directly
@tool("add_player", result_as_answer=True)  
def add_player(...) -> str:
    return asyncio.run(_add_player_async(...))  # CAUSES EVENT LOOP CONFLICTS

# ❌ ANTI-PATTERN - ThreadPoolExecutor workarounds
@tool("send_message")
def send_message(...) -> str:
    try:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, service.send_message(...))
            return future.result()
    except RuntimeError:
        return asyncio.run(service.send_message(...))  # COMPLEX AND ERROR-PRONE

# ❌ ANTI-PATTERN - Mixed async/sync helper patterns  
@tool("create_match")
def create_match(...) -> str:
    return asyncio.run(_create_match_async(...))  # UNNECESSARY COMPLEXITY

async def _create_match_async(...) -> str:
    # Helper function - merge into main tool instead
    pass
```

### ✅ **Async Best Practices for CrewAI Tools**
```python
# ✅ CORRECT - Direct async tool with proper error handling
@tool("team_member_registration", result_as_answer=True)
async def team_member_registration(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    name: str,
    phone_number: str,
    role: str,
    is_admin: bool = False
) -> str:
    """Register team member using native async pattern."""
    try:
        # Get services
        container = get_container()
        team_member_service = container.get_service("TeamMemberService")
        
        # Direct async service calls
        created_id = await team_member_service.create_team_member(team_member)
        
        return create_json_response("success", data={
            'member_id': created_id,
            'status': 'registered'
        })
    except Exception as e:
        logger.error(f"❌ Error in team_member_registration: {e}")
        return create_json_response("error", message=f"Registration failed: {str(e)}")

# ✅ CORRECT - Async communication tool
@tool("send_message", result_as_answer=True)
async def send_message(telegram_id: int, team_id: str, username: str, chat_type: str, message: str) -> str:
    """Send message using native async."""
    try:
        container = get_container()
        communication_service = container.get_service("CommunicationService")
        
        # Direct async call - no threading needed
        success = await communication_service.send_message(message, chat_type_enum, team_id)
        
        if success:
            return create_json_response("success", data="Message sent successfully")
        else:
            return create_json_response("error", message="Failed to send message")
    except Exception as e:
        logger.error(f"❌ Error in send_message: {e}")
        return create_json_response("error", message="Failed to send message")
```

### Task Creation - Native Structured Description
```python
# ✅ CORRECT - Structured task description for async tools
structured_description = f"""
User Request: {task_description}

Context Information:
- Team ID: {team_id}
- User Telegram ID: {telegram_id} 
- Username: {username}
- Chat Type: {chat_type}

Instructions: Use the provided context information to call tools 
with the appropriate parameters. All tools are async and will be 
handled automatically by CrewAI.
"""

task = Task(
    description=structured_description,
    agent=agent.crew_agent,
    expected_output="A clear and helpful response to the user's request",
)
```

### Tool Implementation Requirements (CRITICAL - Dec 2024)
- **❌ NEVER**: Use `async def` for tool functions - CrewAI cannot await them
- **❌ NEVER**: Tools calling other tools or services directly
- **❌ NEVER**: Use `asyncio.run()` directly - causes event loop conflicts
- **❌ NEVER**: ThreadPoolExecutor workarounds - use standard utility
- **✅ ALWAYS**: Tools are synchronous (`def`) functions
- **✅ ALWAYS**: Use `run_async_in_sync` utility from `kickai.utils.async_utils`
- **✅ ALWAYS**: Encapsulate async operations in nested functions
- **✅ ALWAYS**: Parameters passed directly via function signatures
- **✅ ALWAYS**: Tools return simple string responses (JSON formatted)

### Absolute Imports
```python
# ✅ CORRECT
from kickai.features.player_registration.domain.tools.player_tools import get_status

# ❌ WRONG  
from .domain.tools.player_tools import get_status
```

## Key Files to Understand

### Core System (READ THESE FIRST)
- `kickai/agents/agentic_message_router.py` - **Central message routing (MODERNIZED)**
- `kickai/agents/crew_agents.py` - 5-agent system definition  
- `kickai/core/dependency_container.py` - DI and service initialization
- `kickai/core/command_registry.py` - Command discovery system
- `kickai/config/agents.yaml` - Agent configuration

### Feature Pattern (CRITICAL ARCHITECTURE)
Each feature in `kickai/features/` follows clean architecture:
```
feature_name/
├── application/commands/     # @command decorator, NO business logic
├── domain/
│   ├── tools/               # @tool decorator, independent functions
│   ├── services/            # Business logic (async for I/O)
│   └── entities/            # Domain models
└── infrastructure/          # Firebase repositories, external APIs
```
**Rule**: Commands delegate to agents, agents use tools, tools are independent

## AsyncIO Anti-Patterns (FORBIDDEN)

### ❌ **NEVER Create Sync Wrapper Methods**
```python
# ❌ FORBIDDEN - Sync wrapper with asyncio.run()
def approve_player_sync(self, player_id: str, team_id: str) -> str:
    """FORBIDDEN: Sync wrapper using asyncio.run()"""
    try:
        # This causes RuntimeError in event loops
        return asyncio.run(self.approve_player(player_id, team_id))
    except Exception as e:
        return f"Error: {e}"
        
# ✅ CORRECT - Use async method directly in tools
@tool("approve_player", result_as_answer=True)
async def approve_player(telegram_id: int, team_id: str, player_id: str) -> str:
    """Use async service methods directly"""
    player_service = container.get_service(PlayerService)
    result = await player_service.approve_player(player_id, team_id)
    return create_json_response("success", data=result)
```

### ❌ **NEVER Use asyncio.run() in Service Methods**
```python
# ❌ FORBIDDEN - asyncio.run() in service methods
def some_method_sync(self, ...):
    try:
        loop = asyncio.get_running_loop()
        # This pattern is forbidden and causes event loop conflicts
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.some_method(...))
            return future.result()
    except RuntimeError:
        # Even this fallback is problematic
        return asyncio.run(self.some_method(...))

# ✅ CORRECT - Pure async service methods only
async def some_method(self, ...):
    """Pure async method - no sync wrapper needed"""
    return await self.repository.do_something(...)
```

### ❌ **NEVER Call Sync Wrappers from Tools**
```python
# ❌ FORBIDDEN - Calling sync wrapper from async tool
@tool("add_player", result_as_answer=True)
async def add_player(...) -> str:
    # This would cause asyncio.run() conflicts
    result = player_service.approve_player_sync(player_id, team_id)
    return result

# ✅ CORRECT - Direct async service calls
@tool("add_player", result_as_answer=True)
async def add_player(...) -> str:
    result = await player_service.approve_player(player_id, team_id)
    return create_json_response("success", data=result)
```

### 🎯 **AsyncIO Best Practices Summary**
- **✅ DO**: Use native async tools with `@tool` decorator
- **✅ DO**: Call async service methods with `await`
- **✅ DO**: Use single async interface per service
- **❌ NEVER**: Create `*_sync()` wrapper methods
- **❌ NEVER**: Use `asyncio.run()` in service layers
- **❌ NEVER**: Use ThreadPoolExecutor for async workarounds
- **❌ NEVER**: Mix sync/async interfaces in same service

## Coding Standards (Code Review Best Practices)

### ✅ **Use Enums Instead of Magic Strings**
```python
# ✅ CORRECT - Use enums
from kickai.core.enums import ChatType, UserStatus
if chat_type.lower() != ChatType.LEADERSHIP.value:
    raise AuthorizationError("Leadership required")
player_data["status"] = UserStatus.PENDING.value

# ❌ WRONG - Magic strings
if chat_type.lower() != "leadership":
    raise AuthorizationError("Leadership required") 
player_data["status"] = "pending_activation"
```

### ✅ **Always Validate Service Availability**
```python
# ✅ CORRECT - Check service availability
container = get_container()
if not container:
    raise ServiceNotAvailableError("Container not available")
    
team_service = container.get_service(TeamService)
if not team_service:
    raise ServiceNotAvailableError("Team service not available")

# ❌ WRONG - Assume services exist
container = get_container()
team_service = container.get_service(TeamService)
# Will crash with AttributeError if None
```

### ✅ **Use Domain Services, Not Direct Database Access**
```python
# ✅ CORRECT - Use domain service layer
team_service = container.get_service(TeamService)
team = team_service.get_team_sync(team_id=team_id)
if not team:
    raise TeamNotFoundError(f"Team not found: {team_id}")
main_chat_id = team.main_chat_id

# ❌ WRONG - Direct database access from tools
database = container.get_database()
team_config = await database.get_document("kickai_teams", team_id)
main_chat_id = team_config.get("main_chat_id")
```

### ✅ **Throw Exceptions, Don't Return Error JSON**
```python
# ✅ CORRECT - Throw exceptions, let handler format response
if not team_config:
    raise TeamNotFoundError(f"Team not found: {team_id}")

# ❌ WRONG - Return JSON directly from validation
if not team_config:
    return create_json_response("error", message="Team not found")
```

### ✅ **Simple Exception Handling**
```python
# ✅ CORRECT - Single exception handler is sufficient
try:
    # Business logic here
    return create_json_response("success", data=result)
except Exception as e:
    logger.error(f"❌ Error in tool: {e}")
    return create_json_response("error", message=f"System Error: {str(e)}")

# ❌ WRONG - Verbose multiple exception handlers
except ImportError as e:
    # 10 lines of similar handling...
except ServiceNotAvailableError as e:
    # 10 more lines of similar handling...
except TeamNotFoundError as e:
    # 10 more lines of similar handling...
```

### ✅ **Import Organization**
```python
# ✅ CORRECT - All imports at module level
from loguru import logger
from kickai.core.enums import ChatType, UserStatus
from kickai.core.exceptions import TeamNotFoundError
from kickai.features.communication.domain.services.invite_link_service import InviteLinkService

# ❌ WRONG - Imports scattered throughout function
def some_function():
    # business logic...
    from kickai.features.communication.domain.services.invite_link_service import InviteLinkService
    # more business logic...

# ❌ WRONG - Unnecessary try/except for standard dependencies
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
```

### ✅ **Standard Dependencies (NO FALLBACKS)**
```python
# ✅ CORRECT - Direct import of standard project dependencies
from loguru import logger
from kickai.core.enums import ChatType, UserStatus
from kickai.utils.crewai_tool_decorator import tool

# ❌ WRONG - Try/except for dependencies that should always be available
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# ❌ WRONG - Conditional imports for core functionality
try:
    from kickai.utils.crewai_tool_decorator import tool
except ImportError:
    # This creates system inconsistency - just fail fast instead
    def tool(name):
        return lambda func: func
```

**RULE**: If a dependency is part of the project requirements, import it directly. **NO FALLBACKS** - let the system fail fast with clear error messages rather than masking issues.

**Rationale**: Fallback patterns hide system configuration issues and create inconsistent behavior. It's better to fail fast with a clear missing dependency error than to run with degraded functionality.

## Clean Async Architecture for CrewAI Tools (MANDATORY - 2025)

### ✅ **The ONLY Tool Pattern - Use This Everywhere**
```python
from loguru import logger
from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus
from kickai.utils.crewai_tool_decorator import tool
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
        # 1. Get services from container (NOT database directly)
        container = get_container()
        service = container.get_service(ServiceClass)
        if not service:
            raise ServiceNotAvailableError("Service not available")
        
        # 2. Use async service methods directly - NO sync wrappers
        result = await service.async_method(params)  # ✅ Direct await
        
        # 3. Always use ResponseStatus enum
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"❌ Error in tool_name: {e}")
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### ✅ **Service Layer Rules (CRITICAL)**
```python
class TeamService:
    """Services ONLY have async methods - NO sync wrappers."""
    
    def __init__(self, repository: TeamRepositoryInterface):
        self.repository = repository
    
    async def get_team(self, *, team_id: str) -> Optional[Team]:
        """Returns domain model, not raw database document."""
        team = await self.repository.get_team_by_id(team_id)
        # Business logic here if needed
        return team
    
    async def create_player(self, player: Player) -> Player:
        """Business logic in service, not in tool."""
        # Validation, business rules, etc.
        return await self.repository.create(player)
    
    # ❌ NEVER create sync wrappers like get_team_sync()
```

### ✅ **Clean Architecture Flow**
```
Tool (async) → Service (async) → Repository (async) → Database (async)
     ↓              ↓                ↓                    ↓
ResponseStatus  Domain Logic    Domain Models       Firestore
   Enum          & Rules        (Team, Player)       Client
```

### ❌ **FORBIDDEN Anti-Patterns (NEVER DO THESE)**
```python
# ❌ NEVER create sync wrappers in services
def get_team_sync(self, team_id: str):  # FORBIDDEN
    return asyncio.run(self.get_team(team_id))  # Causes event loop conflicts

# ❌ NEVER use ThreadPoolExecutor for async bridging
with concurrent.futures.ThreadPoolExecutor() as executor:  # FORBIDDEN
    future = executor.submit(asyncio.run, async_func)
    return future.result()

# ❌ NEVER bypass services in tools
@tool("bad_tool")
async def bad_tool(...):
    container = get_container()
    database = container.get_database()  # FORBIDDEN - tools shouldn't access DB
    await database.query_documents(...)  # Use services instead!

# ❌ NEVER use string status values
create_json_response("success", ...)  # Use ResponseStatus.SUCCESS
create_json_response("error", ...)    # Use ResponseStatus.ERROR
```

### ✅ **Repository Pattern**
```python
class FirebaseTeamRepository(TeamRepositoryInterface):
    """Repositories handle database operations and model conversion."""
    
    async def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """Get from Firestore, return domain model."""
        doc = await self.db.get_document("kickai_teams", team_id)
        if doc:
            return Team.from_dict(doc)  # Convert to domain model
        return None
    
    async def create(self, team: Team) -> Team:
        """Save domain model to Firestore."""
        await self.db.set_document(
            "kickai_teams",
            team.id,
            team.to_dict()  # Convert from domain model
        )
        return team
```

### ✅ **Domain Model Usage**
```python
# Tools work with domain models via services
team = await team_service.get_team(team_id=team_id)  # Returns Team model
if not team.main_chat_id:  # Access model properties
    raise TeamNotConfiguredError("Main chat not configured")

# Services handle business logic with models
player = Player(name=name, phone=phone, team_id=team_id)
saved_player = await player_service.create_player(player)
```

## Common Issues & Solutions

### CrewAI Async/Sync Issues (CRITICAL - December 2024 Update)
- **`RuntimeWarning: coroutine was never awaited`** → Tool is `async def` - must be `def` with bridge utility
- **`asyncio.run() cannot be called from a running event loop`** → Use `run_async_in_sync` utility from `kickai.utils.async_utils`
- **Tool not executing** → Ensure tool is sync function using the standard pattern
- **`'str' object has no attribute 'value'`** → Use proper enum value comparison (`ChatType.LEADERSHIP.value`)
- **Event loop conflicts** → All tools must be sync, use bridge utility for async operations

### CrewAI Tool Issues  
- **"Tool object is not callable"** → Tool is calling services/other tools
- **Tool not found** → Check registration in feature `__init__.py`
- **Import errors** → Use `PYTHONPATH=.` when running
- **Tools not executing** → Ensure tools are properly async and don't use `asyncio.run()`

### Development Issues  
- **Python version errors** → Must use Python 3.11+ with `venv311`
- **Process already running** → Use `./start_bot_safe.sh` or `./stop_bot.sh`
- **Environment not activated** → Run `source venv311/bin/activate`
- **Module not found errors** → Ensure `PYTHONPATH=.` is set
- **Firebase authentication** → Check credentials file path and permissions

### Router Issues (Post-Modernization)
- **Missing handler methods** → Functionality moved to `AgenticMessageRouter` methods
- **Import errors from handlers/** → Directory removed, update imports
- **Context builder issues** → Logic moved directly into router

### Firebase Issues
- **Authentication failed** → Check `FIREBASE_CREDENTIALS_FILE` path
- **Collection not found** → Ensure `kickai_` prefix on collection names
- **Async errors** → All Firebase operations must use async/await

### Type Consistency
- **telegram_id type errors** → Must be `int` throughout system (NOT string)
- **Message validation** → Use `TelegramMessage` type for consistency

## Testing Strategy

### Test Organization
- `tests/unit/` - Fast, isolated component tests
- `tests/integration/` - Service interaction tests
- `tests/e2e/` - Full workflow tests
- `tests/agents/` - Agent behavior tests
- `tests/mock_telegram/` - Interactive UI testing

### Running Tests
```bash
# Always use PYTHONPATH
PYTHONPATH=. python -m pytest tests/unit/ -v

# Feature-specific tests
PYTHONPATH=. python -m pytest tests/features/player_registration/ -v

# Mock Telegram UI
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
```

## CrewAI Tool Testing Best Practices

**Note**: CrewAI does not provide official testing recommendations for `@tool` decorated functions. These patterns are derived from KICKAI production experience and represent proven approaches for testing async CrewAI tools.

### ✅ **Pattern 1: Test Core Logic Directly**
```python
# Test the business logic without the @tool decorator
async def test_add_player_core_logic():
    """Test the underlying function logic directly."""
    from kickai.features.team_administration.domain.tools.player_management_tools import add_player
    
    # Mock dependencies
    with patch('kickai.core.dependency_container.get_container') as mock_container:
        mock_service = AsyncMock()
        mock_container.return_value.get_service.return_value = mock_service
        
        # Test the actual tool function
        result = await add_player(
            telegram_id=123456789,
            team_id="KTI", 
            username="test_user",
            chat_type="leadership",
            player_name="John Smith",
            phone_number="+447123456789"
        )
        
        # Verify service was called correctly
        mock_service.create_player.assert_called_once()
        
        # Verify JSON response format
        import json
        response_data = json.loads(result)
        assert response_data["status"] == "success"
```

### ✅ **Pattern 2: Mock Dependencies and Services**
```python
from unittest.mock import AsyncMock, patch
import pytest

async def test_tool_with_mocked_services():
    """Test tool with complete service mocking."""
    
    with patch('kickai.core.dependency_container.get_container') as mock_container:
        # Setup mock services
        mock_player_service = AsyncMock()
        mock_team_service = AsyncMock()
        
        mock_container.return_value.get_service.side_effect = lambda service_type: {
            'PlayerService': mock_player_service,
            'TeamService': mock_team_service
        }.get(service_type.__name__, AsyncMock())
        
        # Configure mock responses
        mock_player_service.create_player.return_value = "player_123"
        mock_team_service.get_team.return_value = {"id": "KTI", "name": "Test Team"}
        
        # Test the tool
        from kickai.features.team_administration.domain.tools.player_management_tools import add_player
        
        result = await add_player(
            telegram_id=123456789,
            team_id="KTI",
            username="test_user", 
            chat_type="leadership",
            player_name="John Smith",
            phone_number="+447123456789"
        )
        
        # Verify all service interactions
        mock_player_service.create_player.assert_called_once()
        assert "success" in result
```

### ✅ **Pattern 3: Integration Testing with Real Services**
```python
import os
import pytest

@pytest.mark.integration
async def test_tool_integration():
    """Integration test with real services and test database."""
    
    # Set test environment
    os.environ['KICKAI_INVITE_SECRET_KEY'] = 'test-integration-key'
    os.environ['FIREBASE_PROJECT_ID'] = 'test-project'
    
    # Use test team ID to avoid production data conflicts
    test_team_id = "TEST_INTEGRATION"
    
    from kickai.features.team_administration.domain.tools.player_management_tools import add_player
    
    result = await add_player(
        telegram_id=999999999,  # Test user ID
        team_id=test_team_id,
        username="integration_test",
        chat_type="leadership", 
        player_name="Integration Test Player",
        phone_number="+447999999999"
    )
    
    # Verify real database changes
    import json
    response_data = json.loads(result)
    assert response_data["status"] == "success"
    
    # Cleanup: Remove test data
    # Add cleanup logic here
```

### ✅ **Pattern 4: Test Tool Registration and Metadata**
```python
def test_tool_registration_and_async_validation():
    """Verify tool is properly registered and async."""
    from kickai.agents.tool_registry import initialize_tool_registry
    import asyncio
    
    # Initialize tool registry
    registry = initialize_tool_registry()
    
    # Verify tool is discovered and registered
    all_tools = registry.get_all_tools()
    assert "add_player" in all_tools, "Tool not found in registry"
    
    # Verify tool is async (MANDATORY in 2025 architecture)
    tool_func = all_tools["add_player"]
    if hasattr(tool_func, 'func'):
        actual_func = tool_func.func
    else:
        actual_func = tool_func
        
    assert asyncio.iscoroutinefunction(actual_func), "Tool must be async"
    
    # Verify tool metadata
    tool_metadata = registry.get_tool_metadata("add_player")
    assert tool_metadata is not None
    assert "player" in tool_metadata.description.lower()
```

### ✅ **Pattern 5: Comprehensive Error Handling Tests**
```python
async def test_tool_error_handling():
    """Test various error conditions and edge cases."""
    from kickai.features.team_administration.domain.tools.player_management_tools import add_player
    import json
    
    # Test missing required parameters
    result = await add_player(
        telegram_id=None,  # Invalid - should be int
        team_id="KTI",
        username="test",
        chat_type="leadership",
        player_name="John",
        phone_number="+447123456789"
    )
    response_data = json.loads(result)
    assert response_data["status"] == "error"
    assert "telegram_id" in response_data["message"].lower()
    
    # Test invalid phone format
    result = await add_player(
        telegram_id=123456789,
        team_id="KTI", 
        username="test",
        chat_type="leadership",
        player_name="John",
        phone_number="invalid-phone-format"
    )
    response_data = json.loads(result)
    assert response_data["status"] == "error"
    assert "phone" in response_data["message"].lower()
    
    # Test unauthorized chat type
    result = await add_player(
        telegram_id=123456789,
        team_id="KTI",
        username="test", 
        chat_type="main",  # Should require leadership
        player_name="John",
        phone_number="+447123456789"
    )
    response_data = json.loads(result)
    assert response_data["status"] == "error"
    assert "permission" in response_data["message"].lower() or "leadership" in response_data["message"].lower()
```

### ✅ **Pattern 6: Test JSON Response Format Consistency**
```python
async def test_tool_response_format():
    """Verify all tools return standardized JSON responses."""
    from kickai.features.team_administration.domain.tools.player_management_tools import add_player
    from kickai.utils.tool_helpers import create_json_response
    import json
    
    # Mock successful execution
    with patch('kickai.core.dependency_container.get_container'):
        result = await add_player(
            telegram_id=123456789,
            team_id="KTI",
            username="test",
            chat_type="leadership",
            player_name="John Smith", 
            phone_number="+447123456789"
        )
    
    # Verify JSON format
    response_data = json.loads(result)
    
    # Required fields for all tool responses
    assert "status" in response_data
    assert response_data["status"] in ["success", "error"]
    
    if response_data["status"] == "success":
        assert "data" in response_data
    else:
        assert "message" in response_data
    
    # Verify response is valid JSON
    assert isinstance(response_data, dict)
```

### ✅ **Pattern 7: Test Tool Performance and Timeouts**
```python
import time
import pytest

async def test_tool_performance():
    """Test tool execution time and timeout handling."""
    from kickai.features.team_administration.domain.tools.player_management_tools import add_player
    
    start_time = time.time()
    
    with patch('kickai.core.dependency_container.get_container'):
        result = await add_player(
            telegram_id=123456789,
            team_id="KTI",
            username="test",
            chat_type="leadership",
            player_name="Performance Test",
            phone_number="+447123456789"
        )
    
    execution_time = time.time() - start_time
    
    # Tool should execute within reasonable time (adjust threshold as needed)
    assert execution_time < 5.0, f"Tool took too long: {execution_time:.2f}s"
    
    # Verify result was returned
    assert result is not None
    assert len(result) > 0
```

### ✅ **Pattern 8: Test Agent Tool Integration**
```python
async def test_tool_with_crewai_agent():
    """Test tool integration within CrewAI agent context."""
    from kickai.agents.crew_agents import TeamManagementSystem
    from kickai.core.types import TelegramMessage
    from kickai.core.enums import ChatType
    
    # Initialize team management system
    system = TeamManagementSystem("TEST_TEAM")
    
    # Get the team administrator agent (has add_player tool)
    team_admin_agent = system.get_agent_by_role("TEAM_ADMINISTRATOR")
    
    # Verify agent has the tool
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in team_admin_agent.crew_agent.tools]
    assert "add_player" in tool_names, "Agent missing add_player tool"
    
    # Test message routing to agent (integration test)
    test_message = TelegramMessage(
        telegram_id=123456789,
        text="/addplayer John Smith +447123456789",
        chat_id="-1002002",  # Leadership chat
        chat_type=ChatType.LEADERSHIP,
        team_id="TEST_TEAM",
        username="test_admin"
    )
    
    # This would test full agent execution (may require more complex setup)
    # router = system.get_message_router()
    # response = await router.route_message(test_message)
    # assert "success" in response or "added" in response.lower()
```

### 🔧 **Testing Utilities and Helpers**

```python
# Create test helpers for common patterns
class ToolTestHelper:
    """Helper class for testing CrewAI tools."""
    
    @staticmethod
    def mock_container_with_services(**services):
        """Create mock container with specified services."""
        def container_side_effect():
            mock_container = AsyncMock()
            mock_container.get_service.side_effect = lambda service_type: services.get(service_type.__name__, AsyncMock())
            return mock_container
        return patch('kickai.core.dependency_container.get_container', side_effect=container_side_effect)
    
    @staticmethod
    def assert_valid_json_response(response: str, expected_status: str = None):
        """Assert response is valid JSON with proper format."""
        import json
        data = json.loads(response)
        assert "status" in data
        if expected_status:
            assert data["status"] == expected_status
        if data["status"] == "success":
            assert "data" in data
        elif data["status"] == "error":
            assert "message" in data
        return data
    
    @staticmethod
    def create_test_context(**kwargs):
        """Create standard test context for tools."""
        defaults = {
            "telegram_id": 123456789,
            "team_id": "TEST_TEAM", 
            "username": "test_user",
            "chat_type": "leadership"
        }
        defaults.update(kwargs)
        return defaults

# Usage example:
async def test_tool_with_helper():
    with ToolTestHelper.mock_container_with_services(PlayerService=AsyncMock()):
        context = ToolTestHelper.create_test_context()
        result = await add_player(**context, player_name="Test", phone_number="+447123456789")
        ToolTestHelper.assert_valid_json_response(result, "success")
```

### 📋 **Tool Testing Checklist**

When testing CrewAI tools, ensure you cover:

- ✅ **Async validation** - Verify tool is `async def` 
- ✅ **Parameter validation** - Test required/optional parameters
- ✅ **Error handling** - Test invalid inputs and edge cases
- ✅ **JSON response format** - Verify standardized responses
- ✅ **Service integration** - Test with mocked and real services
- ✅ **Permission validation** - Test chat_type and authorization
- ✅ **Performance** - Verify reasonable execution times
- ✅ **Tool registration** - Verify discovery by tool registry
- ✅ **Agent integration** - Test within CrewAI agent context
- ✅ **Database operations** - Test create/read/update operations
- ✅ **Cleanup** - Remove test data after integration tests

### 🚫 **Testing Anti-Patterns to Avoid**

- ❌ **Don't test the @tool decorator itself** - Test the function logic
- ❌ **Don't use sync test functions for async tools** - Use `async def test_...`
- ❌ **Don't test with production data** - Always use test environments
- ❌ **Don't assume tool registration** - Verify tools are discovered
- ❌ **Don't ignore error cases** - Test failure scenarios thoroughly
- ❌ **Don't test without mocking** - Mock external dependencies
- ❌ **Don't forget cleanup** - Remove test data to avoid conflicts

## Production Deployment

### Railway Deployment
```bash
make deploy-testing
make deploy-production
make health-check
```

### Performance Optimizations
- 55% reduction in agent complexity (11→5)
- Context bypass for common requests
- Optimized for `llama3.1:8b-instruct-q4_k_m` model
- Token-efficient prompt design

## Development Workflow

### Adding New Features
1. Create feature in `kickai/features/` following clean architecture
2. Add CrewAI tools with `@tool` decorator (independent functions)
3. Register commands with `@command` decorator  
4. Update agent tool assignments in `agents.yaml`
5. Add tests (unit, integration, E2E)

### Adding New Tools
1. Create independent tool function with `@tool` decorator
2. Export from feature's `__init__.py`
3. Add to agent configuration in `agents.yaml`
4. Ensure NO service/tool dependencies

### Modifying AgenticMessageRouter
1. **DO NOT** create new handler classes - extend router methods
2. **PRESERVE** resource management and error handling
3. **MAINTAIN** telegram_id as int consistency
4. **TEST** thoroughly - router is critical path

## Quick Validation Commands

### Pre-Development Checklist
```bash
# 1. Verify Python version (MANDATORY)
python3.11 check_python_version.py
source venv311/bin/activate && python --version  # Should show 3.11.x

# 2. Run quick system validation
PYTHONPATH=. python scripts/quick_validation.py

# 3. Test basic functionality
PYTHONPATH=. timeout 30s python run_bot_local.py
```

### System Health
```bash
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

# Router functionality
PYTHONPATH=. python -c "
from kickai.agents.agentic_message_router import AgenticMessageRouter
from kickai.core.types import TelegramMessage
from kickai.core.enums import ChatType
router = AgenticMessageRouter('KTI')
print('✅ Router initialized')
msg = TelegramMessage(telegram_id=123, text='test', chat_id='-100123', chat_type=ChatType.MAIN, team_id='KTI', username='test')
print('✅ Message creation works')
"
```

### Quick Debug
```bash
# Test with timeout
PYTHONPATH=. timeout 30s python run_bot_local.py


# Validation checks
PYTHONPATH=. python scripts/run_health_checks.py
```

## Mock Telegram Testing

### Interactive Testing UI
```bash
# Start Mock Telegram UI (recommended for testing)
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001
```

### Key Benefits
- **Liverpool FC themed interface** for professional testing
- **No real Telegram API calls** needed during development
- **Complete command testing** including slash commands and natural language
- **Real-time agent responses** and system monitoring

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

### System Modernization Benefits
- **-500+ lines** of duplicate code eliminated
- **Single source of truth** for message routing
- **Consistent type handling** (telegram_id as int)
- **Better error handling** with circuit breakers
- **Improved testability** with unified routing

## Async Migration Lessons (2025 Update)

### ✅ **Successfully Resolved Async Issues**

**Problem**: Recurring `asyncio.run() cannot be called from a running event loop` errors plaguing the system.

**Root Cause**: Anti-pattern of using `asyncio.run()` inside CrewAI tools, which conflicts with CrewAI's internal event loop.

**Solution**: Complete migration to CrewAI native async tool support.

### **Files Converted (17 asyncio.run instances eliminated)**
1. **player_management_tools.py** - Merged async helper functions, fixed enum comparisons
2. **team_member_tools.py** - Converted all registration tools to native async
3. **simplified_team_member_tools.py** - Removed complex async wrapping
4. **user_tools.py** - Direct async service calls
5. **match_tools.py** - All 6 match management tools converted
6. **communication_tools.py** - Removed ThreadPoolExecutor complexity
7. **availability_tools.py** - All 4 availability tools converted

### **Technical Implementation**
```python
# BEFORE (Anti-pattern causing errors)
@tool("add_player", result_as_answer=True)  
def add_player(...) -> str:
    return asyncio.run(_add_player_async(...))  # ❌ Event loop conflict

async def _add_player_async(...) -> str:
    # Separate async function
    result = await service.do_something()
    return result

# AFTER (Native async - no errors)
@tool("add_player", result_as_answer=True)
async def add_player(...) -> str:
    # Direct async tool - CrewAI handles execution
    result = await service.do_something()
    return result
```

### **Migration Benefits Achieved**
- ✅ **Zero event loop conflicts** - All asyncio.run() calls eliminated
- ✅ **Cleaner code architecture** - No async/sync bridging needed
- ✅ **Better performance** - Native async execution vs thread pool workarounds
- ✅ **Consistent patterns** - All tools follow same async approach
- ✅ **Future-proof** - Aligns with CrewAI 2025 best practices

### **Key Learnings for Future Development**
1. **Always use native async tools** - CrewAI supports this fully
2. **Never use asyncio.run() in tools** - Causes event loop conflicts
3. **Avoid ThreadPoolExecutor workarounds** - Unnecessary complexity
4. **Merge async helpers into main tools** - Simpler and more maintainable
5. **Test async conversion thoroughly** - Use validation scripts to verify

### **Quick Reference: Async Tool Development (2025)**
```bash
# ✅ CORRECT Pattern for new CrewAI tools:
@tool("tool_name", result_as_answer=True)
async def tool_name(telegram_id: int, team_id: str, ...) -> str:
    try:
        container = get_container()
        service = container.get_service(ServiceClass)
        result = await service.do_async_operation()
        return create_json_response("success", data=result)
    except Exception as e:
        logger.error(f"❌ Error in tool_name: {e}")
        return create_json_response("error", message=str(e))

# ❌ NEVER DO THIS (causes event loop conflicts):
@tool("tool_name")
def tool_name(...) -> str:
    return asyncio.run(async_function(...))
```

## Important Development Notes

### Before Making Changes
1. **Always read existing CLAUDE.md and Cursor rules** in `.cursor/rules/`
2. **Check recent changes** in project status files and documentation
3. **Run validation** with `PYTHONPATH=. python scripts/quick_validation.py`
4. **Use Mock Telegram UI** for testing instead of real bot

### When Adding Features
1. **Follow clean architecture** - see existing features as examples
2. **Tools must be independent** - no service calls in @tool functions
3. **Use absolute imports** - `from kickai.features...`
4. **Register in feature __init__.py** - export tools and commands
5. **Update agents.yaml** - assign tools to appropriate agents

### When Debugging
1. **Check agent logs** for CrewAI execution details
2. **Use validation scripts** in `scripts/` directory
3. **Test with Mock UI** before real Telegram testing
4. **Check dependency container** status with utility functions

