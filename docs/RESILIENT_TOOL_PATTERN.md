# Resilient Tool Parameter Pattern

## Background

**IMPORTANT UPDATE**: This pattern is for **legacy tools** or **complex edge cases** only. Modern KICKAI tools should use **CrewAI Semantic Tool Patterns** with explicit parameter naming as documented in the tool naming convention.

**Current Standard**: Tools should use semantic naming with explicit parameters:
```python
@tool("get_example_self")
async def get_example_self(telegram_id: str, team_id: str, telegram_username: str) -> str:
    """CrewAI semantic pattern with explicit parameter naming - preferred approach."""
```

**This Resilient Pattern**: Use only when dealing with unpredictable parameter formats from external integrations or legacy compatibility.

## When to Use Each Pattern

### ✅ Use Direct Parameter Passing (Preferred)
- **New tools** being developed
- **Standard CrewAI agent interactions**
- **Known parameter requirements**
- **Internal tool communication**

```python
@tool("get_direct_example_self")
async def get_direct_example_self(telegram_id: str, team_id: str, telegram_username: str) -> str:
    """Preferred approach - semantic naming with explicit parameters."""
    if not telegram_id or not team_id:
        return "❌ Required parameters missing"
    return f"✅ Action completed for user {telegram_username} (ID: {telegram_id})"

@tool("get_direct_example_by_identifier") 
async def get_direct_example_by_identifier(telegram_id: str, team_id: str, target_identifier: str) -> str:
    """Look up example by identifier - semantic naming pattern."""
    if not target_identifier:
        return "❌ Please specify who you want to look up"
    return f"✅ Looking up user: {target_identifier}"
```

### ⚠️ Use Resilient Pattern (Edge Cases Only)
- **Legacy compatibility** with existing complex tools
- **External API integrations** with unpredictable formats
- **Multi-format parameter handling** requirements
- **Tools that MUST handle various input formats**

## The Problem (Historical Context)

**Before (Brittle Pattern):**
```python
@tool("example_tool")
async def example_tool(param1: str, param2: int, param3: str) -> str:
    # Tool fails if LLM doesn't pass all 3 parameters
    # LLM might pass different parameter names
    # No way to handle missing critical vs optional parameters
```

**Issues:**
- Tools fail with "missing required positional argument" errors
- LLMs pass parameters inconsistently across different models
- No distinction between critical and optional parameters
- Arbitrary defaults can cause unwanted behavior

## The Solution: Resilient Tool Pattern

### Core Principles (Legacy/Edge Cases Only)

**PREFERRED**: Use direct parameter passing for new tools
```python
@tool("preferred_tool")
async def preferred_tool(telegram_id: str, team_id: str) -> str:
    """Direct parameters - use this approach for new tools."""
```

**RESILIENT PATTERN**: Use only when needed for compatibility
1. **Use `*args, **kwargs` for flexible parameter acceptance**
2. **Handle CrewAI's multiple parameter formats (including JSON strings)**
3. **Only require parameters that are actually used by the tool logic**
4. **Provide clear error messages for missing critical parameters**
5. **Use sensible defaults only for non-critical parameters**
6. **Handle multiple parameter name variations**

### Pattern Implementation

```python
import json
from crewai.tools import tool

# ⚠️ LEGACY PATTERN - Use direct parameters for new tools
@tool("legacy_resilient_tool")
async def legacy_resilient_tool(*args, **kwargs) -> str:
    """
    LEGACY resilient tool pattern - use only for compatibility.
    
    NEW TOOLS should use direct parameters:
    async def new_tool(telegram_id: str, team_id: str) -> str:
    
    Required parameters:
    - critical_param: Description of why this is required
    
    Optional parameters:
    - optional_param: Description (defaults to 'default_value')
    """
    try:
        # 1. CRITICAL: Handle CrewAI's JSON string parameters
        if args and isinstance(args[0], str):
            try:
                # Check if it's a JSON string
                if args[0].strip().startswith('{'):
                    parsed = json.loads(args[0])
                    if isinstance(parsed, dict):
                        kwargs.update(parsed)
                        logger.debug(f"🔧 Parsed JSON parameters: {list(parsed.keys())}")
            except (json.JSONDecodeError, TypeError) as e:
                logger.debug(f"🔧 Not JSON string, continuing: {e}")
        
        # 2. Extract CRITICAL parameters - fail fast if missing
        critical_param = kwargs.get('critical_param', kwargs.get('alternate_name'))
        if not critical_param:
            return "❌ I need the critical parameter to help you. Please provide [specific guidance]."
        
        # 3. Extract OPTIONAL parameters with sensible defaults
        optional_param = kwargs.get('optional_param', 'default_value')
        optional_param = str(optional_param) if optional_param else 'default_value'
        
        # 4. Tool logic using only extracted parameters
        result = business_logic(critical_param, optional_param)
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in example_tool: {e}")
        return f"❌ Unable to complete the request. Error: {str(e)}"
```

