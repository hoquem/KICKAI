#!/usr/bin/env python3
"""
Team ID Migration Script

This script migrates team data from UUID team IDs to human-readable team IDs.
Run this script to migrate your existing data to the new format.

Usage:
    python3 scripts/migrate_team_id.py --validate
    python3 scripts/migrate_team_id.py --migrate
"""

import asyncio
import argparse
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.team_id_migration import team_migration, migrate_team_id
from src.core.config import get_config


async def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='Migrate team IDs from UUID to human-readable format')
    parser.add_argument('--validate', action='store_true', help='Validate migration without executing')
    parser.add_argument('--migrate', action='store_true', help='Execute the migration')
    parser.add_argument('--old-id', type=str, help='Old team ID (UUID)')
    parser.add_argument('--new-id', type=str, help='New team ID (human-readable)')
    
    args = parser.parse_args()
    
    if not args.validate and not args.migrate:
        print("❌ Please specify either --validate or --migrate")
        parser.print_help()
        return
    
    # Get configuration
    config = get_config()
    
    # Default migration mapping
    old_team_id = args.old_id or 'KAI'
    new_team_id = args.new_id or "KT"
    
    print(f"🔄 Team ID Migration Tool")
    print(f"📋 Old Team ID: {old_team_id}")
    print(f"📋 New Team ID: {new_team_id}")
    print(f"📋 Environment: {config.environment}")
    print()
    
    if args.validate:
        print("🔍 Validating migration...")
        validation_result = await team_migration.validate_migration(old_team_id, new_team_id)
        
        print(f"✅ Validation Complete")
        print(f"📊 Can Migrate: {validation_result['can_migrate']}")
        print(f"📊 Data Counts:")
        for data_type, count in validation_result['data_counts'].items():
            print(f"   • {data_type}: {count}")
        
        if validation_result['warnings']:
            print(f"⚠️  Warnings:")
            for warning in validation_result['warnings']:
                print(f"   • {warning}")
        
        if validation_result['errors']:
            print(f"❌ Errors:")
            for error in validation_result['errors']:
                print(f"   • {error}")
        
        if not validation_result['can_migrate']:
            print("\n❌ Migration cannot proceed due to errors above.")
            return
        
        print("\n✅ Validation passed! Migration can proceed.")
    
    if args.migrate:
        if not args.validate:
            # Validate first
            print("🔍 Validating migration...")
            validation_result = await team_migration.validate_migration(old_team_id, new_team_id)
            
            if not validation_result['can_migrate']:
                print("❌ Migration cannot proceed due to validation errors.")
                if validation_result['errors']:
                    for error in validation_result['errors']:
                        print(f"   • {error}")
                return
        
        # Confirm migration
        print(f"\n⚠️  WARNING: This will migrate all data from team ID '{old_team_id}' to '{new_team_id}'")
        print("This operation cannot be easily undone.")
        
        confirm = input("\nType 'YES' to confirm migration: ")
        if confirm != 'YES':
            print("❌ Migration cancelled.")
            return
        
        print("\n🔄 Starting migration...")
        success = await migrate_team_id(old_team_id, new_team_id)
        
        if success:
            print("✅ Migration completed successfully!")
            print(f"📋 All data has been migrated from '{old_team_id}' to '{new_team_id}'")
            print("\n💡 Next steps:")
            print("1. Update your bot configuration to use the new team ID")
            print("2. Restart your bot")
            print("3. Test that all functionality works correctly")
        else:
            print("❌ Migration failed. Check the logs for details.")


if __name__ == "__main__":
    asyncio.run(main()) 