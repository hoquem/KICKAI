# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**KICKAI v3.1** | **Python 3.11+** | **5-Agent CrewAI System** | **Native Hierarchical Process**

## 🚀 Essential Commands

```bash
# Core Development  
export PYTHONPATH=. && export KICKAI_INVITE_SECRET_KEY=test-key  # Always required
make dev                           # Development server (persistent crews)
make test                         # All tests (unit + integration + e2e)  
make lint                         # Code quality (ruff + mypy + type check)
make health-check                  # System health validation

# Testing & Debugging
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py  # Mock UI (localhost:8001)
PYTHONPATH=. python scripts/run_health_checks.py            # System health validation
PYTHONPATH=. python -m pytest tests/unit/features/[feature]/test_[component].py::test_[function] -v -s

# Performance Testing (NEW - Persistent Crews)
PYTHONPATH=. python -m pytest tests/performance/test_persistent_crews.py -v  # Performance tests
PYTHONPATH=. python -c "from kickai.core.team_system_manager import get_global_metrics; import asyncio; print(asyncio.run(get_global_metrics()))"  # Global metrics

# Single Test Examples
PYTHONPATH=. python -m pytest tests/integration/features/team_administration/ -v
PYTHONPATH=. python -m pytest tests/e2e/features/test_cross_feature_flows.py -k "player_registration" -v

# Database Operations
make bootstrap-testing             # Bootstrap testing environment
make cleanup-testing               # Clean testing database
```

## 🏗️ Architecture Quick Reference

**5-Agent CrewAI System (Persistent Crews with Memory):**
1. **MESSAGE_PROCESSOR** - Communication and system operations specialist
2. **HELP_ASSISTANT** - Help system and guidance specialist (5+ tools)
3. **PLAYER_COORDINATOR** - Player management specialist (11+ tools) - **PLAYER context**
4. **TEAM_ADMINISTRATOR** - Team administration specialist (16+ tools) - **MEMBER context**  
5. **SQUAD_SELECTOR** - Match operations specialist (14+ tools)

**🔥 NEW: Persistent Crew Architecture (2025)**
- **One Crew Per Team**: Each team gets a long-lived, persistent crew instance
- **Memory Enabled**: Conversation context preserved across all team interactions
- **Verbose Logging**: Detailed execution visibility for debugging and monitoring
- **Performance**: ~70% faster execution (eliminates crew creation overhead)
- **Async Execution**: All tasks use `kickoff_async()` for concurrency

**Context-Aware Routing:** Chat type determines user treatment and tool selection
- **Main Chat** → Users are PLAYERS → `player_coordinator` + player tools  
- **Leadership Chat** → Users are MEMBERS → `team_administrator` + member tools
- **Private Chat** → Users are PLAYERS → `player_coordinator` + player tools

**Coordination:** Hierarchical process with `manager_llm` for intelligent context-aware routing

**Clean Architecture Structure:**
```
kickai/features/[feature]/
├── application/tools/    # @tool decorators (CrewAI interface)
├── domain/
│   ├── services/        # Pure business logic  
│   ├── entities/        # Business objects
│   └── repositories/    # Interfaces only
└── infrastructure/      # Firebase implementations
```

**Key Feature Areas:**
- `attendance_management/` - Match attendance tracking
- `communication/` - Team communication tools  
- `match_management/` - Match operations
- `player_registration/` - Player onboarding & management
- `squad_selection/` - Squad selection logic
- `system_infrastructure/` - System health & monitoring
- `team_administration/` - Team member management
- `shared/` - Shared utilities and tools

## 📖 Extended Documentation

**Load selectively for token efficiency:**
- **[Agents](CLAUDEMD/agentic-design.md)** (280w) - 5-agent collaboration, routing
- **[Patterns](CLAUDEMD/development-patterns.md)** (320w) - Tools, services, standards
- **[Telegram](CLAUDEMD/telegram-integration.md)** (180w) - Bot API, commands
- **[Database](CLAUDEMD/database.md)** (240w) - Firebase, migrations
- **[Testing](CLAUDEMD/mock-testing.md)** (200w) - Mock UI, frameworks
- **[Deploy](CLAUDEMD/sdlc.md)** (260w) - CI/CD, health checks

