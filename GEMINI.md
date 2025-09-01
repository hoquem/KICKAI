# KICKAI - AI-Powered Football Team Management System

## Project Overview

KICKAI is a sophisticated, AI-powered football team management system designed for Telegram. It leverages a 5-agent CrewAI native collaboration architecture, adhering to Clean Architecture principles for a modular, scalable, and maintainable codebase. The system is built in Python 3.11 and utilizes Firebase/Firestore for its database.

The core of KICKAI is its multi-agent system, where each agent has a specialized role:

*   **MESSAGE_PROCESSOR**: The primary interface for user interactions, with native LLM routing intelligence.
*   **HELP_ASSISTANT**: Provides help and guidance to users.
*   **PLAYER_COORDINATOR**: Manages player registration and status.
*   **TEAM_ADMINISTRATOR**: Handles team member management and administration.
*   **SQUAD_SELECTOR**: Manages matches, player availability, and squad selection.

Command routing is handled via pure CrewAI agent collaboration, with the `MESSAGE_PROCESSOR` agent taking the lead in understanding user intent.

## Building and Running

The project uses a `Makefile` for common development tasks.

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/KICKAI.git
    cd KICKAI
    ```
2.  **Set up the Python environment:**
    ```bash
    python3.11 -m venv venv311
    source venv311/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-local.txt
    ```
4.  **Configure environment variables:**
    ```bash
    cp .env.example .env
    # Edit .env with your credentials
    ```

### Running the Bot

*   **Run the bot locally:**
    ```bash
    make dev
    ```
*   **Run the mock Telegram UI for testing:**
    ```bash
    PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
    # Access at: http://localhost:8001
    ```

### Running Tests

*   **Run all tests:**
    ```bash
    make test
    ```
*   **Run specific test types:**
    ```bash
    make test-unit
    make test-integration
    make test-e2e
    ```

### Linting

*   **Run the linter:**
    ```bash
    make lint
    ```

## Development Conventions

### Clean Architecture

KICKAI follows the principles of Clean Architecture, separating the code into distinct layers within each feature:

*   **Domain**: Pure business logic, with no framework dependencies. Located in `kickai/features/*/domain`.
*   **Application**: CrewAI tools that delegate to the domain layer. Located in `kickai/features/*/application`.
*   **Infrastructure**: Database and external service integrations. Located in `kickai/database` and `kickai/infrastructure`.
*   **Presentation**: The Telegram bot interface.

### Testing

The project has a comprehensive testing strategy, including:

*   **Unit tests**: `tests/unit`
*   **Integration tests**: `tests/integration`
*   **End-to-end (E2E) tests**: `tests/e2e`

### Code Style

The project uses `ruff` for linting and formatting, and `mypy` for type checking. The configuration for these tools can be found in the `pyproject.toml` file.
