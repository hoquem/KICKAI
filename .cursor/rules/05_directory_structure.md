# Directory Structure

The following directory structure is mandatory and must be adhered to.

```text
KICKAI/
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
│   ├── agents/                   # AI Agent System
│   │   ├── crew_agents.py       # 10-agent CrewAI definitions
│   │   ├── capabilities.py      # Agent capability definitions
│   │   └── __init__.py          # Agent system initialization
│   │
│   ├── core/                     # Core System Components
│   │   ├── improved_config_system.py # Advanced configuration management
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── bot_config_manager.py # Bot configuration management
│   │
│   ├── services/                 # Business Logic Layer
│   │   ├── player_service.py    # Player management service
│   │   ├── team_service.py      # Team management service
│   │   ├── daily_status_service.py # Daily status reports
│   │   ├── fa_registration_checker.py # FA registration checking
│   │   ├── reminder_service.py  # Automated reminder system
│   │   ├── background_tasks.py  # Scheduled operations
│   │   ├── message_routing_service.py # Message handling
│   │   ├── team_member_service.py # Team membership management
│   │   ├── payment_service.py   # Payment processing
│   │   ├── financial_report_service.py # Financial reporting
│   │   ├── expense_service.py   # Expense management
│   │   ├── match_service.py     # Match management
│   │   ├── access_control_service.py # Access control
│   │   ├── monitoring.py        # System monitoring
│   │   ├── bot_status_service.py # Bot status management
│   │   ├── multi_team_manager.py # Multi-team management
│   │   ├── stripe_payment_gateway.py # Stripe integration
│   │   ├── interfaces/          # Service interfaces
│   │   └── mocks/               # Mock services for testing
│   │
│   ├── telegram/                 # Telegram Integration
│   │   ├── unified_command_system.py # Unified command architecture
│   │   ├── player_registration_handler.py # Advanced player onboarding
│   │   ├── unified_message_handler.py # Message processing and routing
│   │   ├── onboarding_handler_improved.py # Improved onboarding
│   │   ├── payment_commands.py  # Payment command handlers
│   │   ├── player_commands.py   # Player command handlers
│   │   └── match_commands.py    # Match command handlers
│   │
│   ├── database/                 # Database Layer
│   │   ├── firebase_client.py   # Firebase client
│   │   ├── models_improved.py   # Improved data models
│   │   └── interfaces.py        # Database interfaces
│   │
│   ├── tools/                    # LangChain Tools
│   │   └── payment_tools.py     # Payment tools
│   │
│   ├── tasks/                    # Task Definitions
│   │   └── __init__.py          # Task package initialization
│   │
│   ├── utils/                    # Utilities
│   │   ├── id_generator.py      # Human-readable ID generation
│   │   ├── llm_client.py        # LLM client utilities
│   │   ├── llm_intent.py        # LLM intent processing
│   │   └── __init__.py          # Utils package
│   │
│   └── main.py                   # Application Entry Point
│
├── tests/                        # Test Suite
│   ├── test_agents/             # Agent system tests
│   ├── test_core/               # Core component tests
│   ├── test_integration/        # Integration tests
│   ├── test_services/           # Service layer tests
│   ├── test_telegram/           # Telegram integration tests
│   ├── test_tools/              # Tool tests
│   ├── conftest.py              # Shared test configuration
│   ├── test_models_improved.py  # Model tests
│   ├── test_service_interfaces.py # Service interface tests
│   ├── test_di_integration.py   # Dependency injection tests
│   └── test_mock_data_store_comprehensive.py # Mock data tests
│
├── config/                       # Configuration Files
├── scripts/                      # Deployment Scripts
├── credentials/                  # Credentials (gitignored)
├── run_telegram_bot.py          # Standard bot runner
├── run_telegram_bot_resilient.py # Resilient bot runner
├── requirements.txt              # Production dependencies
├── requirements-local.txt        # Local development dependencies
└── README.md                     # Project documentation