## ⚡ Development Rules

**Clean Architecture (Complete Migration ✅):**
- Application: `@tool` decorators only
- Domain: Pure business logic, no framework deps  
- Infrastructure: Firebase, external services

**Direct Parameter Tool Pattern (CrewAI Standard):**
```python
# Application: kickai/features/*/application/tools/
@tool("name")
async def name(
    telegram_id: str,   # Only if tool needs user identity
    team_id: str,      # Only if tool needs team context  
    specific_param: str # Tool-specific parameters as needed
) -> str:
    """Tool description with clear parameter requirements."""
    # Validate only parameters this tool actually uses
    if not telegram_id:
        return "❌ User identification required"
    
    # Convert types internally when needed
    telegram_id_int = int(telegram_id)
    
    return await name_domain(telegram_id_int, team_id, specific_param)

# Domain: kickai/features/*/domain/tools/  
async def name_domain(telegram_id_int: int, team_id: str, specific_param: str) -> str:
    service = get_container().get_service(ServiceClass)
    result = await service.method(telegram_id_int, team_id, specific_param)
    return f"✅ Operation completed: {result}"
```

**Essential Rules:**
- Always: `async def`, `PYTHONPATH=.`, dependency injection
- Types: `telegram_id` = str (convert to int internally), `team_id` = str
- Never: Framework deps in domain, direct DB access
- CrewAI: Hierarchical process with manager_llm coordination
- Python: Requires 3.11+ with venv311 virtual environment

**Context-Aware Tool Pattern (NEW):**
```python
# Context-aware naming distinguishes player vs member operations
@tool("get_player_status_current")    # For main/private chat (PLAYER context)
def get_player_status_current(telegram_id: str, team_id: str) -> str:
    """Get current user's player status - for game participants."""
    pass

@tool("get_member_status_current")    # For leadership chat (MEMBER context) 
def get_member_status_current(telegram_id: str, team_id: str) -> str:
    """Get current user's member status - for admins/leadership."""
    pass
```

**Current Architecture State (2025-09-03) - PRODUCTION READY:**
- **✅ API Authentication**: Gemini API authentication issues RESOLVED
- **✅ Embedding Integration**: Fixed LiteLLM model format (`gemini/text-embedding-004`)
- **Context-Aware Routing**: Chat type determines user treatment and agent selection
- **Process**: Hierarchical with native CrewAI routing and separate manager_llm coordination
- **Agents**: All 5 agents are worker agents with tools (no dedicated manager agent)
- **Tool Naming**: Context-aware tool names distinguish player vs member operations
- **Tool Validation**: Comprehensive tool validation implemented
- **Response Formatting**: Consistent response formatting across all tools
- **Mixed Async/Sync**: Supported natively by CrewAI framework
- **Testing**: Interactive Mock UI available for development
- **Memory System**: Temporarily disabled (can be re-enabled with valid API permissions)

## 🚀 Using Persistent Crew System (NEW)

```python
# Get team's persistent crew system (creates if doesn't exist)
from kickai.core.team_system_manager import get_team_system

team_system = await get_team_system("KICKAI_MAIN")

# All tasks reuse the same crew with memory continuity
result1 = await team_system.execute_task("help me with player registration", context)
result2 = await team_system.execute_task("list all active players", context)  
result3 = await team_system.execute_task("what did I ask about earlier?", context)  # Uses memory!

# Get performance metrics
metrics = team_system.get_execution_metrics()
print(f"Executed {metrics['total_tasks']} tasks, avg time: {metrics['average_execution_time']:.2f}s")

# Get global system metrics
from kickai.core.team_system_manager import get_global_metrics
global_metrics = await get_global_metrics()
print(f"Total teams: {global_metrics['total_teams']}, Total tasks: {global_metrics['total_tasks_executed']}")
```

