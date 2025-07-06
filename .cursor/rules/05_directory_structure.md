# Directory Structure

The following directory structure is mandatory and must be adhered to.

```text
sunday-league-manager/
├── .cursor/
│   └── rules/
│       ├── 00_project_overview.md
│       ├── 01_architecture.md
│       ├── 02_agentic_design.md
│       ├── 03_technology_stack.md
│       ├── 04_testing_and_quality.md
│       ├── 05_directory_structure.md
│       └── 06_documentation.md
│
├── src/
│   ├── domain/
│   │   ├── models.py         # Pydantic models (Player, Match).
│   │   └── repositories.py   # Abstract repository interfaces (IPlayerRepository).
│   │
│   ├── application/
│   │   ├── services.py       # Abstract service interfaces (INLPService).
│   │   └── use_cases/        # Business logic orchestration (add_player.py).
│   │
│   ├── infrastructure/
│   │   ├── agents/           # CrewAI agent, task, and crew definitions.
│   │   ├── persistence/      # Concrete repositories (json_player_repository.py).
│   │   └── services/         # Concrete services (crewai_nlp_service.py).
│   │
│   ├── presentation/
│   │   └── telegram_bot/
│   │       ├── handlers.py     # Maps Telegram input to application use cases.
│   │       └── bot.py          # Bot initialization and main loop.
│   │
│   └── core/
│       └── container.py      # Dependency Injection container.
│
├── tests/
│   ├── application/
│   └── domain/
│
├── main.py                     # Application entry point.
├── requirements.txt
└── .env