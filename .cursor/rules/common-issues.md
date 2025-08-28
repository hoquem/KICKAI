# Common Issues and Solutions for KICKAI Development

**Version**: 3.1 | **Last Updated**: January 2025 | **Troubleshooting**: Production-Ready Solutions

This document provides comprehensive troubleshooting guidance for common issues encountered during KICKAI development.

## 🚨 Critical System Issues

### 1. Tool Not Found / Tool Registry Issues

**Symptoms:**
- `Tool 'tool_name' not found in registry`
- Agent execution fails with tool discovery errors
- Empty tool registry on startup

**Root Causes & Solutions:**

**A. Tool Not Exported from Feature:**
```bash
# Check feature __init__.py
cat kickai/features/[feature]/__init__.py

# Should contain:
from .application.tools.tool_name import tool_name
__all__ = ['tool_name']
```

**Solution:**
```python
# Add to kickai/features/[feature]/__init__.py
from .application.tools.player_tools import get_player_status, update_player_field
__all__ = ['get_player_status', 'update_player_field']
```

**B. Import Path Issues:**
```bash
# Always use PYTHONPATH=.
PYTHONPATH=. python run_bot_local.py

# Verify tool discovery
PYTHONPATH=. python -c "
from kickai.agents.tool_registry import initialize_tool_registry
registry = initialize_tool_registry()
print(f'Tools loaded: {len(registry.get_all_tools())}')
print(f'Available tools: {list(registry.get_all_tools().keys())[:10]}')
"
```

**C. Container Initialization Issues:**
```bash
# Test container initialization
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized()
print('✅ Container initialized successfully')
"
```

### 2. Async/Await Execution Problems

**Symptoms:**
- `RuntimeError: This event loop is already running`
- `coroutine was never awaited`
- Tools hanging or timing out

**Root Causes & Solutions:**

**A. Missing async def:**
```python
# ❌ WRONG
@tool("my_tool")
def my_tool(params):  # Missing async
    result = await some_operation()  # Can't await in sync function

# ✅ CORRECT
@tool("my_tool")
async def my_tool(params):  # Must be async def
    result = await some_operation()
    return result
```

**B. Nested Event Loop Issues:**
```python
# ❌ WRONG
async def tool_function():
    # Don't use asyncio.run() inside already async context
    result = asyncio.run(some_async_operation())

# ✅ CORRECT
async def tool_function():
    # Just await directly
    result = await some_async_operation()
```

**C. CrewAI Async Compatibility:**
```python
# ✅ CORRECT CrewAI async tool pattern
@tool("async_tool", result_as_answer=True)
async def async_tool(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """CrewAI automatically handles async tools."""
    try:
        result = await domain_function(telegram_id, team_id, username, chat_type)
        return result
    except Exception as e:
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### 3. Database Connection and Firebase Issues

**Symptoms:**
- `ServiceUnavailable: Firebase service not available`
- `PermissionDenied: Insufficient permissions`
- Database operations timing out

**Root Causes & Solutions:**

**A. Credentials Configuration:**
```bash
# Check credentials exist
ls -la credentials/firebase_credentials_*.json

# Verify environment variables
echo $FIREBASE_CREDENTIALS_FILE
echo $FIREBASE_PROJECT_ID
```

**B. Network and Permissions:**
```bash
# Test Firebase connectivity
PYTHONPATH=. python -c "
from kickai.core.dependency_container import get_container
container = get_container()
database = container.get_database()
print('✅ Firebase connection successful')
"
```

**C. Async Database Operations:**
```python
# ✅ CORRECT async Firebase pattern
async def get_player_data(telegram_id: int, team_id: str):
    try:
        database = get_container().get_database()
        doc_ref = database.collection('players').document(f"{team_id}_{telegram_id}")
        doc = await doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
```

## 🔧 Development Workflow Issues

### 4. Python Version and Environment Issues

**Symptoms:**
- `ModuleNotFoundError` for installed packages
- Syntax errors with modern Python features
- Virtual environment activation issues

**Root Causes & Solutions:**

**A. Wrong Python Version:**
```bash
# Check Python version (must be 3.11+)
python --version

