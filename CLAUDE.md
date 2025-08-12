# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KICKAI is an AI-powered football team management system built with **5-agent CrewAI architecture** and clean architecture principles. The system processes ALL user interactions through specialized AI agents, ensuring intelligent, context-aware responses.

**Version:** 5.0  
**Status:** Production Ready with JSON Tool Migration in Progress  
**Python Version:** 3.11+ (MANDATORY - Will NOT work with Python 3.9)  
**Deployment:** Railway (Production), Local Development with Groq  
**Test UI:** Mock Telegram at http://localhost:8001

# ⚠️ MANDATORY CREWAI NATIVE RULES ⚠️

## CRITICAL: Use ONLY CrewAI Native Features

When working with ANY CrewAI-related code, you MUST follow these rules:

### ✅ REQUIRED - Native CrewAI Patterns ONLY
- **`@tool` decorator**: ONLY use `from crewai.tools import tool` 
- **`Agent` class**: ONLY use `from crewai import Agent`
- **`Task` class**: ONLY use `from crewai import Task` with native parameters
- **`Crew` orchestration**: ONLY use `from crewai import Crew`
- **Simple parameter types**: str, int, bool, float ONLY
- **String returns**: All tools MUST return strings for best compatibility

### ❌ FORBIDDEN - Custom Solutions
- **NO custom decorators**: Never create wrappers around @tool
- **NO custom parameter handling**: Don't bypass CrewAI's native parameter passing
- **NO complex data structures**: Avoid passing dicts, lists, or objects as parameters
- **NO framework workarounds**: Don't create solutions that bypass CrewAI behavior

### 🔧 Tool Implementation Rules
```python
# ✅ CORRECT - Native CrewAI Pattern
from crewai.tools import tool

@tool("tool_name")
def my_tool(param1: str, param2: int) -> str:
    """Clear description with Args and Returns.
    
    Args:
        param1: Description of string parameter
        param2: Description of int parameter
        
    Returns:
        Description of string return value
    """
    return f"Result: {param1} with {param2}"

# ❌ WRONG - Custom wrappers or complex handling
@custom_tool_decorator  # FORBIDDEN
def bad_tool(complex_param: dict) -> dict:  # FORBIDDEN
```

### 🚨 Debugging Decision Tree
When encountering CrewAI issues:
1. **FIRST**: Check if current code violates native patterns above
2. **SECOND**: Simplify to basic CrewAI examples from official docs
3. **THIRD**: Consult official CrewAI documentation for proper patterns
4. **LAST**: If native patterns don't work, ask for guidance before creating custom solutions

### 📚 Quick Reference - CrewAI Native Checklist
Before implementing any CrewAI solution, verify:
- ✅ Using `@tool` from `crewai.tools`?
- ✅ Simple parameter types (str, int, bool) only?
- ✅ Clear docstrings with Args/Returns?
- ✅ Returning strings from tools?
- ✅ No custom decorators or wrappers?
- ✅ Following official CrewAI documentation patterns?

**Remember: When in doubt, keep it simple and native to CrewAI!**

## Critical Requirements

### ⚠️ Python 3.11+ MANDATORY
**IMPORTANT**: This project requires Python 3.11+ and will NOT work with Python 3.9.

```bash
# Always verify Python version first
python3.11 check_python_version.py
source venv311/bin/activate
python --version  # Should show: Python 3.11.x
```

### Essential Environment Variables
```bash
# Always use PYTHONPATH when running
PYTHONPATH=. python run_bot_local.py

# Core configuration
AI_PROVIDER=groq  # primary for local development
KICKAI_INVITE_SECRET_KEY=test-invite-secret-key-for-testing-only
FIREBASE_PROJECT_ID=<project name>
FIREBASE_CREDENTIALS_FILE=credentials/<filename>.json
```

## Common Development Commands

### Starting Development
```bash
# Standard startup
source venv311/bin/activate && PYTHONPATH=. python run_bot_local.py

# Safe startup (kills existing processes)
./start_bot_safe.sh

# Mock Telegram UI (recommended for testing)
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

# Run specific test with verbose output
PYTHONPATH=. python -m pytest tests/unit/test_file.py::test_function -v -s

# Feature-specific tests
PYTHONPATH=. python -m pytest tests/unit/features/player_registration/ -v

# With coverage
PYTHONPATH=. python -m pytest tests/ --cov=kickai --cov-report=html
```

