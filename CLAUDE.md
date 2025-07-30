# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KICKAI is an AI-powered football team management system built with a **12-agent CrewAI architecture** and clean architecture principles. The system processes ALL user interactions through specialized AI agents, ensuring intelligent, context-aware responses.

**Version:** 3.1  
**Status:** Production Ready  
**Architecture:** Agentic Clean Architecture with CrewAI  
**Python Version:** 3.11+

## Development Commands

### Environment Setup
```bash
# Set up development environment
make setup-dev

# Start development server
make dev
# OR
python run_bot_local.py

# Activate virtual environment
source venv311/bin/activate
```

### Testing Commands
```bash
# Run all tests
make test
# OR
python -m pytest tests/ -v

# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests only  
make test-e2e          # E2E tests only

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_specific.py::test_function -v -s

# Test LLM connectivity
source venv311/bin/activate && PYTHONPATH=. python test_hf_connectivity.py  # Test Hugging Face connectivity
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
# Deploy to testing
make deploy-testing

# Deploy to production
make deploy-production

# Validate deployment
make validate-testing
make validate-production

# Health checks
make health-check
```

## Architecture Overview

### 12-Agent CrewAI System

The system uses 12 specialized AI agents organized in logical layers:

#### Primary Interface Layer
- **MESSAGE_PROCESSOR**: Primary interface for user interactions and routing
- **INTELLIGENT_SYSTEM**: Central orchestrator for task decomposition and routing

#### Operational Layer  
- **PLAYER_COORDINATOR**: Player registration, status, and management
- **TEAM_ADMINISTRATOR**: Team administration and member management
- **SQUAD_SELECTOR**: Match squad selection and availability
- **AVAILABILITY_MANAGER**: Player availability tracking

#### Specialized Layer
- **HELP_ASSISTANT**: Help system and command guidance
- **ONBOARDING_AGENT**: New user registration and onboarding
- **COMMUNICATION_MANAGER**: Team communications and announcements
- **ANALYTICS_AGENT**: Analytics and reporting

#### Infrastructure Layer
- **SYSTEM_INFRASTRUCTURE**: System health and maintenance
- **COMMAND_FALLBACK_AGENT**: Fallback for unhandled requests

### Unified Processing Pipeline

Both slash commands and natural language use the **exact same processing pipeline**:

1. **Input Processing** → Handle both slash commands and natural language
2. **Command Registry** → Auto-discovery and metadata for slash commands  
3. **Unified Processing** → Both paths converge to `_handle_crewai_processing`
4. **CrewAI System** → Single orchestration pipeline for all requests
5. **Intent Classification** → Determine user intent (for both input types)
6. **Complexity Assessment** → Analyze request complexity
7. **Task Decomposition** → Break down into subtasks with agent assignments
8. **Agent Routing** → Route subtasks to appropriate agents
9. **Task Execution** → Execute tasks through specialized agents
10. **Result Aggregation** → Combine results and format response

## Code Architecture

### Feature-First Clean Architecture
```
kickai/
├── features/                    # Feature-based modules (domain-driven)
│   ├── player_registration/     # Player onboarding and management
│   ├── team_administration/     # Team management and roles
│   ├── match_management/        # Match operations and squad selection
│   ├── attendance_management/   # Attendance tracking
│   ├── payment_management/      # Payment processing with Collectiv
│   ├── communication/           # Messaging and notifications
│   ├── health_monitoring/       # System health checks
│   ├── system_infrastructure/   # Core system services
│   └── shared/                  # Shared domain logic
├── agents/                      # 12-Agent CrewAI System
│   ├── crew_agents.py          # Main agent definitions
│   ├── configurable_agent.py   # Base agent class
│   ├── agentic_message_router.py # Central message routing
│   └── behavioral_mixins.py    # Agent behavior patterns
├── core/                        # Core utilities and registries
│   ├── command_registry.py     # Command registration system
│   ├── dependency_container.py # Dependency injection
│   └── startup_validation/     # System validation checks
├── database/                    # Data layer with Firebase/Firestore
│   ├── firebase_client.py      # Firebase client setup
│   └── interfaces.py           # Repository interfaces
└── utils/                       # Utilities and helpers
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
├── infrastructure/             # External integrations
│   └── firebase_*_repository.py # Firestore repository implementations
└── tests/
    ├── unit/                   # Unit tests
    ├── integration/            # Integration tests
    └── e2e/                    # End-to-end tests
```

## Critical CrewAI Rules

**MANDATORY**: Follow these CrewAI patterns strictly:

### Tool Independence
- **❌ NEVER**: Tools calling other tools or services
- **✅ ALWAYS**: Tools are simple, independent functions
- **✅ ALWAYS**: Parameters passed directly via Task.config
- **✅ ALWAYS**: Tools return simple string responses

### Native CrewAI Features Only
- **✅ REQUIRED**: `@tool` decorator from `crewai.tools`
- **✅ REQUIRED**: `Agent` class from `crewai`
- **✅ REQUIRED**: `Task` class with `config` parameter
- **✅ REQUIRED**: `Crew` orchestration
- **❌ FORBIDDEN**: Custom tool wrappers or parameter passing mechanisms

### Absolute Imports with PYTHONPATH
All code uses absolute imports with `PYTHONPATH=.` or `PYTHONPATH=src`:
```python
# ✅ Correct
from kickai.features.player_registration.domain.tools.player_tools import get_player_status

# ❌ Wrong
from .domain.tools.player_tools import get_player_status
```

