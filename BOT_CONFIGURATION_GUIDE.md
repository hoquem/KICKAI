# Bot Configuration Management Guide

This guide explains how to manage bot configurations in KICKAI across different environments (testing, staging, production).

## Overview

KICKAI supports multiple teams, each with dual bots:
- **Main Bot**: For general team communication
- **Leadership Bot**: For leadership group discussions

The system uses different configuration approaches based on the environment:
- **Testing/Staging**: Local JSON configuration files
- **Production**: Firestore database storage

## Configuration Structure

### Local Configuration Files (Testing/Staging)

Configuration files are stored in the `config/` directory:

```
config/
├── bot_config.json              # Testing environment
├── bot_config.staging.json      # Staging environment
├── bot_config.example.json      # Example configuration
└── bot_config.{env}.json        # Environment-specific configs
```

### Configuration Format

```json
{
  "environment": "testing",
  "teams": {
    "team-id": {
      "name": "Team Name",
      "description": "Team description",
      "bots": {
        "main": {
          "token": "BOT_TOKEN_HERE",
          "username": "bot_username",
          "chat_id": "CHAT_ID_HERE",
          "is_active": true
        },
        "leadership": {
          "token": "LEADERSHIP_BOT_TOKEN_HERE",
          "username": "leadership_bot_username",
          "chat_id": "LEADERSHIP_CHAT_ID_HERE",
          "is_active": true
        }
      },
      "settings": {
        "ai_provider": "google_gemini",
        "ai_model": "gemini-pro",
        "max_members": 50,
        "allow_public_join": false
      }
    }
  },
  "default_team": "team-id",
  "firebase_config": {
    "project_id": "your-firebase-project-id"
  },
  "ai_config": {
    "provider": "google_gemini",
    "api_key": "YOUR_AI_API_KEY",
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

## Setup Instructions

### 1. Interactive Setup

Use the interactive setup script to create your configuration:

```bash
python scripts/setup_bot_config.py
```

This script will guide you through:
- Selecting the environment
- Creating teams
- Configuring bots (main + leadership)
- Setting team parameters
- Configuring Firebase and AI settings

### 2. Manual Setup

1. **Create Configuration Directory**:
   ```bash
   mkdir -p config
   ```

2. **Copy Example Configuration**:
   ```bash
   cp config/bot_config.example.json config/bot_config.json
   ```

3. **Edit Configuration**:
   - Replace placeholder values with your actual bot tokens and chat IDs
   - Update team names and descriptions
   - Configure Firebase project ID
   - Set AI API keys

### 3. Bot Token Setup

For each team, you need to create two Telegram bots:

#### Main Bot
1. Message @BotFather on Telegram
2. Create a new bot: `/newbot`
3. Choose a name and username
4. Save the bot token
5. Add the bot to your main team group
6. Get the chat ID (use @userinfobot or similar)

#### Leadership Bot
1. Create another bot with @BotFather
2. Use a different username (e.g., `team_leadership_bot`)
3. Add to your leadership group
4. Get the leadership chat ID

### 4. Chat ID Discovery

To find your chat IDs:

1. **Add @userinfobot to your group**
2. **Send any message in the group**
3. **The bot will reply with chat information including the ID**

Chat IDs for groups typically start with `-100` followed by numbers.

## Management Commands

### List Teams and Bots

```bash
python scripts/manage_bot_config.py list
```

### Show Team Details

```bash
python scripts/manage_bot_config.py show team-id
```

### Add New Team

```bash
python scripts/manage_bot_config.py add-team team-id "Team Name" "Description"
```

### Add Bot to Team

```bash
# Add main bot
python scripts/manage_bot_config.py add-bot team-id main "BOT_TOKEN" "username" "CHAT_ID"

# Add leadership bot
python scripts/manage_bot_config.py add-bot team-id leadership "BOT_TOKEN" "username" "CHAT_ID"
```

### Remove Bot

```bash
python scripts/manage_bot_config.py remove-bot team-id main
```

### Set Default Team

```bash
python scripts/manage_bot_config.py set-default team-id
```

### Validate Configuration

```bash
python scripts/manage_bot_config.py validate
```

### Export/Import Configuration

```bash
# Export current configuration
python scripts/manage_bot_config.py export config_backup.json

