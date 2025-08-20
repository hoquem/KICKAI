# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# KICKAI - AI Football Team Management System

**Version:** 3.1 | **Python:** 3.11+ (MANDATORY) | **Architecture:** 6-Agent CrewAI Native Collaboration System

## Essential Commands

```bash
# Development (Python 3.11+ Required)
make dev                           # Start development server  
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py  # Mock UI (localhost:8001)
./start_bot_safe.sh               # Safe startup (kills existing processes)

# Testing & Validation
make test                          # All tests (unit + integration + e2e)
make test-unit                     # Unit tests only
make lint                          # Code quality (ruff + mypy)
PYTHONPATH=. python scripts/run_health_checks.py  # System health validation

# Specific Testing
PYTHONPATH=. python -m pytest tests/unit/test_file.py::test_function -v -s
PYTHONPATH=. python -m pytest tests/integration/ -v --tb=short
PYTHONPATH=. python run_comprehensive_e2e_tests.py

# Emergency/Debug
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test-key python -c "..."  # System validation
```

## Architecture Overview

### 6-Agent CrewAI Native Collaboration System
**CrewAI native agent-to-agent collaboration with intelligent routing**

1. **MESSAGE_PROCESSOR** - Primary interface with intelligent coordination (`/ping`, `/version`, `/list`)
2. **HELP_ASSISTANT** - Specialized help system and user guidance (`/help`, command discovery)  
3. **PLAYER_COORDINATOR** - Player management and operations (`/info`, `/myinfo`, `/status`)
4. **TEAM_ADMINISTRATOR** - Team member management (`/addmember`, `/addplayer`)
5. **SQUAD_SELECTOR** - Match management, availability, and squad selection
6. **NLP_PROCESSOR** - Intelligent routing and context analysis agent

### CrewAI Native Collaboration Flow
```
User Input → MESSAGE_PROCESSOR → NLP_PROCESSOR Analysis → Specialist Agent → Coordinated Response
```

**Key:** CrewAI native agent-to-agent collaboration patterns with intelligent routing.

### Project Architecture (Clean Architecture)
```
kickai/
├── agents/                        # 6-agent CrewAI native collaboration system
├── features/<feature>/            # Domain-driven feature modules
│   ├── application/commands/      # @command decorators
│   ├── domain/tools/             # @tool decorators (async only)
│   ├── domain/services/          # Business logic (async)  
│   ├── domain/entities/          # Domain models
│   └── infrastructure/           # Repositories, external APIs
├── config/                       # agents.yaml, tasks.yaml, command_routing.yaml
├── core/                        # DI container, enums, types
└── database/                    # Firebase integration
```

## Critical Development Rules

### Tool Development Pattern (MANDATORY)
```python
from crewai.tools import tool
from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus  
from kickai.utils.tool_helpers import create_json_response

@tool("tool_name", result_as_answer=True)
async def tool_name(
    telegram_id: int,        # MUST be int, not string
    team_id: str, 
    username: str,
    chat_type: str,          # "main", "leadership", "private"
    # ... tool-specific parameters
) -> str:
    """Tool description with clear parameter expectations."""
    try:
        # 1. Get services from dependency container
        container = get_container()
        service = container.get_service(ServiceClass)
        
        # 2. Call service method with await
        result = await service.method_name(param=value)
        
        # 3. Return standardized JSON response
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"Error in tool_name: {e}")
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### Absolute Development Rules
- **Always:** Use `async def` for tools, `ResponseStatus` enum, `PYTHONPATH=.` when running
- **Always:** Use dependency injection via `get_container()` - no direct database access
- **Always:** Use absolute imports (`from kickai.core...`) - no relative imports  
- **Never:** Use `asyncio.run()` inside tools (causes event loop conflicts)
- **Never:** Use legacy `emergency_contact` field - use `emergency_contact_name` + `emergency_contact_phone`
- **Never:** Direct database access from tools - always use service layer
- **Types:** `telegram_id` must be `int` type, `team_id` is `str`

### Service Layer Pattern
```python
class ExampleService:
    def __init__(self, repository: RepositoryInterface):
        self.repository = repository
        
    async def get_item(self, *, item_id: str) -> Optional[DomainModel]:
        """Service methods are async and use keyword arguments."""
        return await self.repository.get_by_id(item_id)
```

## CrewAI Native Collaboration System

### Intelligent Agent Routing
All messages route to MESSAGE_PROCESSOR which collaborates with NLP_PROCESSOR for intelligent routing:

```yaml
# CrewAI Native Collaboration Configuration
collaboration_routing:
  primary_agent: "message_processor"  # All requests start here
  collaboration_pattern: "primary_with_nlp_routing"
  intelligent_routing: true  # Handled by agents, not configuration
