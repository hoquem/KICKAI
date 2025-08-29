# Testing Prompts and Strategies for KICKAI

**Version**: 3.1 | **Coverage**: Comprehensive | **Architecture**: Clean Architecture Testing Patterns

This document provides comprehensive testing prompt templates and strategies for KICKAI development.

## 🧪 Testing Philosophy and Strategy

### Testing Pyramid for KICKAI

```
                    🎯 E2E Tests
                   ┌─────────────┐
                   │ User Journeys│ ← Complete workflows, Mock Telegram UI
                   │ Integration  │   Real system behavior validation
                   └─────────────┘
                 
               🔗 Integration Tests  
            ┌─────────────────────┐
            │ Service Integration │ ← Layer interactions, Firebase integration
            │ Repository Tests    │   External system integration
            └─────────────────────┘
            
        ⚡ Unit Tests (Foundation)
    ┌───────────────────────────────┐
    │ Domain Logic | Application    │ ← Pure business logic, isolated testing
    │ Entities     | Services       │   Fast, independent, comprehensive
    └───────────────────────────────┘
```

### Testing Standards

| Test Type | Purpose | Speed | Dependencies | Coverage Target |
|-----------|---------|-------|--------------|----------------|
| **Unit** | Business logic validation | < 100ms | None (mocked) | 90%+ |
| **Integration** | Service interactions | < 5s | Test DB/Services | 80%+ |
| **E2E** | User workflow validation | < 30s | Full system | 70%+ |

## 🎯 Unit Testing Prompts

### 1. Domain Service Testing

**Prompt Template:**
```
Create comprehensive unit tests for [service_name] in KICKAI:

Test Structure:
- File: tests/unit/features/[feature]/domain/test_[service].py
- Mock all external dependencies (repositories, services)
- Test pure business logic only
- Cover success cases, error cases, and edge cases

Test Classes:
class Test[ServiceName]:
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture  
    def service(self, mock_repository):
        return [ServiceName](mock_repository)
    
    @pytest.mark.asyncio
    async def test_[method]_success(self, service, mock_repository):
        # Given - Setup test data and mocks
        # When - Execute the method
        # Then - Assert expected behavior
    
    @pytest.mark.asyncio
    async def test_[method]_error_handling(self, service, mock_repository):
        # Test error scenarios and exception handling

Coverage Requirements:
- ✅ All public methods tested
- ✅ All error conditions covered
- ✅ All business rules validated
- ✅ Edge cases included
```

### 2. Entity and Value Object Testing

**Prompt Template:**
```
Create unit tests for [entity_name] entity following KICKAI patterns:

Test Coverage:
- Factory methods (from_dict, from_telegram_data)
- Serialization methods (to_dict, to_firebase_doc)
- Business rules and validation
- Property calculations and derived values
- Equality and comparison operations

Example Test Structure:
class Test[EntityName]:
    def test_from_dict_success(self):
        # Given
        data = {
            'telegram_id': 123456789,
            'team_id': 'KTI',
            'name': 'Test Player'
        }
        
        # When
        entity = [EntityName].from_dict(data)
        
        # Then
        assert entity.telegram_id == 123456789
        assert entity.team_id == 'KTI'
        assert entity.name == 'Test Player'
    
    def test_validation_rules(self):
        # Test business rule validation
        # Test required field validation
        # Test format validation (e.g., phone numbers)
```

### 3. Application Layer Tool Testing

**Prompt Template:**
```
Create unit tests for application layer tools in [feature]:

Focus Areas:
- Parameter handling and validation
- CrewAI decorator functionality
- Delegation to domain layer
- Error handling and response format
- JSON response structure

Test Structure:
class Test[ToolName]:
    @pytest.fixture
    def mock_domain_function(self):
        # Mock the domain layer function
        pass
    
    @pytest.mark.asyncio
    async def test_tool_parameter_handling(self):
        # Test both individual and dictionary parameters
        # Test type conversion (string to int for telegram_id)
        # Test validation error handling
    
    @pytest.mark.asyncio
    async def test_tool_delegation(self):
        # Verify proper delegation to domain layer
        # Test parameter passing accuracy
        # Verify response forwarding
```

## 🔗 Integration Testing Prompts

### 1. Service Integration Testing

**Prompt Template:**
```
Create integration tests for [service_name] with real dependencies:

Test Environment:
- Use test Firebase database
- Real repository implementations
- Actual service interactions
- Clean test data between tests

Test Structure:
class Test[ServiceName]Integration:
    @pytest.fixture
    async def test_database(self):
        # Setup test database connection
        # Return configured test database
        pass
    
    @pytest.fixture
    async def repository(self, test_database):
        # Create repository with test database
        pass
    
    @pytest.fixture
    async def service(self, repository):
        # Create service with real repository
        pass
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, service):
        # Test complete business workflow
        # Verify data persistence
        # Check business rule enforcement
        # Validate error handling with real systems
    
    async def cleanup_test_data(self):
        # Clean up test data after each test
```

