# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KICKAI is an AI-powered football team management system built with a **5-agent CrewAI architecture** and clean architecture principles. The system processes ALL user interactions through specialized AI agents, ensuring intelligent, context-aware responses.

**Version:** 5.0  
**Status:** Production Ready with Simplified Agentic Architecture  
**Architecture:** Simplified Agentic Clean Architecture with CrewAI  
**Python Version:** 3.11+  
**Deployment:** Railway (Production), Local Development with Ollama

## Development Commands

### Environment Setup
```bash
# Set up development environment
make setup-dev

# Activate virtual environment (REQUIRED)
source venv311/bin/activate

# Start development server
make dev
# OR
PYTHONPATH=. python run_bot_local.py

# Start with performance optimizations (recommended)
./start_bot_optimized.sh
```

### Essential Environment Variables
```bash
# Core AI Configuration
AI_PROVIDER=ollama                                    # LLM provider
AI_MODEL_NAME=llama3.1:8b-instruct-q4_k_m           # Model name
OLLAMA_BASE_URL=http://localhost:11434               # Ollama server URL
LLM_TEMPERATURE=0.3                                  # Model temperature
LLM_TIMEOUT=120                                      # Request timeout

# Firebase Configuration
FIREBASE_PROJECT_ID=kickai-954c2                     # Firebase project
FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials_testing.json
USE_MOCK_DATASTORE=false                             # Use real Firebase

# System Configuration
KICKAI_INVITE_SECRET_KEY=test-invite-secret-key      # Secret key
PYTHONPATH=.                                         # Python path (REQUIRED)
USE_OPTIMIZED_PROMPTS=true                           # Enable optimizations

# Performance Optimizations (Ollama M1 Mac Mini 8GB)
OLLAMA_CONTEXT_LENGTH=1024
OLLAMA_FLASH_ATTENTION=1
OLLAMA_KV_CACHE_TYPE=q8_0
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_NUM_PARALLEL=1
```

### Testing Commands
```bash
# Run all tests (with virtual environment and PYTHONPATH)
make test
# OR
source venv311/bin/activate && PYTHONPATH=. python -m pytest tests/ -v

# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests only  
make test-e2e          # E2E tests only

# Run with coverage
source venv311/bin/activate && PYTHONPATH=. python -m pytest tests/ --cov=kickai --cov-report=html

# Run specific test file
source venv311/bin/activate && PYTHONPATH=. python -m pytest tests/unit/test_specific.py::test_function -v -s

# Mock Telegram Testing (Enhanced UI)
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001
```

### Debug Commands
```bash
# Test container initialization
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test_key_12345 python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('✅ Container initialized successfully!')
"

# Test bot startup with timeout
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test_key_12345 timeout 30s python run_bot_local.py

# Test with optimized configuration
./start_bot_optimized.sh

# Validate system startup
PYTHONPATH=. python -c "
from kickai.core.startup_validation import run_startup_validation
run_startup_validation()
"

# Test context gathering bypass performance
PYTHONPATH=. python -c "
from kickai.core.context_gathering_bypass import can_bypass_context_gathering
can_bypass, reason = can_bypass_context_gathering('/help', 1004)
print(f'✅ Bypass available: {can_bypass} ({reason})')
"
```

### Code Quality
```bash
# Run linting and formatting
make lint
# OR
scripts/lint.sh

# Individual tools
ruff check kickai/              # Linting
ruff format kickai/            # Formatting  
mypy kickai/                   # Type checking
pre-commit run --all-files     # All pre-commit hooks
```

### Deployment
```bash
# Production deployment (Railway)
python run_bot_railway.py

# Local production-like testing
./start_bot_optimized.sh

# Health check
python scripts/check_bot_status.sh
```

## 🏗️ Current Architecture

### **5-Agent CrewAI System**
The system has been **simplified** from 11 agents to use only 5 essential agents:

1. **MessageProcessorAgent** - Primary user interface and command parsing
2. **HelpAssistantAgent** - Help system and user guidance
3. **PlayerCoordinatorAgent** - Player management and registration
4. **TeamAdministrationAgent** - Team member management
5. **SquadSelectorAgent** - Squad selection and match management

