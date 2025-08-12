# Attendance Management Module

This module handles non-match specific attendance tracking including training sessions, 
team events, social activities, and general RSVP functionality.

**Note:** Match-specific attendance and availability is handled by the `match_management` module.

- Domain: Entities, services, and repositories for event attendance management
- Application: Command handlers and business logic for non-match events
- Infrastructure: Data access and integration
- Tests: Unit, integration, and E2E tests

## Responsibilities
- RSVP tracking for team events and training sessions
- Event attendance reminders
- Training session attendance
- Social event coordination
- Non-match activity tracking

## What this module does NOT handle
- Match availability (handled by match_management)
- Match attendance tracking (handled by match_management)
- Squad selection (handled by match_management)

## Clean Architecture
This module is self-contained and interacts with other modules only via interfaces and dependency injection. Do not introduce direct dependencies on other feature modules. 