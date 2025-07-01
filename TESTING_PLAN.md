# KICKAI Testing Plan

## 🧪 **Testing Strategy Overview**

KICKAI uses a comprehensive testing strategy with **pytest** framework, **mocked dependencies**, and **isolated test environments**. The testing infrastructure supports the **8-agent CrewAI system**, **Firebase integration**, and **multi-team environments**.

## 🏗️ **Testing Architecture**

### **Test Infrastructure**
```
tests/
├── conftest.py                    # Global test configuration and fixtures
├── test_agents/                   # AI Agent Testing
│   ├── test_crew_agents.py       # 8-agent CrewAI system tests
│   ├── test_handlers.py          # SimpleAgenticHandler tests
│   ├── test_routing.py           # Intelligent routing tests
│   └── test_capabilities.py      # Agent capability tests
├── test_integration/             # Integration Testing
│   ├── test_phase1_integration.py # End-to-end workflow tests
│   ├── test_player_registration.py # Player management tests
│   └── test_onboarding_integration.py # Onboarding workflow tests
├── test_core/                    # Core System Testing
│   ├── test_advanced_memory.py   # Memory system tests
│   ├── test_config.py           # Configuration tests
│   └── test_logging.py          # Logging system tests
├── test_services/                # Service Layer Testing
│   ├── test_player_service.py   # Player service tests
│   ├── test_team_service.py     # Team service tests
│   └── test_monitoring.py       # Monitoring service tests
├── test_tools/                   # LangChain Tools Testing
│   ├── test_firebase_tools.py   # Firebase operations tests
│   ├── test_telegram_tools.py   # Telegram integration tests
│   └── test_team_management_tools.py # Team management tests
└── test_telegram/                # Telegram Integration Testing
    ├── test_telegram_command_handler.py # Command processing tests
    └── test_player_registration_handler.py # Player onboarding tests
```

### **Testing Infrastructure Components**
```
src/testing/
├── test_base.py                  # Base test classes with common setup
├── test_fixtures.py              # Test fixtures and mocks
└── test_utils.py                 # Testing utilities and helpers
```

## 🔧 **Test Categories**

### **1. Unit Tests**
- **Purpose**: Test individual components in isolation
- **Coverage**: >90% code coverage
- **Framework**: pytest with mocking

#### **Agent Tests**
```python
# Test individual agents
def test_message_processing_specialist():
    agent = MessageProcessingSpecialist(team_id="test-team")
    response = agent.process_message("help")
    assert "available commands" in response.lower()

def test_team_manager():
    agent = TeamManager(team_id="test-team")
    response = agent.handle_strategic_request("plan next match")
    assert "strategic" in response.lower()
```

#### **Service Tests**
```python
# Test service layer
def test_player_service():
    service = get_player_service()
    player = service.create_player("John", "123456789")
    assert player.name == "John"
    assert player.phone == "123456789"
```

### **2. Integration Tests**
- **Purpose**: Test component interactions and workflows
- **Coverage**: End-to-end workflow validation
- **Framework**: pytest with Firebase mocking

#### **Player Registration Workflow**
```python
# Test complete player registration workflow
def test_player_registration_workflow():
    # 1. Create player
    player = create_test_player("John", "123456789")
    
    # 2. Generate invite
    invite = generate_invite(player)
    
    # 3. Process onboarding
    onboarding_result = process_onboarding(invite)
    
    # 4. Verify completion
    assert onboarding_result.status == "completed"
```

#### **AI Agent Coordination**
```python
# Test multi-agent coordination
def test_agent_coordination():
    handler = SimpleAgenticHandler(team_id="test-team")
    response = handler.process_message("plan next match with squad selection")
    
    # Verify multiple agents were involved
    assert "match" in response.lower()
    assert "squad" in response.lower()
```

### **3. System Tests**
- **Purpose**: Test complete system functionality
- **Coverage**: Full system validation
- **Framework**: pytest with full environment setup

