# Configuration Migration Report

Generated: Fri Jul 11 10:26:42 BST 2025

## ❌ Validation Errors
- FIREBASE_PROJECT_ID is required

## 🔄 Configuration Differences

### environment
- Old: `Environment.DEVELOPMENT`
- New: `Environment.DEVELOPMENT`

### ai_provider
- Old: `AIProvider.GOOGLE_GEMINI`
- New: `AIProvider.OLLAMA`

### ai_model_name
- Old: `gemini-2.0-flash-001`
- New: `gemini-1.5-flash`

### telegram_main_chat_id
- Old: `None`
- New: `-4889304885`

### telegram_leadership_chat_id
- Old: `None`
- New: `-4814449926`

## 🔧 Environment Variable Mapping

| Old Variable | New Variable | Notes |
|--------------|--------------|-------|
| TELEGRAM_BOT_TOKEN | TELEGRAM_BOT_TOKEN | Same |
| TELEGRAM_MAIN_CHAT_ID | TELEGRAM_MAIN_CHAT_ID | Same |
| TELEGRAM_LEADERSHIP_CHAT_ID | TELEGRAM_LEADERSHIP_CHAT_ID | Same |
| FIREBASE_PROJECT_ID | FIREBASE_PROJECT_ID | Same |
| FIREBASE_CREDENTIALS_PATH | FIREBASE_CREDENTIALS_PATH | Same |
| FIREBASE_CREDENTIALS_JSON | FIREBASE_CREDENTIALS_JSON | Same |
| GOOGLE_API_KEY | GOOGLE_API_KEY | Same |
| AI_PROVIDER | AI_PROVIDER | Same |
| AI_MODEL_NAME | AI_MODEL_NAME | Same |
| DEFAULT_TEAM_ID | DEFAULT_TEAM_ID | Same |
| COLLECTIV_API_KEY | COLLECTIV_API_KEY | Same |
| LOG_LEVEL | LOG_LEVEL | Same |
| ENVIRONMENT | ENVIRONMENT | Same |
| DEBUG | DEBUG | Same |

## 🚀 Migration Steps

1. **Update imports**: Replace old config imports with new ones
2. **Update function calls**: Use `get_settings()` instead of old functions
3. **Test thoroughly**: Run tests to ensure everything works
4. **Remove old code**: Delete old configuration files after migration

## 💻 Code Examples

### Old way:
```python
from core.improved_config_system import get_improved_config
config = get_improved_config()
bot_token = config.telegram.bot_token
```

### New way:
```python
from core.settings import get_settings
settings = get_settings()
bot_token = settings.telegram_bot_token
```
