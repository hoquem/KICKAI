# Typing Import Standards

This document outlines the typing import standards for the KICKAI project to prevent `Optional` and other typing import issues.

## 🚨 **The Problem**

The codebase experienced a critical error:
```
❌ Fatal error: name 'Optional' is not defined
```

This happened due to:
1. **Missing typing imports** in files using `Optional[]`, `List[]`, etc.
2. **Inconsistent import patterns** across the codebase
3. **Copy-paste errors** during refactoring
4. **Lack of systematic typing import standards**

## ✅ **The Solution**

### **1. Centralized Typing Imports**

All typing imports should use the centralized module:
```python
from kickai.core.typing_imports import Any, Dict, List, Optional, Union
```

### **2. Standard Import Pattern**

**✅ CORRECT:**
```python
from kickai.core.typing_imports import Any, Dict, List, Optional, Union

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    pass
```

**❌ INCORRECT:**
```python
# Missing import
def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    pass
```

### **3. Import Organization**

Follow this order for imports:
```python
# 1. Standard library imports
import os
import sys
from datetime import datetime
from typing import List  # Only if not using centralized imports

# 2. Third-party imports
from crewai import tool
from loguru import logger

# 3. Local application imports
from kickai.core.typing_imports import Any, Dict, List, Optional, Union
from kickai.core.di.modern_container import get_container
```

## 🔧 **Tools and Automation**

### **1. Pre-commit Hook**

The project includes a pre-commit hook that automatically checks for typing import issues:
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### **2. Fix Script**

Automatically fix typing import issues:
```bash
python scripts/fix_typing_imports.py
```

### **3. Check Script**

Check for typing import issues without fixing:
```bash
python scripts/check_typing_imports.py
```

## 📋 **Common Typing Constructs**

### **Basic Types**
- `Optional[T]` - Value that can be None
- `List[T]` - List of type T
- `Dict[K, V]` - Dictionary with key type K and value type V
- `Tuple[T1, T2, ...]` - Tuple with specific types
- `Union[T1, T2, ...]` - Value that can be one of several types
- `Any` - Any type (use sparingly)

### **Advanced Types**
- `Type[T]` - Type object of type T
- `Callable[[Arg1, Arg2], Return]` - Function type
- `Generic[T]` - Generic type
- `TypeVar('T')` - Type variable for generics

## 🎯 **Best Practices**

### **1. Always Import What You Use**
```python
# ✅ Good
from kickai.core.typing_imports import Optional, Dict, List

def process_data(data: Optional[Dict[str, List[str]]]) -> List[str]:
    pass

# ❌ Bad - Missing imports
def process_data(data: Optional[Dict[str, List[str]]]) -> List[str]:
    pass
```

### **2. Use Centralized Imports**
```python
# ✅ Preferred
from kickai.core.typing_imports import Optional, Dict, List

# ❌ Avoid
from typing import Optional, Dict, List
```

### **3. Be Specific with Types**
```python
# ✅ Good
def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    pass

# ❌ Avoid
def get_user(user_id: str) -> Any:
    pass
```

### **4. Use Optional for Nullable Values**
```python
# ✅ Good
def find_user(name: str) -> Optional[User]:
    pass

# ❌ Bad - Union with None
def find_user(name: str) -> Union[User, None]:
    pass
```

## 🚨 **Common Pitfalls**

### **1. Function Signatures**
```python
# ❌ BROKEN - This will cause runtime errors
def initialize_feature(config: Dict[str, Any], Dict, List) -> None:
    pass

# ✅ CORRECT
def initialize_feature(config: Dict[str, Any]) -> None:
    pass
```

### **2. Missing Imports in New Files**
When creating new files, always check if you need typing imports:
```python
# Check if your file uses any of these patterns:
# - Optional[...]
# - List[...]
# - Dict[...]
# - Union[...]
# - Any
# - etc.

# If yes, add the import:
from kickai.core.typing_imports import Any, Dict, List, Optional, Union
```

### **3. Copy-paste Errors**
When copying code between files, ensure typing imports are also copied or use the centralized imports.

## 🔍 **Debugging Typing Issues**

### **1. Check for Missing Imports**
```bash
python scripts/check_typing_imports.py
```

### **2. Fix All Issues**
```bash
python scripts/fix_typing_imports.py
```

### **3. Verify Fixes**
```bash
python scripts/check_typing_imports.py
```

## 📚 **IDE Configuration**

### **VS Code Settings**
Add to `.vscode/settings.json`:
```json
{
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.autoSearchPaths": true
}
```

### **PyCharm Settings**
- Enable type checking in Settings → Editor → Inspections → Python → Type Checking
- Configure import optimization to use centralized imports

## 🧪 **Testing**

### **1. Unit Tests**
Ensure your tests also follow typing import standards:
```python
from kickai.core.typing_imports import List, Optional

def test_user_creation() -> None:
    users: List[Optional[User]] = []
    # Test logic here
```

### **2. Integration Tests**
```python
from kickai.core.typing_imports import Dict, Any

async def test_api_integration() -> None:
    response: Dict[str, Any] = await api_call()
    # Test logic here
```

## 📈 **Monitoring**

### **1. CI/CD Pipeline**
The pre-commit hooks ensure typing imports are correct before code reaches production.

### **2. Regular Audits**
Run the check script regularly:
```bash
# Add to your development workflow
python scripts/check_typing_imports.py
```

## 🎉 **Success Metrics**

- ✅ Zero `name 'Optional' is not defined` errors
- ✅ All files use centralized typing imports
- ✅ Pre-commit hooks pass consistently
- ✅ Type checking works correctly in IDEs
- ✅ Code is more maintainable and type-safe

## 📞 **Support**

If you encounter typing import issues:

1. **Immediate Fix**: Run `python scripts/fix_typing_imports.py`
2. **Prevention**: Install pre-commit hooks with `pre-commit install`
3. **Documentation**: Refer to this document
4. **Team**: Discuss with the team for complex cases

---

**Remember**: Consistent typing imports lead to better code quality, fewer runtime errors, and improved developer experience! 🚀 