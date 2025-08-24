# Environment Setup - Configuration & Dependencies

## Required Setup
```bash
# 1. Python 3.11+ (MANDATORY)
python3.11 check_python_version.py
source venv311/bin/activate

# 2. Environment variables (.env file)
AI_PROVIDER=groq
KICKAI_INVITE_SECRET_KEY=test-invite-secret-key-for-testing-only  
FIREBASE_PROJECT_ID=<your_project>
FIREBASE_CREDENTIALS_FILE=credentials/<file>.json

# 3. Dependencies
pip install -r requirements.txt
pip install -r requirements-local.txt
```

## Environment Variables
Create `.env` file in project root:

```bash
# Core Configuration
AI_PROVIDER=groq
KICKAI_INVITE_SECRET_KEY=test-invite-secret-key-for-testing-only

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials_testing.json

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_USER_ID=your-admin-id

# Development Settings
PYTHONPATH=.
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Python Version Requirements
**MANDATORY: Python 3.11+**

```bash
# Check Python version
python3.11 --version
# Should output: Python 3.11.x or higher

# Activate virtual environment
source venv311/bin/activate

# Verify in Python
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
```

## Dependencies Overview

### Core Dependencies (`requirements.txt`)
- **CrewAI**: Multi-agent orchestration framework
- **Firebase**: Database and cloud services
- **FastAPI**: Web framework for API endpoints
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI

### Development Dependencies (`requirements-local.txt`)
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **mypy**: Type checking
- **pre-commit**: Git hooks for code quality

## Configuration Files
```
config/
├── agents.yaml              # Agent definitions and tools
├── tasks.yaml              # CrewAI task templates
├── command_routing.yaml    # Command-to-agent routing
├── bot_config.example.json # Telegram bot configuration template
└── nlp_prompts.yaml       # NLP processor prompts

credentials/
├── firebase_credentials_template.json
├── firebase_credentials_testing.json
└── firebase_credentials_production.json
```

## Development Startup Checklist
1. ✅ Python 3.11+ installed and activated
2. ✅ Virtual environment (`venv311`) created and activated
3. ✅ Dependencies installed (`pip install -r requirements.txt requirements-local.txt`)
4. ✅ Environment variables configured (`.env` file)
5. ✅ Firebase credentials configured
6. ✅ System health check passes (`PYTHONPATH=. python scripts/run_health_checks.py`)
7. ✅ Clean Architecture structure validated (tools discoverable from `application/tools/`)

## Quick Development Start
```bash
# Complete setup in one command sequence
cd /path/to/KICKAI
source venv311/bin/activate
pip install -r requirements.txt -r requirements-local.txt
cp env.example .env
# Edit .env with your configuration
make dev
```

## Troubleshooting Environment Issues
- **Import errors**: Ensure `PYTHONPATH=.` is set
- **Python version errors**: Must use Python 3.11+ with `venv311`
- **Firebase errors**: Check credentials file path and permissions
- **Container initialization errors**: Run health checks to identify specific issues