## CrewAI Parameter Formats

### The DEFINITIVE Issue

CrewAI can pass parameters to tools in **FOUR different ways**:

1. **JSON String** (most problematic):
   ```python
   # CrewAI passes: '{"chat_type": "main", "username": "john"}'
   # Tool receives in args[0] as string, NOT in kwargs
   ```

2. **Standard kwargs**:
   ```python
   # CrewAI passes: chat_type="main", username="john"
   # Tool receives in kwargs as expected
   ```

3. **Dict as first positional argument**:
   ```python
   # CrewAI passes: ({'chat_type': 'main', 'username': 'john'})
   # Tool receives dict in args[0]
   ```

4. **Context dict in kwargs**:
   ```python
   # CrewAI passes: context={'chat_type': 'main', 'username': 'john'}
   # Tool receives nested dict in kwargs['context']
   ```

### The Fix

The JSON string format (#1) is the most common issue. Tools must:

1. **Accept `*args, **kwargs`** (not just `**kwargs`)
2. **Check first positional argument for JSON string**
3. **Parse JSON and merge into kwargs**
4. **Continue with normal parameter extraction**

This pattern handles ALL four formats reliably.

## Real Examples from KICKAI

### Example 1: Help Tool (Context-Dependent with JSON String Support)

```python
@tool("show_help_commands")
async def show_help_commands(*args, **kwargs) -> str:
    """Show help commands based on chat context."""
    try:
        # CRITICAL FIX: Handle JSON string as first argument (CrewAI parameter passing)
        if args and isinstance(args[0], str):
            try:
                # Check if it's a JSON string
                if args[0].strip().startswith('{'):
                    parsed = json.loads(args[0])
                    if isinstance(parsed, dict):
                        kwargs.update(parsed)
                        logger.debug(f"🔧 Parsed JSON parameters: {list(parsed.keys())}")
            except (json.JSONDecodeError, TypeError) as e:
                logger.debug(f"🔧 Not JSON string, continuing: {e}")
        
        # CRITICAL: chat_type determines which commands to show
        chat_type_raw = kwargs.get('chat_type', kwargs.get('chat', kwargs.get('type')))
        if not chat_type_raw:
            return f"❌ I need to know the chat context to show the right help. Please specify the chat type ({', '.join([ct.value for ct in ChatType])})."
        
        # Convert to enum with proper error handling
        try:
            chat_type_enum = _normalize_chat_type(str(chat_type_raw))
        except Exception as e:
            valid_types = ', '.join([ct.value for ct in ChatType])
            return f"❌ Invalid chat type '{chat_type_raw}'. Valid options: {valid_types}"
        
        # OPTIONAL: username only for personalization
        username = kwargs.get('username', kwargs.get('user', 'user'))
        
        # Business logic using enum...
        help_content = help_service.generate_help_content(chat_type_enum, username)
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### Example 2: Command Help Tool (Command-Specific with JSON Support)

```python
@tool("show_help_usage")
async def show_help_usage(*args, **kwargs) -> str:
    """Show help for a specific command."""
    try:
        # CRITICAL FIX: Handle JSON string as first argument
        if args and isinstance(args[0], str):
            try:
                if args[0].strip().startswith('{'):
                    parsed = json.loads(args[0])
                    if isinstance(parsed, dict):
                        kwargs.update(parsed)
            except (json.JSONDecodeError, TypeError):
                pass  # Continue with normal processing
        
        # CRITICAL: command is required for this tool to be useful
        command = kwargs.get('command', kwargs.get('cmd'))
        if not command:
            return "❌ Please specify which command you need help with."
        
        # OPTIONAL: username only for logging
        username = kwargs.get('username', 'user')
        
        # Business logic...
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

### Example 3: Welcome Tool (All Optional with JSON Support)

```python
@tool("show_help_welcome")
async def show_help_welcome(*args, **kwargs) -> str:
    """Show welcome message."""
    try:
        # Handle JSON string parameters
        if args and isinstance(args[0], str):
            try:
                if args[0].strip().startswith('{'):
                    kwargs.update(json.loads(args[0]))
            except (json.JSONDecodeError, TypeError):
                pass  # Continue with defaults
        
        # ALL OPTIONAL: Tool works with reasonable defaults
        username = kwargs.get('username', kwargs.get('user', 'user'))
        chat_type = kwargs.get('chat_type', kwargs.get('chat', 'main'))
        
        # Business logic...
    except Exception as e:
        return f"❌ Error: {str(e)}"
```

## Parameter Analysis Guidelines

### Step 1: Analyze Tool Logic
```python
# Ask: What does this tool actually DO with each parameter?
def analyze_tool_parameters():
    # Required: Tool cannot function without this
    # Optional: Tool works better with this, has good default
    # Unused: Tool doesn't actually use this (remove it!)
```

### Step 2: Classify Parameters

| Category | Handling | Example |
|----------|----------|---------|
| **Critical** | Fail fast with helpful message | `chat_type` for help commands |
| **Enhancing** | Use if provided, default if not | `username` for personalization |
| **Legacy** | Remove entirely | `telegram_id` for logging only |

### Step 3: Handle Parameter Variations

```python
# LLMs might use different parameter names
value = kwargs.get('primary_name', 
                   kwargs.get('alternate_name', 
                              kwargs.get('third_option', default)))
```

### Step 4: Type Conversion Best Practices

```python
# Enum conversion with proper error handling
from kickai.core.enums import ChatType

chat_type_raw = kwargs.get('chat_type')
if not chat_type_raw:
    return f"❌ Please specify chat type ({', '.join([ct.value for ct in ChatType])})"

try:
    chat_type_enum = _normalize_chat_type(str(chat_type_raw))
except Exception:
    valid_types = ', '.join([ct.value for ct in ChatType])
    return f"❌ Invalid chat type '{chat_type_raw}'. Valid options: {valid_types}"

# Integer conversion with fallback
telegram_id_raw = kwargs.get('telegram_id', kwargs.get('user_id'))
try:
    telegram_id = int(telegram_id_raw) if telegram_id_raw else 0
except (ValueError, TypeError):
    telegram_id = 0  # Safe fallback

# String conversion with None protection
username = kwargs.get('username', kwargs.get('user', 'user'))
username = str(username) if username else 'user'
```

## Migration Strategy

### 1. Identify Parameter Usage
```bash
# Search for actual parameter usage in tool code
grep -n "parameter_name" tool_file.py
```

### 2. Update Tool Signature
```python
# Before
async def tool(param1: str, param2: int) -> str:

# After  
async def tool(**kwargs) -> str:
```

### 3. Add Parameter Extraction
```python
# Extract with proper error handling
param1 = kwargs.get('param1')
if not param1:  # Only if truly required
    return "❌ Clear error message about what's needed"
```

### 4. Test with Various Inputs
```python
# Test missing parameters
await tool()  # Should handle gracefully
await tool(param1="value")  # Should work
await tool(wrong_name="value")  # Should handle alternate names
```

## Benefits

### ✅ Advantages
- **Resilient**: Works with LLM parameter passing variability
- **Clear**: Explicit error messages guide agents
- **Maintainable**: Only handles parameters actually used
- **Future-proof**: Works with different LLM models
- **CrewAI Compatible**: Works with framework as designed

### ❌ What We Fixed
- No more "missing required positional argument" errors
- No more arbitrary defaults causing unwanted behavior
- No more unused parameter requirements
- No more rigid parameter expectations
- No more framework fighting

## Testing Your Tools

### Unit Test Pattern
```python
async def test_tool_resilience():
    # Test with missing critical parameter
    result = await tool()
    assert "❌" in result  # Should fail gracefully
    
    # Test with critical parameter
    result = await tool(critical_param="value")  
    assert "❌" not in result  # Should work
    
    # Test with alternate parameter names
    result = await tool(alternate_name="value")
    assert "❌" not in result  # Should work
```

## Anti-Patterns to Avoid

### ❌ Don't Do This
```python
# Using arbitrary defaults for critical parameters
telegram_id = kwargs.get('telegram_id', 12345)  # BAD!

# Requiring parameters not actually used by tool logic
if not team_id:  # But tool never uses team_id!
    return "Error"

# Silent failures
param = kwargs.get('param', '')  # Tool fails silently with empty string
```

### ✅ Do This Instead
```python
# Fail fast for truly critical parameters
critical_param = kwargs.get('critical_param')
if not critical_param:
    return "❌ I need X to do Y. Please provide X."

# Only require what you actually use
# If tool logic doesn't use a parameter, don't require it

# Clear error messages
return "❌ Specific guidance on what's needed"
```

## Summary

The Resilient Tool Pattern accepts CrewAI's design reality while making tools robust and user-friendly. It eliminates parameter passing errors by requiring only what's truly needed and providing clear feedback when critical parameters are missing.

This pattern ensures tools work reliably across different LLM models and parameter passing variations while maintaining clear boundaries between critical and optional functionality.