# Use correct virtual environment
source venv311/bin/activate
python --version  # Should show 3.11+
```

**B. Virtual Environment Issues:**
```bash
# Recreate virtual environment if needed
rm -rf venv311/
python3.11 -m venv venv311
source venv311/bin/activate
pip install -r requirements.txt
```

**C. Package Installation Issues:**
```bash
# Clean install
pip cache purge
pip uninstall -y -r requirements.txt
pip install --no-cache-dir -r requirements.txt
```

### 5. Import and Module Resolution Issues

**Symptoms:**
- `ModuleNotFoundError: No module named 'kickai'`
- Relative import errors
- Circular import detection

**Root Causes & Solutions:**

**A. Missing PYTHONPATH:**
```bash
# Always use PYTHONPATH=. for local development
PYTHONPATH=. python run_bot_local.py
PYTHONPATH=. python -m pytest tests/unit/
PYTHONPATH=. python scripts/run_health_checks.py
```

**B. Absolute vs Relative Imports:**
```python
# ✅ CORRECT - Always use absolute imports
from kickai.features.player_registration.domain.entities.player import Player
from kickai.core.enums import MemberStatus

# ❌ WRONG - Never use relative imports
from .domain.entities.player import Player
from ..core.enums import MemberStatus
```

**C. Circular Import Resolution:**
```python
# ✅ CORRECT - Use TYPE_CHECKING for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kickai.features.player_registration.domain.entities.player import Player

def process_player(player: 'Player') -> str:
    # Function implementation
    pass
```

### 6. Testing and Mock Issues

**Symptoms:**
- Tests failing with database connection errors
- Mocks not working as expected
- Test isolation problems

**Root Causes & Solutions:**

**A. Test Environment Setup:**
```bash
# Ensure test environment variables
export KICKAI_TESTING=true
export FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials_testing.json

# Run tests with proper path
PYTHONPATH=. python -m pytest tests/unit/ -v
```

**B. Mock Configuration:**
```python
# ✅ CORRECT mock setup for async functions
@pytest.fixture
def mock_player_service():
    service = AsyncMock()
    service.get_player_by_telegram_id.return_value = test_player
    return service

@pytest.mark.asyncio
async def test_with_mock(mock_player_service):
    result = await service.get_player_status(123456789, "TEST")
    mock_player_service.get_player_by_telegram_id.assert_called_once()
