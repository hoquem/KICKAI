#!/usr/bin/env python3
"""
ID Migration Script

This script migrates existing Firestore data from football-themed IDs to simple ID format:
- Team Member IDs: M + 2-digit number + initials (e.g., M01MH for Mahmudul Hoque)
- Remove "user_" prefixes from user_id fields
- Ensure telegram_id fields are integers
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Set

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kickai.core.dependency_container import ensure_container_initialized
from kickai.database.firebase_client import get_firebase_client
from kickai.utils.id_generator import generate_member_id, generate_team_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IDMigrationService:
    """Service to migrate IDs to simple format."""
    
    def __init__(self):
        self.db = None
        self.processed_teams: Set[str] = set()
        self.processed_members: Set[str] = set()
    
    async def initialize(self):
        """Initialize the migration service."""
        try:
            ensure_container_initialized()
            self.db = get_firebase_client()
            logger.info("✅ Migration service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize migration service: {e}")
            raise
    
    async def migrate_all_data(self) -> Dict[str, int]:
        """Migrate all data to simple ID format."""
        stats = {
            "teams_processed": 0,
            "players_processed": 0,
            "team_members_processed": 0,
            "user_id_fixes": 0,
            "telegram_id_fixes": 0,
            "errors": 0
        }
        
        try:
            # Migrate teams
            teams_stats = await self._migrate_teams()
            stats["teams_processed"] = teams_stats["processed"]
            
            # Migrate players
            players_stats = await self._migrate_players()
            stats["players_processed"] = players_stats["processed"]
            stats["user_id_fixes"] += players_stats["user_id_fixes"]
            stats["telegram_id_fixes"] += players_stats["telegram_id_fixes"]
            
            # Migrate team members
            members_stats = await self._migrate_team_members()
            stats["team_members_processed"] = members_stats["processed"]
            stats["user_id_fixes"] += members_stats["user_id_fixes"]
            stats["telegram_id_fixes"] += members_stats["telegram_id_fixes"]
            
            logger.info(f"✅ Migration completed successfully: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            stats["errors"] += 1
            raise
    
    async def _migrate_teams(self) -> Dict[str, int]:
        """Migrate team IDs to simple format."""
        stats = {"processed": 0}
        
        try:
            # Get all teams
            teams_ref = self.db._client.collection("kickai_teams")
            teams = teams_ref.stream()
            
            for team_doc in teams:
                team_data = team_doc.to_dict()
                team_name = team_data.get("name", "Unknown Team")
                
                # Generate new simple team ID
                new_team_id = generate_team_id(team_name)
                
                # Only update if ID has changed
                if team_doc.id != new_team_id:
                    # Create new document with simple ID
                    new_team_ref = teams_ref.document(new_team_id)
                    await new_team_ref.set(team_data)
                    
                    # Delete old document
                    await team_doc.reference.delete()
                    
                    logger.info(f"✅ Migrated team '{team_name}': {team_doc.id} → {new_team_id}")
                    self.processed_teams.add(new_team_id)
                else:
                    self.processed_teams.add(team_doc.id)
                
                stats["processed"] += 1
                
        except Exception as e:
            logger.error(f"❌ Failed to migrate teams: {e}")
            raise
        
        return stats
    
    async def _migrate_players(self) -> Dict[str, int]:
        """Migrate player IDs to simple format."""
        stats = {"processed": 0, "user_id_fixes": 0, "telegram_id_fixes": 0}
        
        try:
            # Get all players
            players_ref = self.db._client.collection("kickai_players")
            players = players_ref.stream()
            
            # Track existing member IDs per team to avoid collisions
            team_member_ids: Dict[str, Set[str]] = {}
            
            for player_doc in players:
                player_data = player_doc.to_dict()
                player_name = player_data.get("name") or player_data.get("full_name", "Unknown Player")
                team_id = player_data.get("team_id", "")
                
                # Initialize team member IDs tracking
                if team_id not in team_member_ids:
                    team_member_ids[team_id] = set()
                
                # Generate new simple member ID
                new_member_id = generate_member_id(player_name, team_member_ids[team_id])
                team_member_ids[team_id].add(new_member_id)
                
                # Fix user_id (remove "user_" prefix)
                user_id = player_data.get("user_id", "")
                if user_id.startswith("user_"):
                    player_data["user_id"] = user_id.replace("user_", "", 1)
                    stats["user_id_fixes"] += 1
                
                # Fix telegram_id (ensure integer)
                telegram_id = player_data.get("telegram_id")
                if telegram_id is not None and not isinstance(telegram_id, int):
                    try:
                        player_data["telegram_id"] = int(telegram_id)
                        stats["telegram_id_fixes"] += 1
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Could not convert telegram_id '{telegram_id}' to integer for player {player_name}")
                
                # Update player_id to new format
                player_data["player_id"] = new_member_id
                
                # Update the document
                await player_doc.reference.set(player_data)
                
                logger.info(f"✅ Migrated player '{player_name}': player_id → {new_member_id}")
                stats["processed"] += 1
                
        except Exception as e:
            logger.error(f"❌ Failed to migrate players: {e}")
            raise
        
        return stats
    
    async def _migrate_team_members(self) -> Dict[str, int]:
        """Migrate team member IDs to simple format."""
        stats = {"processed": 0, "user_id_fixes": 0, "telegram_id_fixes": 0}
        
        try:
            # Get all team members
            members_ref = self.db._client.collection("kickai_team_members")
            members = members_ref.stream()
            
            # Track existing member IDs per team to avoid collisions
            team_member_ids: Dict[str, Set[str]] = {}
            
            for member_doc in members:
                member_data = member_doc.to_dict()
                member_name = member_data.get("name") or member_data.get("full_name", "Unknown Member")
                team_id = member_data.get("team_id", "")
                
                # Initialize team member IDs tracking
                if team_id not in team_member_ids:
                    team_member_ids[team_id] = set()
                
                # Generate new simple member ID
                new_member_id = generate_member_id(member_name, team_member_ids[team_id])
                team_member_ids[team_id].add(new_member_id)
                
                # Fix user_id (remove "user_" prefix)
                user_id = member_data.get("user_id", "")
                if user_id.startswith("user_"):
                    member_data["user_id"] = user_id.replace("user_", "", 1)
                    stats["user_id_fixes"] += 1
                
                # Fix telegram_id (ensure integer)
                telegram_id = member_data.get("telegram_id")
                if telegram_id is not None and not isinstance(telegram_id, int):
                    try:
                        member_data["telegram_id"] = int(telegram_id)
                        stats["telegram_id_fixes"] += 1
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️ Could not convert telegram_id '{telegram_id}' to integer for member {member_name}")
                
                # Update member_id to new format
                member_data["member_id"] = new_member_id
                
                # Update the document
                await member_doc.reference.set(member_data)
                
                logger.info(f"✅ Migrated team member '{member_name}': member_id → {new_member_id}")
                stats["processed"] += 1
                
        except Exception as e:
            logger.error(f"❌ Failed to migrate team members: {e}")
            raise
        
        return stats


async def main():
    """Main migration function."""
    logger.info("🚀 Starting ID migration to simple format...")
    
    migration_service = IDMigrationService()
    
    try:
        await migration_service.initialize()
        stats = await migration_service.migrate_all_data()
        
        logger.info("🎉 Migration completed successfully!")
        logger.info(f"📊 Final stats: {stats}")
        
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())