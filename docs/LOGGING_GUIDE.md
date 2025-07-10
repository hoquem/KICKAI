# KICKAI Logging Guide

## Overview

This guide documents the centralized logging system for KICKAI, which provides standardized logging configuration, message formats, and error handling patterns for consistent debugging across the entire system.

## Features

- **Structured Logging**: All log messages include context information (team_id, user_id, chat_id, operation, component)
- **Standardized Levels**: Consistent log levels with clear meanings across all components
- **Performance Monitoring**: Built-in performance logging with duration tracking
- **Error Handling**: Comprehensive error logging with stack traces and context
- **Configurable Output**: Support for both text and JSON log formats
- **Business Events**: Specialized logging for business operations and security events

## Quick Start

### Basic Usage

```python
from src.core.logging_config import get_logger, LogContext

# Get a logger
logger = get_logger(__name__)

# Basic logging
logger.info("Operation completed successfully")
logger.error("Something went wrong", exc_info=exception)

# Logging with context
context = LogContext(
    team_id="team123",
    user_id="user456",
    chat_id="chat789",
    operation="player_registration",
    component="player_service"
)
logger.info("Player registered successfully", context=context)
```

### Performance Logging

```python
from src.core.logging_config import log_performance

@log_performance("database_query")
async def get_player_data(player_id: str):
    # Your code here
    pass
```

### Error Logging

```python
from src.core.logging_config import log_errors

@log_errors
def process_payment(payment_data):
    # Your code here
    pass
```

## Log Levels

### DEBUG
- Detailed diagnostic information
- Used for troubleshooting and development
- Not typically enabled in production

```python
logger.debug("Processing user request", context=context)
logger.debug(f"Database query: {query}", context=context)
```

### INFO
- General operational messages
- Confirmation that things are working as expected
- Important business events

```python
logger.info("User login successful", context=context)
logger.info("Payment processed", context=context)
logger.info("System startup completed", context=context)
```

### WARNING
- Something unexpected happened but the system can continue
- Potential issues that should be investigated
- Degraded performance or functionality

```python
logger.warning("Database connection slow", context=context)
logger.warning("User permission denied", context=context)
logger.warning("Fallback to default configuration", context=context)
```

### ERROR
- Something failed and needs attention
- Operations that cannot complete
- System errors that affect functionality

```python
logger.error("Database connection failed", context=context, exc_info=exception)
logger.error("Payment processing failed", context=context, exc_info=exception)
logger.error("User authentication failed", context=context, exc_info=exception)
```

### CRITICAL
- System-level failures that require immediate attention
- Security violations
- Data corruption or loss

```python
logger.critical("Database corruption detected", context=context, exc_info=exception)
logger.critical("Security breach detected", context=context, exc_info=exception)
logger.critical("System shutdown required", context=context, exc_info=exception)
```

## Log Context

The `LogContext` class provides structured information for all log messages:

```python
@dataclass
class LogContext:
    team_id: Optional[str] = None          # Team identifier
    user_id: Optional[str] = None          # User identifier
    chat_id: Optional[str] = None          # Chat identifier
    operation: Optional[str] = None        # Current operation
    component: Optional[str] = None        # Component name
    request_id: Optional[str] = None       # Request identifier
    duration_ms: Optional[float] = None    # Operation duration
    metadata: Optional[Dict[str, Any]] = None  # Additional context
```

### Context Best Practices

1. **Always include relevant context**:
   ```python
   context = LogContext(
       team_id=self.team_id,
       user_id=user_id,
       operation="player_registration"
   )
   ```

2. **Use consistent operation names**:
   - `player_registration`
   - `payment_processing`
   - `match_creation`
   - `user_authentication`

3. **Include component information**:
   - `player_service`
   - `payment_service`
   - `match_service`
   - `auth_service`

4. **Add metadata for complex operations**:
   ```python
   context = LogContext(
       team_id=self.team_id,
       operation="payment_processing",
       metadata={
           "payment_amount": amount,
           "payment_method": method,
           "currency": currency
       }
   )
   ```

## Specialized Logging

### Performance Logging

Track operation performance with automatic duration measurement:

```python
from src.core.logging_config import log_performance

@log_performance("database_query")
async def get_player_data(player_id: str):
    # Your database query here
    pass

# Manual performance logging
logger.performance("payment_processing", 150.5, context=context)
```

### Business Event Logging

Log important business operations:

```python
from src.core.logging_config import log_business_event

@log_business_event("player_registration", {"player_id": "123", "team_id": "456"})
def register_player(player_data):
    # Registration logic here
    pass

# Manual business event logging
logger.business_event("payment_completed", {
    "payment_id": "pay_123",
    "amount": 100.00,
    "currency": "USD"
}, context=context)
```

### Security Event Logging

Log security-related events:

```python
from src.core.logging_config import log_security_event

logger.security_event("access_denied", {
    "user_id": "user123",
    "resource": "admin_panel",
    "reason": "insufficient_permissions"
}, context=context)
```

