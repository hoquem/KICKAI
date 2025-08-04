# CrewAI Agents Test Suite

This directory contains comprehensive tests for CrewAI agents based on the `CREWAI_AGENTS_TEST_SPECIFICATION.md` document.

## 📋 Test Categories

### Category 1: Unit Tests (`unit/`)
- **Agent Initialization**: Test agent creation and configuration
- **Tool Registration**: Test tool addition and removal
- **Context Management**: Test context handling and validation
- **Task Execution**: Test individual task processing
- **Error Handling**: Test agent error responses

### Category 2: Integration Tests (`integration/`)
- **Multi-Agent Coordination**: Test agent collaboration
- **Tool Chain Execution**: Test sequential tool usage
- **Context Propagation**: Test context sharing between agents
- **Error Propagation**: Test error handling across agents

### Category 3: Reasoning Validation Tests (`reasoning/`)
- **Reasoning Quality**: Validate agent reasoning using Ollama LLM
- **Response Consistency**: Test response consistency across runs
- **Context Understanding**: Test agent context comprehension
- **Decision Making**: Test agent decision quality

### Category 4: End-to-End Tests (`e2e/`)
- **Player Registration Flow**: Test complete registration process
- **Team Management Flow**: Test team administration workflows
- **Help System Flow**: Test help and guidance systems
- **Error Recovery Flow**: Test error handling and recovery

## 🚀 Quick Start

### Run All Tests
```bash
python tests/agents/run_agent_tests.py
```

### Run Specific Category
```bash
# Run only unit tests
python tests/agents/run_agent_tests.py --category 1

# Run only integration tests
python tests/agents/run_agent_tests.py --category 2

# Run only reasoning validation tests
python tests/agents/run_agent_tests.py --category 3

# Run only end-to-end tests
python tests/agents/run_agent_tests.py --category 4
```

### Run with Coverage
```bash
python tests/agents/run_agent_tests.py --coverage
```

### Run with Verbose Output
```bash
python tests/agents/run_agent_tests.py --verbose
```

### Check Ollama Availability
```bash
python tests/agents/run_agent_tests.py --check-ollama
```

## 🧪 Running Individual Test Files

### Unit Tests
```bash
python -m pytest tests/agents/unit/test_agent_components.py -v
```

### Integration Tests
```bash
python -m pytest tests/agents/integration/test_agent_interactions.py -v
```

### Reasoning Validation Tests
```bash
python -m pytest tests/agents/reasoning/test_reasoning_validation.py -v
```

### End-to-End Tests
```bash
python -m pytest tests/agents/e2e/test_complete_user_journeys.py -v
```

## ⚙️ Configuration

The test configuration is defined in `conftest.py`:

```python
TEST_CONFIG = {
    "ollama_base_url": "http://macmini1.local:11434",
    "ollama_model": "llama3.1:8b",
    "test_team_id": "test_team_alpha",
    "test_user_id": "test_user_123",
    "mock_services": True,
    "isolated_database": True
}
```

## 🔧 Test Infrastructure

### Fixtures
- `coordinator_agent`: Player coordinator agent for testing
- `manager_agent`: Team manager agent for testing
- `configurable_agent`: Generic configurable agent
- `mock_tool`: Mock tool for testing
- `mock_tools`: Multiple mock tools
- `failing_tool`: Mock tool that fails
- `reasoning_validator`: Ollama reasoning validator
- `test_workflow_data`: Predefined workflow test data

### Mock Services
- `mock_telegram_service`: Mock Telegram service
- `mock_database_service`: Mock database service
- `mock_ollama_client`: Mock Ollama client

## 📊 Test Results

Test results are automatically saved to JSON files with timestamps:
- `agent_test_results_YYYYMMDD_HHMMSS.json`

The test runner provides:
- Success/failure counts per category
- Overall success rate
- Execution duration
- Detailed error messages (with `--verbose`)

## 🎯 Success Criteria

### Minimum Requirements
- **Unit Test Coverage**: ≥ 90% code coverage
- **Integration Test Coverage**: All agent interactions tested
- **E2E Test Coverage**: All user journeys tested
- **Performance Requirements**: Average response time < 5 seconds
- **Reasoning Quality**: Ollama validation score ≥ 0.8
- **Error Handling**: All error scenarios handled gracefully

### Advanced Requirements
- **Load Testing**: Support 100+ concurrent requests
- **Memory Efficiency**: < 100MB memory increase per 100 requests
- **Consistency**: Response consistency score ≥ 0.9
- **Observability**: Complete monitoring and alerting
- **Recovery**: Automatic recovery from failures

## 🔍 Ollama Integration

The reasoning validation tests use Ollama LLM for:
- Validating agent reasoning quality
- Evaluating response consistency
- Testing context understanding
- Assessing decision-making quality

### Ollama Requirements
- **URL**: `http://macmini1.local:11434`
- **Model**: `llama3.1:8b`
- **Availability**: Must be running for reasoning tests

### Fallback Behavior
If Ollama is unavailable, reasoning tests will:
- Use mock responses
- Log warnings
- Continue with basic validation
- Not fail the test suite

## 📁 Directory Structure

```
tests/agents/
├── README.md                    # This file
├── conftest.py                  # Test configuration and fixtures
├── run_agent_tests.py          # Test runner script
├── unit/                       # Category 1: Unit Tests
│   ├── __init__.py
│   └── test_agent_components.py
├── integration/                # Category 2: Integration Tests
│   ├── __init__.py
│   └── test_agent_interactions.py
├── reasoning/                  # Category 3: Reasoning Validation
│   ├── __init__.py
│   └── test_reasoning_validation.py
└── e2e/                       # Category 4: End-to-End Tests
    ├── __init__.py
    └── test_complete_user_journeys.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   curl http://macmini1.local:11434/api/tags
   
   # Start Ollama if needed
   ollama serve
   ```

2. **Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=src:$PYTHONPATH
   
   # Or run from project root
   cd /path/to/KICKAI
   python tests/agents/run_agent_tests.py
   ```

3. **Test Failures**
   ```bash
   # Run with verbose output for details
   python tests/agents/run_agent_tests.py --verbose
   
   # Check specific category
   python tests/agents/run_agent_tests.py --category 1 --verbose
   ```

### Debug Mode
```bash
# Run with maximum verbosity
python -m pytest tests/agents/ -v -s --tb=long
```

## 📈 Performance Monitoring

The tests include performance monitoring:
- Response time tracking
- Memory usage monitoring
- Concurrent request testing
- Error rate calculation

### Performance Thresholds
- **Response Time**: < 5 seconds average
- **Memory Usage**: < 100MB increase per 100 requests
- **Concurrent Requests**: Support 50+ simultaneous
- **Error Rate**: < 5% failure rate

## 🔄 Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
name: Agent Tests
on: [push, pull_request]
jobs:
  agent-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run agent tests
        run: python tests/agents/run_agent_tests.py --coverage
```

## 📚 References

- [CREWAI_AGENTS_TEST_SPECIFICATION.md](../docs/CREWAI_AGENTS_TEST_SPECIFICATION.md)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [pytest Documentation](https://docs.pytest.org/)

---

**Version**: 1.0.0  
**Last Updated**: 2024-12-19  
**Maintainer**: KICKAI Development Team 