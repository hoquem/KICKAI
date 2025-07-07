# Core Architecture: Clean & SOLID

This project's long-term health depends on strict adherence to these architectural principles.

- **Clean Architecture**: The code must be physically and logically separated into four layers: `domain`, `application`, `infrastructure`, and `presentation`.
  - **Dependency Rule**: Dependencies must *only* point inwards. `presentation` -> `application` -> `domain`. The `infrastructure` layer implements interfaces defined in the `application` and `domain` layers. No `domain` code should ever import from another layer.

- **SOLID Principles**: All code must adhere to SOLID principles, with a strong emphasis on the **Single Responsibility Principle (SRP)**. Every class, every function serves one purpose.

- **Dependency Injection (DI)**: All dependencies (repositories, services, agents) **must** be managed by a DI container (`dependency-injector` library). They will be injected into use cases and handlers from a central container in `src/core/container.py`. This is critical for decoupling and testability.

- **Service Interfaces**: All services must implement interfaces defined in `src/services/interfaces/`. This enables:
  - **Dependency Injection**: Services depend on interfaces, not concrete implementations
  - **Easy Testing**: Mock implementations for predictable test behavior
  - **Contract Enforcement**: Clear contracts that all implementations must follow
  - **Code Maintainability**: Easy to swap implementations and add new features

- **Design Patterns**:
  - **Repository Pattern**: Abstract data access interfaces will be defined in the `domain` layer. Concrete implementations (e.g., for a JSON file, a database) will live in the `infrastructure` layer.
  - **Command Pattern**: User actions, whether from a `/command` or natural language, should be translated into command objects that the `application` layer processes.
  - **Strategy Pattern**: Used for permission strategies and configuration sources
  - **Factory Pattern**: Used for agent creation and configuration object creation
  - **Observer Pattern**: Used for configuration change notifications and command logging
  - **Chain of Responsibility**: Used for configuration validation and command processing
  - **Builder Pattern**: Used for complex configuration object construction