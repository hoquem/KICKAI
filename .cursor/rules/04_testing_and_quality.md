# Testing and Code Quality

**Summary: Code complexity must be kept low. All code must be testable, modular, and maintainable. All tests must be isolated, fast, and easy to maintain. These are required for all new code and refactors.**

- **Code Complexity**: Avoid unnecessary complexity. Prefer simple, readable, and maintainable code. Refactor aggressively to keep codebase clean.
- **Testability**: All code must be easy to test in isolation. Avoid tight coupling, global state, and hidden dependencies.
- **Modularity**: New features must be modularized and encapsulated. Avoid monolithic or tangled code.
- **Maintainability**: Code should be easy to refactor, extend, and debug.

---

- **Testing Framework**: All tests will be written using `pytest`.
- **Test Focus**: Prioritize unit tests for the `domain` and `application` layers. These tests must run in isolation without external dependencies.
- **Mocking**: Use `unittest.mock` to stub and mock dependencies (repositories, API clients, agent services) during tests.
- **Code Formatting**: All code is to be auto-formatted with `black` on save.
- **Linting**: Use `ruff` for fast, comprehensive linting to catch errors and style issues early.