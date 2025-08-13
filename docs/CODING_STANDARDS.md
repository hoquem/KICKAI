# KICKAI Coding Standards

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Active Standards

## 🎯 Overview

This document defines the coding standards and best practices for the KICKAI project. All code must adhere to these standards to ensure consistency, maintainability, and reliability.

## 🏗️ Core Architecture Principles

### 1. **Clean Architecture**
- **Dependency Inversion**: High-level modules should not depend on low-level modules
- **Single Responsibility**: Each class/function should have one reason to change
- **Open/Closed Principle**: Open for extension, closed for modification
- **Interface Segregation**: Clients should not be forced to depend on interfaces they don't use

### 2. **Agentic-First Design**
- **ALL user interactions** go through CrewAI agents
- **No direct processing** bypasses the agentic system
- **Context-aware routing** based on user roles and chat types
- **Single source of truth** for command registry and agent orchestration

## 📝 Code Structure Standards

### **Single Try/Except Boundary Pattern**

**REQUIRED PATTERN** for all functions that can raise exceptions:

```python
def function_name(param1: str, param2: int) -> str:
    """
    Function description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        SpecificException: When specific condition occurs
    """
    try:
        # ALL business logic here
        # No nested try/except blocks
        # All validation, processing, and return logic
        
        return 'result'
        
    except Exception as e:
        logger.error(f"❌ Error in function_name: {e}")
        # Either throw or return error response
        raise  # or return error_response
```

**Key Requirements:**
- **Single try/except boundary** per function
- **ALL business logic** inside the try block
- **No nested try/except** blocks
- **Consistent error logging** with function name
- **Clear error handling** - either raise or return error response

### **Function Structure**

```python
@tool("tool_name", result_as_answer=True)
def tool_function(telegram_id: int, team_id: str, username: str, chat_type: str, **kwargs) -> str:
    """
    Tool description following docstring standards.
    
    Args:
        telegram_id: Telegram ID of the requesting user
        team_id: Team ID (required) - available from context
        username: Username of the requesting user
        chat_type: Chat type context
        **kwargs: Additional tool-specific parameters
        
    Returns:
        JSON response string with result or error
    """
    try:
        # 1. Input validation
        team_id = validate_team_id(team_id)
        telegram_id_int = validate_telegram_id(telegram_id)
        
        # 2. Log tool execution
        inputs = {'team_id': team_id, 'telegram_id': telegram_id_int}
        log_tool_execution("tool_name", inputs, True)
        
        # 3. Get services from container
        container = get_container()
        service = container.get_service(ServiceClass)
        
        if not service:
            return create_json_response("error", message="Service is not available")
        
        # 4. Business logic
        result = service.perform_operation(parameters)
        
        # 5. Create response
        return create_tool_response(
            success=True,
            message="Operation completed successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"❌ Error in tool_function: {e}")
        return create_json_response("error", message="Failed to perform operation")
```

## 🔧 Tool Development Standards

### **Required Tool Decorator**
```python
@tool("tool_name", result_as_answer=True)
```

### **Standard Parameters**
All tools must accept these standard parameters:
- `telegram_id: int` - User's Telegram ID
- `team_id: str` - Team identifier
- `username: str` - User's username
- `chat_type: str` - Chat context (main/leadership/private)

### **Return Format**
All tools must return JSON strings using utility functions:
- `create_json_response("success", data=result)` for success
- `create_json_response("error", message="error_description")` for errors
- `create_tool_response(success=True, message="msg", data=data)` for structured responses

## 🛡️ Error Handling Standards

### **Exception Hierarchy**
```python
# Base exceptions
class KICKAIException(Exception):
    """Base exception for KICKAI system."""
    pass

class ValidationError(KICKAIException):
    """Raised when input validation fails."""
    pass

class ServiceError(KICKAIException):
    """Raised when service operations fail."""
    pass

class ToolError(KICKAIException):
    """Raised when tool execution fails."""
    pass
```

### **Error Logging**
```python
# Standard error logging format
logger.error(f"❌ Error in {function_name}: {e}")
logger.warning(f"⚠️ Warning in {function_name}: {message}")
logger.info(f"ℹ️ Info in {function_name}: {message}")
```

### **Error Response Format**
```python
# Standard error response
return create_json_response("error", message="Descriptive error message")
```

## 📊 Data Validation Standards

### **Input Validation**
```python
# Use utility functions for validation
team_id = validate_team_id(team_id)
telegram_id_int = validate_telegram_id(telegram_id)
phone = validate_phone_number(phone)
player_id = validate_player_id(player_id)
```

### **Required Input Validation**
```python
# Validate required inputs
validation_error = validate_required_input(team_id, "Team ID")
if validation_error:
    return create_json_response("error", message=validation_error)
```

## 🔄 Service Integration Standards

### **Service Container Pattern**
```python
# Standard service retrieval
container = get_container()
service = container.get_service(ServiceClass)

if not service:
    return create_json_response("error", message="Service is not available")
```

