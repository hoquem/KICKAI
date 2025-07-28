# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build and Test Commands
```bash
# Development workflow
make dev-workflow         # Run clean, test, lint sequence
make setup-dev           # Set up development environment with Python 3.11 venv and dependencies

# Testing
make test                # Run all tests (unit + integration + e2e)
make test-unit           # Run unit tests only
make test-integration    # Run integration tests only  
make test-e2e            # Run E2E tests only
source venv311/bin/activate && PYTHONPATH=. pytest tests/unit/       # Run specific test directory
source venv311/bin/activate && PYTHONPATH=. pytest tests/unit/agents/ # Run agent-specific tests

# Code quality
make lint                # Run ruff check, format, and mypy
source venv311/bin/activate && ruff check kickai/       # Lint code
source venv311/bin/activate && ruff format kickai/      # Format code
source venv311/bin/activate && mypy kickai/             # Type checking

# Development server
make dev                 # Start local bot with Python 3.11
source venv311/bin/activate && PYTHONPATH=. python run_bot_local.py  # Direct bot startup
./start_bot_safe.sh      # Safe startup with process management (uses Python 3.11)

# Health and validation
make health-check        # Run system health checks
source venv311/bin/activate && PYTHONPATH=. python scripts/run_health_checks.py
source venv311/bin/activate && PYTHONPATH=. python scripts/validate_feature_deployment.py --feature=all
```

### Deployment Commands
```bash
# Railway deployment
make deploy-testing      # Deploy to testing environment
make deploy-production   # Deploy to production environment
make validate-testing    # Validate testing deployment
make validate-production # Validate production deployment

# Environment setup
make bootstrap-testing   # Bootstrap testing environment
make bootstrap-production # Bootstrap production environment
```

### Test Execution Notes
- All tests require `PYTHONPATH=src` environment variable
- E2E tests use real Firestore database in test environment
- Tests are configured with pytest.ini and pyproject.toml
- Test coverage target is 70% minimum

## Architecture Overview

### Agentic Clean Architecture with CrewAI
KICKAI is built on a **unified processing pipeline** where both slash commands and natural language requests are processed through the same 8-agent CrewAI system.

#### Core Processing Flow
1. **Input Processing** → Handle slash commands and natural language
2. **Unified Processing** → Both paths converge to `_handle_crewai_processing`
3. **CrewAI Orchestration** → Single processing pipeline for all requests
4. **Agent Routing** → Context-aware agent selection
5. **Task Execution** → Specialized agents execute domain-specific tasks

#### 8-Agent System Architecture
- **MESSAGE_PROCESSOR**: Primary interface, intent analysis, message routing
- **PLAYER_COORDINATOR**: Player registration, status management, individual support
- **TEAM_MANAGER**: Team administration, member management, leadership operations
- **SQUAD_SELECTOR**: Match operations, squad selection, player availability
- **AVAILABILITY_MANAGER**: Availability tracking, match availability management
- **HELP_ASSISTANT**: Context-aware help, command guidance, user support
- **ONBOARDING_AGENT**: Comprehensive dual-entity onboarding for both players and team members
- **SYSTEM_INFRASTRUCTURE**: System health, monitoring, error logging

### Feature-First Modular Design
```
kickai/
├── features/                    # Feature-based modules (Clean Architecture)
│   ├── player_registration/     # Player onboarding and management
│   ├── team_administration/     # Team and member management  
│   ├── match_management/        # Match operations
│   ├── attendance_management/   # Attendance tracking
│   ├── payment_management/      # Payment processing with Collectiv
│   ├── communication/           # Messaging and notifications
│   ├── health_monitoring/       # System health and monitoring
│   └── shared/                  # Shared components across features
├── agents/                      # CrewAI agent system
├── core/                        # Core utilities and registries
├── database/                    # Firebase/Firestore data layer
└── utils/                       # Utilities and helpers
```

Each feature follows Clean Architecture:
- `application/commands/` - Command definitions
- `domain/entities/` - Domain models
- `domain/services/` - Business logic
- `domain/repositories/` - Data access interfaces
- `infrastructure/` - External service implementations

### Context-Aware Command Processing
Commands behave differently based on chat context:

