# Team Administration Module

This module encapsulates all logic related to team creation, member management, and team settings.

- Domain: Entities, services, and repositories for team administration
- Application: Command handlers and business logic
- Infrastructure: Data access and integration
- Tests: Unit, integration, and E2E tests

## Responsibilities
- Team creation and settings
- Team member management

## Clean Architecture
This module is self-contained and interacts with other modules only via interfaces and dependency injection. Do not introduce direct dependencies on other feature modules. 