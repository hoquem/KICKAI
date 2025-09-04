# CrewAI Tool Guidelines - KICKAI Standards

**CRITICAL RULES - MUST NEVER BE FORGOTTEN**

## Core Principles

### 1. Parameter Passing (CRITICAL)
- **CrewAI passes parameters DIRECTLY** to tool functions via function signature
- **NO `**kwargs` parameter extraction** - use explicit parameters
- **Parameters are matched by name** from agent calls to function arguments

```python
# ✅ CORRECT - Direct parameter passing
@tool("get_player_info")
async def get_player_info(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    player_id: str
) -> str:
    """Get player information."""
    # Parameters come directly - no extraction needed
    
# ❌ WRONG - Never use **kwargs extraction
@tool("get_player_info")
async def get_player_info(**kwargs) -> str:
    player_id = kwargs.get('player_id')  # DON'T DO THIS
```

### 2. Tool Docstrings (CRITICAL)
- **First line**: Clear, concise tool purpose
- **Args section**: Every parameter with clear description
- **Returns section**: What format the output will be
- **Help agents understand** what the tool does and how to use it

```python
@tool("approve_player")
async def approve_player(
    telegram_id: str,  # Only if tool needs user identity for audit
    team_id: str,      # Required for team context
    player_id: str,    # Required - which player to approve
    # username and chat_type omitted if not needed by business logic
) -> str:
    """
    Approve a player for match squad selection.

    This tool handles player approval functionality, changing player status
    from pending to active for squad selection eligibility.

    Args:
        telegram_id: User's Telegram ID (string) - required for audit trail
        team_id: Team identifier - required for team context
        player_id: Player ID to approve - required

    Returns:
        Success message with approval confirmation or error message
    """
```

### 3. Only Required Parameters (CRITICAL)
- **Include only parameters the tool actually needs**
- **Use default values** for optional parameters
- **Don't include unused parameters** just for consistency

```python
# ✅ CORRECT - Only needed parameters
@tool("get_system_status")
async def get_system_status() -> str:
    """Get current system status."""
    # No parameters needed
    
# ✅ CORRECT - Required + optional parameters
@tool("list_players")
async def list_players(team_id: str, status: str = "all") -> str:
    """List players with optional status filter."""
    
# ✅ CORRECT - No unnecessary parameters
@tool("get_system_status")
async def get_system_status() -> str:
    """Get system status - no parameters needed!"""
    
# ❌ WRONG - Including unused parameters
@tool("get_system_status_wrong")
async def get_system_status_wrong(telegram_id: str, username: str, chat_type: str) -> str:
    """Get system status - doesn't need these parameters!"""
```

### 4. Plain Text Responses (CRITICAL)
- **Return clear, formatted plain text** that agents can understand
- **Use emojis and formatting** for user-friendly display
- **NO complex JSON objects** or data structures
- **Agents must be able to read and potentially display the response**

```python
# ✅ CORRECT - Plain text with formatting
return f"""📋 Player Information: {player.name}

🆔 ID: {player.player_id}
📞 Phone: {player.phone_number}
⚽ Position: {player.position}
📊 Status: {player.status}

✅ Player found successfully"""

# ❌ WRONG - Complex objects agents can't use
return {
    "status": "success",
    "data": {
        "player": player_object,
        "metadata": complex_data
    }
}
```

### 5. Exception Handling (CRITICAL)
- **NO EXCEPTIONS SHOULD EVER LEAVE TOOLS**
- **Catch ALL possible exceptions**
- **Return user-friendly error messages as strings**
- **Log technical details** but don't expose them to users

```python
@tool("example_tool")
async def example_tool(param: str) -> str:
    """Example tool with proper exception handling."""
    try:
        # Validate inputs first
        if not param:
            return "❌ Parameter is required"
        
        # Business logic that might fail
        result = await some_operation(param)
        
        if result:
            return f"✅ Operation successful: {result}"
        else:
            return "❌ Operation failed - please try again"
            
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        return f"❌ Invalid input: {str(e)}"
    except ConnectionError as e:
        logger.error(f"❌ Connection error: {e}")
        return "❌ Unable to connect to service - please try again later"
    except Exception as e:
        logger.error(f"❌ Unexpected error in example_tool: {e}")
        return f"❌ An error occurred: {str(e)}"
```

## Naming Conventions

### Tool Names
- **Pattern**: `[action]_[entity]_[modifier]`
- **Examples**: `get_player_info`, `list_players_active`, `show_help_commands`
- **Function name must match tool name**

```python
# ✅ CORRECT
@tool("approve_player")
async def approve_player(...) -> str:

# ✅ CORRECT  
@tool("list_players_active")
async def list_players_active(...) -> str:

# ❌ WRONG - Name mismatch
@tool("approve_player") 
async def do_player_approval(...) -> str:
```

### Function Naming
- **snake_case** for function names
- **Match tool name exactly**
- **Clear, descriptive names**

## Parameter Validation Patterns

### Required Parameter Validation
```python
@tool("example_tool")
async def example_tool(required_param: str, optional_param: str = "default") -> str:
    """Example with parameter validation."""
    try:
        # Validate required parameters
        if not required_param or not required_param.strip():
            return "❌ Required parameter is missing or empty"
        
        # Safe type conversion
        if isinstance(required_param, str):
            required_param = required_param.strip()
        
        # Business logic here...
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"❌ Failed: {str(e)}"
```

### Type Conversion Patterns
```python
# Safe integer conversion (only when tool needs it for database)
try:
    telegram_id_int = int(telegram_id) if telegram_id else 0
except (ValueError, TypeError):
    return "❌ Invalid telegram_id format"

# Safe string handling (only for parameters tool actually uses)
team_id = str(team_id) if team_id else ""
specific_param = str(specific_param) if specific_param else ""
```

