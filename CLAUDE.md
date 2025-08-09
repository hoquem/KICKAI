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

### ⚠️ Python 3.11+ MANDATORY
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
FIREBASE_PROJECT_ID=kickai-954c2
FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials_testing.json

# Groq rate limiting (CRITICAL for local development)
AI_RATE_LIMIT_TPM=6000                    # Tokens per minute limit
AI_RATE_LIMIT_RETRY_DELAY=5.0            # Initial retry delay in seconds
AI_RATE_LIMIT_MAX_RETRIES=3              # Maximum retry attempts
AI_RATE_LIMIT_BACKOFF_MULTIPLIER=2.0     # Exponential backoff multiplier
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

# Run with coverage
PYTHONPATH=. python -m pytest tests/ --cov=kickai --cov-report=html
```

### Code Quality
```bash
make lint  # Run all linting and formatting

# Individual tools
ruff check kickai/
ruff format kickai/
mypy kickai/
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
- **Resource Management**: Built-in rate limiting, circuit breaker patterns
- **Type Safety**: Consistent `telegram_id` handling as `int` throughout
- **Memory Management**: Proper cleanup and garbage collection

## Critical CrewAI Rules (MANDATORY) - UPDATED 2025

### 🚨 ALWAYS USE CREWAI NATIVE METHODS!!! 

**MEMORY: CrewAI tools receive parameters directly via function signatures.**

### Tool Parameter Passing - NEW NATIVE APPROACH
```python
# ✅ CORRECT - Native CrewAI parameter passing
@tool("FINAL_HELP_RESPONSE")
def final_help_response(
    chat_type: str,
    telegram_id: str, 
    team_id: str,
    username: str
) -> str:
    """Tool receives parameters directly from agent."""
    return f"Help for {username} in {chat_type}"
```

### Task Creation - Native Structured Description
```python
# ✅ CORRECT - Structured task description
structured_description = f"""
User Request: {task_description}

Context Information:
- Team ID: {team_id}
- User Telegram ID: {telegram_id} 
- Username: {username}
- Chat Type: {chat_type}

Instructions: Use the provided context information to call tools 
with the appropriate parameters.
"""

task = Task(
    description=structured_description,
    agent=agent.crew_agent,
    expected_output="A clear and helpful response to the user's request",
)
```

### Tool Independence (CRITICAL)
- **❌ NEVER**: Tools calling other tools or services
- **✅ ALWAYS**: Tools are simple, independent functions
- **✅ ALWAYS**: Parameters passed directly via Task descriptions
- **✅ ALWAYS**: Tools return simple string responses

### Absolute Imports
```python
# ✅ CORRECT
from kickai.features.player_registration.domain.tools.player_tools import get_status

# ❌ WRONG  
from .domain.tools.player_tools import get_status
```

## Key Files to Understand

### Core System
- `kickai/agents/agentic_message_router.py` - **Central message routing (MODERNIZED)**
- `kickai/agents/crew_agents.py` - 5-agent system definition  
- `kickai/core/dependency_container.py` - DI and service initialization
- `kickai/core/command_registry.py` - Command discovery system
- `kickai/config/agents.yaml` - Agent configuration

### Feature Pattern
Each feature follows:
- `application/commands/` - Command definitions (`@command` decorator)
- `domain/tools/` - CrewAI tools (`@tool` decorator)
- `domain/services/` - Business logic (async for I/O)
- `infrastructure/` - Firebase repositories

## Common Issues & Solutions

### CrewAI Tool Issues
- **"Tool object is not callable"** → Tool is calling services/other tools
- **Tool not found** → Check registration in feature `__init__.py`
- **Import errors** → Use `PYTHONPATH=.` when running

### Development Issues  
- **Python version errors** → Must use Python 3.11+ with `venv311`
- **Process already running** → Use `./start_bot_safe.sh`
- **Environment not activated** → Run `source venv311/bin/activate`

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
2. **PRESERVE** resource management and rate limiting
3. **MAINTAIN** telegram_id as int consistency
4. **TEST** thoroughly - router is critical path

## Quick Validation Commands

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