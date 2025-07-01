# Team-to-Bot Mapping Across Environments

This document explains how team names map to bots in the KICKAI system across different environments (testing, staging, production).

## Overview

The mapping system uses **Team IDs** as the primary key to link teams to their bots. Each team can have two bots:
- **Main Bot**: For general team communication
- **Leadership Bot**: For leadership group discussions

## Environment-Specific Mapping

### 🔧 Testing Environment

**Configuration Source**: `config/bot_config.json` (local file)

**Mapping Structure**:
```json
{
  "teams": {
    "test-team": {
      "name": "Test Team",
      "bots": {
        "main": {
          "token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
          "username": "kickai_test_main_bot",
          "chat_id": "-1001234567890"
        },
        "leadership": {
          "token": "0987654321:ZYXwvuTSRqpONMlkjIHGfedCBA",
          "username": "kickai_test_leadership_bot",
          "chat_id": "-1000987654321"
        }
      }
    }
  }
}
```

**Mapping Flow**:
```
Team ID: "test-team"
    ↓
Lookup in config/bot_config.json
    ↓
Get team configuration
    ↓
Extract bot tokens and chat IDs
```

### 🚀 Staging Environment

**Configuration Source**: `config/bot_config.staging.json` (local file)

**Mapping Structure**:
```json
{
  "teams": {
    "staging-team": {
      "name": "Staging Team",
      "bots": {
        "main": {
          "token": "5555555555:STAGING_MAIN_BOT_TOKEN",
          "username": "kickai_staging_main_bot",
          "chat_id": "-1005555555555"
        },
        "leadership": {
          "token": "6666666666:STAGING_LEADERSHIP_BOT_TOKEN",
          "username": "kickai_staging_leadership_bot",
          "chat_id": "-1006666666666"
        }
      }
    }
  }
}
```

**Mapping Flow**:
```
Team ID: "staging-team"
    ↓
Lookup in config/bot_config.staging.json
    ↓
Get team configuration
    ↓
Extract bot tokens and chat IDs
```

### 🏭 Production Environment

**Configuration Source**: Firestore Database

**Mapping Structure**:

#### Teams Collection
```json
{
  "team_id": "prod-team-123",
  "name": "Production Team",
  "description": "Live production team",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Team Bots Collection
```json
{
  "team_id": "prod-team-123",
  "bot_token": "9999999999:PROD_BOT_TOKEN",
  "bot_username": "kickai_prod_bot",
  "chat_id": "-1009999999999",
  "leadership_chat_id": "-1008888888888",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Mapping Flow**:
```
Team ID: "prod-team-123"
    ↓
Query Firestore 'teams' collection
    ↓
Get team document by ID
    ↓
Query Firestore 'team_bots' collection
    ↓
Get bot mapping by team_id
    ↓
Extract bot tokens and chat IDs
```

## Code Implementation

### Bot Configuration Manager

The `BotConfigManager` class handles the mapping logic:

```python
class BotConfigManager:
    def get_bot_config(self, team_id: str, bot_type: BotType) -> Optional[BotConfig]:
        """Get configuration for a specific bot."""
        team_config = self.get_team_config(team_id)
        if team_config:
            return team_config.bots.get(bot_type)
        return None
```

### Environment Detection

The system automatically detects the environment and loads the appropriate configuration:

```python
def _detect_environment(self) -> Environment:
    # Check for explicit environment variable
    env = os.getenv("KICKAI_ENV", "").lower()
    
    # Auto-detect production environments
    if env == "production":
        return Environment.PRODUCTION
    
    # Check for Railway environment
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
        return Environment.PRODUCTION
    
    # Check for testing environment
    if env == "testing" or os.getenv("PYTEST_CURRENT_TEST"):
        return Environment.TESTING
    
    # Default to development
    return Environment.DEVELOPMENT
```

## Usage Examples

### Getting Bot Credentials

```python
from src.core.bot_config_manager import get_bot_config_manager, BotType

# Get bot configuration manager
manager = get_bot_config_manager()

# Get main bot for a team
main_bot = manager.get_bot_config("my-team", BotType.MAIN)
if main_bot:
    token = main_bot.token
    chat_id = main_bot.chat_id
    username = main_bot.username

# Get leadership bot for a team
leadership_bot = manager.get_bot_config("my-team", BotType.LEADERSHIP)
if leadership_bot:
    token = leadership_bot.token
    chat_id = leadership_bot.chat_id
    username = leadership_bot.username
```

### Using Telegram Tools

```python
from src.tools.telegram_tools import get_team_bot_credentials_dual

# Get main bot credentials
main_token, main_chat_id = get_team_bot_credentials_dual("my-team", "main")

# Get leadership bot credentials
leadership_token, leadership_chat_id = get_team_bot_credentials_dual("my-team", "leadership")
```

## Key Differences Between Environments

| Aspect | Testing | Staging | Production |
|--------|---------|---------|------------|
| **Config Source** | Local JSON file | Local JSON file | Firestore Database |
| **Team IDs** | Simple strings | Simple strings | Firestore document IDs |
| **Bot Tokens** | Stored in JSON | Stored in JSON | Stored in Firestore |
| **Security** | File-based | File-based | Database + IAM |
| **Scalability** | Limited | Limited | Unlimited |
| **Management** | Manual file editing | Manual file editing | Database operations |

## Team ID Naming Conventions

### Testing/Staging
- Use descriptive, simple names
- Examples: `test-team`, `staging-team`, `my-soccer-team`
- Avoid special characters except hyphens

### Production
- Use Firestore document IDs
- Can be auto-generated UUIDs or custom IDs
- Examples: `0854829d-445c-4138-9fd3-4db562ea46ee`, `prod-team-123`

## Migration Between Environments

### Testing → Staging
1. Copy `config/bot_config.json` to `config/bot_config.staging.json`
2. Update bot tokens and chat IDs for staging
3. Update team names and descriptions

### Staging → Production
1. Create team document in Firestore `teams` collection
2. Create bot mapping in Firestore `team_bots` collection
3. Use the existing `kickai_cli.py` or `manage_team_bots.py` tools

## Troubleshooting

### Common Issues

1. **"Team not found"**
   - Check if team ID exists in configuration
   - Verify environment is correct
   - Check file paths for local configs

2. **"No bot configured"**
   - Ensure team has at least one bot configured
   - Check if bot is marked as active
   - Verify bot token and chat ID are set

3. **"Configuration file not found"**
   - Check if config file exists in `config/` directory
   - Verify environment detection is working
   - Check file permissions

### Debug Commands

```bash
# List all teams and their bots
python scripts/manage_bot_config.py list

# Show detailed team configuration
python scripts/manage_bot_config.py show team-id

# Validate configuration
python scripts/manage_bot_config.py validate

# Test configuration loading
python test_bot_config.py
```

## Best Practices

1. **Consistent Team IDs**: Use the same team ID across environments when possible
2. **Descriptive Names**: Use meaningful team names in the configuration
3. **Bot Username Prefixes**: Use environment-specific prefixes (e.g., `kickai_test_`, `kickai_staging_`)
4. **Regular Validation**: Run validation commands regularly
5. **Backup Configurations**: Export configurations before making changes
6. **Documentation**: Keep team and bot information documented

## Security Considerations

### Testing/Staging
- Never commit bot tokens to Git
- Use environment variables for sensitive data
- Restrict file permissions on config files

### Production
- Use Firestore security rules
- Implement proper access controls
- Monitor bot usage and access logs
- Rotate bot tokens regularly 