# Development Standards - Single Source of Truth

**Status:** ACTIVE - SINGLE SOURCE FOR ALL DEVELOPMENT STANDARDS  
**Last Updated:** January 2025 - Clean Architecture Migration Complete  
**Priority:** HIGHEST - FOLLOW THESE RULES STRICTLY

## 🎯 Overview

This document is the **single source of truth** for all development standards in the KICKAI project. It consolidates tool implementation standards, service layer architecture, coding patterns, and best practices into one authoritative location.

### 🎉 **Clean Architecture Migration Complete (January 2025)**

KICKAI has achieved **complete Clean Architecture compliance** through systematic migration:

- **✅ 62 @tool decorators migrated** from domain to application layer
- **✅ Zero framework dependencies** in domain layer
- **✅ Pure business logic** preserved in domain functions
- **✅ Framework isolation** achieved throughout system

**📋 For related information, see:**
- **Architecture**: [01_architecture.md](01_architecture.md)
- **Commands**: [08_command_system.md](08_command_system.md)
- **Testing**: [05_testing_and_quality.md](05_testing_and_quality.md)

## 🚨 CRITICAL RULES - NEVER VIOLATE

### 1. **Tool Implementation Standards (MANDATORY)**

**CRITICAL**: All tools must follow CrewAI best practices with direct parameter passing:

- **✅ ALWAYS**: Use `@tool` decorator from `crewai.tools`
- **✅ ALWAYS**: Use `async def` for all tool functions
- **✅ ALWAYS**: Use direct parameter passing with type hints
- **✅ ALWAYS**: Tools are simple, independent functions
- **❌ NEVER**: Dictionary-based parameter passing
- **❌ NEVER**: Backward compatibility code in tools
- **❌ NEVER**: Tools calling other tools or services directly

```python
# ❌ WRONG - Dictionary parameter passing (CAUSES VALIDATION ERRORS)
@tool("add_team_member")
async def add_team_member(input_data: dict) -> str:
    telegram_id = input_data.get('telegram_id')
    # DON'T DO THIS - causes Pydantic validation issues

# ✅ CORRECT - Direct parameter passing with async
@tool("add_team_member_simplified", result_as_answer=True)
async def add_team_member_simplified(
    telegram_id: int, 
    team_id: str, 
    username: str, 
    chat_type: str, 
    player_name: str, 
    phone_number: str
) -> str:
    """
    Tool description with comprehensive documentation.
    
    Args:
        telegram_id (int): Admin's Telegram ID
        team_id (str): Team identifier
        username (str): Admin's username
        chat_type (str): Chat type (must be 'leadership')
        player_name (str): Team member's full name
        phone_number (str): Team member's phone number
        
    Returns:
        JSON string with success/error status and formatted message
    """
    try:
        # Input validation
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error)
        
        # Business logic here
        result = await team_service.add_member(telegram_id, team_id, player_name, phone_number)
        
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"❌ Error in add_team_member_simplified: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Failed to add team member")
```

### 2. **Service Layer Architecture (MANDATORY)**

**CRITICAL**: Services must use domain models and repository interfaces, never direct database calls:

- **❌ NEVER**: Services calling database directly (Firebase, Firestore, etc.)
- **❌ NEVER**: Services using raw database clients or SDKs
- **✅ ALWAYS**: Services use domain models (Player, Team, Match, etc.)
- **✅ ALWAYS**: Services use repository interfaces (PlayerRepositoryInterface, etc.)
- **✅ ALWAYS**: Services work with domain entities, not raw data
- **✅ ALWAYS**: Database operations handled by repository implementations

```python
# ❌ WRONG - Service calling database directly
class PlayerService:
    def __init__(self, firebase_client):
        self.firebase_client = firebase_client  # DON'T DO THIS
    
    async def get_player(self, player_id: str):
        # Direct database call - VIOLATION
        doc = await self.firebase_client.get_document("players", player_id)
        return doc  # Raw data, not domain model

# ✅ CORRECT - Service using domain models and repository
class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):
        self.player_repository = player_repository  # Repository interface
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        # Uses repository interface, returns domain model
        return await self.player_repository.get_player_by_id(player_id)
    
    async def create_player(self, player: Player) -> Player:
        # Works with domain model, uses repository
        return await self.player_repository.create_player(player)
```

### 3. **Domain Model Usage (MANDATORY)**

**CRITICAL**: All business logic must work with domain models:

