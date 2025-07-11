# KICKAI Logging Standards

This document outlines the standardized logging practices for the KICKAI system to ensure consistent, debuggable, and observable error handling across the entire codebase.

## Overview

The KICKAI system uses structured logging with comprehensive error context to provide detailed debugging information while maintaining clean, user-friendly error messages.

## Key Principles

1. **Context-Rich Logging**: Every log entry includes relevant context (team_id, user_id, operation, etc.)
2. **Structured Error Messages**: Use standardized templates instead of generic error messages
3. **Full Stack Traces**: Capture complete error information for debugging
4. **User-Friendly Messages**: Provide clear, actionable error messages to users
5. **Security**: Sanitize sensitive information in logs
6. **Performance**: Include performance metrics and timing information

## Error Categories and Severity

### Error Categories
- `VALIDATION`: Input validation errors
- `DATABASE`: Database connection and query errors
- `NETWORK`: Network connectivity issues
- `AUTHENTICATION`: User authentication failures
- `AUTHORIZATION`: Permission and access control errors
- `BUSINESS_LOGIC`: Business rule violations
- `SYSTEM`: System-level errors
- `EXTERNAL_SERVICE`: Third-party service errors
- `CONFIGURATION`: Configuration and setup errors
- `UNKNOWN`: Unclassified errors

### Error Severity Levels
- `LOW`: Minor issues, warnings
- `MEDIUM`: Standard errors that need attention
- `HIGH`: Serious errors that may affect functionality
- `CRITICAL`: System-critical errors requiring immediate attention

## Usage Examples

### Basic Error Logging

```python
from src.core.enhanced_logging import log_error, ErrorCategory, ErrorSeverity

try:
    # Your code here
    result = some_operation()
except Exception as e:
    error_msg = log_error(
        error=e,
        operation="player_registration",
        team_id="KAI",
        user_id="12345",
        chat_id="-4814449926",
        category=ErrorCategory.BUSINESS_LOGIC,
        severity=ErrorSeverity.MEDIUM,
        user_message="Failed to register player. Please try again."
    )
    return False, error_msg
```

### Command Error Logging

```python
from src.core.enhanced_logging import log_command_error

try:
    # Command execution
    result = execute_command(command, args)
except Exception as e:
    error_msg = log_command_error(
        error=e,
        command="/add",
        team_id="KAI",
        user_id="12345",
        chat_id="-4814449926",
        user_message="❌ Error adding player. Please check the information and try again."
    )
    return False, error_msg
```

### Database Error Logging

```python
from src.core.enhanced_logging import log_database_error

try:
    # Database operation
    player = db.get_player(player_id)
except Exception as e:
    error_msg = log_database_error(
        error=e,
        operation="get_player",
        team_id="KAI",
        user_id="12345",
        user_message="❌ Database error. Please try again later."
    )
    return False, error_msg
```

### Validation Error Logging

```python
from src.core.enhanced_logging import log_validation_error

try:
    # Validation
    validate_player_data(data)
except ValueError as e:
    error_msg = log_validation_error(
        error=e,
        operation="validate_player_data",
        field="phone",
        team_id="KAI",
        user_id="12345",
        user_message="❌ Invalid phone number format. Please use: 07123456789"
    )
    return False, error_msg
```

### Using Error Message Templates

```python
from src.core.enhanced_logging import ErrorMessageTemplates

# Use predefined templates
error_msg = ErrorMessageTemplates.format(
    ErrorMessageTemplates.PLAYER_NOT_FOUND,
    player_id="12345",
    team_id="KAI"
)
# Result: "Player '12345' not found in team 'KAI'"

# Custom template with context
error_msg = ErrorMessageTemplates.format(
    ErrorMessageTemplates.GENERIC_ERROR,
    operation="player_registration",
    team_id="KAI",
    user_id="12345",
    reason="Invalid phone number format"
)
# Result: "Error in player_registration for team 'KAI' (user: 12345): Invalid phone number format"
```

### Using the Error Handler Decorator