## Configuration

### Environment Variables

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
KICKAI_LOG_LEVEL=INFO

# Log format (text, json)
KICKAI_LOG_FORMAT=text

# Log file path
KICKAI_LOG_FILE=logs/kickai.log
```

### Programmatic Configuration

```python
from src.core.logging_config import configure_logging

configure_logging(
    log_level="INFO",
    log_format="text",
    log_file="logs/kickai.log",
    include_context=True
)
```

## Log Format Examples

### Text Format
```
2024-01-15T10:30:45.123456 [INFO] src.services.player_service: Player registered successfully | Context: team_id=team123 user_id=user456 operation=player_registration component=player_service
```

### JSON Format
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "src.services.player_service",
  "message": "Player registered successfully",
  "module": "player_service",
  "function": "register_player",
  "line": 45,
  "context": {
    "team_id": "team123",
    "user_id": "user456",
    "operation": "player_registration",
    "component": "player_service"
  }
}
```

## Best Practices

### 1. Use Descriptive Messages
```python
# Good
logger.info("Player registration completed successfully", context=context)

# Bad
logger.info("Done", context=context)
```

### 2. Include Relevant Context
```python
# Good
context = LogContext(
    team_id=self.team_id,
    user_id=user_id,
    operation="payment_processing",
    metadata={"amount": amount, "currency": currency}
)

# Bad
logger.info("Payment processed")  # No context
```

### 3. Handle Exceptions Properly
```python
try:
    result = await process_payment(payment_data)
    logger.info("Payment processed successfully", context=context)
    return result
except PaymentError as e:
    logger.error("Payment processing failed", context=context, exc_info=e)
    raise
except Exception as e:
    logger.error("Unexpected error during payment processing", context=context, exc_info=e)
    raise
```

### 4. Use Appropriate Log Levels
```python
# DEBUG: Detailed diagnostic information
logger.debug(f"Processing request with parameters: {params}", context=context)

# INFO: General operational messages
logger.info("User login successful", context=context)

# WARNING: Unexpected but recoverable issues
logger.warning("Database connection slow, using fallback", context=context)

# ERROR: Failures that need attention
logger.error("Database connection failed", context=context, exc_info=exception)

# CRITICAL: System-level failures
logger.critical("Database corruption detected", context=context, exc_info=exception)
```

### 5. Avoid Sensitive Information
```python
# Good
logger.info("User authentication successful", context=context)

# Bad - Don't log passwords, tokens, or personal data
logger.info(f"User login with password: {password}", context=context)
```

### 6. Use Structured Data
```python
# Good - Use metadata for structured data
context = LogContext(
    team_id=self.team_id,
    operation="match_creation",
    metadata={
        "home_team": "Team A",
        "away_team": "Team B",
        "date": "2024-01-15",
        "venue": "Stadium X"
    }
)

# Bad - Don't concatenate data into messages
logger.info(f"Created match: Team A vs Team B on 2024-01-15 at Stadium X", context=context)
```

## Migration Guide

### From Basic Logging

**Before:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Operation completed")
logger.error("Error occurred", exc_info=exception)
```

**After:**
```python
from src.core.logging_config import get_logger, LogContext
logger = get_logger(__name__)
logger.info("Operation completed", context=LogContext(component="my_service"))
logger.error("Error occurred", context=LogContext(component="my_service"), exc_info=exception)
```

### From Emoji Logging

**Before:**
```python
logger.info("✅ Operation completed successfully")
logger.error("❌ Error occurred")
```

**After:**
```python
logger.info("Operation completed successfully", context=context)
logger.error("Error occurred", context=context, exc_info=exception)
```

## Troubleshooting

### Common Issues

1. **Missing Context**: Always include relevant context information
2. **Inappropriate Log Levels**: Use the correct log level for the message
3. **Sensitive Data**: Never log passwords, tokens, or personal information
4. **Performance Impact**: Avoid expensive operations in log messages
5. **Circular Imports**: Import logging configuration at the top of files

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export KICKAI_LOG_LEVEL=DEBUG
export KICKAI_LOG_FORMAT=text
```

### Log Analysis

Use structured logging for easier log analysis:

```bash
# Filter logs by team
grep "team_id=team123" logs/kickai.log

# Filter logs by operation
grep "operation=payment_processing" logs/kickai.log

# Filter logs by user
grep "user_id=user456" logs/kickai.log
```

## Integration with Monitoring

The logging system integrates with monitoring tools:

- **Performance Metrics**: Automatic duration tracking
- **Error Tracking**: Structured error logging with context
- **Business Metrics**: Business event logging for analytics
- **Security Monitoring**: Security event logging for alerts

## Conclusion

This centralized logging system provides a consistent, structured approach to logging across the entire KICKAI system. By following these guidelines, you'll have better visibility into system operations, easier debugging, and improved monitoring capabilities. 