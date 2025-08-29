# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**KICKAI v3.1** | **Python 3.11+** | **5-Agent CrewAI System** | **Native CrewAI Routing**

## 🚀 Essential Commands

```bash
# Core Development
export PYTHONPATH=. && export KICKAI_INVITE_SECRET_KEY=test-key  # Always required
make dev                           # Development server
make test                         # All tests (unit + integration + e2e)  
make lint                         # Code quality (ruff + mypy + type check)

# Testing & Debugging
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py  # Mock UI (localhost:8001)
PYTHONPATH=. python scripts/run_health_checks.py            # System health validation
PYTHONPATH=. python -m pytest tests/unit/features/[feature]/test_[component].py::test_[function] -v -s

# Single Test Examples
PYTHONPATH=. python -m pytest tests/integration/features/team_administration/ -v
PYTHONPATH=. python -m pytest tests/e2e/features/test_cross_feature_flows.py -k "player_registration" -v
```

## 🏗️ Architecture Quick Reference

**5-Agent CrewAI System:**
1. **MESSAGE_PROCESSOR** - Primary interface with **native LLM routing**
2. **HELP_ASSISTANT** - `/help`, command guidance
3. **PLAYER_COORDINATOR** - `/update`, `/info`, `/myinfo`, `/status`
4. **TEAM_ADMINISTRATOR** - `/addplayer`, `/addmember` (leadership only)
5. **SQUAD_SELECTOR** - `/availability`, match management

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

## 📖 Extended Documentation

**Load selectively for token efficiency:**
- **[Agents](CLAUDEMD/agentic-design.md)** (280w) - 6-agent collaboration, routing
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

**Tool Pattern:**
```python
# Application: kickai/features/*/application/tools/
@tool("name", result_as_answer=True)
async def name(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    return await name_domain(telegram_id, team_id, username, chat_type)

# Domain: kickai/features/*/domain/tools/  
async def name_domain(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    service = get_container().get_service(ServiceClass)
    return create_json_response(ResponseStatus.SUCCESS, data=await service.method())
```

**Essential Rules:**
- Always: `async def`, `PYTHONPATH=.`, dependency injection
- Types: `telegram_id` = int, `team_id` = str
- Never: Framework deps in domain, direct DB access

## 🔧 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool not found | Export from feature `__init__.py` |
| Import errors | Use `PYTHONPATH=.` |
| Service unavailable | Run `ensure_container_initialized()` |
| Python version | Must use 3.11+ with `venv311` |
| Tests fail | Check Firebase test data, verify mocks |

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
```

## 📍 Key Files

**Core System:**
- `kickai/agents/agentic_message_router.py` - Entry point router
- `kickai/agents/crew_agents.py` - 6-agent system
- `kickai/core/dependency_container.py` - DI container
- `kickai/config/agents.yaml` - Agent configurations

**Testing & Development:**
- `tests/mock_telegram/start_mock_tester.py` - Interactive testing UI
- `scripts/run_health_checks.py` - System validation
- `Makefile` - Development commands

## 💡 Token Optimization Guide

**Base context (380 words):** This file contains essential commands and architecture
**Extended docs:** Load only when needed:
- Agents (280w) | Patterns (320w) | Telegram (180w) | Database (240w) | Testing (200w) | Deploy (260w)

**Usage strategy:** Base + 1-2 relevant files = 60-80% token reduction vs full docs

---

**KICKAI v3.1** - 5-Agent CrewAI System with Native Routing and Complete Clean Architecture