```python
from src.core.enhanced_logging import handle_errors, ErrorCategory, ErrorSeverity

@handle_errors(
    category=ErrorCategory.BUSINESS_LOGIC,
    severity=ErrorSeverity.MEDIUM,
    user_message_template="❌ Error adding player '{name}' to team '{team_id}': {reason}"
)
def add_player(name: str, phone: str, position: str, team_id: str, user_id: str):
    # Your implementation here
    # If an exception occurs, it will be automatically logged with context
    pass
```

## Error Message Templates

### Player Operations
- `PLAYER_NOT_FOUND`: "Player '{player_id}' not found in team '{team_id}'"
- `PLAYER_ALREADY_EXISTS`: "Player with phone '{phone}' already exists in team '{team_id}'"
- `PLAYER_REGISTRATION_FAILED`: "Failed to register player '{phone}' in team '{team_id}': {reason}"
- `PLAYER_APPROVAL_FAILED`: "Failed to approve player '{player_id}' in team '{team_id}': {reason}"
- `PLAYER_REMOVAL_FAILED`: "Failed to remove player '{player_id}' from team '{team_id}': {reason}"

### Team Operations
- `TEAM_NOT_FOUND`: "Team '{team_id}' not found"
- `TEAM_CREATION_FAILED`: "Failed to create team '{team_id}': {reason}"
- `TEAM_DELETION_FAILED`: "Failed to delete team '{team_id}': {reason}"

### Match Operations
- `MATCH_NOT_FOUND`: "Match '{match_id}' not found in team '{team_id}'"
- `MATCH_CREATION_FAILED`: "Failed to create match in team '{team_id}': {reason}"
- `MATCH_UPDATE_FAILED`: "Failed to update match '{match_id}' in team '{team_id}': {reason}"

### Payment Operations
- `PAYMENT_RECORDING_FAILED`: "Failed to record payment for player '{player_id}' in team '{team_id}': {reason}"
- `PAYMENT_NOT_FOUND`: "Payment '{payment_id}' not found in team '{team_id}'"
- `PAYMENT_REFUND_FAILED`: "Failed to refund payment '{payment_id}' in team '{team_id}': {reason}"

### Database Operations
- `DATABASE_CONNECTION_FAILED`: "Database connection failed: {reason}"
- `DATABASE_QUERY_FAILED`: "Database query failed for operation '{operation}' in team '{team_id}': {reason}"
- `DATABASE_TRANSACTION_FAILED`: "Database transaction failed for operation '{operation}' in team '{team_id}': {reason}"

### Authentication/Authorization
- `USER_NOT_AUTHORIZED`: "User '{user_id}' not authorized for operation '{operation}' in team '{team_id}'"
- `INVALID_PERMISSIONS`: "Insufficient permissions for operation '{operation}' in team '{team_id}'"

### Validation Errors
- `INVALID_INPUT`: "Invalid input for operation '{operation}': {reason}"
- `MISSING_REQUIRED_FIELD`: "Missing required field '{field}' for operation '{operation}'"
- `INVALID_FORMAT`: "Invalid format for field '{field}' in operation '{operation}': {reason}"

### System Errors
- `CONFIGURATION_ERROR`: "Configuration error: {reason}"
- `EXTERNAL_SERVICE_ERROR`: "External service '{service}' error: {reason}"
- `NETWORK_ERROR`: "Network error for operation '{operation}': {reason}"

### Generic Template
- `GENERIC_ERROR`: "Error in {operation} for team '{team_id}' (user: {user_id}): {reason}"

## Migration Guide

### Before (Generic Error Messages)
```python
try:
    result = some_operation()
except Exception as e:
    return False, f"❌ Error: {str(e)}"
```

### After (Structured Error Messages)
```python
from src.core.enhanced_logging import log_error, ErrorCategory, ErrorSeverity

try:
    result = some_operation()
except Exception as e:
    error_msg = log_error(
        error=e,
        operation="some_operation",
        team_id=team_id,
        user_id=user_id,
        category=ErrorCategory.BUSINESS_LOGIC,
        severity=ErrorSeverity.MEDIUM,
        user_message="❌ Operation failed. Please try again."
    )
    return False, error_msg
```

