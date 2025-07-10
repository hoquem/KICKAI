# One-Off Scripts Directory

This directory is for temporary, one-off, or migration scripts that are not part of the regular development workflow.

## Purpose

- **Temporary scripts** for data migration, cleanup, or debugging
- **One-off utilities** for specific tasks that don't need to be maintained
- **Migration scripts** that are run once and then archived
- **Debugging tools** for specific issues

## Conventions

### Naming
- Use descriptive names: `migrate_user_data.py`, `cleanup_duplicate_players.py`
- Include date if relevant: `fix_enum_values_2025_07.py`
- Use underscores for multi-word names

### Documentation
Each script should include:
- Clear description of what it does
- Prerequisites and dependencies
- Usage instructions
- Expected outcomes
- Date created and purpose

### Structure
```python
#!/usr/bin/env python3
"""
One-Off Script: [Description]

Purpose: [What this script accomplishes]
Created: [Date]
Author: [Name]
Prerequisites: [What needs to be set up first]
"""

# [Script implementation]

if __name__ == "__main__":
    # [Main execution logic]
```

## Examples

### Migration Script
```python
#!/usr/bin/env python3
"""
One-Off Script: Migrate Player IDs to New Format

Purpose: Convert old player ID format to new standardized format
Created: 2025-07-10
Author: Development Team
Prerequisites: 
- Database access configured
- Backup of current data
- Test environment validation
"""
```

### Cleanup Script
```python
#!/usr/bin/env python3
"""
One-Off Script: Clean Duplicate Player Records

Purpose: Remove duplicate player entries from database
Created: 2025-07-10
Author: Development Team
Prerequisites:
- Database backup
- Validation of duplicate detection logic
"""
```

## When to Use This Directory

✅ **Use this directory for:**
- Data migration scripts
- One-time cleanup operations
- Debugging utilities
- Temporary fixes
- Data analysis scripts

❌ **Don't use this directory for:**
- Regular development tools
- CI/CD scripts
- Production utilities
- Reusable components

## Cleanup

Scripts in this directory should be reviewed periodically and removed when:
- The task is completed
- The script is no longer relevant
- The functionality is integrated into the main codebase
- The script is superseded by better tools

## Safety

- Always backup data before running one-off scripts
- Test scripts in a safe environment first
- Document what the script does and its impact
- Consider the rollback plan if something goes wrong 