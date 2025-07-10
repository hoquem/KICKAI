# KICKAI Development Scripts

This directory contains development and quality assurance scripts for the KICKAI project.

## 🛠️ Available Scripts

### 1. `clean_firestore_collections.py`
**Purpose**: Clean up Firestore collections for testing or maintenance

**What it does**:
- Removes test data from Firestore collections
- Supports selective cleanup of specific collections
- Safe cleanup with confirmation prompts

**Usage**:
```bash
python scripts/clean_firestore_collections.py
```

### 2. `clean_player_firestore.py`
**Purpose**: Clean up player-specific data in Firestore

**What it does**:
- Removes player records from Firestore
- Cleans up related player data
- Supports filtering by player criteria

**Usage**:
```bash
python scripts/clean_player_firestore.py
```

### 3. `cleanup_e2e_test_data.py`
**Purpose**: Clean up end-to-end test data

**What it does**:
- Removes test data created during E2E testing
- Cleans up player registrations, payments, etc.
- Ensures clean test environment

**Usage**:
```bash
python scripts/cleanup_e2e_test_data.py
```

### 4. `deploy-production.sh`
**Purpose**: Deploy to production environment

**What it does**:
- Builds and deploys the application to production
- Runs health checks before deployment
- Handles environment-specific configuration

**Usage**:
```bash
./scripts/deploy-production.sh
```

### 5. `deploy-staging.sh`
**Purpose**: Deploy to staging environment

**What it does**:
- Builds and deploys the application to staging
- Runs health checks before deployment
- Handles environment-specific configuration

**Usage**:
```bash
./scripts/deploy-staging.sh
```

### 6. `deploy-testing.sh`
**Purpose**: Deploy to testing environment

**What it does**:
- Builds and deploys the application to testing
- Runs health checks before deployment
- Handles environment-specific configuration

**Usage**:
```bash
./scripts/deploy-testing.sh
```

### 7. `find_chat_ids.py`
**Purpose**: Find Telegram chat IDs for configuration

**What it does**:
- Connects to Telegram API
- Lists available chats and their IDs
- Helps with bot configuration

**Usage**:
```bash
python scripts/find_chat_ids.py
```

### 8. `initialize_firestore_collections.py`
**Purpose**: Initialize Firestore collections with default data

**What it does**:
- Creates required collections if they don't exist
- Sets up default data structures
- Ensures database is properly initialized

**Usage**:
```bash
python scripts/initialize_firestore_collections.py
```

### 9. `kill_bot_processes.sh`
**Purpose**: Stop running bot processes

**What it does**:
- Finds and terminates running bot processes
- Cleans up process resources
- Useful for development and debugging

**Usage**:
```bash
./scripts/kill_bot_processes.sh
```

### 10. `migrate_logging.py`
**Purpose**: Migrate logging configuration

**What it does**:
- Updates logging configuration across the codebase
- Migrates from old to new logging standards
- Ensures consistent logging setup

**Usage**:
```bash
python scripts/migrate_logging.py
```

### 11. `migrate_team_id.py`
**Purpose**: Migrate team ID format

**What it does**:
- Converts team IDs to new format
- Updates database records
- Ensures consistency across the system

**Usage**:
```bash
python scripts/migrate_team_id.py
```

## 📁 One-Off Scripts

For temporary, one-off, or migration scripts, see the [`scripts-oneoff/`](../scripts-oneoff/) directory.

This directory is for:
- Data migration scripts
- One-time cleanup operations
- Debugging utilities
- Temporary fixes
- Data analysis scripts

## 🔧 Integration with Development Workflow

These scripts are designed to support the development workflow:

- **Deployment scripts**: Handle different environments
- **Database scripts**: Manage Firestore data
- **Utility scripts**: Support development tasks
- **Migration scripts**: Handle data format changes

## 📋 Running Scripts

Most scripts can be run directly:

```bash
# Python scripts
python scripts/script_name.py

# Shell scripts
./scripts/script_name.sh
```

## 🚀 Best Practices

1. **Backup data** before running destructive scripts
2. **Test in development** before running in production
3. **Review script output** carefully
4. **Use appropriate environment** for each script
5. **Document any customizations** made to scripts

## 📚 Related Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architectural principles and rules
- [scripts-oneoff/README.md](../scripts-oneoff/README.md) - One-off scripts documentation
- [README.md](../README.md) - Project overview 