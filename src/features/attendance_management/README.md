# Attendance Management Module

This module encapsulates all logic related to attendance tracking, RSVP, and reminders.

- Domain: Entities, services, and repositories for attendance management
- Application: Command handlers and business logic
- Infrastructure: Data access and integration
- Tests: Unit, integration, and E2E tests

## Responsibilities
- RSVP and attendance tracking
- Attendance reminders

## Clean Architecture
This module is self-contained and interacts with other modules only via interfaces and dependency injection. Do not introduce direct dependencies on other feature modules. 