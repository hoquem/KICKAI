# Development Environment Setup Guide

## 🎯 Overview

This guide provides a complete setup for local development of KICKAI using mock services and local tools. This approach ensures fast development cycles, consistent testing, and isolation from external dependencies.

## 🏗️ Development Architecture

### Mock vs Real Services Strategy

| Service | Development Default | When to Use Real | Benefits |
|---------|-------------------|------------------|----------|
| **Database** | Mock DataStore | Firestore integration testing | Fast, consistent, isolated |
| **Telegram** | Mock Client | Bot behavior testing | No tokens needed, controlled scenarios |
| **AI** | Mock/Local Ollama | AI response testing | Fast, no API costs, consistent |
| **Payment** | Mock Gateway | Payment flow testing | No real transactions, controlled testing |

## 🔧 Step 1: Local Environment Setup

### Prerequisites

```bash
# Required software
- Python 3.11+
- Git
- Virtual environment tool (venv, conda, etc.)
- Docker (optional, for Ollama)
```

### Initial Setup

```bash
# Clone repository
git clone https://github.com/your-org/KICKAI.git
cd KICKAI

# Create virtual environment
python -m venv venv311
source venv311/bin/activate  # On Windows: venv311\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-local.txt

# Set up pre-commit hooks
pre-commit install
```

## 🔧 Step 2: Environment Configuration

### Development Environment Variables

Create `.env.development`:

```bash
# Core Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Mock Services Configuration
USE_MOCK_DATASTORE=true
USE_MOCK_TELEGRAM=true
USE_MOCK_AI=true
USE_MOCK_PAYMENT=true

# AI Configuration (for when using real AI)
AI_PROVIDER=mock  # or 'ollama' or 'google_gemini'
AI_MODEL_NAME=mock-model

# Optional: Real Services for Integration Testing
# FIRESTORE_PROJECT_ID=your-dev-firestore-id
# TELEGRAM_BOT_TOKEN=your-dev-bot-token
# GOOGLE_API_KEY=your-google-api-key

# Application Configuration
DEFAULT_TEAM_ID=KAI
PAYMENT_ENABLED=false

# Development-specific
PYTHONPATH=src
TESTING=true
```

### Load Development Environment

```bash
# Load environment variables
export $(cat .env.development | xargs)

# Or use a tool like direnv
echo "export $(cat .env.development | xargs)" > .envrc
direnv allow
```

## 🔧 Step 3: Mock Services Configuration

### Mock DataStore Setup

The Mock DataStore is automatically used when `USE_MOCK_DATASTORE=true`. It provides:

- In-memory data storage
- Consistent test data
- No external dependencies
- Fast operations

```python
# Example: Using Mock DataStore in development
from database.mock_data_store import MockDataStore

# Mock DataStore is automatically configured
data_store = MockDataStore()

# Add test data
await data_store.create_player(test_player)
```

### Mock Telegram Client Setup

The Mock Telegram client simulates Telegram interactions:

```python
# Example: Using Mock Telegram in development
from bot_telegram.mock_client import MockTelegramClient

# Mock client is automatically configured
client = MockTelegramClient()

# Simulate message
await client.send_message(chat_id="-1001234567890", text="/start")
```

### Mock AI Setup

For AI responses, use mock responses or local Ollama:

```python
# Example: Mock AI responses
from utils.llm_factory import get_llm_client

# Mock AI is automatically configured
llm_client = get_llm_client()

# Get mock response
response = await llm_client.generate_response("What is my phone number?")
```

## 🔧 Step 4: Local Development Workflow

### Development Branch Strategy

```bash
# Start from development branch
git checkout development

# Create feature branch
git checkout -b feature/new-feature

# Make changes and test locally
python -m pytest tests/unit/features/your-feature/ -v

# Run integration tests
python -m pytest tests/integration/features/your-feature/ -v

# Run E2E tests (if needed)
python run_e2e_tests.py --suite=smoke

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request to development branch
```

### Local Testing Strategy

#### Unit Tests (Always use mocks)
```bash
# Run unit tests with mocks
python -m pytest tests/unit/ -v

# Run specific feature tests
python -m pytest tests/unit/features/player_registration/ -v

# Run with coverage
python -m pytest tests/unit/ --cov=src --cov-report=html
```

#### Integration Tests (Use mocks by default)
```bash
# Run integration tests
python -m pytest tests/integration/ -v

# Run with real services (optional)
USE_MOCK_DATASTORE=false python -m pytest tests/integration/ -v
```

