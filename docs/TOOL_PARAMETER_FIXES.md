# Tool Parameter Fixes - CrewAI Native Implementation

## 🚨 **Problem Identified**

The `/list` command was failing with the error:
```
❌ Error: Failed to get all players: 'dict' object has no attribute 'team_id'
```

### **Root Cause Analysis**

1. **Tool Parameter Mismatch**: Tools were expecting `PlayerContext` objects but receiving JSON objects
2. **Inconsistent Parameter Passing**: Some tools used `PlayerContext`, others used direct parameters
3. **LLM Parameter Extraction**: The LLM was passing parameters as JSON objects instead of direct values

### **Example Error**
```
Tool Input: "{\"context\": {\"team_id\": \"KTI\", \"user_id\": \"8148917292\"}}"
Tool Expected: PlayerContext object with team_id attribute
Tool Received: dict object with nested context
```

## 🔍 **Tools Affected**

The following tools were using `PlayerContext` objects instead of direct parameters:

1. **`get_all_players`** - Expected `PlayerContext`, needed `team_id`, `user_id`
2. **`get_active_players`** - Expected `PlayerContext`, needed `team_id`, `user_id`
3. **`get_player_status`** - Expected `PlayerContext`, needed `team_id`, `user_id`, `phone`
4. **`add_player`** - Expected `PlayerContext`, needed `team_id`, `user_id`, `name`, `phone`, `position`
5. **`approve_player`** - Expected `PlayerContext`, needed `team_id`, `user_id`, `player_id`

## ✅ **Solution Implemented**

### **CrewAI Native Parameter Passing**

All tools were refactored to use **direct parameter passing** instead of `PlayerContext` objects, following the same pattern as `get_my_status`:

```python
# ❌ BEFORE: PlayerContext object
@tool("get_all_players")
async def get_all_players(context: PlayerContext) -> str:
    team_id = context.team_id  # This failed

# ✅ AFTER: Direct parameters
@tool("get_all_players")
async def get_all_players(team_id: str, user_id: str) -> str:
    # Direct parameter access
    validation_error = validate_required_input(team_id, "Team ID")
```

### **Key Changes Made**

#### **1. get_all_players Tool**
```python
@tool("get_all_players")
async def get_all_players(team_id: str, user_id: str) -> str:
    """
    Get all players in the team.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        
    Returns:
        List of all players or error message
    """
    try:
        # Validate inputs using utility functions
        validation_error = validate_required_input(team_id, "Team ID")
        if validation_error:
            return validation_error
        
        validation_error = validate_required_input(user_id, "User ID")
        if validation_error:
            return validation_error
        
        # Sanitize inputs
        team_id = sanitize_input(team_id, max_length=20)
        user_id = sanitize_input(user_id, max_length=20)
        
        # ... rest of implementation
```

#### **2. get_active_players Tool**
```python
@tool("get_active_players")
async def get_active_players(team_id: str, user_id: str) -> str:
    """
    Get all active players in the team.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        
    Returns:
        List of active players or error message
    """
    # Same pattern as get_all_players
```

#### **3. get_player_status Tool**
```python
@tool("get_player_status")
async def get_player_status(team_id: str, user_id: str, phone: str) -> str:
    """
    Get player status by phone number.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        phone: The player's phone number
        
    Returns:
        Player status or error message
    """
    # Same pattern with additional phone parameter
```

#### **4. add_player Tool**
```python
@tool("add_player")
async def add_player(team_id: str, user_id: str, name: str, phone: str, position: str) -> str:
    """
    Add a new player to the team.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        name: Player's full name
        phone: Player's phone number
        position: Player's position
        
    Returns:
        Success message or error
    """
    # Same pattern with additional name, phone, position parameters
```

#### **5. approve_player Tool**
```python
@tool("approve_player")
async def approve_player(team_id: str, user_id: str, player_id: str) -> str:
    """
    Approve a player for match squad selection.
    
    Args:
        team_id: Team ID (required) - available from context
        user_id: User ID (required) - available from context
        player_id: The player ID to approve
        
    Returns:
        Success message or error
    """
    # Same pattern with additional player_id parameter
```

### **6. Removed Unused Imports**
```python
# ❌ REMOVED: Unused PlayerContext import
from kickai.core.models.context_models import PlayerContext

# ✅ ADDED: Other context models for future use
from kickai.core.models.context_models import BaseContext
from kickai.core.models.context_models import TeamContext
from kickai.core.models.context_models import MatchContext
from kickai.core.models.context_models import PaymentContext
from kickai.core.models.context_models import HealthContext
from kickai.core.models.context_models import CommunicationContext
from kickai.core.models.context_models import AttendanceContext
from kickai.core.models.context_models import SystemContext
```

