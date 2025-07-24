#!/usr/bin/env python3
"""
Bot Configuration Migration Script

This script migrates bot configuration from the old format (stored in settings)
to the new format (explicit fields on team documents).

Old Format:
{
  "settings": {
    "bot_token": "...",
    "main_chat_id": "...",
    "leadership_chat_id": "...",
    "bot_username": "..."
  }
}

New Format:
{
  "bot_token": "...",
  "main_chat_id": "...",
  "leadership_chat_id": "...",
  "bot_id": "..."  // renamed from bot_username
}
"""

import asyncio
import sys
from typing import Dict, Any, List

from loguru import logger

# Add project root to path
sys.path.insert(0, '.')

from kickai.core.dependency_container import initialize_container, get_service
from kickai.core.settings import initialize_settings, get_settings
from kickai.database.firebase_client import FirebaseClient
from kickai.features.team_administration.domain.entities.team import Team, TeamStatus


class BotConfigurationMigrator:
    """Handles migration of bot configuration from settings to explicit fields."""
    
    def __init__(self):
        self.firebase_client = None
        self.migration_stats = {
            'total_teams': 0,
            'teams_with_bot_config': 0,
            'teams_migrated': 0,
            'teams_already_migrated': 0,
            'teams_without_bot_config': 0,
            'errors': []
        }
    
    async def initialize(self):
        """Initialize the migrator with Firebase client."""
        try:
            # Initialize settings and dependency container
            initialize_settings()
            config = get_settings()
            initialize_container()
            
            # Get Firebase client
            self.firebase_client = FirebaseClient(config)
            
            logger.info("✅ BotConfigurationMigrator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize migrator: {e}")
            raise
    
    async def get_all_teams(self) -> List[Dict[str, Any]]:
        """Get all teams from Firestore."""
        try:
            teams = await self.firebase_client.query_documents(
                collection='kickai_teams'
            )
            logger.info(f"📋 Found {len(teams)} teams in Firestore")
            return teams
        except Exception as e:
            logger.error(f"❌ Failed to get teams: {e}")
            raise
    
    def needs_migration(self, team_data: Dict[str, Any]) -> bool:
        """Check if a team needs migration."""
        settings = team_data.get('settings', {})
        
        # Check if bot config exists in settings
        has_bot_config_in_settings = any([
            'bot_token' in settings,
            'main_chat_id' in settings,
            'leadership_chat_id' in settings,
            'bot_username' in settings
        ])
        
        # Check if bot config already exists in explicit fields
        has_bot_config_in_fields = any([
            team_data.get('bot_token'),
            team_data.get('main_chat_id'),
            team_data.get('leadership_chat_id'),
            team_data.get('bot_id')
        ])
        
        return has_bot_config_in_settings and not has_bot_config_in_fields
    
    def extract_bot_config_from_settings(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract bot configuration from settings."""
        settings = team_data.get('settings', {})
        
        bot_config = {
            'bot_token': settings.get('bot_token'),
            'main_chat_id': settings.get('main_chat_id'),
            'leadership_chat_id': settings.get('leadership_chat_id'),
            'bot_id': settings.get('bot_username')  # Rename bot_username to bot_id
        }
        
        return bot_config
    
    def remove_bot_config_from_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Remove bot configuration from settings to avoid duplication."""
        bot_config_keys = ['bot_token', 'main_chat_id', 'leadership_chat_id', 'bot_username']
        
        cleaned_settings = settings.copy()
        for key in bot_config_keys:
            if key in cleaned_settings:
                del cleaned_settings[key]
        
        return cleaned_settings
    
    async def migrate_team(self, team_data: Dict[str, Any]) -> bool:
        """Migrate a single team's bot configuration."""
        team_id = team_data.get('id')
        team_name = team_data.get('name', 'Unknown')
        
        try:
            logger.info(f"🔄 Migrating team: {team_name} ({team_id})")
            
            # Extract bot configuration from settings
            bot_config = self.extract_bot_config_from_settings(team_data)
            
            # Remove bot configuration from settings
            settings = team_data.get('settings', {})
            cleaned_settings = self.remove_bot_config_from_settings(settings)
            
            # Prepare update data
            update_data = {
                'bot_token': bot_config['bot_token'],
                'main_chat_id': bot_config['main_chat_id'],
                'leadership_chat_id': bot_config['leadership_chat_id'],
                'bot_id': bot_config['bot_id'],
                'settings': cleaned_settings
            }
            
            # Update the team document
            await self.firebase_client.update_document(
                collection='kickai_teams',
                document_id=team_id,
                data=update_data
            )
            
            logger.info(f"✅ Successfully migrated team: {team_name}")
            logger.info(f"   Bot Token: {bot_config['bot_token'][:20]}..." if bot_config['bot_token'] else "None")
            logger.info(f"   Main Chat ID: {bot_config['main_chat_id']}")
            logger.info(f"   Leadership Chat ID: {bot_config['leadership_chat_id']}")
            logger.info(f"   Bot Username: {bot_config['bot_id']}")
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to migrate team {team_name} ({team_id}): {e}"
            logger.error(f"❌ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
            return False
    
    async def run_migration(self) -> Dict[str, Any]:
        """Run the complete migration process."""
        logger.info("🚀 Starting bot configuration migration...")
        logger.info("=" * 60)
        
        try:
            # Get all teams
            teams = await self.get_all_teams()
            self.migration_stats['total_teams'] = len(teams)
            
            for team_data in teams:
                team_id = team_data.get('id')
                team_name = team_data.get('name', 'Unknown')
                
                if self.needs_migration(team_data):
                    self.migration_stats['teams_with_bot_config'] += 1
                    
                    # Check if bot config exists in settings
                    settings = team_data.get('settings', {})
                    has_bot_config = any([
                        'bot_token' in settings,
                        'main_chat_id' in settings,
                        'leadership_chat_id' in settings,
                        'bot_username' in settings
                    ])
                    
                    if has_bot_config:
                        success = await self.migrate_team(team_data)
                        if success:
                            self.migration_stats['teams_migrated'] += 1
                    else:
                        logger.info(f"ℹ️ Team {team_name} ({team_id}) has no bot configuration to migrate")
                        self.migration_stats['teams_without_bot_config'] += 1
                else:
                    # Check if already migrated
                    has_explicit_fields = any([
                        team_data.get('bot_token'),
                        team_data.get('main_chat_id'),
                        team_data.get('leadership_chat_id'),
                        team_data.get('bot_id')
                    ])
                    
                    if has_explicit_fields:
                        logger.info(f"✅ Team {team_name} ({team_id}) already migrated")
                        self.migration_stats['teams_already_migrated'] += 1
                    else:
                        logger.info(f"ℹ️ Team {team_name} ({team_id}) has no bot configuration")
                        self.migration_stats['teams_without_bot_config'] += 1
            
            # Print migration summary
            self._print_migration_summary()
            
            return self.migration_stats
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self.migration_stats['errors'].append(f"Migration failed: {e}")
            return self.migration_stats
    
    def _print_migration_summary(self):
        """Print a summary of the migration results."""
        logger.info("=" * 60)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total teams processed: {self.migration_stats['total_teams']}")
        logger.info(f"Teams with bot config: {self.migration_stats['teams_with_bot_config']}")
        logger.info(f"Teams successfully migrated: {self.migration_stats['teams_migrated']}")
        logger.info(f"Teams already migrated: {self.migration_stats['teams_already_migrated']}")
        logger.info(f"Teams without bot config: {self.migration_stats['teams_without_bot_config']}")
        logger.info(f"Errors: {len(self.migration_stats['errors'])}")
        
        if self.migration_stats['errors']:
            logger.warning("⚠️ Migration errors:")
            for error in self.migration_stats['errors']:
                logger.warning(f"   - {error}")
        
        if self.migration_stats['teams_migrated'] > 0:
            logger.info("✅ Migration completed successfully!")
        else:
            logger.info("ℹ️ No teams needed migration")


async def main():
    """Main function to run the migration."""
    logger.info("🤖 Bot Configuration Migration Script")
    logger.info("=" * 60)
    
    try:
        # Create and run migrator
        migrator = BotConfigurationMigrator()
        await migrator.initialize()
        
        # Run migration
        results = await migrator.run_migration()
        
        # Exit with appropriate code
        if results['errors']:
            logger.error("❌ Migration completed with errors")
            sys.exit(1)
        else:
            logger.info("🎉 Migration completed successfully!")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Fatal error during migration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run migration
    asyncio.run(main()) 