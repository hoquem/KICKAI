# Runtime Validation Guide

This guide explains how to use the runtime validation system to catch issues early in development and prevent runtime errors like the `'ToolOutputCapture' object has no attribute 'clear_captured_outputs'` error.

## 🎯 **Problem Solved**

The validation system addresses common runtime issues such as:
- Missing methods on classes
- Incorrect method calls on wrong object types
- Inheritance chain problems
- Import errors
- Missing attributes

## 🛠️ **Validation Tools Available**

### 1. **Quick Validation** (Recommended for daily use)
```bash
# Run quick validation checks
python scripts/quick_validation.py
```

**Use when:**
- Before starting development
- After making code changes
- Before running the bot
- During debugging

### 2. **Comprehensive Validation**
```bash
# Run full validation suite
python scripts/validate_agent_system.py
```

**Use when:**
- Before major commits
- When investigating complex issues
- During system testing
- Before deployment

### 3. **Pre-Commit Validation**
```bash
# Run pre-commit checks (includes tests)
python scripts/pre_commit_validation.py

# Skip tests for faster validation
python scripts/pre_commit_validation.py --skip-tests
```

**Use when:**
- Before committing code
- In CI/CD pipelines
- Before merging pull requests

## 🔍 **What Gets Validated**

### **Agent System Validation**
- ✅ ToolOutputCapture and ToolOutputCaptureMixin methods
- ✅ ConfigurableAgent inheritance and methods
- ✅ Method call correctness
- ✅ AgentFactory functionality

### **Import Validation**
- ✅ Critical module imports
- ✅ Dependency availability
- ✅ Path resolution

### **Method Availability**
- ✅ Required methods exist on classes
- ✅ Inheritance chain is correct
- ✅ Method signatures are valid

### **Runtime Simulation**
- ✅ Object instantiation
- ✅ Method calls that were causing issues
- ✅ Error-free execution paths

## 📋 **Common Issues Detected**

### **1. Method Call Errors**
```python
# ❌ WRONG - Calling method on wrong object type
self.tool_capture.clear_captured_outputs()  # tool_capture is ToolOutputCapture

# ✅ CORRECT - Calling method on the right object
self.clear_captured_outputs()  # self is ToolOutputCaptureMixin
```

### **2. Missing Methods**
```python
# ❌ WRONG - Method doesn't exist
some_object.non_existent_method()

# ✅ CORRECT - Method exists
some_object.existing_method()
```

### **3. Inheritance Issues**
```python
# ❌ WRONG - Class doesn't inherit properly
class MyAgent:  # Missing inheritance
    pass

# ✅ CORRECT - Proper inheritance
class MyAgent(ToolOutputCaptureMixin):
    pass
```

## 🚀 **Integration with Development Workflow**

### **Daily Development**
```bash
# 1. Start your day with validation
python scripts/quick_validation.py

# 2. Make your code changes

# 3. Run validation again before testing
python scripts/quick_validation.py

# 4. Start the bot
./start_bot_safe.sh
```

### **Before Commits**
```bash
# Run comprehensive validation
python scripts/pre_commit_validation.py

# Fix any issues found
# Then commit your changes
git add .
git commit -m "Your commit message"
```

### **CI/CD Integration**
```bash
# Add to your CI pipeline
python scripts/validate_agent_system.py
if [ $? -ne 0 ]; then
    echo "Validation failed - stopping deployment"
    exit 1
fi
```

## 🔧 **Customizing Validation**

### **Adding New Validation Checks**

1. **Edit `kickai/core/validation/agent_validation.py`**
```python
def validate_your_new_check(self) -> ValidationResult:
    """Add your custom validation logic."""
    errors = []
    warnings = []
    details = {}
    
    # Your validation logic here
    
    return ValidationResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        details=details
    )
```

2. **Add to the validation list**
```python
validations = [
    ("Tool Output Capture Methods", self.validate_tool_output_capture_methods()),
    ("Your New Check", self.validate_your_new_check()),  # Add this line
    # ... other validations
]
```

### **Modifying Validation Rules**

Edit the expected methods and attributes in the validation functions:

```python
expected_tool_capture_methods = {
    'add_execution', 'get_latest_output', 'get_all_outputs',
    'get_tool_names', 'get_execution_summary',
    'your_new_method'  # Add new expected methods
}
```

## 📊 **Understanding Validation Results**

### **Success Case**
```
🔍 Quick Agent System Validation
========================================
📋 Tool Output Capture Methods: ✅ PASSED
📋 Configurable Agent Methods: ✅ PASSED
📋 Method Calls: ✅ PASSED
📋 Agent Factory: ✅ PASSED
✅ All agent validations passed!
✅ All validations passed! Ready for development.
```

### **Failure Case**
```
❌ Validation failed with 2 errors:
   - ConfigurableAgent missing tool_capture attribute
   - ToolOutputCaptureMixin missing clear_captured_outputs method
Please fix these issues before running the bot.
```

## 🎯 **Best Practices**

### **1. Run Validation Early and Often**
- Run quick validation before starting work
- Run validation after each significant change
- Run validation before testing

### **2. Fix Issues Immediately**
- Don't ignore validation errors
- Fix the root cause, not just the symptom
- Update validation rules if needed

### **3. Use Validation in CI/CD**
- Automate validation in your pipeline
- Fail fast on validation errors
- Provide clear error messages

### **4. Keep Validation Rules Updated**
- Add new validation rules for new features
- Remove obsolete validation rules
- Update expected methods as code evolves

## 🆘 **Troubleshooting**

### **Validation Script Not Found**
```bash
# Make sure you're in the project root
cd /path/to/KICKAI

# Activate virtual environment
source venv311/bin/activate

# Run validation
python scripts/quick_validation.py
```

### **Import Errors**
```bash
# Check Python path
echo $PYTHONPATH

# Set PYTHONPATH if needed
export PYTHONPATH=src:$PYTHONPATH
```

### **Permission Errors**
```bash
# Make scripts executable
chmod +x scripts/*.py
```

## 📈 **Performance Impact**

- **Quick Validation**: ~2-3 seconds
- **Comprehensive Validation**: ~5-10 seconds
- **Pre-Commit Validation**: ~30-60 seconds (including tests)

The validation overhead is minimal compared to the time saved by catching issues early.

## 🔄 **Continuous Improvement**

The validation system is designed to evolve with your codebase:

1. **Add new validation rules** as you encounter new types of issues
2. **Update existing rules** as your architecture changes
3. **Remove obsolete rules** that are no longer relevant
4. **Share validation patterns** with your team

This ensures that the validation system remains effective and relevant as your project grows. 