## 🔧 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool not found | Export from feature `__init__.py` |
| Import errors | Use `PYTHONPATH=.` |
| Service unavailable | Run `ensure_container_initialized()` |
| Python version | Must use 3.11+ with `venv311` |
| Tests fail | Check Firebase test data, verify mocks |
| Agent delegation fails | Check hierarchical process configuration |
| Mock UI not starting | Ensure port 8001 is available |
| Wrong agent routing | Check chat_type context and agent backstories |
| Tool not context-aware | Use `get_player_*` vs `get_member_*` naming |
| **Crew creation slow** | **First execution per team includes initialization (~30s), subsequent tasks much faster** |
| **Memory not working** | **Verify `memory=True` in crew creation and check health check `memory_status`** |
| **Performance issues** | **Check persistent crew metrics: `team_system.get_execution_metrics()`** |
| **✅ API Authentication Fixed** | **Gemini embedding format: `gemini/text-embedding-004` (not `models/`)** |
| **Memory API errors** | **Re-enable memory by changing `if False:` to `if embedder_config:` in crew_agents.py:269** |

**System Health Check:**
```bash
# Run frequently for validation
PYTHONPATH=. python scripts/run_health_checks.py
make health-check
```

**Emergency Debug:**
```bash
# Quick system validation
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized(); print('✅ System OK')
"

# Tool registry check  
PYTHONPATH=. python -c "
from kickai.agents.tool_registry import initialize_tool_registry
print(f'✅ Tools: {len(initialize_tool_registry().get_all_tools())}')
"

# Context-aware routing check
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
team_system = TeamManagementSystem('TEST')
health = team_system.health_check()
print(f'✅ Context-Aware Routing: {health[\"system\"]}')
for agent, data in health['agents'].items():
    print(f'   {agent}: {data[\"tools_count\"]} tools')
"
```

## 📍 Key Files

**Core System:**
- `kickai/agents/crew_agents.py` - 5-agent CrewAI system (TeamManagementSystem)
- `kickai/core/dependency_container.py` - DI container
- `kickai/config/agents.yaml` - Agent configurations (5 agents)
- `kickai/features/registry.py` - Tool registry and feature exports
- `run_bot_local.py` - Local development server entry point

**Configuration:**
- `pyproject.toml` - Python dependencies, CrewAI==0.150.0
- `requirements.txt` - Runtime dependencies
- `requirements-local.txt` - Development dependencies  
- `.env` - Environment variables (development)
- `Makefile` - Development commands and workflows

**Testing & Development:**
- `tests/mock_telegram/start_mock_tester.py` - Interactive testing UI
- `scripts/run_health_checks.py` - System validation
- `tests/unit/`, `tests/integration/`, `tests/e2e/` - Test suites
- `conftest.py` - Pytest configuration and fixtures

## 💡 Token Optimization Guide

**Base context (450 words):** This file contains essential commands and architecture
**Extended docs:** Load only when needed:
- Agents (280w) | Patterns (320w) | Telegram (180w) | Database (240w) | Testing (200w) | Deploy (260w) | **[CrewAI Tools](CLAUDEMD/crewai-tool-guidelines.md)** (2500w) - CRITICAL tool development guidelines

**Usage strategy:** Base + 1-2 relevant files = 60-80% token reduction vs full docs

## 🔧 Recent Changes & Migration Notes

**September 2025 - Context-Aware Production System:**
- **✅ API Authentication Resolution**: Fixed Gemini embedding authentication issues 
- **✅ LiteLLM Integration**: Corrected model format for CrewAI memory system
- **Context-Aware Routing**: Chat type determines user treatment (Player vs Member)
- **Tool Naming Revolution**: Context-specific tools (`get_player_*` vs `get_member_*`)
- **Intent-Based Agent Selection**: Agents specialized by context and user type
- **Native CrewAI Routing**: Complete migration to hierarchical process with manager_llm
- **Tool Validation**: Comprehensive tool validation across all 52+ tools  
- **Response Formatting**: Consistent JSON response formatting
- **Player Status Normalization**: Advanced player management system
- **Mock Testing UI**: Interactive web-based testing at localhost:8001
- **Health Monitoring**: Comprehensive system health checks

