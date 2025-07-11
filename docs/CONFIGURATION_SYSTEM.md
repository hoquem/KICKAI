# Clean Configuration System

## Overview

The KICKAI system now uses a clean, type-safe configuration system built with **Pydantic Settings**. This replaces the complex 1200+ line configuration system with a simple, maintainable solution that provides:

- ✅ **Type Safety**: All configuration values are validated at runtime
- ✅ **Environment Variable Support**: Automatic loading from `.env` files
- ✅ **Validation**: Built-in validation with clear error messages
- ✅ **Documentation**: Self-documenting configuration with descriptions
- ✅ **Backward Compatibility**: Gradual migration support
- ✅ **Zero Dependencies**: Uses existing Pydantic installation

## Quick Start

### Basic Usage

```python
from core.settings import get_settings

# Get configuration
settings = get_settings()

# Access configuration values
bot_token = settings.telegram_bot_token
api_key = settings.google_api_key
project_id = settings.firebase_project_id
```

### Environment Detection

```python
# Automatic environment detection
if settings.is_development:
    print("Running in development mode")
elif settings.is_production:
    print("Running in production mode")
elif settings.is_testing:
    print("Running in testing mode")
```

### Validation

```python
# Validate required fields
errors = settings.validate_required_fields()
if errors:
    for error in errors:
        print(f"Configuration error: {error}")
```

## Configuration Structure

### Environment Variables

The system automatically loads from environment variables with these mappings:

| Environment Variable | Configuration Field | Required | Default |
|---------------------|-------------------|----------|---------|
| `ENVIRONMENT` | `environment` | No | `development` |
| `TELEGRAM_BOT_TOKEN` | `telegram_bot_token` | Yes | - |
| `TELEGRAM_MAIN_CHAT_ID` | `telegram_main_chat_id` | Yes | - |
| `TELEGRAM_LEADERSHIP_CHAT_ID` | `telegram_leadership_chat_id` | Yes | - |
| `FIREBASE_PROJECT_ID` | `firebase_project_id` | Yes | - |
| `FIREBASE_CREDENTIALS_PATH` | `firebase_credentials_path` | No | - |
| `FIREBASE_CREDENTIALS_JSON` | `firebase_credentials_json` | No | - |
| `GOOGLE_API_KEY` | `google_api_key` | Yes* | - |
| `AI_PROVIDER` | `ai_provider` | No | `google_gemini` |
| `AI_MODEL_NAME` | `ai_model_name` | No | `gemini-1.5-flash` |
| `DEFAULT_TEAM_ID` | `default_team_id` | No | `KAI` |
| `COLLECTIV_API_KEY` | `collectiv_api_key` | No | - |
| `LOG_LEVEL` | `log_level` | No | `INFO` |
| `DEBUG` | `debug` | No | `False` |

*Required only for Google Gemini provider

### Configuration Sections

#### Database Configuration
```python
# Firebase settings
settings.firebase_project_id          # Firebase project ID
settings.firebase_credentials_path    # Path to credentials file
settings.firebase_credentials_json    # Credentials as JSON string
settings.firebase_batch_size          # Batch size for operations
settings.firebase_timeout             # Timeout in seconds
```

#### AI Configuration
```python
# AI provider settings
settings.ai_provider                  # AIProvider enum
settings.google_api_key              # Google API key
settings.ai_model_name               # Model name
settings.ai_temperature              # Temperature (0.0-1.0)
settings.ai_max_tokens               # Max tokens
settings.ai_timeout                  # Timeout in seconds
settings.ai_max_retries              # Max retries

# Get API key for current provider
api_key = settings.get_ai_api_key()
```

#### Telegram Configuration
```python
# Telegram bot settings
settings.telegram_bot_token          # Bot token
settings.telegram_bot_username       # Bot username
settings.telegram_main_chat_id       # Main chat ID
settings.telegram_leadership_chat_id # Leadership chat ID
settings.telegram_webhook_url        # Webhook URL
settings.telegram_parse_mode         # Parse mode
settings.telegram_timeout            # Timeout in seconds
```

#### Team Configuration
```python
# Team settings
settings.default_team_id             # Default team ID
```

#### Payment Configuration
```python
# Payment settings
settings.collectiv_api_key           # Collectiv API key
settings.collectiv_base_url          # Collectiv base URL
settings.payment_enabled             # Enable payment system
```

#### Logging Configuration
```python
# Logging settings
settings.log_level                   # Log level
settings.log_format                  # Log format
settings.log_file_path               # Log file path
settings.log_max_file_size           # Max file size
settings.log_backup_count            # Number of backups
```

#### Performance Configuration
```python
# Performance settings
settings.cache_ttl_seconds           # Cache TTL
settings.max_concurrent_requests     # Max concurrent requests
settings.request_timeout             # Request timeout
settings.retry_attempts              # Retry attempts
settings.retry_delay                 # Retry delay
```

