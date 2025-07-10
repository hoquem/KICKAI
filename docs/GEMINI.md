# Project Overview for Gemini

This document provides essential information for the Gemini CLI agent to effectively understand, navigate, and contribute to the `KICKAI` project.

## 1. Project Type and Technologies

- **Primary Language:** Python 3.11
- **Frameworks/Libraries:**
    - Telegram Bot API (via `python-telegram-bot`)
    - Firebase (via `firebase-admin`)
    - CrewAI (for agent orchestration)
    - `pytest` for testing
    - `pre-commit` for code quality hooks
- **Database:** Firebase (Firestore)
- **Key Concepts:** Modular architecture, service-oriented design, agent-based systems, unified command system.

## 2. Core Commands

These are the essential commands for setting up, running, testing, and maintaining the project.

### 2.1. Setup

- **Install Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
- **Set up Local Environment:**
  ```bash
  python setup_local_environment.py
  ```
- **Generate Telegram Session (if needed):**
  ```bash
  python generate_session.py
  ```
- **Validate Setup:**
  ```bash
  python validate_setup.py
  ```

### 2.2. Running the Application

- **Run Telegram Bot (Resilient Mode):**
  ```bash
  python run_telegram_bot_resilient.py
  ```
- **Run Telegram Bot (Standard Mode):**
  ```bash
  python run_telegram_bot.py
  ```

### 2.3. Testing

- **Run All Tests:**
  ```bash
  pytest
  ```
- **Run E2E Tests:**
  ```bash
  python run_e2e_tests.py
  ```
- **Run Specific Test File (Example):**
  ```bash
  pytest tests/test_core/test_bot_config_manager.py
  ```

### 2.4. Code Quality and Standards

The project uses `pre-commit` hooks to enforce code quality. These are the commands used by the hooks:

- **Format Code (Black):**
  ```bash
  black .
  ```
- **Sort Imports (isort):**
  ```bash
  isort .
  ```
- **Linting (flake8):**
  ```bash
  flake8 .
  ```
- **Type Checking (mypy):**
  ```bash
  mypy src/
  ```
- **Security Scan (Bandit):**
  ```bash
  bandit -r src -f json -o bandit-report.json
  ```
- **Architectural Checks (Custom Scripts):**
    - `python scripts/check_architectural_imports.py`
    - `python scripts/check_circular_imports.py`
    - `python scripts/check_in_function_imports.py`
- **Docstring Style (pydocstyle):**
  ```bash
  pydocstyle src/
  ```
- **Unused Code (Vulture):**
  ```bash
  vulture src --min-confidence 80
  ```
- **Cyclomatic Complexity (mccabe):**
  ```bash
  mccabe .
  ```
- **Pylint:**
  ```bash
  pylint src/
  ```

It's recommended to run `pre-commit install` to set up these hooks to run automatically before each commit.

## 3. Directory Structure

- `src/`: Contains the main application source code.
    - `agents/`: Logic for intelligent agents and CrewAI integration.
    - `core/`: Core utilities, configuration management, and exceptions.
    - `database/`: Database interaction logic (Firebase client, models, interfaces).
    - `domain/`: Business logic, command operations, and adapters for external services.
    - `services/`: Application services (e.g., payment, player management, access control).
    - `tasks/`: Definitions for various tasks the bot can perform.
    - `telegram/`: Telegram bot specific handlers, commands, and message processing.
    - `testing/`: E2E testing framework components.
    - `tools/`: Utility tools for agents.
    - `utils/`: General utility functions (ID generation, LLM client).
- `tests/`: Unit and integration tests, mirroring the `src/` structure.
- `config/`: Configuration files for different environments.
- `scripts/`: Helper scripts (deployment, migration, utility).
- `credentials/`: (Sensitive) Credentials and session files.
- `examples/`: Example usage of service interfaces.
- `docs/`: (If present) Project documentation.
- `e2e_reports/`: (If present) E2E test reports.

## 4. Coding Conventions and Architectural Patterns

- **Python Style:** Adherence to PEP 8, enforced by Black and flake8.
- **Import Sorting:** Enforced by isort.
- **Type Hinting:** Strongly encouraged and enforced by mypy.
- **Docstrings:** Google style docstrings are preferred, enforced by pydocstyle.
- **Modular Design:** Code is organized into logical modules and services to promote separation of concerns.
- **Dependency Injection:** Used where appropriate to manage dependencies between services.
- **Unified Command System:** A central system for handling and routing commands across different interfaces.
- **Error Handling:** Centralized exception handling where possible.

## 5. Deployment

- **CI/CD:** GitHub Actions workflows are used for continuous integration and deployment to various environments (staging, production). Refer to `.github/workflows/` for details.
- **Deployment Scripts:** Located in `scripts/` (e.g., `deploy-production.sh`).

## 6. Important Notes for Gemini

- **Context is Key:** Always try to understand the surrounding code and existing patterns before making changes.
- **Test Coverage:** Prioritize writing or updating tests when implementing new features or fixing bugs.
- **Configuration:** Be aware of the different `bot_config.*.json` files in the `config/` directory for environment-specific settings.
- **Sensitive Information:** Never hardcode sensitive information (API keys, tokens) directly into the code. Use environment variables or secure configuration management.
- **User Confirmation:** For significant changes or commands that modify the file system, always explain the action and seek confirmation.
