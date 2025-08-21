# Development Patterns - Architecture & Coding Standards

## Project Architecture (Clean Architecture)
```
kickai/
├── agents/                        # 6-agent CrewAI native collaboration system
├── features/<feature>/            # Domain-driven feature modules
│   ├── application/commands/      # @command decorators
│   ├── domain/tools/             # @tool decorators (async only)
│   ├── domain/services/          # Business logic (async)  
│   ├── domain/entities/          # Domain models
│   └── infrastructure/           # Repositories, external APIs
├── config/                       # agents.yaml, tasks.yaml, command_routing.yaml
├── core/                        # DI container, enums, types
└── database/                    # Firebase integration
```

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

## Absolute Development Rules
- **Always:** Use `async def` for tools, `ResponseStatus` enum, `PYTHONPATH=.` when running
- **Always:** Use dependency injection via `get_container()` - no direct database access
- **Always:** Use absolute imports (`from kickai.core...`) - no relative imports  
- **Never:** Use `asyncio.run()` inside tools (causes event loop conflicts)
- **Never:** Use legacy `emergency_contact` field - use `emergency_contact_name` + `emergency_contact_phone`
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