## Response Formatting Standards

### Success Responses
```python
# User information
return f"""📋 **{player.name}** - Player Information

🆔 ID: {player.player_id}
📞 Phone: {player.phone_number}
⚽ Position: {player.position}
📊 Status: {player.status}

✅ Information retrieved successfully"""

# List responses
return f"""📋 **Active Players** ({len(players)} total)

1. ⚽ John Doe (Forward) - ID: P001
2. ⚽ Jane Smith (Midfielder) - ID: P002

✅ {len(players)} active players found"""

# Action confirmations
return f"✅ Player {player_id} approved successfully"
```

### Error Responses
```python
# Input validation errors
return "❌ Player ID is required"
return "❌ Team ID cannot be empty"
return "❌ Invalid telegram_id format"

# Business logic errors  
return f"❌ Player {player_id} not found in team {team_id}"
return "❌ You don't have permission to perform this action"

# System errors
return "❌ Service is currently unavailable - please try again later"
return f"❌ An error occurred: {str(e)}"
```

## Architecture Integration

### Container Pattern
```python
@tool("example_tool")
async def example_tool(param: str) -> str:
    """Example with proper container usage."""
    try:
        # Get container and services
        container = get_container()
        service = container.get_service(ServiceInterface)
        
        # Delegate to domain service
        result = await service.domain_operation(param)
        
        return f"✅ Operation completed: {result}"
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return f"❌ Failed: {str(e)}"
```

### Clean Architecture Compliance
- **Tools in application layer** (`/application/tools/`)
- **Delegate to domain services** (never access infrastructure directly)
- **Use dependency injection** via container
- **Handle framework concerns** in application layer

## Testing Considerations

### Tool Testing Pattern
```python
# Tools should be testable with direct parameter passing
async def test_tool():
    result = await example_tool("test_param")
    assert "✅" in result  # Success indicator
    assert isinstance(result, str)  # Always string response
```

## Performance Guidelines

### Response Size Limits
- **Keep responses under 2000 characters** when possible
- **Truncate long lists** with clear indication
- **Paginate large datasets** if needed

```python
# Limit response size
if len(formatted_response) > 2000:
    formatted_response = formatted_response[:1900] + "...\n\n(Response truncated)"
```

### Async Best Practices
- **Use async/await** for I/O operations
- **Don't mix sync/async** inappropriately
- **Handle async exceptions** properly

## Common Anti-Patterns to Avoid

### ❌ DON'T DO THESE:
1. **Parameter extraction from kwargs**
2. **Returning complex objects**
3. **Letting exceptions escape**
4. **Including unused parameters**
5. **Missing docstrings or poor documentation**
6. **Hardcoded values** instead of parameters
7. **Direct database access** (use services)
8. **Inconsistent response formats**

### ✅ DO THESE:
1. **Direct parameter passing**
2. **Plain text responses with formatting**
3. **Comprehensive exception handling**
4. **Only required parameters**
5. **Clear, helpful docstrings**
6. **Use dependency injection**
7. **Consistent response formatting**
8. **Proper logging for debugging**

## Tool Quality Checklist

Before committing any tool, verify:

- [ ] Parameters passed directly (no **kwargs)
- [ ] Complete docstring with Args and Returns
- [ ] Only required parameters included
- [ ] Plain text response format
- [ ] All exceptions caught and handled
- [ ] Proper naming convention followed
- [ ] Clean architecture compliance
- [ ] Container-based dependency injection
- [ ] User-friendly error messages
- [ ] Consistent response formatting

## Examples of Perfect Tools

### Information Retrieval Tool
```python
@tool("get_player_status")
async def get_player_status(player_id: str, team_id: str) -> str:
    """
    Get the current status of a specific player.

    Args:
        player_id: Player ID to check status for
        team_id: Team identifier

    Returns:
        Formatted player status information or error message
    """
    try:
        # Validate inputs
        if not player_id:
            return "❌ Player ID is required"
        if not team_id:
            return "❌ Team ID is required"
        
        # Get service and execute
        container = get_container()
        player_service = container.get_service(IPlayerService)
        player = await player_service.get_player(player_id, team_id)
        
        if player:
            return f"📊 Player {player.name} status: {player.status}"
        else:
            return f"❌ Player {player_id} not found in team {team_id}"
            
    except Exception as e:
        logger.error(f"❌ Error getting player status: {e}")
        return f"❌ Failed to get player status: {str(e)}"
```

### Action Tool
```python
@tool("approve_player")
async def approve_player(player_id: str, team_id: str, admin_id: str) -> str:
    """
    Approve a player for active status.

    Args:
        player_id: Player ID to approve
        team_id: Team identifier  
        admin_id: Admin performing the approval

    Returns:
        Approval confirmation message or error message
    """
    try:
        # Validate all required inputs
        if not player_id:
            return "❌ Player ID is required"
        if not team_id:
            return "❌ Team ID is required"
        if not admin_id:
            return "❌ Admin ID is required"
        
        # Execute approval
        container = get_container()
        player_service = container.get_service(IPlayerService)
        success = await player_service.approve_player(player_id, team_id)
        
        if success:
            logger.info(f"✅ Player {player_id} approved by {admin_id}")
            return f"✅ Player {player_id} approved successfully"
        else:
            return f"❌ Failed to approve player {player_id} - may not exist or already approved"
            
    except Exception as e:
        logger.error(f"❌ Error approving player {player_id}: {e}")
        return f"❌ Failed to approve player: {str(e)}"
```

---

**REMEMBER: These rules are CRITICAL for CrewAI integration. Tools that don't follow these patterns will not work correctly with agents and may cause system failures.**