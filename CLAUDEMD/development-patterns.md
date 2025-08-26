# Development Patterns - Architecture & Coding Standards

## Project Architecture (Clean Architecture)

### Layer Structure & Dependency Rules
The KICKAI project follows Uncle Bob's Clean Architecture with strict dependency inversion:

```
┌─────────────────────────────────────────────────────────────┐
│                    OUTER LAYERS                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            INTERFACE ADAPTERS                       │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │              USE CASES                      │    │    │
│  │  │  ┌─────────────────────────────────────┐    │    │    │
│  │  │  │            ENTITIES                 │    │    │    │
│  │  │  │         (Domain Core)              │    │    │    │
│  │  │  └─────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────┐    │
└─────────────────────────────────────────────────────────────┘
```

### KICKAI Layer Mapping
```
kickai/
├── agents/                        # Framework Layer (CrewAI integration)
├── features/<feature>/            # Feature-first organization
│   ├── application/commands/      # Use Cases Layer (@command decorators)
│   ├── domain/                   # Core Business Logic (INNERMOST)
│   │   ├── entities/             # Entities (Domain Models)
│   │   ├── services/             # Use Cases (Business Logic)
│   │   ├── repositories/         # Interface Adapters (Abstractions)
│   │   └── tools/               # Use Cases (@tool decorators)
│   └── infrastructure/           # Framework Layer (Database, External APIs)
├── config/                       # Framework Layer (Configuration)
├── core/                        # Interface Adapters (DI, shared interfaces)
└── database/                    # Framework Layer (Firebase integration)
```

### Dependency Flow Rules (STRICTLY ENFORCED)
1. **Inward Dependencies Only**: All source code dependencies point toward the center
2. **Layer Isolation**: Inner layers have ZERO knowledge of outer layers
3. **Dependency Inversion**: Use interfaces and abstractions for boundary crossing

## Clean Architecture Compliance Analysis

### ✅ **GOOD PRACTICES** - Following Clean Architecture Rules

**Proper Dependency Inversion:**
```python
# ✅ Domain Service depends on abstraction, not concrete implementation
class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):  # Interface dependency
        self.player_repository = player_repository
```

**Repository Pattern Implementation:**
```python
# ✅ Abstract interface in domain layer
class PlayerRepositoryInterface(ABC):
    @abstractmethod
    async def get_player_by_id(self, player_id: str, team_id: str) -> Optional[Player]:
        pass

# ✅ Concrete implementation in infrastructure layer
class FirebasePlayerRepository(PlayerRepositoryInterface):
    def __init__(self, database: DataStoreInterface):  # Depends on abstraction
        self.database = database
```

**Dependency Injection Container:**
```python
# ✅ Proper dependency injection at application boundaries
@tool("tool_name", result_as_answer=True)
async def tool_name(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    container = get_container()  # DI at boundary
    service = container.get_service(ServiceClass)  # Interface resolution
    result = await service.method_name(param=value)  # Pure business logic
```

### ✅ **VIOLATIONS RESOLVED** - Clean Architecture Migration Complete (January 2025)

**Previously resolved violations:**

**Direct Database Access in Domain Services:**
```python
# ✅ RESOLVED: Domain service now uses repository pattern
class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):
        self.player_repository = player_repository  # Pure interface dependency
    
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str):
        return await self.player_repository.get_player_by_telegram_id(telegram_id, team_id)
```

**Framework Dependencies in Domain Layer:**
```python
# ✅ RESOLVED: Domain functions are now pure (no @tool decorators)
# Domain layer: kickai/features/*/domain/tools/example_tools.py
async def approve_player(...):  # Pure domain function
    """Pure business logic with no framework dependencies."""
    # Business logic only

# Application layer: kickai/features/*/application/tools/example_tools.py  
@tool("approve_player", result_as_answer=True)  # Framework decorator
async def approve_player_tool(...):  # Application layer tool
    return await approve_player(...)  # Delegates to domain function
```

**Container Dependencies in Domain:**
```python
# ✅ RESOLVED: Domain services use constructor injection
class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):
        # No container knowledge - pure dependency injection
        self.player_repository = player_repository
```

### ✅ **ARCHITECTURAL IMPROVEMENTS COMPLETED** (January 2025)

All recommended fixes have been implemented through comprehensive Clean Architecture migration:

1. ✅ **Framework Integration Moved to Application Layer**
   - **62 @tool decorators migrated** from `domain/tools/` to `application/tools/` 
   - Pure domain logic preserved in `domain/tools/` functions
   - Complete adapter pattern implementation with delegation

2. ✅ **Database Access Eliminated from Domain**
   - All database access now goes through repository interfaces
   - `get_database()` calls removed from domain services
   - Repository interfaces expanded to cover all operations

3. ✅ **Pure Dependency Injection Implemented**
   - Domain services only know about interfaces
   - Container access limited to application boundaries  
   - Constructor injection pattern implemented throughout

## Proper Clean Architecture Implementation

### Ideal Layer Structure
```
Application Layer (Tools/Commands)    ──→  Domain Interfaces
      │                                         │
      ▼                                         ▼
Domain Services  ──→  Domain Entities    ←──  Repository Interfaces
      │                                         │
      ▼                                         ▼
Infrastructure Layer (Database, APIs)    ────►
```

### Dependency Direction Rules
1. **Domain Layer**: Pure business logic, no external dependencies
   - `entities/`: Domain models with business rules
   - `services/`: Business logic and use cases
   - `repositories/interfaces.py`: Abstract contracts

2. **Application Layer**: Orchestrates domain operations
   - `commands/`: Entry points (`@command`, `@tool`)
   - Depends on: Domain interfaces only
   - Knows about: Framework requirements (CrewAI)

