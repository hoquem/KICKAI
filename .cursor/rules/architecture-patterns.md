# Architecture Patterns for KICKAI Development

**Version**: 3.1 | **Architecture**: Clean Architecture Migration Complete | **Pattern**: Feature-First Design

This document defines architecture-specific prompt patterns and development guidelines for the KICKAI system's Clean Architecture implementation.

## 🏗️ Clean Architecture Overview

### Layer Responsibilities

```
Application Layer (kickai/features/*/application/)
├── tools/          # CrewAI @tool decorators, parameter handling
├── commands/       # Command handlers and routing
└── handlers/       # Application service coordination

Domain Layer (kickai/features/*/domain/)
├── entities/       # Business objects and value objects  
├── services/       # Pure business logic (no external dependencies)
├── repositories/   # Repository interfaces (abstractions)
└── exceptions/     # Domain-specific exceptions

Infrastructure Layer (kickai/features/*/infrastructure/)
├── repositories/   # Firebase implementations
├── adapters/       # External service adapters
└── configs/        # Infrastructure-specific configuration
```

### Dependency Flow
```
Application Layer → Domain Layer ← Infrastructure Layer
     ↓                   ↑                    ↑
CrewAI Tools    Pure Business Logic    Firebase/External
```

## 🔧 Development Patterns

### 1. Tool Implementation Pattern

**Application Layer Tool:**
```python
# kickai/features/[feature]/application/tools/[feature]_tools.py
from crewai.tools import tool
from kickai.features.[feature].domain.tools.[tool_name]_domain import [tool_name]_domain

@tool("[tool_name]", result_as_answer=True)
async def [tool_name](telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """Application layer CrewAI tool with framework concerns."""
    return await [tool_name]_domain(telegram_id, team_id, username, chat_type)
```

**Domain Layer Function:**
```python
# kickai/features/[feature]/domain/tools/[tool_name]_domain.py
from kickai.utils.json_response import create_json_response, ResponseStatus

async def [tool_name]_domain(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """Pure domain business logic with no framework dependencies."""
    try:
        # Repository access through dependency injection
        container = get_container()
        service = container.get_service(ServiceClass)
        result = await service.method_name(param=value)
        return create_json_response(ResponseStatus.SUCCESS, data=result)
    except Exception as e:
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

### 2. Service Layer Pattern

**Domain Service:**
```python
# kickai/features/[feature]/domain/services/[service_name].py
from typing import Protocol
from kickai.features.[feature].domain.repositories.[repo_interface] import [RepoInterface]

class [ServiceName]:
    def __init__(self, repository: [RepoInterface]):
        self._repository = repository
    
    async def business_method(self, param: type) -> ReturnType:
        """Pure business logic implementation."""
        # Validate input
        # Execute business rules
        # Return results
        pass
```

**Repository Interface:**
```python
# kickai/features/[feature]/domain/repositories/[entity]_repository_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional
from kickai.features.[feature].domain.entities.[entity] import [Entity]

class [Entity]RepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, entity_id: str, team_id: str) -> Optional[[Entity]]:
        pass
    
    @abstractmethod
    async def create(self, entity: [Entity]) -> [Entity]:
        pass
```

**Infrastructure Implementation:**
```python
# kickai/features/[feature]/infrastructure/firestore_[entity]_repository.py
from kickai.features.[feature].domain.repositories.[entity]_repository_interface import [Entity]RepositoryInterface
from kickai.features.[feature].domain.entities.[entity] import [Entity]

class Firestore[Entity]Repository([Entity]RepositoryInterface):
    def __init__(self, database):
        self._db = database
    
    async def get_by_id(self, entity_id: str, team_id: str) -> Optional[[Entity]]:
        # Firebase implementation
        pass
```

### 3. Entity Pattern

**Domain Entity:**
```python
# kickai/features/[feature]/domain/entities/[entity].py
from dataclasses import dataclass
from typing import Optional, Dict, Any
from kickai.core.enums import [RelevantEnum]