### **Service Error Handling**
```python
# Handle service unavailability
try:
    result = service.operation(parameters)
except ServiceNotAvailableError:
    return create_json_response("error", message="Service is not available")
except Exception as e:
    logger.error(f"❌ Service operation failed: {e}")
    return create_json_response("error", message="Service operation failed")
```

## 📝 Documentation Standards

### **Docstring Format**
```python
def function_name(param1: str, param2: int) -> str:
    """
    Brief description of what the function does.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1 and its expected format
        param2: Description of param2 and its constraints
        
    Returns:
        Description of return value and its format
        
    Raises:
        ValidationError: When input validation fails
        ServiceError: When service operation fails
        
    Example:
        >>> result = function_name("value1", 42)
        >>> print(result)
        "success"
    """
```

### **Type Hints**
- **Required** for all function parameters and return values
- **Use specific types** (str, int, bool, List[str], Dict[str, Any])
- **Import types** from typing module when needed

## 🧪 Testing Standards

### **Test Structure**
```python
async def test_function_name():
    """Test description."""
    try:
        # Arrange
        test_data = setup_test_data()
        
        # Act
        result = await function_name(test_data)
        
        # Assert
        assert result.success is True
        assert "expected_value" in result.data
        
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
```

### **Test Coverage Requirements**
- **Unit tests** for all business logic functions
- **Integration tests** for service interactions
- **E2E tests** for complete user workflows
- **Minimum 80% code coverage** required

## 🔍 Code Quality Standards

### **Linting and Formatting**
- **Ruff** for linting and formatting
- **Black** code style (enforced by Ruff)
- **isort** for import sorting (enforced by Ruff)
- **mypy** for type checking

### **Pre-commit Hooks**
```bash
# Run before committing
ruff check --fix src/
ruff format src/
mypy src/
```

### **Code Review Checklist**
- [ ] Follows Single Try/Except Boundary Pattern
- [ ] Includes proper type hints
- [ ] Has comprehensive docstrings
- [ ] Includes error handling
- [ ] Uses utility functions for common operations
- [ ] Follows naming conventions
- [ ] Includes appropriate tests
- [ ] No duplicate code patterns

## 🏷️ Naming Conventions

### **Functions and Variables**
- **snake_case** for functions and variables
- **descriptive names** that explain purpose
- **avoid abbreviations** unless widely understood

### **Classes**
- **PascalCase** for class names
- **descriptive names** that indicate purpose
- **suffix with type** when appropriate (Service, Repository, etc.)

### **Constants**
- **UPPER_SNAKE_CASE** for constants
- **descriptive names** that explain value
- **group related constants** in modules

### **Files and Directories**
- **snake_case** for file names
- **descriptive names** that indicate content
- **use appropriate extensions** (.py, .yaml, .md)

## 🔄 Refactoring Guidelines

### **When to Refactor**
- **Duplicate code** patterns (3+ occurrences)
- **Long functions** (>50 lines)
- **Complex conditional logic** (>3 nested levels)
- **Multiple responsibilities** in single function
- **Inconsistent patterns** across similar functions

### **Refactoring Patterns**
```python
# Extract common patterns into utility functions
def create_player_data(player: Player, telegram_id: int, team_id: str) -> Dict[str, Any]:
    """Create standardized player data structure."""
    return {
        "type": "player",
        "name": player.name or "Not provided",
        "position": player.position or "Not assigned",
        "status": player.status.title() if player.status else "Unknown",
        "player_id": player.player_id or "Not assigned",
        "phone_number": player.phone_number or "Not provided",
        "telegram_id": telegram_id,
        "team_id": team_id,
        "is_active": player.status and player.status.lower() == "active",
        "is_pending": player.status and player.status.lower() == "pending"
    }

# Use in tools
player_data = create_player_data(player, telegram_id_int, team_id)
```

## 📋 Compliance Checklist

Before submitting code for review, ensure:

- [ ] **Single Try/Except Boundary Pattern** implemented
- [ ] **All business logic** inside try block
- [ ] **Proper error logging** with function name
- [ ] **Type hints** for all parameters and returns
- [ ] **Comprehensive docstrings** following format
- [ ] **Input validation** using utility functions
- [ ] **Service container pattern** for service access
- [ ] **Standard return format** using utility functions
- [ ] **No duplicate code** patterns
- [ ] **Appropriate tests** included
- [ ] **Linting passes** (Ruff, mypy)
- [ ] **Naming conventions** followed

## 🚀 Performance Standards

### **Async/Await Usage**
- **Use async/await** for I/O operations
- **Avoid blocking operations** in async functions
- **Use asyncio.gather()** for concurrent operations
- **Implement proper timeouts** for external calls

### **Resource Management**
- **Use context managers** for resource cleanup
- **Implement proper error handling** for resource failures
- **Monitor memory usage** in long-running operations
- **Use connection pooling** for database operations

---

**Remember:** These standards ensure code quality, maintainability, and consistency across the KICKAI project. All team members must follow these standards for all code contributions.

