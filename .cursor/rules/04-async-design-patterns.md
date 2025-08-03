# Async/Sync Design Patterns for KICKAI

## Principle: Context-Appropriate Async/Sync Patterns

### **System Validation: Synchronous & Sequential**
- **System startup validation** must be **synchronous and sequential**
- **Bot startup** is blocked until ALL validation passes
- **No async patterns** for critical startup validation
- **Fail-fast approach** - critical failures prevent bot startup

```python
# ✅ CORRECT - Synchronous validation for startup
def validate_system_startup(self) -> ComprehensiveValidationResult:
    """Synchronous comprehensive validation."""
    
    # Phase 1: Environment (sync)
    env_result = self.environment_validator.validate_environment()
    
    # Phase 2: Database (sync)
    db_result = self.database_validator.validate_database()
    
    # Phase 3: Registry (sync)
    registry_result = self.registry_validator.validate_all_registries()
    
    return ComprehensiveValidationResult(...)
```

### **CrewAI Operations: Async Patterns**
- **Agent creation** is **synchronous** (CrewAI standard)
- **Task execution** is **asynchronous** (CrewAI standard)
- **Tool execution** can be **sync or async** depending on operation type
- **Telegram handlers** should be **async** for I/O operations

```python
# ✅ CORRECT - CrewAI patterns
# Agent creation (sync)
agent = Agent(role="Assistant", goal="Help users")

# Task execution (async)
result = await crew.execute_task(task_description)

# Tool definitions (mixed)
@tool("sync_tool")
def sync_tool() -> str:  # SYNC for simple computations
    return "result"

@tool("async_tool")
async def async_tool() -> str:  # ASYNC for I/O operations
    result = await database.query()
    return result
```

### **Service Layer: Async for I/O**
- All service methods that perform I/O (database, network, LLM, etc.) **must be async**
- Never call `asyncio.run()` inside the bot, agent, or handler code
- If you must call sync code from async, use `await loop.run_in_executor(...)`

```python
# ✅ CORRECT - Async service layer
class PlayerService:
    async def create_player(self, player_data: dict) -> Player:
        # Database operation - async
        player_id = await self.repository.create(player_data)
        return await self.repository.get_by_id(player_id)
    
    async def get_players(self, team_id: str) -> List[Player]:
        # Database operation - async
        return await self.repository.get_by_team(team_id)
```

## Pattern: CQRS + Async Service Layer
- Define clear async interfaces for all operations that may touch the network, database, or external APIs
- Use dependency injection to provide these services to your agents/tools/handlers
- All command/query operations should be async and use `await`

## Pattern: Adapter for Legacy Sync Code
- If you have legacy sync code, wrap it in an async adapter using `run_in_executor`
- This keeps the async/sync boundary explicit and safe

## Summary Table
| Context | Pattern | What to do | Why? |
|---------|---------|------------|------|
| **System Validation** | Synchronous | Make all validation sync, sequential | Predictable startup, no race conditions |
| **Agent Creation** | Synchronous | Create agents with sync patterns | CrewAI standard |
| **Task Execution** | Asynchronous | Use async for task execution | CrewAI standard |
| **Tool Definitions** | Mixed | Sync for simple ops, async for I/O | Performance and clarity |
| **Service Layer** | Asynchronous | Make all I/O methods async | Prevents event loop issues |
| **Telegram Handlers** | Asynchronous | Use async for handlers | Proper I/O handling |

## Migration Checklist
- [x] **System validation is synchronous** - ✅ COMPLETED
- [x] **Agent creation is synchronous** - ✅ COMPLETED  
- [x] **Task execution is asynchronous** - ✅ COMPLETED
- [ ] Refactor all service methods to be async if they perform I/O
- [ ] Update all callers to use `await` for async operations
- [ ] Remove all `asyncio.run()` from the codebase (except CLI/test entry points)
- [ ] Use `run_in_executor` for any sync code that must be called from async
- [ ] Add type hints and docstrings to clarify which methods are async

## Critical Rules

### **❌ NEVER DO: Mix Sync/Async in Validation**
```python
# ❌ WRONG - Inconsistent patterns
env_result = self.environment_validator.validate_environment()  # SYNC
db_result = await self.database_validator.validate_database()  # ASYNC
registry_result = self.registry_validator.validate_all_registries()  # SYNC
```

### **❌ NEVER DO: Async-First for Startup**
```python
# ❌ WRONG - Not recommended for startup validation
async def validate_system_startup(self):
    # This creates complexity and potential race conditions
    # during critical startup phase
```

### **✅ ALWAYS DO: Context-Appropriate Patterns**
```python
# ✅ CORRECT - Synchronous validation for startup
def validate_system_startup(self) -> ComprehensiveValidationResult:
    # All validation is synchronous and sequential
    # Bot startup is blocked until ALL validation passes
    pass

# ✅ CORRECT - Async for I/O operations
async def create_player(self, player_data: dict) -> Player:
    # Database operations are async
    pass
``` 