## Database & Infrastructure

### Firestore Collections
- Prefix: `kickai_` for all collections
- Collections: `kickai_teams`, `kickai_players`, `kickai_matches`, etc.
- Use async patterns for all database operations

### LLM Provider Architecture
The system supports multiple LLM providers with agent-specific model optimization:

#### Supported Providers
- **Hugging Face** (`AIProvider.HUGGINGFACE`) - Primary provider with free tier
- **Google Gemini** (`AIProvider.GOOGLE`) - Fallback provider
- **OpenAI** (`AIProvider.OPENAI`) - Optional provider
- **Ollama** (`AIProvider.OLLAMA`) - Local deployment option

#### Agent-Specific Models
Each agent uses optimized models based on task requirements:
- **Data-critical agents** (temp 0.1): `Qwen2.5-1.5B-Instruct` for anti-hallucination
- **Administrative agents** (temp 0.3): `Gemma-2-2B-IT` for balanced performance
- **Creative agents** (temp 0.7): Larger models for complex reasoning

#### Configuration Files
- `kickai/config/agent_models.py` - Agent-specific model mappings
- `kickai/utils/llm_factory.py` - Multi-provider LLM factory
- `kickai/core/settings.py` - Provider API token configuration

### Security & Permissions
- **Role-Based Access Control**: PUBLIC, PLAYER, LEADERSHIP, ADMIN, SYSTEM
- **Chat-Based Permissions**: Different permissions for main chat vs leadership chat
- **Unified Security**: Same permission checking for slash commands and natural language

### Configuration
- **Environment Files**: `.env`, `.env.development`, `.env.testing`, `.env.production`
- **LLM API Keys**: `HUGGINGFACE_API_TOKEN`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`
- **Bot Configs**: `config/bot_config.json` for different environments
- **Firebase**: `credentials/firebase_credentials_*.json`

## Testing Strategy

### Test Pyramid
- **Unit Tests**: Individual components with mocked dependencies
- **Integration Tests**: Service interactions with mock external services
- **E2E Tests**: Complete user workflows with real APIs

### Test Commands by Type
```bash
# Unit tests (fast, isolated)
python -m pytest tests/unit/ -v

# Integration tests (service interactions)  
python -m pytest tests/integration/ -v

# E2E tests (full workflows)
python -m pytest tests/e2e/ -v

# Agent-specific tests
python -m pytest tests/unit/agents/ -v

# Feature-specific tests
python -m pytest tests/unit/features/player_registration/ -v
```

## Development Workflow

### Adding New Features
1. **Follow Feature-First Architecture**: Create in `kickai/features/`
2. **Implement Clean Architecture**: Domain → Application → Infrastructure layers
3. **Use Agentic Patterns**: Delegate to CrewAI agents for user interactions
4. **Write Comprehensive Tests**: Unit, integration, and E2E tests
5. **Update Agent Tools**: Add new tools to appropriate agents

### Command Development
1. **Register Command**: Use `@command` decorator in feature module
2. **Delegate to Agent**: No direct implementation - delegate to CrewAI agent
3. **Define Permissions**: Set appropriate permission levels
4. **Add Tests**: Test command registration and agent routing

### Agent Development
1. **Define Agent Role**: Clear responsibility and primary commands
2. **Implement Tools**: Create domain-specific tools for the agent
3. **Configure Context**: Ensure proper context configuration
4. **Test Agent Behavior**: Verify agent responses and tool usage

## Key Implementation Files

### Core System Files
- `kickai/agents/agentic_message_router.py` - Central message routing
- `kickai/core/command_registry.py` - Command registration system
- `kickai/core/dependency_container.py` - Dependency injection container

### Agent System Files
- `kickai/agents/crew_agents.py` - 12 specialized agents
- `kickai/agents/configurable_agent.py` - Base agent class
- `kickai/agents/tool_registry.py` - Tool discovery and registration

### Entry Points
- `run_bot_local.py` - Local development entry point
- `run_bot_railway.py` - Production deployment entry point

## Common Issues & Solutions

### CrewAI Tool Issues
- **Tool not found**: Check tool registration in feature `__init__.py`
- **Import errors**: Ensure absolute imports with `PYTHONPATH=.`
- **Tool parameter issues**: Pass parameters via `Task.config`, not tool arguments

### Testing Issues
- **Test isolation**: Use separate test environment and cleanup between tests
- **Async test issues**: Use `pytest-asyncio` and proper async test patterns
- **Mock issues**: Mock external services but use real Firebase for E2E tests

### Development Issues
- **Environment setup**: Run `make setup-dev` for complete environment setup
- **Dependency issues**: Check `requirements.txt` and `requirements-local.txt`
- **Type checking**: Use `mypy kickai/` to catch type issues early

## Production Considerations

### Deployment
- **Railway**: Used for production deployment
- **Environment Variables**: Set in Railway dashboard
- **Health Checks**: Automatic health monitoring via agents
- **Logging**: Structured logging with proper context

### Monitoring
- **System Health**: Via `SYSTEM_INFRASTRUCTURE` agent
- **Agent Performance**: Track response times and success rates
- **Error Handling**: Comprehensive error logging and user feedback

### Security
- **Access Control**: Multi-layered permission system
- **Data Validation**: Pydantic models for all data structures
- **Secret Management**: Environment variables and Firebase credentials