#### Security Configuration
```python
# Security settings
settings.jwt_secret                  # JWT secret
settings.session_timeout             # Session timeout
settings.max_login_attempts          # Max login attempts
settings.password_min_length         # Password min length
```

#### Advanced Memory Configuration
```python
# Memory settings
settings.enable_advanced_memory      # Enable advanced memory
settings.memory_max_short_term       # Max short-term items
settings.memory_max_long_term        # Max long-term items
settings.memory_max_episodic         # Max episodic items
settings.memory_max_semantic         # Max semantic items
settings.memory_pattern_learning     # Enable pattern learning
settings.memory_preference_learning  # Enable preference learning
settings.memory_cleanup_interval     # Cleanup interval
```

## Environment-Specific Configuration

### Development
```bash
# .env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
AI_PROVIDER=ollama
```

### Production
```bash
# .env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
AI_PROVIDER=google_gemini
GOOGLE_API_KEY=your_api_key_here
```

### Testing
```bash
# .env.test
ENVIRONMENT=testing
TEST_MODE=true
AI_PROVIDER=ollama
ADMIN_SESSION_STRING=your_session_string
```

## Migration from Old System

### Step 1: Update Imports

**Old:**
```python
from core.improved_config_system import get_improved_config
from core.bot_config_manager import get_bot_config_manager
```

**New:**
```python
from core.settings import get_settings
```

### Step 2: Update Function Calls

**Old:**
```python
config = get_improved_config()
bot_token = config.telegram.bot_token
team_id = config.teams.default_team_id
api_key = config.ai.api_key
```

**New:**
```python
settings = get_settings()
bot_token = settings.telegram_bot_token
team_id = settings.default_team_id
api_key = settings.get_ai_api_key()
```

### Step 3: Update Environment Checks

**Old:**
```python
if config.is_development():
    # development code
```

**New:**
```python
if settings.is_development:
    # development code
```

### Step 4: Update Validation

**Old:**
```python
# Complex validation logic
```

**New:**
```python
errors = settings.validate_required_fields()
if errors:
    for error in errors:
        print(f"Error: {error}")
```

## Backward Compatibility

During migration, the old configuration system is still available through the adapter:

```python
# Still works during migration
from core.config_adapter import get_improved_config
config = get_improved_config()  # Shows deprecation warning
```

**Note**: The adapter shows deprecation warnings to encourage migration to the new system.

## Advanced Features

### Custom Environment Files

```python
from core.settings import initialize_settings

# Load from custom env file
settings = initialize_settings(".env.production")
```

### Reload Configuration

```python
from core.settings import reload_settings

# Reload from environment
settings = reload_settings()
```

### Validation

```python
# Validate all required fields
errors = settings.validate_required_fields()

# Check specific conditions
if not settings.telegram_bot_token:
    print("Bot token is required")

if settings.is_production and settings.jwt_secret == "default-secret":
    print("Change JWT secret in production")
```

## Benefits

### 1. **Simplicity**
- Single file instead of 1200+ lines
- Clear, readable configuration structure
- No complex design patterns

### 2. **Type Safety**
- All values validated at runtime
- IDE autocomplete support
- Clear error messages

### 3. **Maintainability**
- Self-documenting with field descriptions
- Easy to add new configuration options
- No complex inheritance hierarchies

### 4. **Performance**
- Fast loading and validation
- No complex object creation
- Minimal memory footprint

### 5. **Standards Compliance**
- Uses industry-standard Pydantic
- Follows Python best practices
- Compatible with modern tooling

## Troubleshooting

### Common Issues

1. **"Field required" errors**
   - Check that all required environment variables are set
   - Use `settings.validate_required_fields()` to see all errors

2. **Environment not detected correctly**
   - Set `ENVIRONMENT` explicitly
   - Check for `RAILWAY_ENVIRONMENT` or `PYTEST_CURRENT_TEST`

3. **AI provider validation errors**
   - Ensure `AI_PROVIDER` is set to a valid value
   - Check that required API keys are provided

4. **Deprecation warnings**
   - These indicate you're using the old system
   - Migrate to `get_settings()` from `core.settings`

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check configuration values
settings = get_settings()
print(f"Environment: {settings.environment}")
print(f"AI Provider: {settings.ai_provider}")
print(f"Bot Token: {'Set' if settings.telegram_bot_token else 'Missing'}")
```

## Future Enhancements

The new configuration system is designed to be easily extensible:

1. **Additional Providers**: Easy to add new AI providers
2. **Configuration Sources**: Can add database, file, or API sources
3. **Dynamic Updates**: Support for runtime configuration changes
4. **Secrets Management**: Integration with external secrets managers

## Conclusion

The new configuration system provides a clean, maintainable solution that replaces the complex old system while maintaining full functionality and adding type safety and validation. The migration is straightforward and the system is designed for future growth. 