```

**Key:** MESSAGE_PROCESSOR uses NLP_PROCESSOR for context-aware agent selection.

## System Integration Points

### Key Files & Their Purposes
- `kickai/agents/agentic_message_router.py` - **Central router** with CrewAI collaboration
- `kickai/agents/crew_agents.py` - 6-agent CrewAI native collaboration system
- `kickai/config/agents.yaml` - Agent definitions with intelligent routing capabilities
- `kickai/config/tasks.yaml` - CrewAI task templates for multi-agent coordination
- `kickai/config/command_routing.yaml` - Simplified collaboration configuration
- `kickai/core/dependency_container.py` - Service container and DI system

### Agent Tool Assignment
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

## Database & Critical Migrations

### Emergency Contact Field Migration (CRITICAL)
**Current Architecture:** Uses separate fields with NO fallback support
- ✅ `emergency_contact_name` (string)
- ✅ `emergency_contact_phone` (string)  
- ❌ `emergency_contact` (legacy - completely removed, no fallback)

**Migration:** `PYTHONPATH=. python scripts/migrate_emergency_contact_fields.py`

### Firebase Integration
- Collections prefixed with `kickai_` (e.g., `kickai_teams`, `kickai_players`)
- All database operations are async
- Use repository pattern - no direct Firestore access from tools/services

## Testing Strategy

### Test Types & Commands
```bash
# Unit Tests - Component isolation
PYTHONPATH=. python -m pytest tests/unit/ -v

# Integration Tests - Service interactions  
PYTHONPATH=. python -m pytest tests/integration/ -v

# E2E Tests - Complete user workflows
PYTHONPATH=. python run_comprehensive_e2e_tests.py

# Mock Telegram UI - Interactive testing
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001 (Liverpool FC themed)
```

### Test Pattern
```python
from unittest.mock import AsyncMock, patch

async def test_tool_with_mock():
    with patch('kickai.core.dependency_container.get_container') as mock_container:
        mock_service = AsyncMock()
        mock_container.return_value.get_service.return_value = mock_service
        
        result = await tool_name(123456789, "KTI", "testuser", "main")
        
        mock_service.method_name.assert_called_once()
        assert "success" in result
```

## Common Issues & Solutions

| Issue | Root Cause | Solution |
|-------|------------|----------|
| Tool not executing | Missing registration in feature `__init__.py` | Export tool from feature's `__init__.py` |
| Import errors | Missing PYTHONPATH | Always use `PYTHONPATH=.` when running |
| "User ID cannot be zero" | Mock service bot ID issue | Fixed in mock_telegram_service.py |
| Chat type conversion warnings | String vs enum mismatch | Fixed in bot_integration.py fallback class |
| Service not available | Container initialization | Check `ensure_container_initialized()` |
| Wrong agent routing | Command not in routing config | Add command to `command_routing.yaml` |
| Python version errors | Using Python < 3.11 | Must use Python 3.11+ with `venv311` |
| Emergency contact errors | Using legacy field | Use separate `name` + `phone` fields |

## System Health Validation

```bash
# Complete system health check
PYTHONPATH=. python scripts/run_health_checks.py

# Quick validation commands
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test-key python -c "
from kickai.core.dependency_container import ensure_container_initialized
from kickai.agents.tool_registry import initialize_tool_registry
ensure_container_initialized()
registry = initialize_tool_registry()
print(f'✅ {len(registry.get_all_tools())} tools registered')
"

# Agent system validation
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test-key python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('KTI') 
print(f'✅ {len(system.agents)} agents initialized')
"
```

## MCP Server Integration

```bash
# Documentation access (always up-to-date)
claude mcp add --transport http context7 https://mcp.context7.com/mcp

# UI testing and automation
claude mcp add puppeteer -s user -- npx -y @modelcontextprotocol/server-puppeteer
```

**Usage:** Add `use context7` to prompts needing current documentation (CrewAI, Firebase, Python libraries).

## Development Environment

### Required Setup
```bash
# 1. Python 3.11+ (MANDATORY)
python3.11 check_python_version.py
source venv311/bin/activate

# 2. Environment variables (.env file)
AI_PROVIDER=groq
KICKAI_INVITE_SECRET_KEY=test-invite-secret-key-for-testing-only  
FIREBASE_PROJECT_ID=<your_project>
FIREBASE_CREDENTIALS_FILE=credentials/<file>.json

# 3. Dependencies
pip install -r requirements.txt
pip install -r requirements-local.txt
```

### Architecture Modernization (2025)
- **CrewAI Native Collaboration:** Agent-to-agent collaboration using CrewAI best practices
- **Intelligent Routing:** NLP_PROCESSOR provides context-aware agent selection
- **Multi-Agent Patterns:** Sequential, parallel, and hierarchical collaboration workflows
- **Native Async:** All tools use `async def` with CrewAI native support
- **Clean Architecture:** Feature-first structure with domain-driven design
- **Type Safety:** Consistent `telegram_id` as `int` throughout system

This CLAUDE.md reflects the current production-ready state of KICKAI's 6-agent CrewAI native collaboration architecture with intelligent routing and multi-agent coordination patterns.