# CLAUDE.md - KICKAI AI Football Team Management System

**Version:** 3.1 | **Python:** 3.11+ (MANDATORY) | **Architecture:** 6-Agent CrewAI Native Collaboration System

This file provides guidance to Claude Code (claude.ai/code) when working with the KICKAI codebase. For detailed documentation, refer to the domain-specific files in the `CLAUDEMD/` directory.

## 🚀 Quick Start

```bash
# Essential Commands
make dev                           # Start development server  
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py  # Mock UI (localhost:8001)
make test                          # All tests (unit + integration + e2e)
make lint                          # Code quality (ruff + mypy)
PYTHONPATH=. python scripts/run_health_checks.py  # System health validation
```

## 📚 Documentation Structure

### Core Architecture & Design
- **[Agentic Design](CLAUDEMD/agentic-design.md)** - 6-agent CrewAI collaboration system, intelligent routing, agent tool assignments
- **[Development Patterns](CLAUDEMD/development-patterns.md)** - Tool patterns, service layers, coding standards, common issues

### Integration & Communication  
- **[Telegram Integration](CLAUDEMD/telegram-integration.md)** - Bot API, command processing, message routing, permissions
- **[Database](CLAUDEMD/database.md)** - Firebase patterns, migrations, repository design, data access rules

### Testing & Development
- **[Mock Testing](CLAUDEMD/mock-testing.md)** - Mock Telegram UI, test frameworks, user simulation, interactive testing
- **[SDLC](CLAUDEMD/sdlc.md)** - Testing strategy, CI/CD pipeline, deployment, health validation
- **[Environment Setup](CLAUDEMD/environment-setup.md)** - Configuration, dependencies, Python 3.11+ requirements

## ⚡ Critical Rules (Quick Reference)

### Tool Development Pattern
```python
@tool("tool_name", result_as_answer=True)
async def tool_name(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    try:
        container = get_container()
        service = container.get_service(ServiceClass)
        result = await service.method_name(param=value)
        return create_json_response(ResponseStatus.SUCCESS, data=result)
    except Exception as e:
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### Absolute Development Rules
- **Always:** `async def` for tools, `PYTHONPATH=.` when running, dependency injection via `get_container()`
- **Never:** `asyncio.run()` inside tools, direct database access, legacy `emergency_contact` field
- **Types:** `telegram_id` must be `int`, `team_id` is `str`

## 🏗️ Architecture Overview

### 6-Agent CrewAI System
1. **MESSAGE_PROCESSOR** - Primary interface (`/ping`, `/version`, `/list`)
2. **HELP_ASSISTANT** - Help system (`/help`, command discovery)  
3. **PLAYER_COORDINATOR** - Player operations (`/info`, `/myinfo`, `/status`)
4. **TEAM_ADMINISTRATOR** - Team management (`/addmember`, `/addplayer`)
5. **SQUAD_SELECTOR** - Match management, availability, squad selection
6. **NLP_PROCESSOR** - Intelligent routing and context analysis

### Collaboration Flow
```
User Input → MESSAGE_PROCESSOR → NLP_PROCESSOR Analysis → Specialist Agent → Coordinated Response
```

## 🔧 Common Issues & Quick Fixes

| Issue | Solution |
|-------|----------|
| Tool not executing | Export tool from feature's `__init__.py` |
| Import errors | Always use `PYTHONPATH=.` when running |
| Service not available | Check `ensure_container_initialized()` |
| Python version errors | Must use Python 3.11+ with `venv311` |

## 📍 Key File Locations
- `kickai/agents/agentic_message_router.py` - Central router with CrewAI collaboration
- `kickai/agents/crew_agents.py` - 6-agent CrewAI native collaboration system  
- `kickai/config/agents.yaml` - Agent definitions with intelligent routing
- `kickai/core/dependency_container.py` - Service container and DI system

## 🔥 Claude Code Token Optimization

**IMPORTANT FOR CLAUDE CODE MODELS**: Use selective documentation loading to minimize token consumption:

### Token-Efficient Usage Patterns
```bash
# Base context (always include)
CLAUDE.md (475 words) - Essential commands, rules, architecture overview

# Domain-specific additions (load only when needed)
+ agentic-design.md (340 words)     # Agent system, routing, collaboration
+ development-patterns.md (440 words) # Tools, services, coding standards  
+ telegram-integration.md (219 words) # Bot API, commands, messaging
+ database.md (314 words)           # Firebase, migrations, data access
+ mock-testing.md (276 words)       # Mock UI, testing frameworks
+ sdlc.md (367 words)              # Testing strategy, CI/CD, deployment
+ environment-setup.md (342 words)  # Configuration, dependencies, setup
```

### Optimization Strategy
- **60-80% token reduction** vs. loading full documentation
- **Load base + domain-specific only**: Agent work → +agentic-design.md | Testing → +mock-testing.md+sdlc.md | Database → +database.md+development-patterns.md
- **Dynamic loading**: Analyze task requirements to determine minimal needed documentation

---

**Note:** This is the optimized index file. For comprehensive documentation on specific domains, refer to the dedicated files in the `CLAUDEMD/` directory. Each file is designed for Claude Code token efficiency while maintaining complete technical accuracy.