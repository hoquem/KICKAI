# Python Version Policy

## 🐍 Python 3.11 Only

**CRITICAL**: This project uses **Python 3.11 exclusively**. No other Python versions are supported.

### 🚨 Requirements

- **Python Version**: 3.11.x only
- **Virtual Environment**: Must use `venv311`
- **Development**: All development must use Python 3.11
- **Deployment**: All deployments must use Python 3.11

### 🔧 Setup Instructions

```bash
# Activate the Python 3.11 virtual environment
source venv311/bin/activate

# Verify Python version
python --version  # Should show Python 3.11.x

# Install dependencies
pip install -r requirements-local.txt
```

### ❌ What's Not Supported

- **Python 3.9**: Not supported - causes CrewAI compatibility issues
- **Python 3.10**: Not tested - use 3.11 only
- **Python 3.12+**: Not tested - use 3.11 only
- **System Python**: Never use system Python - always use venv311

### 🛠️ Type Hints

Use Python 3.11 type hint syntax:

```python
# ✅ CORRECT - Python 3.11 syntax
def process_data(data: list[str] | None) -> dict[str, Any]:
    pass

# ❌ WRONG - Python 3.9 syntax
def process_data(data: Optional[List[str]]) -> Dict[str, Any]:
    pass
```

### 🔍 Verification

Always verify you're using Python 3.11:

```bash
# Check Python version
python --version

# Should output: Python 3.11.x
```

### 🚨 Error Resolution

If you see Python 3.9 compatibility errors:

1. **Activate venv311**: `source venv311/bin/activate`
2. **Check version**: `python --version`
3. **Reinstall if needed**: `pip install -r requirements-local.txt`

### 📋 Development Commands

```bash
# Always start with this
source venv311/bin/activate

# Then run your commands
python run_bot_local.py
python -m pytest tests/
ruff check src/
```

### 🎯 Why Python 3.11?

- **CrewAI Compatibility**: CrewAI requires Python 3.11+ for proper operation
- **Type Hints**: Modern type hint syntax with union operators (`|`)
- **Performance**: Better performance and features
- **Future-Proof**: Latest stable Python version with long-term support