```

**C. Test Data Cleanup:**
```python
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Automatically clean up test data after each test."""
    yield
    # Cleanup logic here
    await cleanup_test_players()
    await cleanup_test_teams()
```

## 📱 Telegram Bot and API Issues

### 7. Telegram Bot API Issues

**Symptoms:**
- Bot not responding to commands
- `Unauthorized: Bot token invalid`
- Rate limiting errors

**Root Causes & Solutions:**

**A. Bot Token Configuration:**
```bash
# Check bot token configuration
echo $TELEGRAM_BOT_TOKEN

# Test bot token validity
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

**B. Webhook vs Polling Issues:**
```bash
# For local development, ensure no webhook is set
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/deleteWebhook"

# Start local bot with polling
PYTHONPATH=. python run_bot_local.py
```

**C. Rate Limiting Handling:**
```python
# ✅ CORRECT rate limiting implementation
import asyncio
from functools import wraps

def rate_limit(calls_per_second=1):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                await asyncio.sleep(left_to_wait)
            ret = await func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
```

### 8. Message Routing and Command Processing

**Symptoms:**
- Commands not routing to correct agents
- NLP processing errors
- Response formatting issues

**Root Causes & Solutions:**

**A. Command Routing Configuration:**
```yaml
# Check config/command_routing.yaml
commands:
  "/update":
    agent: "PLAYER_COORDINATOR"
    permissions: ["PLAYER", "LEADERSHIP"]
    chat_types: ["main", "leadership", "private"]
```

**B. Agent Tool Assignment:**
```yaml
# Check config/agents.yaml
PLAYER_COORDINATOR:
  tools:
    - "update_player_field"
    - "get_player_info" 
    - "get_my_status"
```

**C. NLP Processing Validation:**
```bash
# Test NLP processor functionality
PYTHONPATH=. python -c "
from kickai.agents.nlp_processor import advanced_intent_recognition
result = advanced_intent_recognition(
    message='I want to update my position',
    telegram_id=123456789,
    team_id='TEST',
    username='testuser',
    chat_type='main'
)
print(f'Intent analysis: {result}')
"
```

## 🧪 Testing and Validation Issues

### 9. Mock Telegram UI Issues

**Symptoms:**
- Mock UI not loading (localhost:8001)
- API integration failures
- User switching not working

**Root Causes & Solutions:**

**A. Mock UI Startup:**
```bash
# Start mock Telegram UI
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py

# Check if service is running
curl -s http://localhost:8001/health
```

**B. API Integration:**
```bash
# Test API endpoints
curl -X POST http://localhost:8001/api/send_message \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123456789, "chat_id": 2002, "text": "/help"}'
```

**C. Backend Bot Integration:**
```bash
# Verify bot integration
PYTHONPATH=. python tests/mock_telegram/backend/bot_integration.py
```

### 10. Health Check and System Validation Issues

**Symptoms:**
- Health checks failing
- System startup validation errors
- Service discovery issues

**Root Causes & Solutions:**

**A. System Health Validation:**
```bash
# Run comprehensive health checks
PYTHONPATH=. python scripts/run_health_checks.py

# Check specific components
PYTHONPATH=. python -c "
from kickai.core.startup_validation.validator import SystemValidator
validator = SystemValidator()
result = validator.run_all_checks()
print(f'Health status: {result.overall_status}')
"
```

**B. Service Discovery:**
```bash
# Test service registration
PYTHONPATH=. python -c "
from kickai.core.dependency_container import get_container
container = get_container()
services = container.list_services()
print(f'Registered services: {services}')
"
```

## 📋 Quick Diagnostic Commands

### System Health Check

```bash
#!/bin/bash
echo "🔍 KICKAI System Diagnostic"
echo "=========================="

echo "1. Python Version Check:"
python --version

echo "2. Environment Setup:"
echo "PYTHONPATH: $PYTHONPATH"
echo "Current directory: $(pwd)"

echo "3. Container Initialization:"
PYTHONPATH=. python -c "
try:
    from kickai.core.dependency_container import ensure_container_initialized
    ensure_container_initialized()
    print('✅ Container: SUCCESS')
except Exception as e:
    print(f'❌ Container: {e}')
"

echo "4. Tool Registry:"
PYTHONPATH=. python -c "
try:
    from kickai.agents.tool_registry import initialize_tool_registry
    registry = initialize_tool_registry()
    print(f'✅ Tools: {len(registry.get_all_tools())} loaded')
except Exception as e:
    print(f'❌ Tools: {e}')
"

echo "5. Database Connection:"
PYTHONPATH=. python -c "
try:
    from kickai.core.dependency_container import get_container
    container = get_container()
    database = container.get_database()
    print('✅ Database: SUCCESS')
except Exception as e:
    print(f'❌ Database: {e}')
"

echo "6. Agent System:"
PYTHONPATH=. python -c "
try:
    from kickai.agents.crew_agents import TeamManagementSystem
    system = TeamManagementSystem('TEST')
    print('✅ Agents: SUCCESS')
except Exception as e:
    print(f'❌ Agents: {e}')
"
```

### Emergency Recovery Commands

```bash
# Clean restart procedure
echo "🚑 Emergency Recovery Procedure"
echo "=============================="

# 1. Stop all processes
pkill -f "python.*run_bot"
pkill -f "python.*mock_tester"

# 2. Clean Python cache
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 3. Reset virtual environment if needed
source venv311/bin/activate

# 4. Reinstall dependencies if needed
pip install --no-deps --force-reinstall -r requirements.txt

# 5. Run system validation
PYTHONPATH=. python scripts/run_health_checks.py

# 6. Start services
PYTHONPATH=. python run_bot_local.py &
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py &

echo "✅ Recovery procedure complete"
```

### Performance Monitoring

```bash
# Monitor system performance
echo "📊 Performance Monitoring"
echo "======================="

# Memory usage
ps aux | grep python | grep -E "(run_bot|mock_tester)"

# Database connection health
PYTHONPATH=. python -c "
import time
from kickai.core.dependency_container import get_container

start = time.time()
container = get_container()
database = container.get_database()
end = time.time()

print(f'Database connection time: {(end-start)*1000:.2f}ms')
"

# Tool registry performance
PYTHONPATH=. python -c "
import time
from kickai.agents.tool_registry import initialize_tool_registry

start = time.time()
registry = initialize_tool_registry()
tools = registry.get_all_tools()
end = time.time()

print(f'Tool registry load time: {(end-start)*1000:.2f}ms')
print(f'Total tools loaded: {len(tools)}')
"
```

---

**Status**: Production-Ready Troubleshooting  
**Coverage**: Critical Issues and Emergency Recovery  
**Maintenance**: Updated with Latest System Changes