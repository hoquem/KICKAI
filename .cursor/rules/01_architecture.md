# Architecture Rules

## Core Principles

### Clean Architecture
- Follow Clean Architecture principles with clear layer separation
- Presentation → Application → Domain → Infrastructure
- No circular dependencies
- Domain layer has no external dependencies

### Feature-First Modular Design
- Organize code by business features, not technical layers
- Each feature is self-contained with its own domain, application, and infrastructure
- Shared code goes in `src/features/shared/`
- Core system code goes in `src/core/`

### Dependency Injection
- Use dependency injection container for service resolution
- Services are registered in the container and resolved at runtime
- Avoid direct instantiation of services in business logic

### Async-First Design
- Prefer async/await patterns for I/O operations
- Use async services and repositories
- Handle async operations properly with proper error handling

### Type Safety
- Use type hints throughout the codebase
- Use Pydantic models for data validation
- Prefer dataclasses for simple data structures

## Agentic Architecture

### CrewAI Integration
- All user interactions processed through CrewAI agents
- No dedicated command handlers - commands delegate to agents
- Agents are specialized for specific domains (player management, team management, etc.)
- Use the 8-agent CrewAI system as defined in the architecture

### Tool Management
- Tools are independent functions with @tool decorator
- Tools must not call other tools or services (see CrewAI best practices)
- Tools are discovered automatically from feature directories
- Tools are assigned to agents based on role configuration

## Database Design

### Firestore Collections
- Use `kickai_` prefix for all collections
- Collections: `kickai_teams`, `kickai_players`, `kickai_matches`, etc.
- Follow Firestore best practices for data modeling

### Repository Pattern
- Each feature has its own repository interface and implementation
- Repositories handle data access and persistence
- Use async patterns for database operations

## Testing Strategy

### Test Pyramid
- Unit tests for business logic
- Integration tests for service interactions
- E2E tests for complete user workflows

### Test Data
- Use separate test environment (.env.test)
- Use real Firestore for E2E tests
- Mock external services in unit tests

## Error Handling

### Exception Strategy
- Use custom exceptions for business logic errors
- Log all exceptions with proper context
- Return meaningful error messages to users
- Handle async exceptions properly

## Logging

### Logging Strategy
- Use structured logging with loguru
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages
- Use consistent log format

## Security

### Access Control
- Implement role-based access control
- Validate user permissions for all operations
- Use team context for multi-tenant isolation
- Sanitize all user inputs

## Performance

### Optimization
- Use async operations for I/O
- Implement caching where appropriate
- Optimize database queries
- Monitor performance metrics

## Documentation

### Code Documentation
- Document all public APIs
- Use docstrings for complex functions
- Keep documentation up to date
- Use type hints for better documentation

## Critical CrewAI Requirements

**IMPORTANT**: For CrewAI integration, see `.cursor/rules/13_crewai_best_practices.md` for critical rules that must be followed:

- Tool independence (tools cannot call other tools or services)
- Absolute imports with PYTHONPATH=src
- Proper tool discovery and registration patterns
- Common error solutions and debugging procedures

**These CrewAI rules are CRITICAL for system stability and must be followed strictly.**