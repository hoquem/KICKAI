# Player Registration Module

This module encapsulates all logic related to player registration, player info, and player status management.

- Domain: Entities, services, and repositories for player management
- Application: Command handlers and business logic
- Infrastructure: Data access and integration
- Tests: Unit, integration, and E2E tests

## Responsibilities
- Player registration
- Player info and status
- Player listing

## Clean Architecture
This module is self-contained and interacts with other modules only via interfaces and dependency injection. Do not introduce direct dependencies on other feature modules. 