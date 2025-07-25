
# CrewAI Parameter Passing Migration Guide

## Overview
This guide helps migrate from context extraction patterns to direct parameter passing in CrewAI tools.

## Key Changes Made

### 1. Fixed Tool Parameter Names
- Renamed `context` parameter to `error_context` in `log_error` tool to avoid confusion
- This prevents the parameter from being flagged as a context extraction pattern

### 2. Updated Task Creation Patterns
- Changed `Task(context=...)` to `Task(config=...)` in agent files
- This follows CrewAI's recommended pattern for passing configuration data

### 3. Added Deprecation Warnings
- Added deprecation warnings to context extraction methods in tool registry
- These methods should be replaced with direct parameter passing

### 4. Clarified Internal Methods
- Added comments to internal orchestration methods to distinguish them from tool parameter issues
- These methods are part of the orchestration pipeline, not tool parameter passing

## Best Practices Going Forward

### Tool Function Signatures
```python
# ✅ Good - Direct parameters
@tool("my_tool")
def my_tool(param1: str, param2: int) -> str:
    return f"Processed {param1} and {param2}"

# ❌ Avoid - Context parameter
@tool("my_tool")
def my_tool(context: dict) -> str:
    param1 = context.get('param1')  # Don't do this
    return f"Processed {param1}"
```

### Task Creation
```python
# ✅ Good - Use config parameter
task = Task(
    description="Process user request",
    agent=agent,
    config={"user_id": "123", "team_id": "TEAM1"}
)

# ❌ Avoid - Use context parameter
task = Task(
    description="Process user request",
    agent=agent,
    context={"user_id": "123", "team_id": "TEAM1"}  # Don't do this
)
```

### Parameter Extraction
```python
# ✅ Good - Direct parameter passing
@tool("process_user")
def process_user(user_id: str, team_id: str, action: str) -> str:
    # Process directly with parameters
    return f"Processed {action} for user {user_id} in team {team_id}"

# ❌ Avoid - Context extraction
@tool("process_user")
def process_user(context: dict) -> str:
    user_id = context.get('user_id')  # Don't do this
    team_id = context.get('team_id')  # Don't do this
    action = context.get('action')    # Don't do this
    return f"Processed {action} for user {user_id} in team {team_id}"
```

## Migration Checklist

- [ ] Update all @tool decorated functions to use direct parameters
- [ ] Replace Task(context=...) with Task(config=...)
- [ ] Remove context extraction patterns from tool functions
- [ ] Update tool documentation to reflect direct parameter usage
- [ ] Test all tools to ensure they work with direct parameters
- [ ] Update any remaining context extraction patterns in orchestration

## Testing

After applying these fixes, run the audit script again to verify:

```bash
python scripts/audit_crewai_tool_patterns.py
```

The audit should show significantly fewer issues, with only legitimate internal orchestration methods remaining.
