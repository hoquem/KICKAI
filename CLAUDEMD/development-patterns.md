# Development Patterns - Clean Architecture Guide

## Layer Structure (Clean Architecture ✅)
```
kickai/features/[feature]/
├── application/tools/     # @tool decorators (CrewAI interface)
├── domain/
│   ├── entities/         # Business objects
│   ├── services/         # Pure business logic
│   └── repositories/     # Abstract interfaces
└── infrastructure/       # Firebase, external APIs
```

**Rules:** Domain → no external deps | Application → uses domain | Infrastructure → implements domain interfaces

## Development Patterns

### Tool Implementation (Standard Pattern)
```python
# Application: features/*/application/tools/
@tool("name", result_as_answer=True)
async def name(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    return await name_domain(telegram_id, team_id, username, chat_type)

# Domain: features/*/domain/tools/ (no @tool decorator)
async def name_domain(telegram_id: int, team_id: str, username: str, chat_type: str) -> str:
    service = get_container().get_service(ServiceClass)
    result = await service.method()
    return create_json_response(ResponseStatus.SUCCESS, data=result)
```

### Service Implementation Pattern
```python
# Domain service with dependency injection
class PlayerService:
    def __init__(self, repository: PlayerRepositoryInterface):
        self.repository = repository
    
    async def get_by_telegram_id(self, telegram_id: int, team_id: str):
        return await self.repository.get_player_by_telegram_id(telegram_id, team_id)

# Repository interface (domain)
class PlayerRepositoryInterface(ABC):
    @abstractmethod
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str) -> Optional[Player]:
        pass

# Repository implementation (infrastructure)
class FirebasePlayerRepository(PlayerRepositoryInterface):
    def __init__(self, database: DataStoreInterface):
        self.database = database
        
    async def get_player_by_telegram_id(self, telegram_id: int, team_id: str):
        # Firebase implementation
        pass
```

### Entity Pattern
```python
@dataclass
class Player:
    id: str
    team_id: str
    telegram_id: int
    name: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tool not found | Export from feature `__init__.py` |
| Import errors | Always use `PYTHONPATH=.` |
| Service unavailable | Check container initialization |
| Async errors | Use `async def` for all tools |
| Type errors | `telegram_id` must be `int`, `team_id` is `str` |

## Testing Patterns
```python
# Unit test (domain)
@pytest.mark.asyncio
async def test_service_logic():
    mock_repo = Mock()
    service = PlayerService(mock_repo)
    result = await service.get_by_telegram_id(123, "TEST")
    mock_repo.get_player_by_telegram_id.assert_called_once()

# Integration test (tool)  
@pytest.mark.asyncio
async def test_tool_integration():
    result = await tool_name(123456789, "TEST", "user", "main")
    assert '"status": "success"' in result
```

**Migration Status:** ✅ 62 @tool decorators moved to application layer, clean architecture complete