#### **Telegram Bot Integration**
```python
# Test Telegram bot functionality
def test_telegram_bot_commands():
    bot = create_test_bot()
    
    # Test help command
    response = bot.handle_message("/help")
    assert "available commands" in response
    
    # Test player management
    response = bot.handle_message("add player John with phone 123456789")
    assert "player added" in response.lower()
```

## 🛠️ **Testing Infrastructure**

### **Test Configuration (`conftest.py`)**
```python
import pytest
from unittest.mock import Mock, patch
from src.core.config import get_config
from src.tools.firebase_tools import get_firebase_client

@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return get_config()

@pytest.fixture(scope="function")
def mock_firebase():
    """Mock Firebase client for tests."""
    with patch('src.tools.firebase_tools.get_firebase_client') as mock:
        mock.return_value = Mock()
        yield mock

@pytest.fixture(scope="function")
def mock_telegram():
    """Mock Telegram bot for tests."""
    with patch('src.telegram.telegram_command_handler.Bot') as mock:
        mock.return_value = Mock()
        yield mock

@pytest.fixture(scope="function")
def test_team_id():
    """Provide test team ID."""
    return "test-team-123"

@pytest.fixture(scope="function")
def test_user_id():
    """Provide test user ID."""
    return "test-user-456"
```

### **Base Test Classes (`src/testing/test_base.py`)**
```python
import pytest
from unittest.mock import Mock, patch
from src.core.config import get_config

class BaseTestCase:
    """Base test class with common setup."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_config, mock_firebase, mock_telegram):
        """Setup test environment."""
        self.config = test_config
        self.mock_firebase = mock_firebase
        self.mock_telegram = mock_telegram
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup test data."""
        self.test_team_id = "test-team-123"
        self.test_user_id = "test-user-456"
        self.test_player_data = {
            "name": "John Smith",
            "phone": "123456789",
            "email": "john@example.com",
            "position": "Forward"
        }
    
    def create_mock_player(self, **kwargs):
        """Create a mock player for testing."""
        player_data = self.test_player_data.copy()
        player_data.update(kwargs)
        return Mock(**player_data)
```

### **Test Fixtures (`src/testing/test_fixtures.py`)**
```python
import pytest
from unittest.mock import Mock, patch
from src.agents.crew_agents import create_agents_for_team

@pytest.fixture
def mock_agents():
    """Mock CrewAI agents for testing."""
    with patch('src.agents.crew_agents.create_agents_for_team') as mock:
        agents = [
            Mock(name="MessageProcessor"),
            Mock(name="TeamManager"),
            Mock(name="PlayerCoordinator"),
            Mock(name="MatchAnalyst"),
            Mock(name="CommunicationSpecialist"),
            Mock(name="FinanceManager"),
            Mock(name="SquadSelectionSpecialist"),
            Mock(name="AnalyticsSpecialist")
        ]
        mock.return_value = agents
        yield mock

@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    with patch('src.agents.handlers._create_llm') as mock:
        mock_llm = Mock()
        mock_llm.generate.return_value = "Test response"
        mock.return_value = mock_llm
        yield mock
```

## 📊 **Test Coverage**

### **Coverage Targets**
- **Overall Coverage**: >90%
- **Critical Paths**: 100%
- **AI Components**: >95%
- **Database Operations**: >95%
- **Telegram Integration**: >90%

### **Coverage Report**
```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# View coverage in browser
open htmlcov/index.html
```

### **Coverage Categories**
```python
# Test coverage by category
COVERAGE_TARGETS = {
    "agents": 95,        # AI agent system
    "core": 100,         # Core system components
    "services": 95,      # Business logic layer
    "tools": 95,         # LangChain tools
    "telegram": 90,      # Telegram integration
    "testing": 100,      # Testing infrastructure
}
```

## 🚀 **Test Execution**

### **Running Tests**
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_agents/          # Agent tests
pytest tests/test_integration/     # Integration tests
pytest tests/test_core/           # Core system tests
pytest tests/test_services/       # Service layer tests
pytest tests/test_tools/          # Tools tests
pytest tests/test_telegram/       # Telegram tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_player_registration.py

