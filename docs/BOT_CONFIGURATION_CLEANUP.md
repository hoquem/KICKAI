# Bot Configuration Cleanup - Firestore-Only Approach

**Date:** July 24, 2025  
**Status:** ✅ **COMPLETED**  
**Objective:** Remove all bot configuration from `.env` files and ensure the system only uses Firestore for bot configuration

## 🎯 Overview

This cleanup ensures that bot configuration (bot token, main chat ID, leadership chat ID) is **only** stored in the Firestore `kickai_teams` collection and never falls back to environment variables. This provides a single source of truth for bot configuration and prevents configuration drift.

## ✅ Changes Made

### 1. **MultiBotManager Updates** ✅
- **File:** `kickai/features/team_administration/domain/services/multi_bot_manager.py`
- **Changes:**
  - Removed all environment variable fallbacks (`os.getenv('TELEGRAM_BOT_TOKEN')`, etc.)
  - Updated to only read bot configuration from team explicit fields
  - Added validation to skip teams with incomplete bot configuration
  - Updated startup and shutdown message methods to use Firestore-only config

### 2. **Settings Configuration** ✅
- **File:** `kickai/core/settings.py`
- **Changes:**
  - Removed bot configuration fields from Settings class:
    - `telegram_bot_token`
    - `telegram_main_chat_id` 
    - `telegram_leadership_chat_id`
    - `telegram_bot_username`
  - Kept only non-bot Telegram settings (webhook_url, parse_mode, timeout)
  - Updated validation to not check for bot configuration fields

### 3. **Bootstrap Team Script** ✅
- **File:** `scripts/bootstrap_team.py`
- **Changes:**
  - Added `--bot-token` as a required command line argument
  - Removed environment variable dependency for bot token
  - Updated all methods to accept bot_token as parameter
  - Updated team creation to use explicit bot configuration

### 4. **Get Bot Token Script** ✅
- **File:** `scripts/get_bot_token.py`
- **Changes:**
  - Updated to read bot configuration from team explicit fields instead of settings
  - Removed environment variable setting functionality
  - Added informational messages about Firestore-only approach

### 5. **Leadership Admin Script** ✅
- **File:** `scripts/add_leadership_admins.py`
- **Changes:**
  - Added `_load_bot_config()` method to load bot configuration from Firestore
  - Removed environment variable dependency
  - Updated to accept team ID as command line argument
  - Added proper error handling for missing bot configuration

### 6. **Migration Script** ✅
- **File:** `scripts/migrate_bot_configuration.py` (NEW)
- **Purpose:** Dedicated migration script to move bot configuration from settings to explicit fields
- **Features:**
  - Comprehensive migration with statistics tracking
  - Data cleanup (removes bot config from settings)
  - Field renaming (`bot_username` → `bot_id`)
  - Error handling and reporting
- **Results:** Successfully migrated 1 team with complete bot configuration

### 7. **Legacy Code Cleanup** ✅
- **File:** `kickai/features/team_administration/infrastructure/firebase_team_repository.py`
- **Changes:** Removed migration logic from `_doc_to_team()` method
- **File:** `kickai/features/team_administration/domain/entities/team.py`
- **Changes:** Removed `_ensure_bot_config_consistency()` method and simplified `set_bot_config()`
- **File:** `scripts/get_bot_token.py`
- **Changes:** Updated to use explicit fields only (no migration support needed)
- **File:** `scripts/add_leadership_admins_standalone.py`
- **Changes:** Updated to read bot configuration from explicit fields instead of settings
- **File:** `scripts/manage_team_members_standalone.py`
- **Changes:** Updated to read bot configuration from explicit fields instead of settings
- **File:** `kickai/features/payment_management/domain/services/financial_report_service.py`
- **Changes:** Updated to get bot configuration from team entity instead of settings
- **File:** `kickai/agents/behavioral_mixins.py`
- **Changes:** Updated to get bot configuration from team service instead of settings
- **File:** `kickai/features/player_registration/domain/tools/player_tools.py`
- **Changes:** Updated to get bot configuration from team service instead of settings

## 🔧 Bot Configuration Structure

### Team Entity (Firestore)
```python
@dataclass
class Team:
    # ... other fields ...
    
    # Bot configuration - SINGLE SOURCE OF TRUTH
    bot_id: str | None = None
    bot_token: str | None = None
    main_chat_id: str | None = None
    leadership_chat_id: str | None = None
    
    # Settings dict should NOT contain duplicate bot config
    settings: dict[str, Any] = field(default_factory=dict)
```

### Migration Completed
Bot configuration has been successfully migrated from the old format to the new format:

- **Old Format:** `settings.bot_token`, `settings.main_chat_id`, etc.
- **New Format:** `bot_token`, `main_chat_id`, etc.
- **Migration:** Completed using `scripts/migrate_bot_configuration.py`
- **Status:** All teams migrated, legacy code removed

