# KICKAI Setup Scripts

## 📁 **Setup Directory Structure**

The KICKAI setup scripts are organized into logical categories for better maintainability and ease of use:

```
setup/
├── README.md                 # This file
├── environment/             # Environment setup scripts
├── credentials/             # Credential and session management
├── database/               # Database initialization and setup
├── migration/              # Data and code migration scripts
└── cleanup/                # Data cleanup and maintenance scripts
```

## 🎯 **Setup Categories**

### **Environment Setup** (`setup/environment/`)
Scripts for setting up the local development environment.

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup_local_environment.py` | Set up local development environment | `python setup/environment/setup_local_environment.py` |

### **Credentials Management** (`setup/credentials/`)
Scripts for managing Telegram credentials and sessions.

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup_telegram_credentials.py` | Set up Telegram bot credentials | `python setup/credentials/setup_telegram_credentials.py` |
| `generate_session.py` | Generate Telegram session | `python setup/credentials/generate_session.py` |
| `generate_session_string.py` | Generate session string for deployment | `python setup/credentials/generate_session_string.py` |

### **Database Setup** (`setup/database/`)
Scripts for initializing and setting up the database.

| Script | Purpose | Usage |
|--------|---------|-------|
| `initialize_firestore_collections.py` | Initialize Firestore collections | `python setup/database/initialize_firestore_collections.py` |
| `setup_e2e_test_data.py` | Set up test data for E2E tests | `python setup/database/setup_e2e_test_data.py` |

### **Migration Scripts** (`setup/migration/`)
Scripts for migrating data and code between versions.

| Script | Purpose | Usage |
|--------|---------|-------|
| `migrate_logging.py` | Migrate logging configuration | `python setup/migration/migrate_logging.py` |
| `migrate_team_id.py` | Migrate team ID format | `python setup/migration/migrate_team_id.py` |
| `migrate_to_modular_handlers.py` | Migrate to modular handler architecture | `python setup/migration/migrate_to_modular_handlers.py` |

### **Cleanup Scripts** (`setup/cleanup/`)
Scripts for cleaning up data and maintaining the system.

| Script | Purpose | Usage |
|--------|---------|-------|
| `clean_firestore_collections.py` | Clean Firestore collections | `python setup/cleanup/clean_firestore_collections.py` |
| `clean_player_firestore.py` | Clean player data from Firestore | `python setup/cleanup/clean_player_firestore.py` |
| `cleanup_database_enums.py` | Clean up database enum values | `python setup/cleanup/cleanup_database_enums.py` |
| `cleanup_e2e_test_data.py` | Clean up E2E test data | `python setup/cleanup/cleanup_e2e_test_data.py` |
| `cleanup_test_data.py` | Clean up general test data | `python setup/cleanup/cleanup_test_data.py` |

## 🚀 **Quick Start Guide**

### **1. Initial Environment Setup**
```bash
# Set up local development environment
python setup/environment/setup_local_environment.py

# Set up Telegram credentials
python setup/credentials/setup_telegram_credentials.py
```

### **2. Database Setup**
```bash
# Initialize Firestore collections
python setup/database/initialize_firestore_collections.py

# Set up test data (for development/testing)
python setup/database/setup_e2e_test_data.py
```

### **3. Generate Session (for deployment)**
```bash
# Generate session string for Railway deployment
python setup/credentials/generate_session_string.py
```

## 📋 **Detailed Usage**

### **Environment Setup**

#### **Local Environment Setup**
```bash
python setup/environment/setup_local_environment.py
```
This script:
- Creates virtual environment
- Installs dependencies
- Sets up environment variables
- Configures development tools

#### **Telegram Credentials Setup**
```bash
python setup/credentials/setup_telegram_credentials.py
```
This script:
- Guides through Telegram bot creation
- Sets up API credentials
- Configures chat IDs
- Creates `.env` file

### **Database Management**

#### **Initialize Firestore Collections**
```bash
python setup/database/initialize_firestore_collections.py
```
This script:
- Creates required Firestore collections
- Sets up indexes
- Initializes default data
- Configures security rules

#### **Setup E2E Test Data**
```bash
python setup/database/setup_e2e_test_data.py
```
This script:
- Creates test players
- Sets up test teams
- Initializes test matches
- Configures test environment

### **Session Management**

#### **Generate Session String**
```bash
python setup/credentials/generate_session_string.py
```
This script:
- Authenticates with Telegram
- Generates session string
- Saves for deployment use
- Configures for Railway

### **Data Migration**

#### **Migrate Logging Configuration**
```bash
python setup/migration/migrate_logging.py
```
This script:
- Updates logging configuration
- Migrates log formats
- Preserves existing logs
- Updates log paths

#### **Migrate Team ID Format**
```bash
python setup/migration/migrate_team_id.py
```
This script:
- Converts team IDs to new format
- Updates database records
- Maintains data integrity
- Preserves relationships

### **Data Cleanup**

#### **Clean Firestore Collections**
```bash
python setup/cleanup/clean_firestore_collections.py
```
This script:
- Removes test data
- Cleans up old records
- Maintains data integrity
- Preserves production data

#### **Clean Player Data**
```bash
python setup/cleanup/clean_player_firestore.py
```
This script:
- Removes player test data
- Cleans up player records
- Maintains team structure
- Preserves admin data

## ⚠️ **Important Notes**

### **Backup Before Migration**
Always backup your data before running migration scripts:
```bash
# Backup Firestore data
python setup/cleanup/backup_firestore.py  # (if available)
```

### **Environment Variables**
Ensure your environment variables are set correctly:
```bash
# Check environment setup
python setup/environment/check_environment.py  # (if available)
```

### **Test Environment**
For testing, use the test environment:
```bash
# Use test environment
export ENV=test
python setup/database/setup_e2e_test_data.py
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=src:$PYTHONPATH
```

#### **Permission Errors**
```bash
# Make scripts executable
chmod +x setup/*/*.py
```

#### **Environment Issues**
```bash
# Activate virtual environment
source venv311/bin/activate
```

### **Debug Mode**
Run scripts with debug output:
```bash
# Enable debug logging
export DEBUG=1
python setup/environment/setup_local_environment.py
```

## 📝 **Script Development**

### **Adding New Setup Scripts**

1. **Choose the appropriate category**:
   - `environment/` - Environment setup
   - `credentials/` - Credential management
   - `database/` - Database operations
   - `migration/` - Data/code migration
   - `cleanup/` - Data cleanup

2. **Follow naming conventions**:
   - Use descriptive names
   - Include category prefix
   - Use snake_case

3. **Add documentation**:
   - Update this README
   - Include usage examples
   - Document parameters

### **Script Template**
```python
#!/usr/bin/env python3
"""
Script description and purpose.
"""

import os
import sys
import logging

def main():
    """Main function."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Script logic here
        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 🔄 **Maintenance**

### **Regular Cleanup**
```bash
# Weekly cleanup
python setup/cleanup/cleanup_test_data.py
python setup/cleanup/cleanup_e2e_test_data.py
```

### **Database Maintenance**
```bash
# Monthly maintenance
python setup/cleanup/clean_firestore_collections.py
python setup/database/initialize_firestore_collections.py
```

### **Environment Updates**
```bash
# Update environment
python setup/environment/setup_local_environment.py
```

---

## 📞 **Support**

For setup-related questions or issues:
1. Check this README first
2. Review script documentation
3. Check environment configuration
4. Contact the development team

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Status**: Active 