**Main Chat:**
- `/list` → Shows active players only (via PLAYER_COORDINATOR)
- `/myinfo` → Player status information
- `/status` → Player registration status

**Leadership Chat:**
- `/list` → Shows all players with detailed status (via MESSAGE_PROCESSOR)
- `/approve` → Player approval workflow
- `/addplayer` → Direct player addition
- `/addmember` → Team member management

### Tool Architecture
- Tools are **independent functions** with `@tool` decorator from `crewai.tools`
- Tools **MUST NOT** call other tools or services (CrewAI requirement)
- Parameters passed directly via `Task.config`
- Tools return simple string responses
- Tool discovery is automatic from feature directories

## Critical Development Rules

### CrewAI Best Practices (CRITICAL)
Based on `.cursor/rules/13_crewai_best_practices.md`:

1. **Tool Independence**: Tools cannot call other tools or services
2. **Native CrewAI Only**: Use only `@tool`, `Agent`, `Task`, `Crew` from CrewAI
3. **Absolute Imports**: Always use `PYTHONPATH=src` and absolute imports
4. **Parameter Passing**: Use `Task.config` for parameter passing
5. **Simple Responses**: Tools return simple string responses only

### Architecture Rules
Based on `.cursor/rules/01_architecture.md`:

1. **Clean Architecture**: Presentation → Application → Domain → Infrastructure
2. **No Circular Dependencies**: Strict layer separation
3. **Feature-First**: Organize by business features, not technical layers
4. **Dependency Injection**: Use DI container for service resolution
5. **Async-First**: Prefer async/await for I/O operations

### Database Design
- **Firestore Collections**: Use `kickai_` prefix with team-specific naming for multi-tenant isolation
  - **Global Collections**: `kickai_teams`, `kickai_system_config` (team-independent data)
  - **Team-Specific Collections**: `kickai_{TEAM_ID}_{entity}` format for team-isolated data
    - `kickai_KTI_players` (players for team KTI)
    - `kickai_KTI_members` (team members for team KTI)  
    - `kickai_KTI_matches` (matches for team KTI)
    - `kickai_KTI_attendance` (attendance records for team KTI)
    - `kickai_KTI_payments` (payment records for team KTI)
- **Repository Pattern**: Each feature has interface + implementation
- **Team Context**: Complete data isolation using team_id in collection names
- **Collection Naming Helper**: Use `get_team_members_collection(team_id)` from `kickai/core/constants.py`

### Permission System
- **Role-Based Access**: PUBLIC, PLAYER, LEADERSHIP, ADMIN, SYSTEM levels
- **Chat-Based Control**: Different permissions for main vs leadership chat
- **Unified Security**: Same permission checking for commands and natural language

## Configuration Files

### Key Configuration Files
- `pyproject.toml` - Python project configuration, dependencies, linting rules
- `pytest.ini` - Test configuration with markers and execution settings
- `Makefile` - Development workflow commands
- `kickai/core/constants.py` - Centralized command definitions and constants
- `kickai/core/enums.py` - System enums (ChatType, PermissionLevel, etc.)
- `.cursor/rules/` - Cursor AI rules for architecture and development patterns

### Environment Files
- `.env.example` - Environment template for system-level configuration
- `credentials/` - Firebase service account credentials (template provided)
  - `firebase_credentials_template.json` - Template for Firebase credentials
  - `firebase_credentials_testing.json` - Testing environment credentials

### Bot Configuration
- **Team-Specific Configuration**: Bot configuration is stored in Firestore, NOT in local files
- **Database Location**: Each team document in `kickai_teams` collection contains bot configuration
- **Configuration Fields**: Team documents include bot tokens, chat IDs, and team-specific settings
- **Dynamic Loading**: Bot configuration is loaded dynamically from Firestore at runtime
- **Multi-Team Support**: Different teams can have different bot configurations within the same deployment

## Testing Strategy

### Test Structure
```
tests/
├── unit/                # Unit tests for individual components
├── integration/         # Integration tests for service interactions  
├── e2e/                # End-to-end tests for complete workflows
├── frameworks/         # Test frameworks and utilities
└── conftest.py         # Shared test configuration
```