@dataclass
class [Entity]:
    # Core attributes
    id: str
    team_id: str
    # Additional attributes...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '[Entity]':
        """Create entity from dictionary data (e.g., from Firebase)."""
        return cls(
            id=data.get('id'),
            team_id=data.get('team_id'),
            # Map additional fields...
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for persistence."""
        return {
            'id': self.id,
            'team_id': self.team_id,
            # Additional fields...
        }
```

## 🎯 Prompt Templates for Architecture Tasks

### New Feature Creation

**Comprehensive Feature Prompt:**
```
Create a new feature [feature_name] following KICKAI Clean Architecture:

1. Domain Layer Setup:
   - Create entities in domain/entities/ with proper validation
   - Define repository interfaces in domain/repositories/
   - Implement business services in domain/services/
   - Add feature-specific exceptions in domain/exceptions.py

2. Infrastructure Layer:
   - Implement Firebase repositories in infrastructure/
   - Add external service adapters if needed
   - Configure infrastructure dependencies

3. Application Layer:
   - Create CrewAI tools in application/tools/
   - Add command handlers in application/commands/
   - Implement application services for coordination

4. Integration:
   - Export tools from feature __init__.py
   - Register with dependency container
   - Update agent tool assignments
   - Add routing configuration

5. Testing:
   - Unit tests for domain services
   - Integration tests for repositories
   - E2E tests for user workflows
```

### Tool Migration Prompt

**Migration from Domain to Application:**
```
Migrate existing domain tools to Clean Architecture pattern:

1. Identify Current State:
   - List all @tool decorators in domain layer
   - Map tools to business logic functions
   - Identify external dependencies

2. Create Application Layer Tools:
   - Move @tool decorators to application/tools/
   - Create thin wrapper functions
   - Handle parameter validation and conversion

3. Extract Domain Logic:
   - Create pure business functions in domain/tools/
   - Remove framework dependencies
   - Use dependency injection for services

4. Update Registrations:
   - Update feature __init__.py exports
   - Verify tool discovery works
   - Test integration with CrewAI agents

5. Testing Updates:
   - Update test imports
   - Test both layers separately
   - Verify end-to-end functionality
```

### Service Refactoring Prompt

**Service Layer Enhancement:**
```
Refactor [service_name] to follow Clean Architecture:

1. Interface Extraction:
   - Create abstract interface in domain/repositories/
   - Define clear method contracts
   - Add proper type hints and documentation

2. Implementation Separation:
   - Move Firebase logic to infrastructure/
   - Keep business logic in domain/services/
   - Remove external dependencies from domain

3. Dependency Injection:
   - Update service constructors
   - Configure container bindings
   - Test injection works correctly

4. Error Handling:
   - Add domain-specific exceptions
   - Handle infrastructure errors appropriately
   - Provide meaningful error messages

5. Testing Strategy:
   - Mock repositories in domain tests
   - Test infrastructure implementations
   - Verify service behavior independently
```

## 🔍 Architecture Validation Prompts

### Clean Architecture Compliance Check

**Validation Template:**
```
Validate Clean Architecture compliance for [component]:

1. Layer Boundaries:
   - ✅ Application layer only contains framework concerns
   - ✅ Domain layer has no external dependencies
   - ✅ Infrastructure layer implements domain interfaces
   - ✅ No circular dependencies between layers

2. Dependency Rules:
   - ✅ Application depends on Domain
   - ✅ Infrastructure depends on Domain
   - ✅ Domain depends on nothing external
   - ✅ All dependencies point inward

3. Framework Isolation:
   - ✅ @tool decorators only in application layer
   - ✅ Firebase code only in infrastructure layer
   - ✅ CrewAI imports only in application layer
   - ✅ Pure Python in domain layer

4. Testing Independence:
   - ✅ Domain tests run without external dependencies
   - ✅ Infrastructure tests isolated to their concerns
   - ✅ Application tests verify integration only
```

### Performance and Scalability Review

**Performance Template:**
```
Review [component] for performance and scalability:

1. Database Patterns:
   - Efficient Firebase queries
   - Proper indexing usage
   - Batch operations where appropriate
   - Connection pooling considerations

2. Memory Management:
   - Proper async/await patterns
   - Resource cleanup
   - Avoiding memory leaks
   - Efficient data structures

3. Caching Strategy:
   - Identify cacheable operations
   - Implement appropriate caching levels
   - Cache invalidation patterns
   - Performance monitoring

4. Concurrency:
   - Thread-safe operations
   - Async operation efficiency
   - Resource contention avoidance
   - Scalability bottlenecks
```

## 🧪 Testing Architecture Patterns

### Domain Layer Testing

**Domain Test Pattern:**
```python
# tests/unit/features/[feature]/domain/test_[service].py
import pytest
from unittest.mock import Mock, AsyncMock
from kickai.features.[feature].domain.services.[service] import [Service]
from kickai.features.[feature].domain.entities.[entity] import [Entity]

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def service(mock_repository):
    return [Service](mock_repository)

@pytest.mark.asyncio
async def test_business_logic_success(service, mock_repository):
    # Given
    mock_repository.method.return_value = expected_result
    
    # When
    result = await service.business_method(valid_input)
    
    # Then
    assert result == expected_result
    mock_repository.method.assert_called_once_with(valid_input)

@pytest.mark.asyncio
async def test_business_logic_error_handling(service, mock_repository):
    # Given
    mock_repository.method.side_effect = Exception("Database error")
    
    # When/Then
    with pytest.raises(DomainException) as exc_info:
        await service.business_method(invalid_input)
    
    assert "Expected error message" in str(exc_info.value)
```

### Infrastructure Testing

**Infrastructure Test Pattern:**
```python
# tests/integration/features/[feature]/infrastructure/test_[repository].py
import pytest
from kickai.features.[feature].infrastructure.firestore_[entity]_repository import Firestore[Entity]Repository
from kickai.features.[feature].domain.entities.[entity] import [Entity]

@pytest.fixture
async def repository():
    # Setup test database connection
    database = get_test_database()
    return Firestore[Entity]Repository(database)

@pytest.mark.asyncio
async def test_repository_crud_operations(repository):
    # Create test entity
    entity = [Entity](id="test-id", team_id="test-team")
    
    # Test create
    created = await repository.create(entity)
    assert created.id == entity.id
    
    # Test read
    retrieved = await repository.get_by_id("test-id", "test-team")
    assert retrieved is not None
    assert retrieved.id == entity.id
    
    # Cleanup
    await repository.delete("test-id", "test-team")
```

### Application Layer Testing

**Application Test Pattern:**
```python
# tests/integration/features/[feature]/application/test_[tool].py
import pytest
from kickai.features.[feature].application.tools.[tool] import [tool_name]

@pytest.mark.asyncio
async def test_tool_integration():
    # Given
    valid_params = {
        'telegram_id': 123456789,
        'team_id': 'TEST',
        'username': 'testuser',
        'chat_type': 'main'
    }
    
    # When
    result = await [tool_name](**valid_params)
    
    # Then
    assert result is not None
    # Verify JSON response format
    # Verify business logic execution
```

## 📋 Migration Checklist

### Pre-Migration Assessment
- [ ] Identify all components requiring migration
- [ ] Map current dependencies and coupling
- [ ] Plan migration order (dependencies first)
- [ ] Identify breaking changes and mitigation strategies

### During Migration
- [ ] Create application layer wrappers
- [ ] Extract domain business logic
- [ ] Implement infrastructure adapters
- [ ] Update dependency injection configuration
- [ ] Maintain backward compatibility during transition

### Post-Migration Validation
- [ ] Run full test suite
- [ ] Validate Clean Architecture compliance
- [ ] Check performance impact
- [ ] Verify feature functionality
- [ ] Update documentation

---

**Status**: Clean Architecture Migration Complete | **Pattern Compliance**: ✅ Verified | **Performance**: Optimized