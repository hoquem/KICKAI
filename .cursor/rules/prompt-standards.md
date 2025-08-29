# Prompt Standards for KICKAI Development

**Version**: 3.1 | **Last Updated**: January 2025 | **Architecture**: Clean Architecture Migration Complete

This document establishes standardized prompt engineering patterns for Cursor IDE when working with the KICKAI AI-Powered Football Team Management System.

## 🎯 Core Prompt Engineering Standards

### 1. Context-Aware Prompting

**Standard Pattern:**
```
Context: KICKAI v3.1 - 6-Agent CrewAI System with Clean Architecture
Task: [Specific task description]
Requirements:
- Python 3.11+ mandatory
- Clean Architecture compliance
- CrewAI native patterns
- Firebase async operations
- Comprehensive testing
```

### 2. Architecture-First Prompting

**Always Specify:**
- **Layer**: Application, Domain, or Infrastructure
- **Pattern**: Tool, Service, Repository, or Entity
- **Framework**: CrewAI (@tool decorator) or Pure Domain Logic
- **Testing**: Unit, Integration, or E2E requirements

**Example:**
```
Create a new player status tool following Clean Architecture:
- Application Layer: @tool decorator with parameter handling
- Domain Layer: Pure business logic function
- Infrastructure Layer: Firebase repository access
- Testing: Unit tests for business logic, integration tests for Firebase
```

### 3. Feature-First Development Prompts

**Structure:**
```
Feature: [Feature name from kickai/features/]
Component: [Specific component - tool, service, repository, entity]
Standards: 
- Follow existing patterns in the feature
- Maintain Clean Architecture boundaries
- Use established naming conventions
- Include comprehensive error handling
```

## 🏗️ Architecture-Specific Prompt Patterns

### Clean Architecture Tool Creation

**Prompt Template:**
```
Create a new tool for [feature_name] following KICKAI Clean Architecture standards:

Application Layer (kickai/features/[feature]/application/tools/):
- @tool decorator with proper metadata
- Parameter validation and type conversion
- Delegates to domain layer function

Domain Layer (kickai/features/[feature]/domain/tools/):
- Pure business logic with no framework dependencies
- Dependency injection through constructor
- Returns JSON formatted responses

Testing:
- Unit tests for domain logic
- Integration tests for application layer
- Mock all external dependencies
```

### Service Layer Prompts

**Template:**
```
Implement [service_name] service following KICKAI patterns:

Interface (domain/repositories/):
- Abstract base class with typing
- Clear method signatures
- Docstring documentation

Implementation (infrastructure/):
- Firebase async operations
- Error handling with try/catch
- Logging for operations

Domain Service (domain/services/):
- Constructor injection of repositories
- Pure business logic
- No external dependencies
```

### Agent System Prompts

**Template:**
```
Work with KICKAI's 6-Agent CrewAI system:

Agents:
1. MESSAGE_PROCESSOR - Primary interface orchestrator
2. NLP_PROCESSOR - Intelligent routing and intent analysis  
3. PLAYER_COORDINATOR - Player operations
4. TEAM_ADMINISTRATOR - Team management
5. SQUAD_SELECTOR - Match and availability management
6. HELP_ASSISTANT - Help and documentation

Routing: NLP_PROCESSOR analyzes intent and recommends specialist
Execution: Specialist agent handles specific request types
Response: MESSAGE_PROCESSOR coordinates final response
```

## 🔧 Development Workflow Prompts

### New Feature Development

**Step-by-Step Prompt:**
```
Implement new feature [feature_name] following KICKAI standards:

1. Architecture Planning:
   - Design domain entities and value objects
   - Define repository interfaces
   - Plan service layer interactions

2. Implementation Order:
   - Domain entities (kickai/features/[feature]/domain/entities/)
   - Repository interfaces (domain/repositories/)
   - Service implementations (domain/services/)
   - Infrastructure repositories (infrastructure/)
   - Application tools (application/tools/)

3. Testing Strategy:
   - Unit tests for domain logic
   - Integration tests for services
   - E2E tests for user workflows
   - Mock all external dependencies

4. Registration:
   - Export tools from feature __init__.py
   - Register with agent system
   - Update command routing if needed
```

### Bug Fixing Prompts

**Debugging Template:**
```
Debug issue in KICKAI system:

1. Identify Layer:
   - Application layer (tools, commands)
   - Domain layer (services, entities)
   - Infrastructure layer (repositories, Firebase)

2. Check Common Issues:
   - Import errors: Use PYTHONPATH=.
   - Tool not found: Check feature __init__.py export
   - Service unavailable: Verify container initialization
   - Async issues: Ensure proper await patterns

3. Testing Verification:
   - Run specific test: python -m pytest tests/path/to/test.py -v
   - Check system health: PYTHONPATH=. python scripts/run_health_checks.py
   - Validate with mock UI: PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
```

## 📋 Code Quality Prompts

### Code Review Prompts