```python
# ✅ CORRECT - Domain model usage in services
from kickai.features.player_registration.domain.entities.player import Player

class PlayerService:
    async def register_player(self, name: str, phone: str, team_id: str) -> Player:
        # Create domain model with business logic
        player = Player(
            player_id=generate_player_id(name),
            name=name,
            phone_number=phone,
            team_id=team_id,
            status="pending",
            created_at=datetime.now()
        )
        
        # Validate domain model
        player.validate()
        
        # Save via repository
        return await self.player_repository.create_player(player)
    
    async def approve_player(self, player_id: str) -> Player:
        # Get domain model
        player = await self.player_repository.get_player_by_id(player_id)
        if not player:
            raise PlayerNotFoundError(f"Player {player_id} not found")
        
        # Update domain model with business logic
        player.approve()  # Domain model method
        player.updated_at = datetime.now()
        
        # Save via repository
        return await self.player_repository.update_player(player)
```

### 4. **Tool Independence (MANDATORY)**

**CRITICAL**: Tools must be completely independent functions:

- **❌ NEVER**: Tools calling other tools or services directly
- **✅ ALWAYS**: Tools are simple, independent async functions
- **✅ ALWAYS**: Use direct parameter passing with type hints
- **✅ ALWAYS**: Tools return simple string responses
- **Rationale**: CrewAI tools must be lightweight and independent to work properly

```python
# ❌ WRONG - Tool calling services directly
@tool("get_available_commands")
async def get_available_commands(telegram_id: str, chat_type: str) -> str:
    service = get_container().get(PlayerService)  # DON'T DO THIS
    return await service.get_commands(telegram_id)

# ✅ CORRECT - Independent tool with direct parameters
@tool("get_available_commands")
async def get_available_commands(telegram_id: str, chat_type: str) -> str:
    if chat_type == "main_chat":
        return "Available commands: /register, /help, /status"
    return "Leadership commands: /approve, /reject, /list"
```

### 5. **System Validation: Synchronous & Sequential (MANDATORY)**

**CRITICAL**: Use synchronous, sequential validation for startup:

- **❌ NEVER**: Mix sync/async patterns in system validation
- **✅ ALWAYS**: Use synchronous, sequential validation for startup
- **Rationale**: Predictable startup, no race conditions, safe operation

```python
# ❌ WRONG - Inconsistent validation patterns
env_result = self.environment_validator.validate_environment()  # SYNC
db_result = await self.database_validator.validate_database()  # ASYNC
registry_result = self.registry_validator.validate_all_registries()  # SYNC

# ✅ CORRECT - Synchronous validation for startup
def validate_system_startup(self) -> ComprehensiveValidationResult:
    env_result = self.environment_validator.validate_environment()
    db_result = self.database_validator.validate_database()
    registry_result = self.registry_validator.validate_all_registries()
    return ComprehensiveValidationResult(...)
```

### 6. **CrewAI Operations: Context-Appropriate Patterns (MANDATORY)**

**CRITICAL**: Use appropriate patterns for different operations:

- **Agent Creation**: Synchronous (CrewAI standard)
- **Task Execution**: Asynchronous (CrewAI standard)
- **Tool Definitions**: Asynchronous for all tools (new standard)
- **Service Layer**: Asynchronous for I/O operations

```python
# ✅ CORRECT - CrewAI patterns
# Agent creation (sync)
agent = Agent(role="Assistant", goal="Help users")

# Task execution (async)
result = await crew.execute_task(task_description)

# Tool definitions (async for all tools)
@tool("async_tool")
async def async_tool(param1: str, param2: int) -> str:  # ASYNC for all tools
    result = await database.query(param1, param2)
    return result
```

### 7. **Absolute Imports with PYTHONPATH (MANDATORY)**

**CRITICAL**: Always use absolute imports and proper environment setup:

- **ALWAYS** use absolute imports: `from src.features...`
- **ALWAYS** set `PYTHONPATH=src` when running scripts
- **ALWAYS** activate virtual environment: `source venv311/bin/activate`

```bash
# ✅ CORRECT - Always use this pattern
source venv311/bin/activate && PYTHONPATH=src python run_bot_local.py
```

### 8. **Error Handling Patterns (MANDATORY)**

**CRITICAL**: Use consistent error handling patterns:

```python
# ✅ CORRECT - Standard error handling pattern
@tool("tool_name", result_as_answer=True)
async def tool_name(param1: str, param2: int) -> str:
    """
    Tool description with comprehensive documentation.
    
    Args:
        param1 (str): Description of parameter 1
        param2 (int): Description of parameter 2
        
    Returns:
        JSON string with success/error status and formatted message
    """
    try:
        # Input validation
        validation_error = validate_required_input(param1, "Parameter 1")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error)
        
        # Business logic here
        result = await some_service_method(param1, param2)
        
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"❌ Error in tool_name: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Tool execution failed")
```

## 📋 **Implementation Standards**

### **Function Structure**