### **Key Changes from Previous System**
- **Removed**: 6 agents (ONBOARDING_AGENT, AVAILABILITY_MANAGER, COMMUNICATION_MANAGER, PERFORMANCE_ANALYST, COMMAND_FALLBACK_AGENT, INTELLIGENT_SYSTEM)
- **Consolidated**: Functionality moved to remaining 5 agents through tool consolidation
- **Simplified**: Routing logic and agent selection
- **Improved**: Performance with 55% reduction in agent complexity

### **Agent Responsibilities**

#### **MessageProcessorAgent**
- **Primary Commands**: `/start`, `/version`, general natural language
- **Tools**: `send_message`, `get_user_status`, `get_available_commands`, `get_active_players`, `get_all_players`
- **Responsibilities**: Primary user interface, command parsing, general task orchestration, report generation

#### **HelpAssistantAgent**
- **Primary Commands**: `/help`, help-related natural language
- **Tools**: `get_available_commands`, `get_command_help`, `get_welcome_message`
- **Responsibilities**: Context-aware help information, user validation, command discovery, fallback handling

#### **PlayerCoordinatorAgent**
- **Primary Commands**: `/addplayer`, `/myinfo`, player-related natural language
- **Tools**: `get_my_status`, `get_player_status`, `approve_player`, `team_member_registration`
- **Responsibilities**: Player registration, status management, player onboarding (absorbed from ONBOARDING_AGENT)

#### **TeamAdministrationAgent**
- **Primary Commands**: `/addmember`, team administration natural language
- **Tools**: `send_message`, `send_announcement`
- **Responsibilities**: Team member management, administrative operations

#### **SquadSelectorAgent**
- **Primary Commands**: Squad selection, match management natural language
- **Tools**: `get_available_players_for_match`, `select_squad`
- **Responsibilities**: Squad selection, match operations, availability management (absorbed from AVAILABILITY_MANAGER)

## Code Architecture

### Feature-First Clean Architecture
```
kickai/
├── features/                    # Feature-based modules (domain-driven)
│   ├── player_registration/     # Player onboarding and management
│   ├── team_administration/     # Team management and roles
│   ├── match_management/        # Match operations and squad selection
│   ├── attendance_management/   # Attendance tracking
│   ├── communication/           # Messaging and notifications
│   ├── system_infrastructure/   # Core system services
│   └── shared/                  # Shared domain logic and tools
├── agents/                      # 5-Agent CrewAI System
│   ├── crew_agents.py          # Main agent definitions
│   ├── configurable_agent.py   # Base agent class
│   └── agentic_message_router.py # Central message routing
├── core/                        # Core utilities and registries
│   ├── command_registry.py     # Command registration system
│   ├── dependency_container.py # Dependency injection
│   ├── enums.py                # System enumerations
│   └── startup_validation/     # System validation checks
├── database/                    # Data layer with Firebase/Firestore
│   ├── firebase_client.py      # Firebase client setup
│   └── interfaces.py           # Repository interfaces
├── config/                      # Configuration files
│   ├── agents.yaml             # Agent configurations
│   ├── optimized_agent_prompts.py # Agent prompt optimizations
│   └── langgpt_integration.py  # LangGPT template system
└── utils/                       # Utilities and helpers
    ├── llm_factory.py          # Multi-provider LLM factory
    ├── async_utils.py          # Async/sync wrappers
    └── crewai_tool_decorator.py # CrewAI tool wrapper
```

### Each Feature Module Structure
```
feature_name/
├── application/
│   ├── commands/               # Command definitions with @command decorator
│   └── handlers/               # Command handlers (minimal - delegate to agents)
├── domain/
│   ├── entities/               # Domain entities and business objects
│   ├── repositories/           # Repository interfaces
│   ├── services/               # Business logic services
│   └── tools/                  # CrewAI tools for agents (@tool decorator)
└── infrastructure/             # External integrations
    └── firebase_*_repository.py # Firestore repository implementations
```

## Critical CrewAI Rules

**MANDATORY**: Follow these CrewAI patterns strictly:

### Tool Independence
- ❌ **NEVER**: Tools calling other tools or services
- ✅ **ALWAYS**: Tools are simple, independent functions
- ✅ **ALWAYS**: Parameters passed directly via Task.config
- ✅ **ALWAYS**: Tools return simple string responses

### Native CrewAI Features Only
- ✅ **REQUIRED**: `@tool` decorator from `crewai.tools`
- ✅ **REQUIRED**: `Agent` class from `crewai`
- ✅ **REQUIRED**: `Task` class with `config` parameter for context
- ✅ **REQUIRED**: `Crew` orchestration
- ❌ **FORBIDDEN**: Custom tool wrappers or parameter injection mechanisms

