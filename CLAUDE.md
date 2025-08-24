# CLAUDE.md - KICKAI AI Football Team Management System

**Version:** 3.1 | **Python:** 3.11+ (MANDATORY) | **Architecture:** 6-Agent CrewAI Native Collaboration System with **Intelligent NLP Routing**

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
- **[Agentic Design](CLAUDEMD/agentic-design.md)** - 6-agent CrewAI native collaboration with NLP_PROCESSOR intelligent routing
- **[Development Patterns](CLAUDEMD/development-patterns.md)** - Tool patterns, service layers, coding standards, common issues

### Integration & Communication  
- **[Telegram Integration](CLAUDEMD/telegram-integration.md)** - Bot API, command processing, message routing, permissions
- **[Database](CLAUDEMD/database.md)** - Firebase patterns, migrations, repository design, data access rules

### Testing & Development
- **[Mock Testing](CLAUDEMD/mock-testing.md)** - Mock Telegram UI, test frameworks, user simulation, interactive testing
- **[SDLC](CLAUDEMD/sdlc.md)** - Testing strategy, CI/CD pipeline, deployment, health validation
- **[Environment Setup](CLAUDEMD/environment-setup.md)** - Configuration, dependencies, Python 3.11+ requirements

## ⚡ Critical Rules (Quick Reference)

### Clean Architecture Tool Pattern ✅ (Migration Complete)

**✅ Application Layer Tool (with @tool decorator):**
```python
# kickai/features/*/application/tools/*.py
@tool("tool_name", result_as_answer=True)
async def tool_name(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """Application layer CrewAI tool that delegates to domain layer."""
    return await tool_name_domain(telegram_id, team_id, username, chat_type)
```

**✅ Domain Layer Function (pure business logic):**
```python
# kickai/features/*/domain/tools/*.py
# REMOVED: @tool decorator - this is now a domain service function only
# Application layer provides the CrewAI tool interface
async def tool_name_domain(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """Pure domain business logic with no framework dependencies."""
    try:
        container = get_container()  # DI resolution in domain
        service = container.get_service(ServiceClass)
        result = await service.method_name(param=value)
        return create_json_response(ResponseStatus.SUCCESS, data=result)
    except Exception as e:
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### Clean Architecture Compliance ✅ (January 2025)
- **✅ 62 @tool decorators migrated** from domain to application layer
- **✅ Zero framework dependencies** in domain layer  
- **✅ Complete layer separation** achieved
- **Application Layer:** CrewAI tools with framework concerns
- **Domain Layer:** Pure business logic functions (no @tool decorators) 
- **Domain Layer:** Pure business logic, NO container dependencies, constructor injection only
- **Infrastructure Layer:** Database access, external services, Firebase repositories
- **Tool Location:** All tools in `application/tools/`, NOT `domain/tools/`

### Absolute Development Rules
- **Always:** `async def` for tools, `PYTHONPATH=.` when running, dependency injection patterns
- **Never:** `get_container()` in domain services, direct database access, legacy fields
- **Types:** `telegram_id` must be `int`, `team_id` is `str`

## 🏗️ Architecture Overview

### 6-Agent CrewAI Native Collaboration System
1. **MESSAGE_PROCESSOR** - Interface orchestrator and response coordinator
2. **NLP_PROCESSOR** - **PRIMARY ROUTING INTELLIGENCE** with advanced intent analysis
3. **PLAYER_COORDINATOR** - Player operations (`/update`, `/info`, `/myinfo`, `/status`)
4. **TEAM_ADMINISTRATOR** - Team management (`/addmember`, `/addplayer`)
5. **SQUAD_SELECTOR** - Match management, availability, squad selection
6. **HELP_ASSISTANT** - Help system (`/help`, command discovery)

### CrewAI Native Collaboration Flow
```
USER MESSAGE 
    ↓
📱 AgenticMessageRouter (Entry Point)
    ↓
🔄 CrewLifecycleManager 
    ↓
🎯 TeamManagementSystem.execute_task()
    ↓
🧠 INTELLIGENT ROUTING: _route_command_to_agent()
    ├── PRIMARY: NLP_PROCESSOR analyzes intent & recommends specialist
    │   ├── Uses: advanced_intent_recognition
    │   ├── Uses: analyze_update_context
    │   └── Uses: routing_recommendation_tool
    └── FALLBACK: Rule-based routing (only if NLP fails)
    ↓
👤 SELECTED SPECIALIST AGENT executes task
    ├── PLAYER_COORDINATOR (for /update, /info, /status)
    ├── TEAM_ADMINISTRATOR (for /addmember, /addplayer)  
    ├── SQUAD_SELECTOR (for /attendance, /availability)
    ├── HELP_ASSISTANT (for /help)
    └── MESSAGE_PROCESSOR (for /ping, /version, /list)
    ↓
📤 Response coordinated through MESSAGE_PROCESSOR
```

### Architecture Highlights
- **TRUE CREWAI COLLABORATION**: NLP_PROCESSOR provides intelligent routing analysis
- **SPECIALIST EXECUTION**: Right agent handles each request type
- **INTELLIGENT FALLBACK**: Rule-based routing when AI collaboration fails
- **UNIFIED INTERFACE**: MESSAGE_PROCESSOR orchestrates all responses

## 🔧 Common Issues & Quick Fixes

| Issue | Solution |
|-------|----------|
| Tool not executing | Export tool from feature's `__init__.py` |
| Import errors | Always use `PYTHONPATH=.` when running |
| Service not available | Check `ensure_container_initialized()` |
| Python version errors | Must use Python 3.11+ with `venv311` |

## 📍 Key File Locations

### Core System
- `kickai/agents/agentic_message_router.py` - Central router with CrewAI collaboration
- `kickai/agents/crew_agents.py` - 6-agent CrewAI native collaboration system  
- `kickai/config/agents.yaml` - Agent definitions with intelligent routing
- `kickai/core/dependency_container.py` - Service container and DI system

### Clean Architecture Structure
- `kickai/features/*/application/tools/` - Application layer tools (CrewAI @tool)
- `kickai/features/*/domain/services/` - Pure business logic services
- `kickai/features/*/domain/repositories/` - Repository interfaces
- `kickai/features/*/infrastructure/` - Database implementations, external services

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