# KICKAI Coding Standards

## Overview

This document defines the coding standards and best practices for the KICKAI project. All code must adhere to these standards to ensure consistency, maintainability, and quality.

## Python Code Style

### General Guidelines

- **Python Version**: Use Python 3.11+ features
- **Line Length**: Maximum 88 characters (Black formatter default)
- **Indentation**: 4 spaces (no tabs)
- **String Quotes**: Use double quotes for strings
- **Import Order**: Standard library, third-party, local imports
- **Type Hints**: Use type hints for all function parameters and return values

### Naming Conventions

- **Classes**: PascalCase (e.g., `TeamMember`, `PlayerService`)
- **Functions/Methods**: snake_case (e.g., `get_team_members`, `create_player`)
- **Variables**: snake_case (e.g., `team_id`, `player_name`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_ATTEMPTS`)
- **Private Methods**: Prefix with underscore (e.g., `_validate_input`)

## Docstring Standards

### reStructuredText (reST) Format

**All docstrings MUST use reStructuredText format, NOT Google-style or NumPy-style.**

#### Function/Method Docstrings

```python
def my_function(param1: str, param2: int, optional_param: bool = False) -> str:
    """
    Brief description of what the function does.

    :param param1: Description of the first parameter
    :type param1: str
    :param param2: Description of the second parameter
    :type param2: int
    :param optional_param: Description of optional parameter (default: False)
    :type optional_param: bool
    :return: Description of what is returned
    :rtype: str
    :raises ValueError: When something goes wrong
    :raises TypeError: When parameter types are incorrect
    """
```

#### Class Docstrings

```python
class MyClass:
    """
    Brief description of the class.

    :param name: Description of the name parameter
    :type name: str
    :param value: Description of the value parameter
    :type value: int
    """

    def __init__(self, name: str, value: int):
        """
        Initialize the class.

        :param name: Description of the name parameter
        :type name: str
        :param value: Description of the value parameter
        :type value: int
        """
```

#### Tool Docstrings (CrewAI)

```python
@tool("tool_name")
def my_tool(telegram_id: int, team_id: str, field: str) -> str:
    """
    Brief description of what the tool does.

    :param telegram_id: Telegram user ID of the user
    :type telegram_id: int
    :param team_id: Team ID for context
    :type team_id: str
    :param field: Field name to process
    :type field: str
    :return: Tool execution result
    :rtype: str
    """
```

### Docstring Requirements

1. **Always use reStructuredText format** with `:param:`, `:type:`, `:return:`, `:rtype:` tags
2. **Include type information** for all parameters and return values
3. **Document exceptions** with `:raises:` when applicable
4. **Keep descriptions concise** but informative
5. **Use consistent terminology** across the codebase
6. **Include examples** for complex functions when helpful

### Forbidden Formats

❌ **DO NOT USE Google-style:**
```python
def my_function(param1: str, param2: int) -> str:
    """
    Brief description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description of return value
    """
```

❌ **DO NOT USE NumPy-style:**
```python
def my_function(param1: str, param2: int) -> str:
    """
    Brief description.

    Parameters
    ----------
    param1 : str
        Description
    param2 : int
        Description

    Returns
    -------
    str
        Description
    """
```

## Type Hints

### Required Type Hints

- All function parameters
- All function return values
- All class attributes
- All variable assignments where type is not obvious

### Type Hint Examples

```python
from typing import Optional, List, Dict, Any, Union

def process_data(
    data: List[Dict[str, Any]], 
    config: Optional[Dict[str, str]] = None
) -> Union[str, None]:
    """
    Process the given data.

    :param data: List of data dictionaries to process
    :type data: List[Dict[str, Any]]
    :param config: Optional configuration dictionary
    :type config: Optional[Dict[str, str]]
    :return: Processed result or None if failed
    :rtype: Union[str, None]
    """
```

## Error Handling

### Exception Handling Guidelines

1. **Use specific exceptions** rather than generic `Exception`
2. **Include context** in error messages
3. **Log errors** with appropriate log levels
4. **Use custom exceptions** for domain-specific errors
5. **Handle exceptions at appropriate levels**

### Error Handling Example

```python
from loguru import logger
from kickai.core.exceptions import ValidationError, ServiceNotAvailableError

def process_user_data(user_id: int, data: Dict[str, Any]) -> str:
    """
    Process user data with proper error handling.

    :param user_id: User ID to process
    :type user_id: int
    :param data: User data dictionary
    :type data: Dict[str, Any]
    :return: Processing result
    :rtype: str
    :raises ValidationError: When data validation fails
    :raises ServiceNotAvailableError: When required service is unavailable
    """
    try:
        if not data:
            raise ValidationError("User data cannot be empty")
        
        # Process data
        result = validate_and_process(data)
        return result
        
    except ValidationError as e:
        logger.error(f"Validation failed for user {user_id}: {e}")
        raise
    except ServiceNotAvailableError as e:
        logger.error(f"Service unavailable for user {user_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing user {user_id}: {e}")
        raise
```

## Logging Standards

### Logging Guidelines

1. **Use loguru** for all logging
2. **Use appropriate log levels**:
   - `DEBUG`: Detailed information for debugging
   - `INFO`: General information about program execution
   - `WARNING`: Warning messages for potentially problematic situations
   - `ERROR`: Error messages for serious problems
   - `CRITICAL`: Critical errors that may prevent the program from running
3. **Include context** in log messages
4. **Use structured logging** when appropriate

### Logging Example

```python
from loguru import logger

def process_team_member(telegram_id: int, team_id: str) -> bool:
    """
    Process team member data.

    :param telegram_id: Telegram user ID
    :type telegram_id: int
    :param team_id: Team ID
    :type team_id: str
    :return: Success status
    :rtype: bool
    """
    logger.info(f"Processing team member {telegram_id} for team {team_id}")
    
    try:
        # Process member
        result = perform_processing(telegram_id, team_id)
        logger.info(f"Successfully processed team member {telegram_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process team member {telegram_id}: {e}")
        return False
```

## Testing Standards

### Test Requirements

1. **Unit tests** for all business logic
2. **Integration tests** for service interactions
3. **End-to-end tests** for complete workflows
4. **Test coverage** minimum 80%
5. **Use pytest** for all testing

### Test Example

```python
import pytest
from kickai.features.team_administration.domain.entities.team_member import TeamMember

def test_team_member_creation():
    """
    Test team member creation with valid data.

    :return: None
    :rtype: None
    """
    # Arrange
    telegram_id = 123456789
    team_id = "TEST"
    name = "John Doe"
    
    # Act
    member = TeamMember.create_from_telegram(
        team_id=team_id,
        telegram_id=telegram_id,
        name=name
    )
    
    # Assert
    assert member.telegram_id == str(telegram_id)
    assert member.team_id == team_id
    assert member.name == name
```

## File Organization

### Directory Structure

```
kickai/
├── features/           # Feature modules
│   ├── feature_name/
│   │   ├── application/    # Application layer
│   │   ├── domain/         # Domain layer
│   │   └── infrastructure/ # Infrastructure layer
├── core/              # Core functionality
├── utils/             # Utility functions
└── tests/             # Test files
```

### File Naming

- **Python files**: snake_case (e.g., `team_member_service.py`)
- **Test files**: `test_` prefix (e.g., `test_team_member_service.py`)
- **Configuration files**: descriptive names (e.g., `config.yaml`)

## Code Quality Tools

### Required Tools

1. **Ruff**: Linting and formatting
2. **Black**: Code formatting (via Ruff)
3. **isort**: Import sorting (via Ruff)
4. **mypy**: Type checking
5. **pytest**: Testing

### Pre-commit Hooks

All code must pass pre-commit hooks:
- Ruff linting and formatting
- Type checking
- Test execution

## Documentation Standards

### Code Documentation

1. **All public APIs** must be documented
2. **Use reStructuredText** for all docstrings
3. **Include examples** for complex functionality
4. **Keep documentation up-to-date** with code changes

### README Files

Each major component should have a README.md file with:
- Purpose and functionality
- Usage examples
- Configuration requirements
- Dependencies

## Security Standards

### Security Guidelines

1. **Never commit secrets** or sensitive data
2. **Use environment variables** for configuration
3. **Validate all inputs** from external sources
4. **Use secure defaults** for all configurations
5. **Log security events** appropriately

### Security Example

```python
import os
from typing import Optional

def get_database_connection() -> Optional[str]:
    """
    Get database connection string from environment.

    :return: Database connection string or None if not configured
    :rtype: Optional[str]
    """
    # Use environment variable for sensitive data
    connection_string = os.getenv("DATABASE_URL")
    
    if not connection_string:
        logger.warning("Database connection string not configured")
        return None
    
    return connection_string
```

## Performance Standards

### Performance Guidelines

1. **Use async/await** for I/O operations
2. **Implement caching** for expensive operations
3. **Use connection pooling** for database connections
4. **Optimize database queries** with proper indexing
5. **Monitor performance** with appropriate metrics

## Review Process

### Code Review Requirements

1. **All code changes** must be reviewed
2. **Check for adherence** to coding standards
3. **Verify test coverage** requirements
4. **Ensure documentation** is updated
5. **Validate security** considerations

### Review Checklist

- [ ] Code follows style guidelines
- [ ] All functions have proper docstrings (reStructuredText format)
- [ ] Type hints are included
- [ ] Error handling is appropriate
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact considered

## Enforcement

### Compliance

- **Automated checks** via CI/CD pipeline
- **Manual review** for complex changes
- **Regular audits** of codebase compliance
- **Training** for team members on standards

### Tools

- **Pre-commit hooks** for automatic checking
- **CI/CD pipeline** for continuous validation
- **Code review** process for manual validation
- **Documentation** for reference and training

---

**Last Updated**: 2024-12-19
**Version**: 1.0
**Maintainer**: KICKAI Development Team