### Before (Generic Database Errors)
```python
try:
    player = db.get_player(player_id)
except Exception as e:
    return False, f"❌ Error getting player info: {str(e)}"
```

### After (Structured Database Errors)
```python
from src.core.enhanced_logging import log_database_error

try:
    player = db.get_player(player_id)
except Exception as e:
    error_msg = log_database_error(
        error=e,
        operation="get_player",
        team_id=team_id,
        user_id=user_id,
        user_message="❌ Error retrieving player information. Please try again."
    )
    return False, error_msg
```

## Log Output Format

### Text Format (Default)
```
2025-07-08T14:30:00.123456 [ERROR] src.services.player_service: Error in player_registration: Player with phone '07123456789' already exists | Context: team_id=KAI user_id=12345 operation=player_registration component=src.services.player_service | Exception: PlayerExistsError: Player already registered
```

### JSON Format (When KICKAI_LOG_FORMAT=json)
```json
{
  "timestamp": "2025-07-08T14:30:00.123456",
  "level": "ERROR",
  "logger": "src.services.player_service",
  "message": "Error in player_registration: Player with phone '07123456789' already exists",
  "module": "player_service",
  "function": "register_player",
  "line": 45,
  "context": {
    "team_id": "KAI",
    "user_id": "12345",
    "chat_id": "-4814449926",
    "operation": "player_registration",
    "component": "src.services.player_service",
    "request_id": "req_12345",
    "duration_ms": 150.5,
    "metadata": {
      "error_type": "PlayerExistsError",
      "error_category": "BUSINESS_LOGIC",
      "error_severity": "MEDIUM",
      "input_summary": "Input: phone='07123456789' name='John Smith' position='midfielder'",
      "suggestions": [
        "Check if player already exists before registration",
        "Verify phone number format and uniqueness"
      ]
    }
  },
  "exception": {
    "type": "PlayerExistsError",
    "message": "Player already registered",
    "traceback": ["Traceback (most recent call last):", "..."]
  }
}
```

## Best Practices

1. **Always include context**: team_id, user_id, operation name
2. **Use appropriate error categories**: Helps with filtering and analysis
3. **Set correct severity levels**: Ensures proper alerting and prioritization
4. **Provide user-friendly messages**: Clear, actionable error messages
5. **Use error message templates**: Ensures consistency across the system
6. **Sanitize sensitive data**: Never log passwords, tokens, or personal information
7. **Include debugging suggestions**: Help developers understand and fix issues
8. **Log performance metrics**: Include timing and resource usage information
9. **Use structured logging**: Consistent format for better parsing and analysis
10. **Test error scenarios**: Ensure error messages are helpful and accurate

## Configuration

### Environment Variables
- `KICKAI_LOG_FORMAT`: Set to "json" for structured JSON logging (default: "text")
- `KICKAI_LOG_LEVEL`: Set minimum log level (default: "INFO")
- `KICKAI_LOG_FILE`: Path to log file (optional)

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General information about system operation
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for actual problems
- `CRITICAL`: Critical errors requiring immediate attention

## Monitoring and Alerting

The structured logging system provides rich context for monitoring and alerting:

1. **Error Rate Monitoring**: Track error rates by category, severity, and operation
2. **Performance Monitoring**: Monitor operation duration and resource usage
3. **User Impact Analysis**: Identify which users and teams are affected by errors
4. **Trend Analysis**: Track error patterns over time
5. **Root Cause Analysis**: Use stack traces and context for debugging

## Integration with Existing Systems

The enhanced logging system integrates with:
- **Firebase**: Error logs are stored in Firestore for analysis
- **Monitoring**: Performance metrics and error rates
- **Alerting**: Critical errors trigger immediate notifications
- **Analytics**: Error patterns and user impact analysis 