# Import configuration
python scripts/manage_bot_config.py import config_backup.json
```

## Environment-Specific Configuration

### Testing Environment

- **File**: `config/bot_config.json`
- **Purpose**: Local development and testing
- **Bots**: Test bots with limited functionality
- **Database**: Test Firebase project

### Staging Environment

- **File**: `config/bot_config.staging.json`
- **Purpose**: Pre-production testing
- **Bots**: Staging bots with full functionality
- **Database**: Staging Firebase project

### Production Environment

- **Storage**: Firestore database
- **Purpose**: Live production system
- **Bots**: Production bots with full functionality
- **Database**: Production Firebase project

## Production Configuration (Firestore)

In production, bot configurations are stored in Firestore collections:

### Teams Collection
```json
{
  "name": "Team Name",
  "description": "Team description",
  "is_active": true,
  "created_at": "timestamp",
  "settings": {
    "ai_provider": "google_gemini",
    "max_members": 100
  }
}
```

### Team Bots Collection
```json
{
  "team_id": "team-document-id",
  "bot_token": "BOT_TOKEN",
  "bot_username": "bot_username",
  "chat_id": "MAIN_CHAT_ID",
  "leadership_chat_id": "LEADERSHIP_CHAT_ID",
  "is_active": true,
  "created_at": "timestamp"
}
```

## Security Considerations

### Local Configuration Files

1. **Never commit bot tokens to Git**:
   ```bash
   # Add to .gitignore
   echo "config/bot_config.json" >> .gitignore
   echo "config/bot_config.staging.json" >> .gitignore
   ```

2. **Use environment variables for sensitive data**:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export GOOGLE_AI_API_KEY="your_key"
   ```

3. **Restrict file permissions**:
   ```bash
   chmod 600 config/bot_config.json
   ```

### Production Security

1. **Firestore Security Rules**: Ensure only authorized users can access bot configurations
2. **Environment Variables**: Store sensitive data in Railway environment variables
3. **Access Control**: Limit who can modify bot configurations

## Troubleshooting

### Common Issues

1. **"No bot found for team"**
   - Check if team ID exists in configuration
   - Verify bot is marked as active
   - Ensure bot token is valid

2. **"Invalid chat ID"**
   - Chat IDs for groups should start with `-100`
   - Verify bot is added to the group
   - Check bot permissions in the group

3. **"Configuration validation failed"**
   - Run validation: `python scripts/manage_bot_config.py validate`
   - Check for missing required fields
   - Verify JSON syntax

4. **"Firebase client not available"**
   - Check Firebase credentials
   - Verify project ID is correct
   - Ensure Firebase Admin SDK is properly initialized

### Debug Commands

```bash
# Validate configuration
python scripts/manage_bot_config.py validate

# Show detailed team info
python scripts/manage_bot_config.py show team-id

# Test bot configuration
python -c "
from src.core.bot_config_manager import get_bot_config_manager
manager = get_bot_config_manager()
config = manager.load_configuration()
print(f'Teams: {list(config.teams.keys())}')
print(f'Default: {config.default_team}')
"
```

## Migration from Old System

If you're migrating from the old single-bot system:

1. **Backup existing configuration**:
   ```bash
   cp .env .env.backup
   ```

2. **Create new configuration**:
   ```bash
   python scripts/setup_bot_config.py
   ```

3. **Update environment variables**:
   - Remove `TELEGRAM_BOT_TOKEN` from environment
   - Add team-specific variables if needed

4. **Test configuration**:
   ```bash
   python scripts/manage_bot_config.py validate
   ```

## Best Practices

1. **Use descriptive team IDs**: `my-soccer-team` instead of `team1`
2. **Keep bot usernames unique**: `myteam_main_bot` and `myteam_leadership_bot`
3. **Document team settings**: Include descriptions and member limits
4. **Regular backups**: Export configurations regularly
5. **Test in staging**: Always test bot changes in staging first
6. **Monitor bot activity**: Check bot logs for errors and usage patterns

## Support

For issues with bot configuration:

1. Check the troubleshooting section above
2. Run validation commands
3. Review bot permissions in Telegram
4. Check Firebase security rules
5. Consult the main project documentation

## Related Files

- `src/core/bot_config_manager.py` - Core configuration management
- `scripts/manage_bot_config.py` - CLI management tool
- `scripts/setup_bot_config.py` - Interactive setup script
- `src/tools/telegram_tools.py` - Telegram utilities
- `config/bot_config.example.json` - Example configuration 