3. **Infrastructure Layer**: Technical implementation
   - `repositories/`: Concrete database implementations
   - Depends on: Domain interfaces, external libraries
   - Implements: All domain interfaces

### Boundary Crossing Pattern
```python
# ✅ CORRECT: Application layer orchestrates, domain executes
@tool("get_player_status")
async def get_player_status_tool(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    """Application boundary - handles framework concerns"""
    try:
        # DI resolution at application boundary
        container = get_container()
        player_service = container.get_service(IPlayerService)
        
        # Pure domain operation
        player = await player_service.get_player_by_telegram_id(telegram_id, team_id)
        
        # Application layer formats response for framework
        return create_json_response(ResponseStatus.SUCCESS, data=player_data)
    except Exception as e:
        return create_json_response(ResponseStatus.ERROR, message=str(e))

# ✅ CORRECT: Pure domain service
class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):
        """Pure dependency injection - no container knowledge"""
        self.player_repository = player_repository
    
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[Player]:
        """Pure business logic - no framework knowledge"""
        return await self.player_repository.get_player_by_telegram_id(telegram_id, team_id)
```

### Data Flow Rules
- **Simple Data Structures**: Pass DTOs/primitives across boundaries
- **No Entity Leakage**: Domain entities stay within domain boundary
- **Interface Contracts**: Define clear contracts for all boundary crossings

## Tool Development Pattern (MANDATORY)
```python
from crewai.tools import tool
from kickai.core.dependency_container import get_container
from kickai.core.enums import ResponseStatus  
from kickai.utils.tool_helpers import create_json_response

@tool("tool_name", result_as_answer=True)
async def tool_name(
    telegram_id: int,        # MUST be int, not string
    team_id: str, 
    username: str,
    chat_type: str,          # "main", "leadership", "private"
    # ... tool-specific parameters
) -> str:
    """Tool description with clear parameter expectations."""
    try:
        # 1. Get services from dependency container
        container = get_container()
        service = container.get_service(ServiceClass)
        
        # 2. Call service method with await
        result = await service.method_name(param=value)
        
        # 3. Return standardized JSON response
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"Error in tool_name: {e}")
        return create_json_response(ResponseStatus.ERROR, message=str(e))
```

## Clean Architecture Implementation Status ✅

**COMPLETED:** Full Clean Architecture refactoring with Uncle Bob's dependency rules (January 2025)

### Implementation Results (100% Compliant)
- ✅ **Tools Migration:** **62 tools migrated** from `domain/tools/` to `application/tools/`
- ✅ **Repository Pattern:** Complete interfaces created in domain layer
- ✅ **Dependency Inversion:** All `get_container()` calls removed from domain services  
- ✅ **Infrastructure Layer:** Firebase repositories with proper abstractions
- ✅ **Layer Separation:** Clean boundaries between application, domain, and infrastructure
- ✅ **Framework Isolation:** Zero framework dependencies in domain layer
- ✅ **Business Logic Preservation:** All domain functions maintained functionality

### Migrated Features (Complete Coverage)
- ✅ **team_administration**: 18 tools migrated
- ✅ **shared**: 11 tools migrated  
- ✅ **communication**: 4 tools migrated
- ✅ **match_management**: 17 tools migrated
- ✅ **system_infrastructure**: 2 tools migrated
- ✅ **player_registration**: 10 tools migrated

### Current Clean Architecture Structure
```
kickai/features/<feature>/
├── application/tools/          # ✅ CrewAI @tool decorators (Framework Layer)
├── domain/
│   ├── entities/              # ✅ Pure business objects
│   ├── services/              # ✅ Pure business logic (no framework deps)
│   ├── tools/                 # ✅ Pure domain functions (no @tool decorators)
│   └── repositories/          # ✅ Abstract interfaces
└── infrastructure/            # ✅ Firebase implementations
```

### Domain Layer Exports (All Features)
```python
# All domain/tools/__init__.py files now have:
__all__ = []  # No exports - Complete Clean Architecture compliance
```

## Absolute Development Rules
- **Always:** Tools in `application/tools/`, dependency injection via `get_container()`
- **Always:** Domain services use constructor injection, NO container dependencies  
- **Always:** Use `async def` for tools, `ResponseStatus` enum, `PYTHONPATH=.` when running
- **Always:** Use absolute imports (`from kickai.core...`) - no relative imports  
- **Never:** Use `asyncio.run()` inside tools (causes event loop conflicts)
- **Never:** `get_container()` in domain layer - domain services are pure business logic
- **Never:** Direct database access from tools - always use service layer
- **Types:** `telegram_id` must be `int` type, `team_id` is `str`

## Service Layer Pattern
```python
class ExampleService:
    def __init__(self, repository: RepositoryInterface):
        self.repository = repository
        
    async def get_item(self, *, item_id: str) -> Optional[DomainModel]:
        """Service methods are async and use keyword arguments."""
        return await self.repository.get_by_id(item_id)
```

## Common Issues & Solutions

| Issue | Root Cause | Solution |
|-------|------------|----------|
| Tool not executing | Missing registration in feature `__init__.py` | Export tool from feature's `__init__.py` |
| Import errors | Missing PYTHONPATH | Always use `PYTHONPATH=.` when running |
| "User ID cannot be zero" | Mock service bot ID issue | Fixed in mock_telegram_service.py |
| Chat type conversion warnings | String vs enum mismatch | Fixed in bot_integration.py fallback class |
| Service not available | Container initialization | Check `ensure_container_initialized()` |
| Wrong agent routing | Command not in routing config | Add command to `command_routing.yaml` |
| Python version errors | Using Python < 3.11 | Must use Python 3.11+ with `venv311` |
| Emergency contact errors | Using legacy field | Use separate `name` + `phone` fields |