**September 3, 2025 - API Authentication & Embedding Fixes:**
- **Root Cause**: CrewAI memory system using wrong model format for LiteLLM
- **Issue**: `models/text-embedding-004` → `litellm.AuthenticationError`
- **Solution**: Auto-format as `gemini/text-embedding-004` for LiteLLM compatibility
- **Environment**: Added `AI_MODEL_EMBEDDER=text-embedding-004` to `.env`
- **Code Fix**: Updated `crew_agents.py:158-161` with proper model formatting
- **Fallback**: Memory system gracefully disabled if embedding fails
- **Status**: ✅ System fully operational without API authentication errors

**Key Technologies:**
- **Python 3.11+** (strict requirement)
- **CrewAI 0.150.0** (hierarchical process)
- **Firebase Firestore** (database)
- **Telethon** (Telegram Bot API)
- **Pydantic** (data validation)
- **pytest** (testing framework)
- **ruff + mypy** (code quality)

**Critical Process Notes:**
- **Context-Aware Routing**: Main chat = PLAYER context, Leadership chat = MEMBER context  
- **CrewAI Process**: Hierarchical with native routing and separate manager_llm coordination
- **Agent Architecture**: All 5 agents are worker agents with tools (no dedicated manager agent)
- **Tool Naming**: Context-specific naming prevents routing confusion (`_player_` vs `_member_`)
- **Tool Execution**: Mixed async/sync supported by CrewAI framework
- **Error Handling**: Comprehensive validation with graceful degradation
- **Mock Testing**: Interactive UI available at localhost:8001
- **Development**: Always use `PYTHONPATH=.` for proper imports
- **Environment**: Requires `KICKAI_INVITE_SECRET_KEY=test-key` for testing

## 📝 Docstring Standards

**Maintainable Tool Documentation**

All CrewAI tools must follow semantic, business-focused docstring patterns that remain stable as UI and commands evolve.

### Core Pattern
```python
@tool("tool_name")
async def tool_name(...) -> str:
    """
    [SEMANTIC ACTION] - What business action does this perform?
    
    [BUSINESS CONTEXT] - Why and impact explanation
    
    Use when: [BUSINESS INTENT TRIGGER]
    Required: [BUSINESS PERMISSIONS/CONDITIONS]
    
    Returns: [SEMANTIC BUSINESS OUTCOME]
    """
```

### Key Principles
- **Focus on WHAT (semantics)** not HOW (implementation)
- **Business intent** over UI commands (/status vs "when status verification needed")
- **Timeless descriptions** that survive interface changes
- **Agent-friendly** for intelligent routing decisions

### Anti-Patterns to Avoid
❌ Implementation details ("serves as application boundary")
❌ Command examples ("USE THIS FOR: /info [player]") 
❌ UI coupling ("JSON formatted response")
❌ Technical parameters ("telegram_id: User's Telegram ID")

**Full standards**: See `docs/DOCSTRING_STANDARDS.md`

## 🚀 Getting Started for New Contributors

**Quick Setup:**
```bash
# Clone and setup
git clone [repository-url]
cd KICKAI

# Setup development environment  
make setup-dev
source venv311/bin/activate

# Verify installation
export PYTHONPATH=. && export KICKAI_INVITE_SECRET_KEY=test-key
make health-check

# Start development
make dev  # or python run_bot_local.py
```

**Development Workflow:**
1. `make test` - Run all tests before changes
2. `make lint` - Check code quality
3. Use Mock UI at `localhost:8001` for interactive testing
4. `make health-check` - Validate system before commits

---

**KICKAI v3.1** - 5-Agent CrewAI System with Hierarchical Process and Complete Clean Architecture