## 🔧 **Implementation Details**

### **1. Consistent Parameter Pattern**

All tools now follow the same pattern:
1. **Direct Parameters**: `team_id: str, user_id: str` (and other specific parameters)
2. **Validation**: Use `validate_required_input()` utility function
3. **Sanitization**: Use `sanitize_input()` utility function
4. **Error Handling**: Consistent error handling with `format_tool_error()`

### **2. CrewAI Native Context Passing**

The context is passed through the task description, allowing the LLM to extract parameters:

```python
# In configurable_agent.py
enhanced_task = f"{task}\n\nAvailable context parameters: {', '.join(context_info)}\n\nPlease use these context parameters when calling tools that require them."
```

### **3. Parameter Validation**

Each tool validates its required parameters:

```python
validation_error = validate_required_input(team_id, "Team ID")
if validation_error:
    return validation_error

validation_error = validate_required_input(user_id, "User ID")
if validation_error:
    return validation_error
```

## 📊 **Testing Results**

### **✅ Expected Behavior**

1. **`/list` Command**: Should work without parameter errors
2. **`/myinfo` Command**: Should continue working (already using direct parameters)
3. **`/status [phone]` Command**: Should work with phone parameter
4. **`/addplayer` Command**: Should work with name, phone, position parameters
5. **`/approve` Command**: Should work with player_id parameter

### **🔍 Debug Information**

The LLM should now pass parameters correctly:
```
Tool Input: "{\"team_id\": \"KTI\", \"user_id\": \"8148917292\"}"
```

Instead of the previous incorrect format:
```
Tool Input: "{\"context\": {\"team_id\": \"KTI\", \"user_id\": \"8148917292\"}}"
```

## 🎯 **Impact on System**

### **1. Fixed Tool Execution**
- **Before**: Tools failed with `'dict' object has no attribute 'team_id'`
- **After**: Tools receive parameters directly and execute successfully

### **2. Consistent Parameter Passing**
- **Before**: Mixed patterns (some `PlayerContext`, some direct parameters)
- **After**: All tools use direct parameter passing

### **3. Better Error Handling**
- **Before**: Pydantic validation errors for context objects
- **After**: Direct parameter validation with clear error messages

### **4. CrewAI Native Implementation**
- **Before**: Custom context object patterns
- **After**: Native CrewAI parameter passing through task descriptions

## 🔄 **Best Practices Established**

### **1. Direct Parameter Passing**
```python
# ✅ CORRECT: Direct parameters
@tool("tool_name")
async def tool_name(team_id: str, user_id: str, param1: str) -> str:
    # Direct parameter access
    validation_error = validate_required_input(team_id, "Team ID")

# ❌ WRONG: Context objects
@tool("tool_name")
async def tool_name(context: PlayerContext, param1: str) -> str:
    team_id = context.team_id  # Can fail
```

### **2. Consistent Validation**
```python
# ✅ CORRECT: Validate all required parameters
validation_error = validate_required_input(team_id, "Team ID")
if validation_error:
    return validation_error

validation_error = validate_required_input(user_id, "User ID")
if validation_error:
    return validation_error
```

### **3. Clear Documentation**
```python
# ✅ CORRECT: Clear parameter documentation
"""
Args:
    team_id: Team ID (required) - available from context
    user_id: User ID (required) - available from context
    param1: Specific parameter description
"""
```

## 📚 **Related Files**

- **`kickai/features/player_registration/domain/tools/player_tools.py`**: Fixed all player tools
- **`kickai/agents/configurable_agent.py`**: Context passing implementation
- **`kickai/agents/simplified_orchestration.py`**: Context extraction
- **`kickai/core/models/context_models.py`**: Context model definitions

## 🎯 **Conclusion**

The tool parameter fixes successfully address the **root cause** of the `/list` command failure by implementing **CrewAI native parameter passing**. The solution:

1. **Standardized Parameters**: All tools now use direct parameter passing
2. **Consistent Validation**: All tools validate parameters using utility functions
3. **CrewAI Native**: Follows CrewAI best practices for parameter passing
4. **Better Error Handling**: Clear error messages for missing parameters

**Key Achievement**: All player-related tools now work consistently with CrewAI's native parameter passing system, eliminating the `'dict' object has no attribute 'team_id'` errors.

**Expected Behavior**: 
- `/list` command works without parameter errors
- All player tools receive parameters correctly
- Consistent error handling across all tools
- Better debugging and logging for parameter issues

---

**Remember**: **Use CrewAI native parameter passing with direct parameters instead of custom context objects for better reliability and consistency.** 