#### E2E Tests (Use mocks by default)
```bash
# Run E2E tests with mocks
python run_e2e_tests.py --suite=smoke

# Run with real services (optional)
USE_MOCK_TELEGRAM=false python run_e2e_tests.py --suite=smoke
```

## 🔧 Step 5: Integration Testing Setup

### When to Use Real Services

Use real services for:
- Firestore integration testing
- Telegram bot behavior testing
- AI response validation
- Payment flow testing

### Integration Testing Environment

Create `.env.development.integration`:

```bash
# Core Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Real Services Configuration
USE_MOCK_DATASTORE=false
USE_MOCK_TELEGRAM=false
USE_MOCK_AI=false
USE_MOCK_PAYMENT=false

# Real Service Credentials
FIRESTORE_PROJECT_ID=your-dev-firestore-id
TELEGRAM_BOT_TOKEN=your-dev-bot-token
GOOGLE_API_KEY=your-google-api-key

# AI Configuration
AI_PROVIDER=google_gemini
AI_MODEL_NAME=gemini-pro

# Application Configuration
DEFAULT_TEAM_ID=KAI
PAYMENT_ENABLED=false
```

### Integration Testing Workflow

```bash
# Load integration environment
export $(cat .env.development.integration | xargs)

# Run integration tests
python -m pytest tests/integration/ -v

# Run E2E tests with real services
python run_e2e_tests.py --suite=smoke
```

## 🔧 Step 6: Local AI Setup (Optional)

### Option 1: Local Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama service
ollama serve

# Update environment
export AI_PROVIDER=ollama
export AI_MODEL_NAME=llama2
```

### Option 2: Google Gemini (Real API)

```bash
# Get API key from Google Cloud Console
export GOOGLE_API_KEY=your-api-key
export AI_PROVIDER=google_gemini
export AI_MODEL_NAME=gemini-pro
```

## 🔧 Step 7: Development Tools

### Code Quality Tools

```bash
# Run linting
python -m flake8 src/
python -m black src/
python -m isort src/

# Run type checking
python -m mypy src/

# Run all quality checks
make lint
```

### Testing Tools

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test types
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python run_e2e_tests.py --suite=smoke
```

### Development Scripts

```bash
# Validate feature deployment
python scripts/validate_feature_deployment.py --feature=player_registration

# Run health checks
python scripts/run_health_checks.py

# Bootstrap team (for integration testing)
python scripts/bootstrap_team.py --environment=development
```

## 🔧 Step 8: Debugging and Troubleshooting

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug logging
python run_bot_local.py
```

### Common Issues

#### Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src

# Check imports
python -c "from src.core.dependency_container import get_container; print('OK')"
```

#### Mock Service Issues
```bash
# Verify mock configuration
python -c "from src.database.mock_data_store import MockDataStore; print('Mock OK')"

# Check environment variables
echo $USE_MOCK_DATASTORE
echo $USE_MOCK_TELEGRAM
```

#### Test Failures
```bash
# Run tests with verbose output
python -m pytest tests/ -v -s

# Run specific failing test
python -m pytest tests/unit/test_specific.py::test_function -v -s
```

## 🔧 Step 9: Performance Optimization

### Development Performance

#### Mock Service Performance
- Mock services are in-memory and very fast
- No network latency
- Consistent response times

#### Local AI Performance
- Ollama runs locally (no network latency)
- Gemini API has network latency but is fast
- Mock AI is instant

### Memory Management

```bash
# Monitor memory usage
python -c "import psutil; print(psutil.virtual_memory().percent)"

# Profile memory usage
python -m memory_profiler your_script.py
```

## 🔧 Step 10: Best Practices

### Development Workflow

1. **Always start with mocks** for new development
2. **Use real services** only when testing integration
3. **Write tests** for all new features
4. **Run quality checks** before committing
5. **Test locally** before pushing to remote

### Code Organization

1. **Feature-based development** in `src/features/`
2. **Clean architecture** principles
3. **Dependency injection** for all services
4. **Comprehensive testing** at all levels

### Environment Management

1. **Separate environments** for different purposes
2. **Environment-specific** configuration files
3. **Never commit secrets** to version control
4. **Use .env files** for local configuration

## 📚 Additional Resources

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Ollama Documentation](https://ollama.ai/docs)
- [Google Gemini API](https://ai.google.dev/docs)

## 🆘 Support

### Common Commands

```bash
# Quick setup
make setup-dev

# Run all tests
make test

# Run quality checks
make lint

# Start development server
make dev

# Clean up
make clean
```

### Getting Help

1. Check the troubleshooting section above
2. Review the logs with debug mode enabled
3. Run validation scripts
4. Check the [README.md](README.md) for additional information 