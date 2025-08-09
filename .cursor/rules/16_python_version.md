# Python Version Rule

## CRITICAL: Python Version Requirement

**This project uses Python 3.11, NOT Python 3.9**

### Key Points:
- **Python Version**: 3.11
- **Type Hints**: Full support for modern type hints including Union types with `|` operator
- **Syntax**: All Python 3.11 features are available
- **Compatibility**: No need to use `Optional[]` or `List[]` from typing for basic types

### What This Means:
1. **Union Types**: Can use `type | None` instead of `Optional[type]`
2. **List Types**: Can use `list[type]` instead of `List[type]`
3. **Dict Types**: Can use `dict[str, type]` instead of `Dict[str, type]`
4. **All Modern Features**: Pattern matching, improved error messages, etc.

### Common Mistakes to Avoid:
- ❌ Don't assume Python 3.9 compatibility
- ❌ Don't use `Optional[list[type]]` when `list[type] | None` works
- ❌ Don't import `List`, `Dict`, `Optional` from typing unnecessarily

### Correct Usage:
```python
# ✅ Python 3.11 - Correct
def process_data(data: list[str] | None) -> dict[str, Any]:
    pass

# ✅ Also acceptable (explicit imports)
from typing import List, Dict, Optional
def process_data(data: Optional[List[str]]) -> Dict[str, Any]:
    pass

# ❌ Don't do this (unnecessary complexity)
from typing import List, Dict, Optional
def process_data(data: Optional[List[str]]) -> Dict[str, Any]:
    pass
```

### Remember:
- **Always assume Python 3.11** when writing code
- **Use modern type hints** when possible
- **Don't downgrade** to Python 3.9 syntax
- **Check existing code** for patterns to follow

### Files to Check for Python Version Issues:
- `kickai/core/types.py`
- `kickai/core/context_types.py`
- `kickai/agents/agentic_message_router.py`
- `kickai/core/interfaces/agent_interfaces.py`
- `kickai/core/command_registry.py`
- `kickai/core/di/modern_container.py`

### Testing:
- All tests should run on Python 3.11
- Mock Telegram tester uses Python 3.11
- Comprehensive test runner uses Python 3.11
- No compatibility mode needed

**NEVER FORGET: This is a Python 3.11 project!**
