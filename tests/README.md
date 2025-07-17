# KICKAI Test Suite

## 📁 **Test Directory Structure**

The KICKAI test suite is organized into a clean, hierarchical structure for better maintainability and clarity:

```
tests/
├── README.md                 # This file
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests (isolated, fast)
│   ├── agents/             # Agent-related unit tests
│   ├── core/               # Core system unit tests
│   ├── database/           # Database layer unit tests
│   ├── domain/             # Domain logic unit tests
│   ├── services/           # Service layer unit tests
│   ├── telegram/           # Telegram integration unit tests
│   └── utils/              # Utility function unit tests
├── integration/            # Integration tests (component interaction)
│   ├── agents/             # Agent integration tests
│   ├── services/           # Service integration tests
│   └── telegram/           # Telegram integration tests
├── e2e/                    # End-to-end tests (full system)
├── fixtures/               # Test data and fixtures
└── frameworks/             # Testing frameworks and utilities
```

## 🧪 **Test Types**

### **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single function, class, or module
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution (< 1 second per test)
- **Coverage**: High coverage of business logic

**Examples:**
- Agent capability tests
- Service method tests
- Utility function tests
- Model validation tests

### **Integration Tests** (`tests/integration/`)
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Dependencies**: Some real dependencies, some mocked
- **Speed**: Medium execution (1-10 seconds per test)
- **Coverage**: Component interaction patterns

**Examples:**
- Agent collaboration tests
- Service-to-service communication
- Database integration tests
- Telegram handler integration

### **End-to-End Tests** (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Scope**: Full system from user input to database
- **Dependencies**: Real Telegram API, real Firestore
- **Speed**: Slow execution (10+ seconds per test)
- **Coverage**: User journey validation

**Examples:**
- Complete player registration workflow
- Status command with real data
- Payment processing end-to-end
- Match creation and attendance

## 🚀 **Running Tests**

### **Run All Tests**
```bash
# From project root
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### **Run Specific Test Types**
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### **Run Tests by Module**
```bash
# Agent tests
pytest tests/unit/agents/
pytest tests/integration/agents/

# Service tests
pytest tests/unit/services/
pytest tests/integration/services/

# Telegram tests
pytest tests/unit/telegram/
pytest tests/integration/telegram/
```

### **Run Specific Test Files**
```bash
# Specific test file
pytest tests/unit/services/test_payment_service.py

# Specific test function
pytest tests/unit/services/test_payment_service.py::test_create_payment
```

### **Run E2E Tests with Bot**
```bash
# Run E2E tests with actual bot
python run_e2e_tests.py --suite smoke