### Code Quality
```bash
make lint  # Run all linting and formatting

# Individual tools (must be in venv311)
source venv311/bin/activate && ruff check kickai/
source venv311/bin/activate && ruff format kickai/
source venv311/bin/activate && mypy kickai/
```

### Deployment
```bash
make deploy-testing         # Deploy to testing environment
make deploy-production      # Deploy to production environment
make health-check          # Run health checks
make validate-testing      # Validate testing deployment
make validate-production   # Validate production deployment
```

## Architecture Overview

### 5-Agent CrewAI System
The system uses **5 essential agents**:

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
│   └── agentic_message_router.py # Central routing
├── core/                        # Core utilities
│   ├── command_registry.py     # Command discovery
│   └── dependency_container.py # DI container
└── database/                    # Firebase/Firestore
```

## Current Migration: JSON Tool Output

### Migration Status (Phase 3)
- **9/48 tools migrated** to JSON output format
- Player Registration: 100% complete (7/7 tools)
- Team Administration: 18% complete (2/11 tools)

### New JSON Response Pattern
```python
from kickai.utils.json_response import create_data_response

@json_tool("tool_name")
def tool_function(**kwargs) -> str:
    """Tool that returns structured JSON."""
    data = {"key": "value"}
    return create_data_response(
        data=data,
        ui_format="User-friendly message"
    )
```

### Migration Guidelines
- Use `@json_tool` decorator for new tools
- Use `@migrate_tool_to_json` for backward compatibility
- All tools should return `ToolResponse` JSON structure
- Preserve human-friendly UI formatting

## Critical CrewAI Rules (MANDATORY)

### Tool Parameter Passing - Native Approach
```python
# ✅ CORRECT - Native CrewAI parameter passing
@tool("tool_name")
def tool_function(param1: str, param2: str) -> str:
    """Tool receives parameters directly."""
    return f"Result for {param1} and {param2}"
```

### Task Creation - Structured Description
```python
# ✅ CORRECT - Structured task description
structured_description = f"""
User Request: {task_description}

Context Information:
- Team ID: {team_id}
- User Telegram ID: {telegram_id} 
- Username: {username}
- Chat Type: {chat_type}

Instructions: Use the provided context to call tools.
"""

task = Task(
    description=structured_description,
    agent=agent.crew_agent,
    expected_output="Clear response to user request",
)
```

### Tool Independence
- **❌ NEVER**: Tools calling other tools or services
- **✅ ALWAYS**: Tools are simple, independent functions
- **✅ ALWAYS**: Parameters passed directly via Task descriptions
- **✅ ALWAYS**: Tools return simple string responses (or JSON)

### Absolute Imports
```python
# ✅ CORRECT
from kickai.features.player_registration.domain.tools.player_tools import get_status

# ❌ WRONG  
from .domain.tools.player_tools import get_status
```

## Key Files to Understand

### Core System
- `kickai/agents/agentic_message_router.py` - Central message routing
- `kickai/agents/crew_agents.py` - 5-agent system definition  
- `kickai/core/dependency_container.py` - DI and service initialization
- `kickai/core/command_registry.py` - Command discovery system
- `kickai/config/agents.yaml` - Agent configuration

### JSON Migration Infrastructure
- `kickai/utils/json_response.py` - JSON response utilities
- `kickai/utils/ui_formatter.py` - UI formatting system
- `kickai/utils/crewai_tool_decorator.py` - Enhanced tool decorators

### Feature Pattern
Each feature in `kickai/features/` follows clean architecture:
```
feature_name/
├── application/commands/     # @command decorator, NO business logic
├── domain/
│   ├── tools/               # @tool/@json_tool decorator, independent functions
│   ├── services/            # Business logic (async for I/O)
│   └── entities/            # Domain models
└── infrastructure/          # Firebase repositories, external APIs
```

## Common Issues & Solutions

### Python Version
- **Error**: Module not found or syntax errors
- **Solution**: Must use Python 3.11+ with `venv311`
```bash
source venv311/bin/activate
python --version  # Must show 3.11.x
```

### Tool Issues
- **"Tool object is not callable"**: Tool is calling services/other tools
- **"Tool not found"**: Check registration in feature `__init__.py`
- **Import errors**: Use `PYTHONPATH=.` when running

### Development Issues
- **Process already running**: Use `./start_bot_safe.sh`
- **Firebase authentication**: Check credentials file path
- **Type errors with telegram_id**: Must be `int` throughout system

### Testing
- **Mock UI recommended**: Use `tests/mock_telegram/start_mock_tester.py`
- **Always use PYTHONPATH**: `PYTHONPATH=. python -m pytest`
- **Feature tests**: Test at feature level for better isolation

## Testing Strategy

### Test Organization
- `tests/unit/` - Fast, isolated component tests
- `tests/integration/` - Service interaction tests
- `tests/e2e/` - Full workflow tests (requires telethon)
- `tests/agents/` - Agent behavior tests
- `tests/mock_telegram/` - Interactive UI testing

### Mock Telegram UI
```bash
# Start Mock UI (Liverpool FC themed)
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001
```

Benefits:
- No real Telegram API calls needed
- Complete command testing
- Real-time agent responses
- Professional testing interface

## Development Workflow

### Adding New Features
1. Create feature in `kickai/features/` following clean architecture
2. Add CrewAI tools with `@tool` or `@json_tool` decorator
3. Register commands with `@command` decorator  
4. Update agent tool assignments in `agents.yaml`
5. Add comprehensive tests

### Adding New Tools (JSON Pattern)
```python
from kickai.utils.json_response import create_data_response
from kickai.utils.crewai_tool_decorator import json_tool

