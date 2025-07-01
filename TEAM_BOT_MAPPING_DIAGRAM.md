# Team-to-Bot Mapping Flow Diagram

## Visual Representation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TEAM-TO-BOT MAPPING FLOW                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TESTING       │    │   STAGING       │    │  PRODUCTION     │
│   ENVIRONMENT   │    │   ENVIRONMENT   │    │  ENVIRONMENT    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ config/         │    │ config/         │    │ Firestore       │
│ bot_config.json │    │ bot_config.     │    │ Database        │
│                 │    │ staging.json    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Team ID:        │    │ Team ID:        │    │ Team ID:        │
│ "test-team"     │    │ "staging-team"  │    │ "prod-team-123" │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Main Bot    │ │    │ │ Main Bot    │ │    │ │ Main Bot    │ │
│ │ Token: ...  │ │    │ │ Token: ...  │ │    │ │ Token: ...  │ │
│ │ Chat: ...   │ │    │ │ Chat: ...   │ │    │ │ Chat: ...   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Leadership  │ │    │ │ Leadership  │ │    │ │ Leadership  │ │
│ │ Bot Token:  │ │    │ │ Bot Token:  │ │    │ │ Bot Token:  │ │
│ │ Chat: ...   │ │    │ │ Chat: ...   │ │    │ │ Chat: ...   │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Detailed Flow Examples

### 1. Testing Environment Flow

```
Request: Get bot for team "test-team"
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ BotConfigManager.load_configuration()                          │
│ 1. Detect environment = TESTING                                │
│ 2. Load from: config/bot_config.json                           │
│ 3. Parse JSON configuration                                    │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Configuration Structure:                                        │
│ {                                                              │
│   "teams": {                                                    │
│     "test-team": {                                             │
│       "name": "Test Team",                                     │
│       "bots": {                                                │
│         "main": {                                              │
│           "token": "1234567890:ABC...",                       │
│           "username": "kickai_test_main_bot",                 │
│           "chat_id": "-1001234567890"                         │
│         },                                                     │
│         "leadership": {                                        │
│           "token": "0987654321:ZYX...",                       │
│           "username": "kickai_test_leadership_bot",            │
│           "chat_id": "-1000987654321"                         │
│         }                                                      │
│       }                                                        │
│     }                                                          │
│   }                                                            │
│ }                                                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Result: BotConfig object with token, username, chat_id         │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Production Environment Flow

```
Request: Get bot for team "prod-team-123"
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ BotConfigManager.load_configuration()                          │
│ 1. Detect environment = PRODUCTION                             │
│ 2. Initialize Firebase client                                  │
│ 3. Query Firestore collections                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Firestore Query 1: teams collection                            │
│ WHERE team_id = "prod-team-123" AND is_active = true          │
│ Result: Team document with name, description, settings         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Firestore Query 2: team_bots collection                       │
│ WHERE team_id = "prod-team-123" AND is_active = true          │
│ Result: Bot mapping document with:                             │
│ - bot_token                                                    │
│ - bot_username                                                 │
│ - chat_id (for main bot)                                       │
│ - leadership_chat_id (for leadership bot)                      │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Result: BotConfig objects for both main and leadership bots    │
└─────────────────────────────────────────────────────────────────┘
```

## Code Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Application Code                                               │
│ get_team_bot_credentials("my-team", "main")                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ telegram_tools.py                                              │
│ get_team_bot_credentials_dual()                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ bot_config_manager.py                                          │
│ BotConfigManager.get_bot_config()                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Environment Detection                                          │
│ - Check KICKAI_ENV                                             │
│ - Check Railway environment                                    │
│ - Check other indicators                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Configuration Loading                                          │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│ │ Testing:    │ │ Staging:    │ │ Production: │               │
│ │ Local JSON  │ │ Local JSON  │ │ Firestore   │               │
│ └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Team Lookup                                                    │
│ - Find team by ID                                              │
│ - Extract bot configurations                                   │
│ - Return BotConfig objects                                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Result: (bot_token, chat_id) tuple                             │
└─────────────────────────────────────────────────────────────────┘
```

## Key Mapping Points

### 1. Team ID as Primary Key
- **Testing/Staging**: Team ID is a string key in JSON
- **Production**: Team ID is a Firestore document ID

### 2. Dual Bot Support
- Each team can have both main and leadership bots
- Different chat IDs for different purposes
- Same bot token can be used for both (Telegram limitation)

### 3. Environment Isolation
- Each environment has its own configuration
- No cross-environment data sharing
- Independent bot tokens and chat IDs

### 4. Fallback Mechanisms
- If team not found, return None/error
- If bot not configured, skip that bot type
- Validation ensures required fields are present

## Example Usage in Code

```python
# Get bot configuration manager
manager = get_bot_config_manager()

# Get team configuration
team_config = manager.get_team_config("my-team")
if team_config:
    print(f"Team: {team_config.name}")
    
    # Get main bot
    main_bot = team_config.bots.get(BotType.MAIN)
    if main_bot:
        print(f"Main Bot: @{main_bot.username}")
        print(f"Chat ID: {main_bot.chat_id}")
    
    # Get leadership bot
    leadership_bot = team_config.bots.get(BotType.LEADERSHIP)
    if leadership_bot:
        print(f"Leadership Bot: @{leadership_bot.username}")
        print(f"Chat ID: {leadership_bot.chat_id}")
```

This mapping system provides a clean, consistent interface across all environments while maintaining the flexibility to use different storage mechanisms for different environments. 