### LangGPT Prompt System
- ✅ **USE**: LangGPT templates for all agent prompts
- ✅ **CONTEXT**: Pass via Task.config, not injection
- ✅ **OPTIONAL FIELDS**: `player_id`, `member_id` (only for registered users)
- ✅ **OPTIONAL FIELDS**: `telegram_name` (only if user has set it)
- ❌ **AVOID**: Old prompt systems (use LangGPT exclusively)

### Absolute Imports
```python
# ✅ Correct
from kickai.features.player_registration.domain.tools.player_tools import get_player_status

# ❌ Wrong
from .domain.tools.player_tools import get_player_status
```

## Database & Infrastructure

### Firestore Collections
- **Prefix**: `kickai_` for all collections
- **Collections**: `kickai_teams`, `kickai_players`, `kickai_matches`, etc.
- **Async Patterns**: All database operations use async/await

### LLM Provider Architecture
- **Primary**: Ollama (`AI_PROVIDER=ollama`) for local development
- **Alternative**: Google Gemini, OpenAI, Hugging Face
- **Configuration**: Agent-specific model optimization in `agents.yaml`

### Security & Permissions
- **Role-Based Access**: PUBLIC, PLAYER, LEADERSHIP, ADMIN, SYSTEM
- **Chat-Based Permissions**: Different permissions for main vs leadership chat
- **Context Validation**: Validate optional fields before use

## Testing Strategy

### Test Pyramid
```bash
# Unit tests (fast, isolated)
source venv311/bin/activate && PYTHONPATH=. python -m pytest tests/unit/ -v

# Integration tests (service interactions)  
source venv311/bin/activate && PYTHONPATH=. python -m pytest tests/integration/ -v

# E2E tests (full workflows)
source venv311/bin/activate && PYTHONPATH=. python -m pytest tests/e2e/ -v

# Agent-specific tests
source venv311/bin/activate && PYTHONPATH=. python -m pytest tests/unit/agents/ -v
```

## Development Workflow

### Adding New Features
1. Create feature in `kickai/features/` following clean architecture
2. Implement domain, application, and infrastructure layers
3. Add CrewAI tools for agent interaction
4. Register commands with `@command` decorator
5. Add comprehensive tests (unit, integration, E2E)
6. Update agent tool assignments in `agents.yaml`

### Adding New Tools
1. Create tool function with `@tool` decorator from `crewai.tools`
2. Ensure tool is independent (no service/tool dependencies)
3. Export tool from feature's `__init__.py`
4. Add to agent configuration in `agents.yaml`
5. Update LangGPT templates if tool affects prompts

### Common Issues & Solutions

**CrewAI Tool Issues**
- **Tool not found**: Check tool registration in feature `__init__.py`
- **Import errors**: Ensure absolute imports with `PYTHONPATH=.`
- **Tool parameter issues**: Pass parameters via `Task.config`, not tool arguments

**Agent/Prompt Issues**
- **Missing tools**: Create tools referenced in prompts (e.g., `get_active_players`, `get_all_players`)
- **Context errors**: Validate optional fields (`player_id`, `member_id`, `telegram_name`)
- **Prompt consistency**: Use LangGPT templates exclusively

**Development Issues**
- **Python version**: Must use Python 3.11+ with `venv311`
- **Import errors**: Always use `PYTHONPATH=.` when running
- **Environment**: Activate virtual environment with `source venv311/bin/activate`

## Production Considerations

### Deployment
- **Railway**: Production deployment platform
- **Environment Variables**: Set in Railway dashboard
- **Health Checks**: Automatic health monitoring
- **Logging**: Structured logging with Loguru

### Performance Optimizations
- **Agent Reduction**: 55% reduction in agent complexity (11→5)
- **Context Bypass**: Fast path for common requests
- **Token Optimization**: Efficient prompt design
- **Model Selection**: Optimized for llama3.1:8b-instruct-q4_k_m

### System Features
- ✅ Simplified 5-agent architecture
- ✅ LangGPT prompt templates
- ✅ CrewAI Task.config for context
- ✅ Tool consolidation and optimization
- ✅ Firebase Firestore integration
- ✅ Multi-LLM provider support
- ✅ Role-based access control
- ✅ Mock Telegram testing UI