# Run specific test function
pytest tests/test_player_registration.py::test_create_player
```

### **Test Environment Setup**
```bash
# Install test dependencies
pip install -r requirements-local.txt

# Install testing tools
pip install pytest pytest-cov pytest-mock pytest-asyncio

# Setup test environment
export TESTING=true
export FIREBASE_PROJECT_ID=test-project
export GOOGLE_API_KEY=test-key

# Run tests
pytest
```

## 🔍 **Test Validation**

### **Pre-commit Testing**
```bash
# Run tests before commit
pytest tests/ --cov=src --cov-fail-under=90

# Check code quality
flake8 src/
mypy src/

# Run integration tests
pytest tests/test_integration/ -v
```

### **CI/CD Pipeline**
```yaml
# GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements-local.txt
          pip install pytest pytest-cov pytest-mock
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 🐛 **Debugging Tests**

### **Common Test Issues**

1. **Mock Configuration**
   ```python
   # Ensure mocks are properly configured
   @patch('src.tools.firebase_tools.get_firebase_client')
   def test_firebase_operation(self, mock_firebase):
       mock_firebase.return_value.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {"test": "data"}
       # Test implementation
   ```

2. **Async Test Issues**
   ```python
   # Handle async tests properly
   @pytest.mark.asyncio
   async def test_async_operation(self):
       result = await async_function()
       assert result is not None
   ```

3. **Environment Variables**
   ```python
   # Set test environment variables
   @patch.dict(os.environ, {'TESTING': 'true', 'FIREBASE_PROJECT_ID': 'test'})
   def test_with_env_vars(self):
       # Test implementation
   ```

### **Test Debugging Tools**
```bash
# Run tests with debug output
pytest -s -v tests/test_specific.py

# Run single test with debugger
pytest tests/test_specific.py::test_function -s --pdb

# Run tests with detailed logging
pytest --log-cli-level=DEBUG tests/
```

## 📈 **Performance Testing**

### **Load Testing**
```python
# Test system performance under load
def test_system_performance():
    handler = SimpleAgenticHandler(team_id="test-team")
    
    # Test multiple concurrent requests
    import asyncio
    import time
    
    async def make_request():
        start_time = time.time()
        response = handler.process_message("help")
        end_time = time.time()
        return end_time - start_time
    
    # Run multiple requests
    times = asyncio.run(asyncio.gather(*[make_request() for _ in range(10)]))
    
    # Verify performance
    avg_time = sum(times) / len(times)
    assert avg_time < 2.0  # Average response time < 2 seconds
```

### **Memory Testing**
```python
# Test memory usage
def test_memory_usage():
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform operations
    handler = SimpleAgenticHandler(team_id="test-team")
    for i in range(100):
        handler.process_message(f"test message {i}")
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Verify reasonable memory usage
    assert memory_increase < 100 * 1024 * 1024  # < 100MB increase
```

## 🎯 **Test Success Metrics**

### **Quality Metrics**
- **Test Coverage**: >90% overall coverage
- **Test Execution Time**: <30 seconds for full test suite
- **Test Reliability**: 100% test pass rate
- **Code Quality**: flake8 and mypy compliance

### **Performance Metrics**
- **Response Time**: <2 seconds for most operations
- **Memory Usage**: <100MB increase under load
- **Database Performance**: <100ms for most queries
- **AI Processing**: <5 seconds for complex requests

## 📚 **Test Documentation**

### **Test Documentation Standards**
- **Docstrings**: All test functions must have descriptive docstrings
- **Comments**: Complex test logic must be commented
- **Examples**: Include usage examples in test documentation
- **Edge Cases**: Document edge cases and error conditions

### **Test Maintenance**
- **Regular Updates**: Update tests when code changes
- **Coverage Monitoring**: Monitor coverage trends
- **Performance Tracking**: Track test execution time
- **Bug Prevention**: Use tests to prevent regression bugs

---

**Last Updated**: December 19, 2024  
**Version**: 1.5.0  
**Status**: ✅ **COMPREHENSIVE TESTING INFRASTRUCTURE** 