**Review Checklist:**
```
Review code for KICKAI compliance:

Clean Architecture:
- ✅ Application layer has @tool decorators only
- ✅ Domain layer has pure business logic only
- ✅ Infrastructure layer handles external concerns
- ✅ No layer violations or circular dependencies

CrewAI Standards:
- ✅ Tools use @tool decorator with metadata
- ✅ Proper parameter handling and validation
- ✅ Async def for all tool functions
- ✅ JSON response format consistency

Code Quality:
- ✅ Type hints throughout
- ✅ Comprehensive error handling
- ✅ Proper logging and monitoring
- ✅ Adequate test coverage
```

### Refactoring Prompts

**Refactoring Template:**
```
Refactor [component] following KICKAI standards:

1. Assess Current State:
   - Identify architecture violations
   - Check for code duplication
   - Review error handling patterns

2. Plan Improvements:
   - Align with Clean Architecture
   - Extract common patterns
   - Improve error handling

3. Execute Changes:
   - Maintain backward compatibility
   - Update tests accordingly
   - Verify system integration

4. Validation:
   - Run full test suite
   - Check system health
   - Validate with mock UI
```

## 🧪 Testing-Focused Prompts

### Test Creation

**Testing Template:**
```
Create comprehensive tests for [component]:

Unit Tests (tests/unit/):
- Test pure business logic
- Mock all external dependencies
- Cover edge cases and error conditions
- Fast execution (< 100ms per test)

Integration Tests (tests/integration/):
- Test service interactions
- Use real database (test environment)
- Verify end-to-end workflows
- Include error scenarios

E2E Tests (tests/e2e/):
- Test complete user journeys
- Use mock Telegram interface
- Verify system behavior
- Include regression scenarios
```

### Test Debugging

**Debugging Template:**
```
Debug failing tests in KICKAI:

1. Identify Test Type:
   - Unit: Check mocking and business logic
   - Integration: Verify service interactions and database
   - E2E: Check system integration and user workflows

2. Common Issues:
   - Import errors: Ensure PYTHONPATH=.
   - Database issues: Check Firebase test data
   - Async issues: Verify await patterns
   - Mock issues: Check mock setup and expectations

3. Debugging Commands:
   - Run single test: python -m pytest tests/path/test.py::test_name -v -s
   - Run with logging: python -m pytest tests/path/test.py -v --log-cli-level=DEBUG
   - Check test data: Use Firebase console for data verification
```

## 🔄 Migration and Updates

### Legacy Code Migration

**Migration Template:**
```
Migrate legacy code to KICKAI v3.1 standards:

1. Architecture Assessment:
   - Identify current architecture violations
   - Map components to Clean Architecture layers
   - Plan migration strategy

2. Migration Steps:
   - Extract domain logic from mixed concerns
   - Create proper repository interfaces
   - Implement infrastructure adapters
   - Update tool registrations

3. Validation:
   - Maintain functionality during migration
   - Update tests to match new structure
   - Verify system integration
```

### Version Updates

**Update Template:**
```
Update KICKAI system component:

1. Impact Assessment:
   - Identify affected components
   - Check breaking changes
   - Plan backward compatibility

2. Update Strategy:
   - Update in dependency order
   - Maintain API contracts
   - Update documentation

3. Validation:
   - Run full test suite
   - Check system health
   - Validate with users (if applicable)
```

## 📚 Documentation Standards

### Code Documentation

**Documentation Template:**
```
Document [component] following KICKAI standards:

1. Module Docstring:
   - Purpose and responsibility
   - Architecture layer and role
   - Key dependencies and interfaces

2. Function/Method Docstrings:
   - Purpose and behavior
   - Parameter types and validation
   - Return value format
   - Error conditions and handling

3. Inline Comments:
   - Complex business logic
   - Non-obvious implementation details
   - Important architectural decisions
```

### API Documentation

**API Template:**
```
Document API for [component]:

1. Interface Definition:
   - Method signatures with types
   - Parameter validation rules
   - Return value specifications

2. Usage Examples:
   - Common use cases
   - Error handling examples
   - Integration patterns

3. Testing Guidance:
   - Unit test patterns
   - Mock setup examples
   - Integration test scenarios
```

---

## 🎯 Quick Reference Commands

### Essential Development Commands
```bash
# System validation
PYTHONPATH=. python scripts/run_health_checks.py

# Development server
make dev

# Testing
make test                    # All tests
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make test-e2e              # E2E tests only

# Code quality
make lint                   # Linting and formatting
ruff check kickai/          # Linting only
mypy kickai/               # Type checking

# Mock testing
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py  # Mock UI
```

### Emergency Debugging
```bash
# Quick system check
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('✅ System initialization: SUCCESS')
"

# Tool registry validation
PYTHONPATH=. python -c "
from kickai.agents.tool_registry import initialize_tool_registry
registry = initialize_tool_registry()
print(f'✅ Tools loaded: {len(registry.get_all_tools())}')
"
```

---

**Status**: Production Ready | **Architecture**: Clean Architecture Complete | **Testing**: Comprehensive Coverage