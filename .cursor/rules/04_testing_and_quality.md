# Testing and Code Quality

- **Testing Framework**: All tests will be written using `pytest`.
- **Test Focus**: Prioritize unit tests for the `domain` and `application` layers. These tests must run in isolation without external dependencies.
- **Mocking**: Use `unittest.mock` to stub and mock dependencies (repositories, API clients, agent services) during tests.
- **Code Formatting**: All code is to be auto-formatted with `black` on save.
- **Linting**: Use `ruff` for fast, comprehensive linting to catch errors and style issues early.