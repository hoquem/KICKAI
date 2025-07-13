# Core Architecture: Clean, Modular, and Testable

**These rules are non-negotiable and apply to all new code and refactors.**

- **Keep Code Complexity Low**: Prioritize simplicity, readability, and maintainability. Avoid clever hacks, deep inheritance, and over-engineering. Code should be easy to reason about and fix.
- **Feature Modularity**: All new features must be modularized. Use a feature-first structure (e.g., `src/features/feature_name/`) and avoid monolithic or tangled code. Each feature should encapsulate its own domain, application, and infrastructure logic.
- **Dependency Injection (DI) & Container**: All dependencies (services, repositories, agents, etc.) must be injected via a DI container. No direct instantiation or singleton patterns. This is critical for decoupling, testability, and maintainability.
- **Clean Architecture Dependency Rules**: Dependencies must only point inwards. Presentation → Application → Domain. Infrastructure implements interfaces defined in Application/Domain. No domain code should ever import from another layer.
- **Service Interfaces**: All services must implement interfaces defined in `src/services/interfaces/`. This enables DI, easy testing, contract enforcement, and maintainability.
- **Testable, Clean Code**: All code must be easily testable. Avoid tight coupling, global state, and hidden dependencies. Use composition over inheritance. Write code that is easy to mock and verify in tests.
- **Code Reviews**: All code reviews must check for architectural violations, complexity creep, and testability issues.

---

# (Original content follows)

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