### Test Markers (pytest)
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.async` - Asynchronous tests
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.smoke` - Basic smoke tests

### Test Data Management
- Use separate test environment configuration
- E2E tests use real Firestore with test data
- Mock external services in unit tests
- Test data cleanup scripts in `setup/cleanup/`

## Key Development Workflows

### Adding New Features
1. Create feature directory in `kickai/features/`
2. Follow Clean Architecture structure (application/domain/infrastructure)
3. Define commands in feature's `commands/` directory
4. Implement tools following CrewAI independence rules
5. Add agent assignment in agent configuration
6. Write comprehensive tests (unit, integration, e2e)

### Agent Development
1. Define agent role and responsibilities in agent configuration
2. Create domain-specific tools (independent functions only)
3. Configure context and routing rules
4. Test agent behavior with both slash commands and natural language
5. Update registry and tool discovery

### Command Development
1. Define command in `kickai/core/constants.py`
2. Set appropriate permission level and chat types
3. Implement command delegation to appropriate agent
4. Test command registration and agent routing
5. Update documentation and help system

## Debugging and Monitoring

### Logging
- Structured logging with loguru
- Log levels: DEBUG, INFO, WARNING, ERROR
- Logs stored in `logs/` directory
- Agent performance and tool usage tracking

### Health Monitoring
```bash
# System health checks
python scripts/run_health_checks.py
python scripts/validate_feature_deployment.py

# Check bot status
./check_bot_status.sh

# Monitor logs
tail -f logs/kickai.log
```

## Enhanced ONBOARDING_AGENT Features

### Dual-Entity Onboarding System
The ONBOARDING_AGENT now supports comprehensive onboarding for both players and team members:

**Phase 1 - Core Expansion:**
- **EntityType.TEAM_MEMBER** support added alongside EntityType.PLAYER
- **Dual workflow routing** with context-aware detection
- **Enhanced register_team_member tool** with better feedback

**Phase 2 - Enhanced Experience:**
- **Progressive information collection** with step-by-step guidance
- **Role-specific guidance** with detailed explanations for positions/roles
- **Enhanced validation** with smart suggestions and error correction

**Phase 3 - Intelligence Features:**
- **Dual role detection** for users wanting both player and admin roles
- **Cross-entity linking** for unified profiles and data synchronization
- **Smart recommendations** based on user characteristics and team needs

### Key Onboarding Tools

**Progressive Collection:**
- `progressive_onboarding_step` - Step-by-step user guidance
- `get_onboarding_progress` - Track onboarding status

**Role Guidance:**
- `explain_player_position` - Detailed position explanations
- `explain_team_role` - Administrative role guidance
- `compare_positions/roles` - Help users choose between options

**Enhanced Validation:**
- `validate_name_enhanced` - Smart name validation with suggestions
- `validate_phone_enhanced` - UK phone format with corrections
- `validate_position/role_enhanced` - Smart suggestions for typos

**Dual Role Management:**
- `detect_existing_registrations` - Check for existing user records
- `analyze_dual_role_potential` - Determine if user wants both roles
- `execute_dual_registration` - Register for both player and team member

**Smart Recommendations:**
- `get_smart_position_recommendations` - AI-powered position suggestions
- `get_onboarding_path_recommendation` - Personalized onboarding paths
- `get_personalized_welcome_message` - Custom welcome based on choices

### Usage Examples

**Dual Role Registration:**
```
User: "I want to help coach and also play midfielder"
→ ONBOARDING_AGENT detects dual intent
→ Suggests dual registration path
→ Registers as team member (immediate) + player (pending approval)
```

**Smart Position Recommendation:**
```
User: "I'm new to football, what position should I play?"
→ Agent asks about experience, physical attributes, playing style
→ Provides personalized recommendations with reasoning
→ Explains each position in detail
```

### Common Issues
- **Import Errors**: Ensure `PYTHONPATH=src` is set
- **Tool Registration**: Check tool discovery in feature directories  
- **Agent Routing**: Verify agent configuration and context rules
- **Database Access**: Validate Firebase credentials and collection naming
- **Onboarding Tools**: Ensure shared/domain/tools are properly imported