### Bot Configuration Flow
1. **Team Creation:** Bot configuration stored in team explicit fields
2. **Bot Startup:** MultiBotManager reads from team explicit fields only
3. **Validation:** Teams with incomplete bot configuration are skipped
4. **No Fallbacks:** System never falls back to environment variables

## 🚫 Environment Variables Removed

The following environment variables are **no longer used** for bot configuration:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_MAIN_CHAT_ID`
- `TELEGRAM_LEADERSHIP_CHAT_ID`
- `TELEGRAM_BOT_USERNAME`

## ✅ Benefits Achieved

### 1. **Single Source of Truth** ✅
- All bot configuration comes from Firestore teams collection
- No risk of configuration drift between environment and database
- Consistent configuration across all environments

### 2. **Better Security** ✅
- Bot tokens not stored in environment files
- Configuration managed through secure Firestore access
- Reduced risk of accidental token exposure

### 3. **Improved Maintainability** ✅
- Clear separation between environment config and bot config
- Easier to manage multiple teams with different bot configurations
- Centralized configuration management

### 4. **Enhanced Scalability** ✅
- Support for multiple teams with different bot configurations
- No need to manage environment variables per team
- Dynamic bot configuration loading

## 🔄 Migration Impact

### Scripts Updated
- `scripts/bootstrap_team.py` - Now requires `--bot-token` parameter
- `scripts/get_bot_token.py` - Shows configuration but doesn't set env vars
- `scripts/add_leadership_admins.py` - Loads config from Firestore

### Bot Startup
- Bot will only start for teams with complete bot configuration
- Clear logging when teams are skipped due to missing configuration
- No silent fallbacks to environment variables

### Testing
- Test configuration still includes mock bot token for testing purposes
- Tests don't require actual bot configuration
- Mock data can be used for testing scenarios

## 📋 Usage Examples

### Creating a New Team
```bash
python scripts/bootstrap_team.py \
  --team-name "My Team" \
  --bot-token "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz" \
  --main-chat-id "-1001234567890" \
  --leadership-chat-id "-1001234567891" \
  --bot-username "myteam_bot" \
  --admin-phone "+1234567890" \
  --admin-name "John Doe" \
  --admin-email "john@example.com"
```

### Viewing Bot Configuration
```bash
python scripts/get_bot_token.py
# Shows configuration from Firestore without setting environment variables
```

### Adding Leadership Admins
```bash
python scripts/add_leadership_admins.py KTI
# Loads bot configuration from Firestore for team KTI
```

## 🔧 Issue Resolution & Migration

### **Problem Identified**
The Firestore document for team KTI had bot configuration stored in the `settings` object:
- `settings.bot_token: "7958401227:AAGh1oqoAG3hNt8cheEcb8rfdvzYfRWi1Tg"`
- `settings.main_chat_id: "-4829855674"`
- `settings.leadership_chat_id: "-4969733370"`
- `settings.bot_username: "KickAITesting_bot"`

But the updated code was looking for these as explicit fields on the team document.

### **Migration Solution Implemented**
Created a dedicated migration script `scripts/migrate_bot_configuration.py`:
- **Comprehensive Migration:** Moves all bot configuration from settings to explicit fields
- **Data Cleanup:** Removes bot configuration from settings to avoid duplication
- **Field Renaming:** `bot_username` → `bot_id` for consistency
- **Statistics Tracking:** Provides detailed migration summary

### **Migration Results**
```
📊 MIGRATION SUMMARY
============================================================
Total teams processed: 1
Teams with bot config: 1
Teams successfully migrated: 1
Teams already migrated: 0
Teams without bot config: 0
Errors: 0
✅ Migration completed successfully!
```

### **Legacy Code Cleanup**
After successful migration, removed all legacy migration code:
- ✅ Removed migration logic from `FirebaseTeamRepository._doc_to_team()`
- ✅ Removed `_ensure_bot_config_consistency()` from Team entity
- ✅ Simplified `set_bot_config()` method
- ✅ Updated `get_bot_token.py` to use explicit fields only

### **Verification**
- ✅ `scripts/get_bot_token.py` finds bot configuration correctly
- ✅ MultiBotManager can access bot configuration from Firestore
- ✅ Bot startup works with migrated team documents
- ✅ All legacy migration code removed

## 🎉 Result

The system now has a **clean, secure, and scalable** approach to bot configuration management:

- ✅ **No environment variable dependencies** for bot configuration
- ✅ **Single source of truth** in Firestore teams collection
- ✅ **Clear validation** and error handling
- ✅ **Support for multiple teams** with different configurations
- ✅ **Improved security** and maintainability
- ✅ **Migration completed** - all teams moved to new format
- ✅ **Legacy code removed** - clean, maintainable codebase

The bot will only start for teams that have complete bot configuration in their Firestore documents, ensuring reliable operation and preventing configuration-related issues. 