### 2. Repository Integration Testing

**Prompt Template:**
```
Create integration tests for [repository_name] Firebase implementation:

Test Coverage:
- CRUD operations with real Firebase
- Query performance and indexing
- Transaction handling
- Error scenarios (network issues, permissions)
- Data consistency and integrity

Test Structure:
class Test[RepositoryName]Integration:
    @pytest.fixture
    async def repository(self):
        database = get_test_firebase_database()
        return [RepositoryName](database)
    
    @pytest.mark.asyncio
    async def test_create_and_retrieve(self, repository):
        # Test entity creation and retrieval
        # Verify data integrity
        # Check ID generation and assignment
    
    @pytest.mark.asyncio
    async def test_query_operations(self, repository):
        # Test complex queries
        # Verify filtering and sorting
        # Check pagination if applicable
    
    @pytest.mark.asyncio
    async def test_error_scenarios(self, repository):
        # Test network failures
        # Test invalid data scenarios
        # Verify proper exception handling
```

### 3. Cross-Feature Integration Testing

**Prompt Template:**
```
Create integration tests for cross-feature interactions in KICKAI:

Scenarios to Test:
- Player registration → Team administration
- Match creation → Availability management  
- Team member addition → Notification system
- Command routing → Agent delegation

Test Structure:
class TestCrossFeatureIntegration:
    @pytest.mark.asyncio
    async def test_player_registration_to_team_workflow(self):
        # Given - New player registration
        # When - Add to team workflow
        # Then - Verify end-to-end integration
    
    @pytest.mark.asyncio
    async def test_match_availability_workflow(self):
        # Given - Match created
        # When - Players update availability
        # Then - Verify squad selection integration
```

## 🎯 E2E Testing Prompts

### 1. User Journey Testing

**Prompt Template:**
```
Create E2E tests for [user_journey] using Mock Telegram UI:

User Journey Steps:
1. User authentication and registration
2. Core feature interaction
3. System response and feedback
4. Data persistence verification
5. Cross-system integration validation

Test Implementation:
class Test[UserJourney]E2E:
    @pytest.fixture
    async def mock_ui_controller(self):
        from tests.mock_telegram.mock_ui_controller import MockUIController
        controller = MockUIController()
        await controller.initialize()
        return controller
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, mock_ui_controller):
        # Step 1: User setup
        await mock_ui_controller.switch_user('player')
        
        # Step 2: Execute command sequence
        result1 = await mock_ui_controller.send_command('/myinfo', 'Get player information')
        assert 'success' in result1['response_text'].lower()
        
        # Step 3: Verify system behavior
        result2 = await mock_ui_controller.send_command('/update position goalkeeper', 'Update position')
        assert 'position' in result2['response_text'].lower()
        
        # Step 4: Validate data persistence
        result3 = await mock_ui_controller.send_command('/myinfo', 'Verify update')
        assert 'goalkeeper' in result3['response_text'].lower()
```

### 2. System Integration Testing

**Prompt Template:**
```
Create system-wide integration tests for KICKAI:

System Components:
- CrewAI agent system
- NLP processing and routing
- Database operations
- Command processing
- Response generation

Test Structure:
class TestSystemIntegration:
    @pytest.mark.asyncio
    async def test_intelligent_routing_system(self):
        # Given - Complex user request
        # When - System processes request
        # Then - Verify correct agent selection and execution
    
    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self):
        # Test NLP_PROCESSOR → Specialist Agent workflow
        # Verify context sharing between agents
        # Check response coordination
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_fallback(self):
        # Test system behavior with component failures
        # Verify fallback routing mechanisms
        # Check error handling and user feedback
```

### 3. Performance and Load Testing

**Prompt Template:**
```
Create performance tests for KICKAI system:

Performance Metrics:
- Response time < 5 seconds for complex operations
- Memory usage within acceptable limits
- Database query efficiency
- Concurrent user handling

Test Implementation:
class TestSystemPerformance:
    @pytest.mark.asyncio
    async def test_response_time_benchmarks(self):
        # Test critical path operations
        # Measure and assert response times
        # Identify performance bottlenecks
    
    @pytest.mark.asyncio
    async def test_concurrent_user_handling(self):
        # Simulate multiple users
        # Test system stability under load
        # Verify data consistency
```

## 🔧 Testing Utilities and Helpers

### 1. Test Data Factory Prompt

