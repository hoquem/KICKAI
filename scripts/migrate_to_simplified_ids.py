#!/usr/bin/env python3
"""
Migration Script: Convert to Simplified IDs

This script migrates existing player and team member IDs from the complex format
to the new simplified format (e.g., 01MH, 02MH).

Usage:
    python scripts/migrate_to_simplified_ids.py --dry-run  # Preview changes
    python scripts/migrate_to_simplified_ids.py --execute  # Apply changes
"""

import argparse
import asyncio
import sys
from typing import Dict, List, Tuple, Set
from collections import defaultdict

from loguru import logger

# Add src to path for imports
sys.path.insert(0, "kickai")

from kickai.core.dependency_container import get_container
from kickai.database.firebase_client import FirebaseClient
from kickai.utils.simple_id_generator import SimpleIDGenerator
from kickai.features.player_registration.domain.entities.player import Player
from kickai.features.team_administration.domain.entities.team_member import TeamMember


class SimplifiedIDMigration:
    """Handles migration of existing IDs to simplified format."""
    
    def __init__(self):
        self.container = get_container()
        self.firebase_client = self.container.get(FirebaseClient)
        self.id_generator = SimpleIDGenerator()
        self.migration_log = []
        
    async def get_all_players(self) -> List[Player]:
        """Retrieve all players from Firestore."""
        try:
            players = await self.firebase_client.get_all_documents("kickai_players")
            return [Player(**player) for player in players]
        except Exception as e:
            logger.error(f"Failed to retrieve players: {e}")
            return []
    
    async def get_all_team_members(self) -> List[TeamMember]:
        """Retrieve all team members from Firestore."""
        try:
            members = await self.firebase_client.get_all_documents("kickai_team_members")
            return [TeamMember(**member) for member in members]
        except Exception as e:
            logger.error(f"Failed to retrieve team members: {e}")
            return []
    
    def generate_new_player_id(self, player: Player, existing_ids: Set[str]) -> str:
        """Generate new simplified ID for player."""
        return self.id_generator.generate_player_id(
            name=player.name,
            team_id=player.team_id,
            existing_ids=existing_ids
        )
    
    def generate_new_member_id(self, member: TeamMember, existing_ids: Set[str]) -> str:
        """Generate new simplified ID for team member."""
        return self.id_generator.generate_team_member_id(
            name=member.name,
            team_id=member.team_id,
            existing_ids=existing_ids
        )
    
    async def migrate_players(self, dry_run: bool = True) -> List[Dict]:
        """Migrate player IDs to simplified format."""
        logger.info("Starting player ID migration...")
        
        players = await self.get_all_players()
        if not players:
            logger.warning("No players found to migrate")
            return []
        
        # Group players by team
        players_by_team = defaultdict(list)
        for player in players:
            players_by_team[player.team_id].append(player)
        
        migration_results = []
        
        for team_id, team_players in players_by_team.items():
            logger.info(f"Processing team {team_id} with {len(team_players)} players")
            
            # Track existing IDs for this team
            existing_ids = set()
            
            for player in team_players:
                old_id = player.player_id
                new_id = self.generate_new_player_id(player, existing_ids)
                existing_ids.add(new_id)
                
                migration_result = {
                    "type": "player",
                    "team_id": team_id,
                    "name": player.name,
                    "old_id": old_id,
                    "new_id": new_id,
                    "phone": player.phone
                }
                
                migration_results.append(migration_result)
                
                if not dry_run:
                    # Update the player document
                    try:
                        await self.firebase_client.update_document(
                            collection="kickai_players",
                            document_id=old_id,
                            data={"player_id": new_id}
                        )
                        logger.info(f"✅ Updated player {player.name}: {old_id} → {new_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to update player {player.name}: {e}")
                        migration_result["error"] = str(e)
                else:
                    logger.info(f"📝 Would update player {player.name}: {old_id} → {new_id}")
        
        return migration_results
    
    async def migrate_team_members(self, dry_run: bool = True) -> List[Dict]:
        """Migrate team member IDs to simplified format."""
        logger.info("Starting team member ID migration...")
        
        members = await self.get_all_team_members()
        if not members:
            logger.warning("No team members found to migrate")
            return []
        
        # Group members by team
        members_by_team = defaultdict(list)
        for member in members:
            members_by_team[member.team_id].append(member)
        
        migration_results = []
        
        for team_id, team_members in members_by_team.items():
            logger.info(f"Processing team {team_id} with {len(team_members)} members")
            
            # Track existing IDs for this team
            existing_ids = set()
            
            for member in team_members:
                old_id = member.member_id
                new_id = self.generate_new_member_id(member, existing_ids)
                existing_ids.add(new_id)
                
                migration_result = {
                    "type": "team_member",
                    "team_id": team_id,
                    "name": member.name,
                    "old_id": old_id,
                    "new_id": new_id,
                    "phone": member.phone
                }
                
                migration_results.append(migration_result)
                
                if not dry_run:
                    # Update the team member document
                    try:
                        await self.firebase_client.update_document(
                            collection="kickai_team_members",
                            document_id=old_id,
                            data={"member_id": new_id}
                        )
                        logger.info(f"✅ Updated team member {member.name}: {old_id} → {new_id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to update team member {member.name}: {e}")
                        migration_result["error"] = str(e)
                else:
                    logger.info(f"📝 Would update team member {member.name}: {old_id} → {new_id}")
        
        return migration_results
    
    def generate_migration_report(self, player_results: List[Dict], member_results: List[Dict]) -> str:
        """Generate a comprehensive migration report."""
        report = []
        report.append("# Migration Report: Simplified IDs")
        report.append("")
        
        # Player migration summary
        report.append("## Player Migration")
        report.append(f"- Total players processed: {len(player_results)}")
        successful_players = [r for r in player_results if "error" not in r]
        failed_players = [r for r in player_results if "error" in r]
        report.append(f"- Successful migrations: {len(successful_players)}")
        report.append(f"- Failed migrations: {len(failed_players)}")
        report.append("")
        
        if successful_players:
            report.append("### Successful Player Migrations")
            for result in successful_players:
                report.append(f"- {result['name']} ({result['phone']}): {result['old_id']} → {result['new_id']}")
            report.append("")
        
        if failed_players:
            report.append("### Failed Player Migrations")
            for result in failed_players:
                report.append(f"- {result['name']}: {result['error']}")
            report.append("")
        
        # Team member migration summary
        report.append("## Team Member Migration")
        report.append(f"- Total team members processed: {len(member_results)}")
        successful_members = [r for r in member_results if "error" not in r]
        failed_members = [r for r in member_results if "error" in r]
        report.append(f"- Successful migrations: {len(successful_members)}")
        report.append(f"- Failed migrations: {len(failed_members)}")
        report.append("")
        
        if successful_members:
            report.append("### Successful Team Member Migrations")
            for result in successful_members:
                report.append(f"- {result['name']} ({result['phone']}): {result['old_id']} → {result['new_id']}")
            report.append("")
        
        if failed_members:
            report.append("### Failed Team Member Migrations")
            for result in failed_members:
                report.append(f"- {result['name']}: {result['error']}")
            report.append("")
        
        return "\n".join(report)
    
    async def run_migration(self, dry_run: bool = True) -> None:
        """Run the complete migration process."""
        logger.info(f"Starting migration (dry_run={dry_run})")
        
        try:
            # Migrate players
            player_results = await self.migrate_players(dry_run)
            
            # Migrate team members
            member_results = await self.migrate_team_members(dry_run)
            
            # Generate and save report
            report = self.generate_migration_report(player_results, member_results)
            
            report_filename = f"migration_report_{'dry_run' if dry_run else 'executed'}.md"
            with open(report_filename, "w") as f:
                f.write(report)
            
            logger.info(f"Migration report saved to {report_filename}")
            logger.info(f"Migration completed: {len(player_results)} players, {len(member_results)} team members")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


async def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate to simplified IDs")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying them")
    parser.add_argument("--execute", action="store_true", help="Execute the migration")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        logger.error("Please specify either --dry-run or --execute")
        sys.exit(1)
    
    if args.dry_run and args.execute:
        logger.error("Cannot specify both --dry-run and --execute")
        sys.exit(1)
    
    migration = SimplifiedIDMigration()
    
    try:
        await migration.run_migration(dry_run=args.dry_run)
        logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 