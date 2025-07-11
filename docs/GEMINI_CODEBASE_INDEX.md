# KICKAI Codebase Index (for Gemini)

This document provides a structured overview of the KICKAI codebase for the Gemini CLI agent.

## 1. Project Overview

-   **Purpose**: A Python-based Telegram bot for managing football teams.
-   **Core Technologies**:
    -   Python 3.11
    -   `python-telegram-bot`
    -   Firebase (Firestore)
    -   CrewAI
    -   `pytest`

## 2. Key Directories

-   `src/`: Main application source code.
    -   `agents/`: CrewAI agent definitions.
    -   `core/`: Core utilities, configuration, logging.
    -   `database/`: Firebase client and data models.
    -   `domain/`: Business logic and service adapters.
    -   `services/`: Application services (player, team, payment, etc.).
    -   `telegram/`: Telegram-specific command handlers and message processing.
    -   `testing/`: E2E testing framework.
-   `tests/`: Unit and integration tests.
-   `config/`: Environment-specific configurations (`bot_config.*.json`).
-   `scripts/`: Helper and automation scripts.

## 3. Core Files & Entrypoints

-   `run_telegram_bot.py`: Main entry point for running the bot.
-   `src/main.py`: Main application logic.
-   `src/telegram/unified_command_system.py`: Central command router.
-   `src/core/bot_config_manager.py`: Manages bot configuration.
-   `src/database/firebase_client.py`: Firebase database connection.
-   `requirements.txt`: Project dependencies.
-   `GEMINI.md`: Project context for Gemini.

## 4. Key Architectural Concepts

-   **Modular Design**: Code is separated into distinct services and domains.
-   **Unified Command System**: A single entry point for all bot commands, simplifying routing and handling.
-   **Service-Oriented**: Functionality is encapsulated in services (e.g., `PlayerService`, `PaymentService`).
-   **Agentic System**: Uses CrewAI for orchestrating more complex, intelligent tasks.
-   **Configuration Management**: Environment-specific settings are loaded from `config/` directory.

## 5. How to...

-   **Run the bot**: `python run_telegram_bot.py`
-   **Run tests**: `pytest`
-   **Install dependencies**: `pip install -r requirements.txt`
-   **Check code quality**: `black .`, `isort .`, `flake8 .`, `mypy src/`

This index will be my primary reference for understanding the codebase. I will update it as I make changes to the project structure.