@json_tool("tool_name")
def new_tool(param: str) -> str:
    """Tool description."""
    # Business logic
    result = {"data": "value"}
    
    return create_data_response(
        data=result,
        ui_format="Human-friendly message"
    )
```

### Modifying AgenticMessageRouter
1. **DO NOT** create new handler classes - extend router methods
2. **PRESERVE** resource management and error handling
3. **MAINTAIN** telegram_id as int consistency
4. **TEST** thoroughly - router is critical path

## Quick Validation

### Pre-Development Checklist
```bash
# 1. Verify Python version
python3.11 check_python_version.py

# 2. Activate environment
source venv311/bin/activate

# 3. Run validation
PYTHONPATH=. python scripts/quick_validation.py

# 4. Test basic functionality
PYTHONPATH=. timeout 30s python run_bot_local.py
```

### System Health Checks
```bash
# Container initialization
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('✅ Container OK')
"

# Agent system check
PYTHONPATH=. python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('KTI')
print(f'✅ {len(system.agents)} agents loaded')
"

# Health check script
PYTHONPATH=. python scripts/run_health_checks.py
```

## Recent System Changes

### Completed Modernizations
- **Removed Legacy Components**: Handler classes consolidated into router
- **AgenticMessageRouter**: Single source of truth for routing
- **Resource Management**: Circuit breakers and memory management
- **Type Consistency**: `telegram_id` as `int` throughout
- **JSON Tool Migration**: Structured output for LLM parsing

### Benefits Achieved
- **-500+ lines** of duplicate code eliminated
- **Single routing logic** for all message types
- **Consistent error handling** with fail-fast behavior
- **Improved LLM parsing** with JSON responses
- **Better testability** with Mock UI

## Important Notes

### Before Making Changes
1. **Check Python version**: Must be 3.11+
2. **Review this CLAUDE.md**: Understand architecture and patterns
3. **Run validation**: `PYTHONPATH=. python scripts/quick_validation.py`
4. **Use Mock UI**: Test with mock interface before real bot

### When Adding Features
1. **Follow clean architecture**: See existing features as examples
2. **Tools must be independent**: No service calls in @tool functions
3. **Use absolute imports**: `from kickai.features...`
4. **Consider JSON migration**: New tools should use JSON pattern
5. **Update agents.yaml**: Assign tools to appropriate agents

### When Debugging
1. **Check agent logs**: CrewAI execution details
2. **Use Mock UI**: Interactive testing without Telegram
3. **Validation scripts**: Use scripts in `scripts/` directory
4. **Check DI container**: Ensure services initialized
5. **Monitor tool outputs**: Verify JSON structure if migrated

## Migration Notes

### JSON Tool Migration (In Progress)
- Currently migrating all tools to return structured JSON
- Use `@json_tool` for new tools, `@migrate_tool_to_json` for existing
- Preserves UI formatting while providing structured data
- See `MIGRATION_PROGRESS_SUMMARY.md` for current status

### For Legacy Code
- Handler classes removed - logic in `AgenticMessageRouter`
- Context builder removed - logic in router methods
- Use dependency container instead of factories
- All new tools should follow JSON pattern
- use telegram_id in tools, telegram_id is int.