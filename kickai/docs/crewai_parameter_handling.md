# CrewAI Native Parameter Handling - Simplified Solution

## Overview

This document explains the simplified parameter handling solution for CrewAI tools in the KICKAI system, using CrewAI's native delegation and simple string parameters.

## The Solution

### **Use CrewAI's Native Delegation**

Instead of complex custom delegation tools, use CrewAI's built-in delegation:

```yaml
# Manager agent
- name: message_processor
  allow_delegation: true  # ✅ Enable native CrewAI delegation
  tools: []  # ✅ No custom delegation tools needed

# Specialist agents  
- name: help_assistant
  allow_delegation: false  # ✅ Focus on expertise
- name: player_coordinator
  allow_delegation: false  # ✅ Focus on expertise
```

### **Simple String Parameters**

All tools use simple string parameters for maximum compatibility:

```python
@tool("update_player_field")
async def update_player_field(
    telegram_id: str,  # ✅ Simple string
    team_id: str,      # ✅ Simple string
    username: str,     # ✅ Simple string
    chat_type: str,    # ✅ Simple string
    field: str,        # ✅ Simple string
    value: str         # ✅ Simple string
) -> str:
    """Update a single field for a player."""
    try:
        # Simple type conversion
        telegram_id_int = int(telegram_id)
        
        # Process the update
        # ... business logic here
        
        return "✅ Field updated successfully"
        
    except ValueError:
        return "❌ Invalid telegram_id format"
```

### **Native CrewAI Delegation**

When `allow_delegation=true`, CrewAI automatically provides:

```python
# CrewAI's built-in delegation tools
Delegate work to coworker(task: str, context: str, coworker: str)
Ask question to coworker(question: str, context: str, coworker: str)
```

**Usage Example:**
```python
# Agent creates context string
context = f"User: {username}, Team: {team_id}, Chat: {chat_type}, Request: {user_request}"

# CrewAI handles delegation automatically
Delegate work to coworker(
    task="Update phone number",
    context=context,
    coworker="player_coordinator"
)
```

## Implementation Patterns

### **Pattern 1: Simple String Parameters**
```python
@tool("get_player_info")
async def get_player_info(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    player_identifier: str
) -> str:
    """Get player information."""
    # Simple validation
    if not all([telegram_id, team_id, username, chat_type, player_identifier]):
        return "❌ All parameters are required"
    
    # Simple conversion
    try:
        telegram_id_int = int(telegram_id)
    except ValueError:
        return "❌ Invalid telegram_id format"
    
    # Process request
    # ... business logic here
```

### **Pattern 2: Helper Functions**
```python
from kickai.utils.native_crewai_helpers import convert_telegram_id, validate_required_strings

@tool("update_player_field")
async def update_player_field(
    telegram_id: str,
    team_id: str,
    username: str,
    chat_type: str,
    field: str,
    value: str
) -> str:
    """Update player field."""
    # Validate required strings
    error = validate_required_strings(
        telegram_id, team_id, username, chat_type, field, value,
        names=["telegram_id", "team_id", "username", "chat_type", "field", "value"]
    )
    if error:
        return error
    
    # Convert telegram_id
    telegram_id_int = convert_telegram_id(telegram_id)
    if not telegram_id_int:
        return "❌ Invalid telegram_id format"
    
    # Process update
    # ... business logic here
```

### **Pattern 3: Context String Creation**
```python
from kickai.utils.native_crewai_helpers import create_context_string

# Create context for delegation
context = create_context_string(
    telegram_id=telegram_id,
    team_id=team_id,
    username=username,
    chat_type=chat_type,
    additional_context=f"Update {field} to {value}"
)

# CrewAI handles the rest automatically
```

## Benefits

### **1. Simplicity**
- **No complex parameter handlers**
- **No custom delegation tools**
- **No parameter conversion logic**
- **Native CrewAI compatibility**

### **2. Reliability**
- **Direct CrewAI delegation**
- **No custom tool overhead**
- **Simpler agent decision-making**
- **Better error handling**

### **3. Maintainability**
- **Fewer custom tools to maintain**
- **Standard CrewAI patterns**
- **Easier to debug**
- **Future-proof**

## Migration Guide

### **For Existing Tools**

1. **Convert to String Parameters**
   ```python
   # Before
   async def my_tool(telegram_id: int, context: str):
   
   # After
   async def my_tool(telegram_id: str, context: str):
   ```

2. **Add Simple Validation**
   ```python
   # Add at start of tool function
   try:
       telegram_id_int = int(telegram_id)
   except ValueError:
       return "❌ Invalid telegram_id format"
   ```

3. **Remove Complex Parameter Handling**
   ```python
   # Remove these imports
   # from kickai.utils.crewai_parameter_handler import extract_crewai_parameters
   # from kickai.utils.crewai_parameter_handler import handle_crewai_delegation_context
   ```

### **For Agent Configuration**

1. **Enable Native Delegation**
   ```yaml
   # Manager agent
   allow_delegation: true
   tools: []
   
   # Specialist agents
   allow_delegation: false
   ```

2. **Remove Custom Delegation Tools**
   ```yaml
   # Remove from tool lists
   # - delegate_work_to_coworker
   # - process_delegation_request
   # - flexible_delegation_tool
   ```

## Best Practices

### **1. Always Use String Parameters**
```python
# ✅ Good
telegram_id: str
team_id: str
username: str

# ❌ Avoid
telegram_id: int
telegram_id: Union[int, str]
```

### **2. Simple Type Conversion**
```python
# ✅ Good - Simple conversion
try:
    telegram_id_int = int(telegram_id)
except ValueError:
    return "❌ Invalid telegram_id format"

# ❌ Avoid - Complex validation
# Complex parameter extraction and validation
```

### **3. Use Helper Functions**
```python
# ✅ Good - Use helpers
from kickai.utils.native_crewai_helpers import convert_telegram_id

telegram_id_int = convert_telegram_id(telegram_id)
if not telegram_id_int:
    return "❌ Invalid telegram_id format"

# ❌ Avoid - Manual validation
# Complex manual validation logic
```

### **4. Clear Error Messages**
```python
# ✅ Good - Clear errors
return "❌ Invalid telegram_id format"

# ❌ Avoid - Generic errors
return "Error occurred"
```

## Conclusion

This simplified approach ensures that KICKAI tools work reliably with CrewAI's native delegation while maintaining clean, maintainable code. The solution eliminates complexity and follows CrewAI best practices.