```python
@tool("tool_name", result_as_answer=True)
async def tool_function(
    telegram_id: int, 
    team_id: str, 
    username: str, 
    chat_type: str, 
    **kwargs
) -> str:
    """
    Tool description following docstring standards.
    
    Args:
        telegram_id (int): Telegram ID of the requesting user
        team_id (str): Team ID (required) - available from context
        username (str): Username of the requesting user
        chat_type (str): Chat type context
        **kwargs: Additional tool-specific parameters
        
    Returns:
        JSON response string with result or error
    """
    try:
        # 1. Input validation
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return create_json_response(ResponseStatus.ERROR, message=validation_error)
        
        # 2. Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id}
        log_tool_execution("tool_name", inputs, True)
        
        # 3. Get services from container
        container = get_container()
        service = container.get_service(ServiceClass)
        
        if not service:
            return create_json_response(ResponseStatus.ERROR, message="Service is not available")
        
        # 4. Business logic
        result = await service.method_name(telegram_id, team_id, **kwargs)
        
        # 5. Return success response
        return create_json_response(ResponseStatus.SUCCESS, data=result)
        
    except Exception as e:
        logger.error(f"❌ Error in tool_name: {e}")
        return create_json_response(ResponseStatus.ERROR, message="Tool execution failed")
```

### **Repository Pattern**

**MANDATORY**: Use repository interfaces for all data access:

```python
# ✅ CORRECT - Repository interface usage
from kickai.features.player_registration.domain.repositories.player_repository_interface import (
    PlayerRepositoryInterface,
)

class PlayerService:
    def __init__(self, player_repository: PlayerRepositoryInterface):
        self.player_repository = player_repository
    
    async def get_all_players(self, team_id: str) -> List[Player]:
        # Uses repository interface
        return await self.player_repository.get_players_by_team(team_id)
    
    async def update_player_status(self, player_id: str, status: str) -> Player:
        # Get domain model
        player = await self.player_repository.get_player_by_id(player_id)
        if not player:
            raise PlayerNotFoundError(f"Player {player_id} not found")
        
        # Update domain model
        player.status = status
        player.updated_at = datetime.now()
        
        # Save via repository
        return await self.player_repository.update_player(player)
```

## 🚫 **FORBIDDEN PATTERNS**

### **1. Dictionary Parameters**
```python
# ❌ WRONG - Causes validation errors
async def tool_name(input_data: dict) -> str:
    param1 = input_data.get('param1')
```

### **2. Backward Compatibility**
```python
# ❌ WRONG - Don't include legacy code
if isinstance(first_param, dict):
    # Legacy handling code
```

### **3. Tool-to-Tool Calls**
```python
# ❌ WRONG - Tools calling other tools
async def tool_name(param1: str) -> str:
    result = await another_tool(param1)  # DON'T DO THIS
```

### **4. Sync Functions**
```python
# ❌ WRONG - Use async for all tools
def tool_name(param1: str) -> str:
    return "result"
```

### **5. Direct Database Calls in Services**
```python
# ❌ WRONG - Service calling database directly
class PlayerService:
    def __init__(self, firebase_client):
        self.firebase_client = firebase_client  # DON'T DO THIS
    
    async def get_player(self, player_id: str):
        # Direct database call - VIOLATION
        doc = await self.firebase_client.get_document("players", player_id)
        return doc  # Raw data, not domain model
```

## 📋 **Migration Checklist**

When updating existing tools:

- [ ] Change function signature to `async def`
- [ ] Replace dictionary parameters with individual parameters
- [ ] Add type hints to all parameters
- [ ] Update docstring with proper Args section
- [ ] Remove any backward compatibility code
- [ ] Ensure single try/except boundary
- [ ] Use `create_json_response()` for all responses
- [ ] Add proper error logging
- [ ] Test with CrewAI parameter validation

When updating existing services:

- [ ] Replace direct database calls with repository interfaces
- [ ] Use domain models for all business logic
- [ ] Inject repository dependencies instead of database clients
- [ ] Return domain models instead of raw data
- [ ] Add proper error handling and validation
- [ ] Update tests to use repository mocks

## 🎯 **Benefits of These Standards**

### **1. CrewAI Compatibility**
- Direct parameter passing works with CrewAI's validation
- No more Pydantic validation errors
- Proper async support for performance

### **2. Code Quality**
- Clean, modern implementation
- No backward compatibility bloat
- Clear parameter types and validation

### **3. Maintainability**
- Consistent patterns across all tools and services
- Easy to understand and modify
- Proper error handling and logging

### **4. Performance**
- Async functions for better I/O handling
- Direct parameter access (no dictionary lookups)
- Efficient validation and processing

### **5. Clean Architecture**
- Proper separation of concerns
- Domain models contain business logic
- Repository pattern for data access
- Testable and maintainable code

---

**📋 For related information, see:**
- **Architecture**: [01_architecture.md](01_architecture.md)
- **Commands**: [08_command_system.md](08_command_system.md)
- **Testing**: [05_testing_and_quality.md](05_testing_and_quality.md)