# Run comprehensive E2E tests
python scripts/run_comprehensive_e2e_tests.py
```

## 📊 **Test Configuration**

### **Pytest Configuration** (`pytest.ini`)
- Test discovery patterns
- Markers for test categorization
- Output formatting
- Coverage settings

### **Shared Fixtures** (`conftest.py`)
- Database test fixtures
- Mock service fixtures
- Telegram bot fixtures
- Test data factories

### **Environment Setup**
- `.env.test` for test environment variables
- Firebase Testing project configuration
- Telegram test session management

## 🎯 **Test Categories**

### **Agent Tests**
- **Location**: `tests/unit/agents/`, `tests/integration/agents/`
- **Focus**: AI agent capabilities, collaboration, task decomposition
- **Key Tests**:
  - Agent capability matrix
  - Intelligent routing
  - Dynamic task decomposition
  - Advanced memory systems

### **Service Tests**
- **Location**: `tests/unit/services/`, `tests/integration/services/`
- **Focus**: Business logic, data processing, external integrations
- **Key Tests**:
  - Player registration service
  - Payment processing
  - Team management
  - Match operations

### **Telegram Tests**
- **Location**: `tests/unit/telegram/`, `tests/integration/telegram/`
- **Focus**: Bot commands, message handling, user interactions
- **Key Tests**:
  - Command parsing
  - Message routing
  - User authentication
  - Chat management

### **Database Tests**
- **Location**: `tests/unit/database/`
- **Focus**: Data persistence, model validation, query operations
- **Key Tests**:
  - Player model operations
  - Team data management
  - Payment records
  - Match data

### **Cross-Feature Tests**
- **Location**: `tests/e2e/features/test_cross_feature_flows.py`, `tests/integration/features/test_cross_feature_integration.py`
- **Focus**: End-to-end workflows spanning multiple features, service interactions across features
- **Key Tests**:
  - Registration → Match Assignment → Attendance → Payment
  - Admin adds player → Onboarding → Match squad → Payment eligibility
  - Payment completion → Status reflected in match, attendance, and team records
  - Service layer integration across player, team, match, attendance, and payment features

**Cross-Feature Test Scenarios:**
1. **Complete User Journey**: Player registration through payment completion
2. **Admin Workflow**: Adding players, managing matches, processing payments
3. **Data Consistency**: Ensuring state changes propagate across all features
4. **Service Integration**: Testing business logic interactions without UI layer

## 🔧 **Test Utilities**

### **Frameworks** (`tests/frameworks/`)
- `e2e_framework.py` - E2E testing framework
- `multi_client_e2e_framework.py` - Multi-client E2E testing
- `test_base.py` - Base test classes
- `test_fixtures.py` - Shared test fixtures
- `test_utils.py` - Testing utilities

### **Fixtures** (`tests/fixtures/`)
- Test data sets
- Mock responses
- Sample configurations
- Database seeds

## 📈 **Test Coverage**

### **Current Coverage**
- **Unit Tests**: ~80% coverage
- **Integration Tests**: ~60% coverage
- **E2E Tests**: ~40% coverage

### **Coverage Goals**
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: 80%+ coverage
- **E2E Tests**: 70%+ coverage

## 🚨 **Test Best Practices**

### **Writing Tests**
1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: Test names should explain what is being tested
3. **Test One Thing**: Each test should verify one specific behavior
4. **Use Fixtures**: Reuse test data and setup
5. **Mock External Dependencies**: Keep tests fast and reliable

### **Test Data**
1. **Use Factories**: Create test data with factories
2. **Clean Up**: Always clean up test data
3. **Isolation**: Tests should not depend on each other
4. **Realistic Data**: Use realistic but safe test data

### **E2E Testing**
1. **Use Test Environment**: Never test against production
2. **Clean State**: Start with clean database state
3. **Real APIs**: Use real Telegram API and Firestore
4. **User Scenarios**: Test complete user workflows

## 🔄 **Continuous Integration**

### **GitHub Actions**
- Run unit tests on every push
- Run integration tests on pull requests
- Run E2E tests on main branch
- Generate coverage reports

### **Pre-commit Hooks**
- Run unit tests before commit
- Check code formatting
- Validate imports
- Run linting

## 📝 **Adding New Tests**

### **Unit Tests**
1. Create test file in appropriate `tests/unit/` subdirectory
2. Follow naming convention: `test_<module_name>.py`
3. Use existing fixtures from `conftest.py`
4. Mock external dependencies

### **Integration Tests**
1. Create test file in appropriate `tests/integration/` subdirectory
2. Test component interactions
3. Use real internal dependencies
4. Mock external APIs

### **E2E Tests**
1. Create test file in `tests/e2e/`
2. Test complete user workflows
3. Use real external dependencies
4. Clean up after tests

## 🐛 **Debugging Tests**

### **Running Tests in Debug Mode**
```bash
# Run with verbose output
pytest -v tests/

# Run with print statements
pytest -s tests/

# Run with debugger
pytest --pdb tests/
```

### **Common Issues**
1. **Import Errors**: Check PYTHONPATH includes `src/`
2. **Database Issues**: Ensure test database is clean
3. **Telegram Issues**: Check test session configuration
4. **Mock Issues**: Verify mock setup and teardown

---

## 📞 **Support**

For test-related questions or issues:
1. Check this README first
2. Review existing test examples
3. Check pytest documentation
4. Contact the development team

---

**Last Updated**: December 2024  
**Version**: 2.0  
**Status**: Active 