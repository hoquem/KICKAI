# Service Interfaces & Dependency Injection

**Summary: All services must use interfaces. Dependency injection is mandatory. Code must be testable, maintainable, and easy to mock. Mocks are required for all interfaces. This is required for all new code and refactors.**

- **Interface-Driven Design**: Every service must have an interface in `src/services/interfaces/`. No direct dependencies on concrete implementations.
- **Dependency Injection**: All services, repositories, and agents must be injected via the DI container. No singletons, global state, or direct instantiation.
- **Testability**: All code must be easy to test in isolation. Mocks must be provided for every interface in `src/services/mocks/`.
- **Maintainability**: Interfaces and DI make it easy to swap implementations, add features, and refactor safely.
- **Contract Enforcement**: Interfaces define clear contracts for all implementations.

---

## Overview

The KICKAI system implements a comprehensive service interface system using Python's Abstract Base Classes (ABCs) and corresponding mock implementations. This approach provides dependency injection, easy testing, contract enforcement, and code maintainability.

## Architecture

### Interface Structure
```
src/services/
├── interfaces/                    # Abstract base classes (interfaces)
│   ├── __init__.py
│   ├── player_service_interface.py
│   ├── team_service_interface.py
│   ├── team_member_service_interface.py
│   ├── access_control_service_interface.py
│   ├── fa_registration_checker_interface.py
│   ├── daily_status_service_interface.py
│   ├── bot_status_service_interface.py
│   ├── monitoring_service_interface.py
│   └── multi_team_manager_interface.py
├── mocks/                        # Mock implementations for testing
│   ├── __init__.py
│   ├── mock_player_service.py
│   ├── mock_team_service.py
│   ├── mock_team_member_service.py
│   ├── mock_access_control_service.py
│   ├── mock_fa_registration_checker.py
│   ├── mock_daily_status_service.py
│   ├── mock_bot_status_service.py
│   ├── mock_monitoring_service.py
│   └── mock_multi_team_manager.py
└── ... (existing concrete services)
```

## Interface Definitions

### Core Service Interfaces

#### IPlayerService
```python
class IPlayerService(ABC):
    @abstractmethod
    async def create_player(self, name: str, phone: str, team_id: str, ...) -> Player:
        pass
    
    @abstractmethod
    async def get_player(self, player_id: str) -> Optional[Player]:
        pass
    
    @abstractmethod
    async def update_player(self, player_id: str, **updates) -> Player:
        pass
```

#### ITeamService
```python
class ITeamService(ABC):
    @abstractmethod
    async def create_team(self, name: str, description: Optional[str] = None, ...) -> Team:
        pass
    
    @abstractmethod
    async def get_team(self, team_id: str) -> Optional[Team]:
        pass
    
    @abstractmethod
    async def add_team_member(self, team_id: str, user_id: str, role: str = "player", ...) -> TeamMember:
        pass
```

#### ITeamMemberService
```python
class ITeamMemberService(ABC):
    @abstractmethod
    async def create_team_member(self, team_member: TeamMember) -> str:
        pass
    
    @abstractmethod
    async def get_team_member(self, member_id: str) -> Optional[TeamMember]:
        pass
    
    @abstractmethod
    async def get_team_members_by_team(self, team_id: str) -> List[TeamMember]:
        pass
```

## Mock Implementations

### MockPlayerService
- In-memory storage using dictionaries
- Realistic behavior that mimics the actual service
- Reset functionality for clean test state
- Comprehensive logging for debugging

### MockTeamService
- In-memory storage for teams, members, and bot mappings
- Proper validation and error handling
- Reset functionality for test isolation

### MockTeamMemberService
- In-memory storage for team members
- Role validation and management
- Chat access control simulation

## Usage Patterns

### Dependency Injection
```python
class PlayerOnboardingService:
    def __init__(self,
                 player_service: IPlayerService,
                 team_service: ITeamService,
                 team_member_service: ITeamMemberService):
        self.player_service = player_service
        self.team_service = team_service
        self.team_member_service = team_member_service
```

### Testing with Mocks
```python
@pytest.mark.asyncio
async def test_player_onboarding():
    # Create mock services
    player_service = MockPlayerService()
    team_service = MockTeamService()
    team_member_service = MockTeamMemberService()
    
    # Create service with injected mocks
    onboarding_service = PlayerOnboardingService(
        player_service=player_service,
        team_service=team_service,
        team_member_service=team_member_service
    )
```

## Benefits

### 1. Easy Testing
- **No External Dependencies**: Mocks don't require real databases or external services
- **Predictable Behavior**: Mock responses can be controlled and configured
- **Fast Execution**: No network calls or database operations
- **Isolation**: Each test can have its own clean state

### 2. Dependency Injection
- **Loose Coupling**: Services depend on interfaces, not concrete implementations
- **Easy Swapping**: Can easily swap between mock and real implementations
- **Testability**: Easy to inject test doubles for isolated testing
- **Flexibility**: Can use different implementations for different environments

### 3. Contract Enforcement
- **Type Safety**: IDE support and static type checking
- **Clear Contracts**: Interfaces define exactly what methods must be implemented
- **Documentation**: Interfaces serve as living documentation
- **Consistency**: All implementations must follow the same contract

### 4. Code Maintainability
- **Separation of Concerns**: Clear boundaries between different services
- **Easy Refactoring**: Can change implementations without affecting consumers
- **Extensibility**: Easy to add new implementations or extend existing ones
- **Debugging**: Clear interfaces make it easier to understand and debug code

## Implementation Requirements

### For New Services
1. **Define Interface**: Create interface in `src/services/interfaces/`
2. **Implement Service**: Create concrete implementation
3. **Create Mock**: Create mock implementation in `src/services/mocks/`
4. **Add Tests**: Write tests using mock implementations
5. **Update Documentation**: Document the service interface

### For Existing Services
1. **Extract Interface**: Extract interface from existing service
2. **Create Mock**: Create mock implementation
3. **Update Dependencies**: Update all consumers to use interface
4. **Add Tests**: Write tests using mock implementations
5. **Validate**: Ensure all functionality works with both implementations 