**Prompt Template:**
```
Create test data factories for [entity_name] in KICKAI:

Factory Features:
- Generate valid test entities
- Support different scenarios (new player, existing player, etc.)
- Provide realistic test data
- Support batch creation for performance testing

Implementation:
class [EntityName]Factory:
    @staticmethod
    def create_valid_[entity](override_params=None):
        default_params = {
            'telegram_id': 123456789,
            'team_id': 'TEST',
            'name': 'Test Player',
            # Additional realistic defaults
        }
        
        if override_params:
            default_params.update(override_params)
        
        return [EntityName].from_dict(default_params)
    
    @staticmethod
    def create_batch(count: int, **kwargs):
        return [
            [EntityName]Factory.create_valid_[entity]({
                'telegram_id': 100000000 + i,
                'name': f'Test Player {i}',
                **kwargs
            })
            for i in range(count)
        ]
```

### 2. Mock Service Prompt

**Prompt Template:**
```
Create mock services for testing [service_name]:

Mock Features:
- Implement all interface methods
- Support configurable responses
- Track method calls and parameters
- Provide realistic behavior simulation

Implementation:
class Mock[ServiceName]:
    def __init__(self):
        self.calls = []
        self.responses = {}
        self.exceptions = {}
    
    def set_response(self, method_name: str, response):
        self.responses[method_name] = response
    
    def set_exception(self, method_name: str, exception):
        self.exceptions[method_name] = exception
    
    async def [method_name](self, *args, **kwargs):
        self.calls.append(('method_name', args, kwargs))
        
        if 'method_name' in self.exceptions:
            raise self.exceptions['method_name']
        
        return self.responses.get('method_name', default_response)
```

## 📋 Test Maintenance and Quality

### Test Code Quality Prompts

**Code Review for Tests:**
```
Review test code for [component] following KICKAI standards:

Quality Checklist:
- ✅ Clear test names describing behavior
- ✅ AAA pattern (Arrange, Act, Assert)
- ✅ Single responsibility per test
- ✅ Proper async/await usage
- ✅ Cleanup and resource management
- ✅ Realistic test data usage
- ✅ Comprehensive edge case coverage

Example Review:
def test_player_registration_success(self):  # ✅ Clear name
    # Arrange - Setup test data
    player_data = PlayerFactory.create_valid_data()
    
    # Act - Execute the operation
    result = await service.register_player(player_data)
    
    # Assert - Verify expected outcome
    assert result.success is True
    assert result.player.telegram_id == player_data['telegram_id']
```

### Test Data Management

**Test Data Strategy:**
```
Manage test data for [feature] testing:

Strategies:
1. **Factory Pattern**: Generate realistic test data
2. **Builder Pattern**: Construct complex test scenarios
3. **Fixture Management**: Share common test setup
4. **Data Cleanup**: Ensure test isolation
5. **Snapshot Testing**: Verify complex object structures

Implementation Guidelines:
- Use factories for entity creation
- Implement proper teardown methods
- Avoid hard-coded test data
- Use meaningful test identifiers
- Implement data versioning for API changes
```

## 🚀 Testing Commands and Automation

### Essential Testing Commands

```bash
# Unit tests (fast, isolated)
make test-unit
python -m pytest tests/unit/ -v --tb=short

# Integration tests (with real dependencies)  
make test-integration
python -m pytest tests/integration/ -v

# E2E tests (full system)
make test-e2e
python -m pytest tests/e2e/ -v

# Specific feature testing
python -m pytest tests/unit/features/player_registration/ -v

# Coverage reporting
python -m pytest tests/unit/ --cov=kickai --cov-report=html

# Performance testing
python -m pytest tests/performance/ -v --benchmark-only

# Parallel test execution
python -m pytest tests/unit/ -n auto --dist=loadfile
```

### Continuous Testing Setup

```bash
# Watch mode for development
pytest-watch tests/unit/ kickai/

# Pre-commit testing validation
python -m pytest tests/unit/ --tb=no -q

# Full system validation
PYTHONPATH=. python scripts/run_comprehensive_tests.py
```

## 🎯 Testing Best Practices Summary

### Quick Reference

**Before Writing Tests:**
- [ ] Identify the component's layer (Application/Domain/Infrastructure)
- [ ] Choose appropriate test type (Unit/Integration/E2E)
- [ ] Plan test data and mocking strategy
- [ ] Consider error scenarios and edge cases

**During Test Development:**
- [ ] Follow AAA pattern (Arrange, Act, Assert)
- [ ] Use descriptive test names
- [ ] Keep tests independent and isolated
- [ ] Mock external dependencies appropriately
- [ ] Include both positive and negative test cases

**After Test Implementation:**
- [ ] Verify test coverage meets requirements
- [ ] Run tests in isolation to ensure independence
- [ ] Check test performance and execution time
- [ ] Validate error messages and exception handling
- [ ] Review test maintainability and readability

---

**Status**: Comprehensive Testing Strategy Implemented  
**Coverage**: 90%+ Unit | 80%+ Integration | 70%+ E2E  
**Architecture**: Clean Architecture Testing Patterns  
**Automation**: CI/CD Integration Complete