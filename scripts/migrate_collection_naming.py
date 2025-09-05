#!/usr/bin/env python3
"""
Database Migration Script: Fix Collection Naming

This script migrates data from incorrectly named global collections
to properly team-scoped collections for Firebase consistency.

Collections to migrate:
- kickai_invite_links -> kickai_KTI_invite_links
- kickai_activation_logs -> kickai_KTI_activation_logs (if exists)
- kickai_team_member_activation_logs -> kickai_KTI_team_member_activation_logs

Global collections that should remain:
- kickai_teams (team metadata)
- kickai_test_markers (test/debug data)
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kickai.core.dependency_container import ensure_container_initialized, get_container
from kickai.database.firebase_client import FirebaseClient
from loguru import logger


class CollectionMigrator:
    """Handles migration of Firebase collections to proper naming convention."""
    
    def __init__(self):
        self.firebase_client: FirebaseClient = None
        self.team_id = "KTI"  # Primary team
        
    async def initialize(self):
        """Initialize Firebase connection."""
        try:
            ensure_container_initialized()
            container = get_container()
            self.firebase_client = container.get_database()
            logger.info("✅ Firebase client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            raise
    
    async def check_collections_exist(self):
        """Check which collections exist and need migration."""
        collections_to_check = [
            "kickai_invite_links",
            "kickai_activation_logs", 
            "kickai_team_member_activation_logs"
        ]
        
        existing_collections = []
        
        for collection_name in collections_to_check:
            try:
                # Try to get a single document to check if collection exists
                docs = await self.firebase_client.query_documents(
                    collection=collection_name,
                    limit=1
                )
                if docs:
                    existing_collections.append({
                        'name': collection_name,
                        'count': len(docs),
                        'sample': docs[0] if docs else None
                    })
                    logger.info(f"✅ Found collection: {collection_name} ({len(docs)} sample docs)")
                else:
                    logger.info(f"📭 Collection empty or doesn't exist: {collection_name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not check collection {collection_name}: {e}")
        
        return existing_collections
    
    async def migrate_invite_links(self):
        """Migrate invite links from global to team-specific collection."""
        source_collection = "kickai_invite_links"
        target_collection = f"kickai_{self.team_id}_invite_links"
        
        logger.info(f"🔄 Migrating {source_collection} -> {target_collection}")
        
        try:
            # Get all documents from source collection
            source_docs = await self.firebase_client.query_documents(
                collection=source_collection
            )
            
            if not source_docs:
                logger.info(f"📭 No documents to migrate in {source_collection}")
                return
            
            logger.info(f"📊 Found {len(source_docs)} documents to migrate")
            
            # Migrate each document
            migrated_count = 0
            for doc in source_docs:
                try:
                    # Add migration timestamp
                    doc['migrated_at'] = datetime.now().isoformat()
                    doc['migrated_from'] = source_collection
                    
                    # Create in target collection
                    doc_id = doc.get('invite_id', doc.get('id'))
                    if doc_id:
                        await self.firebase_client.create_document(
                            collection=target_collection,
                            document_id=doc_id,
                            data=doc
                        )
                        migrated_count += 1
                        logger.debug(f"✅ Migrated document {doc_id}")
                    else:
                        logger.warning(f"⚠️ Document missing ID, skipping: {doc}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to migrate document {doc.get('id', 'unknown')}: {e}")
            
            logger.info(f"✅ Successfully migrated {migrated_count}/{len(source_docs)} documents")
            
            if migrated_count == len(source_docs):
                logger.info(f"🗑️ All documents migrated successfully. Source collection {source_collection} can be safely deleted.")
            else:
                logger.warning(f"⚠️ Only {migrated_count}/{len(source_docs)} migrated. Check errors before deleting source.")
                
        except Exception as e:
            logger.error(f"❌ Migration failed for {source_collection}: {e}")
            raise
    
    async def migrate_activation_logs(self, collection_suffix: str):
        """Migrate activation logs to team-specific collection."""
        source_collection = f"kickai_{collection_suffix}"
        target_collection = f"kickai_{self.team_id}_{collection_suffix}"
        
        logger.info(f"🔄 Migrating {source_collection} -> {target_collection}")
        
        try:
            # Get all documents from source collection
            source_docs = await self.firebase_client.query_documents(
                collection=source_collection
            )
            
            if not source_docs:
                logger.info(f"📭 No documents to migrate in {source_collection}")
                return
            
            logger.info(f"📊 Found {len(source_docs)} documents to migrate")
            
            # Migrate each document
            migrated_count = 0
            for doc in source_docs:
                try:
                    # Add migration timestamp
                    doc['migrated_at'] = datetime.now().isoformat()
                    doc['migrated_from'] = source_collection
                    
                    # Create in target collection with auto-generated ID
                    await self.firebase_client.create_document(
                        collection=target_collection,
                        data=doc
                    )
                    migrated_count += 1
                    logger.debug(f"✅ Migrated activation log document")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to migrate activation log: {e}")
            
            logger.info(f"✅ Successfully migrated {migrated_count}/{len(source_docs)} activation logs")
                
        except Exception as e:
            logger.error(f"❌ Migration failed for {source_collection}: {e}")
            raise
    
    async def run_migration(self, dry_run: bool = True):
        """Run the complete migration process."""
        logger.info(f"🚀 Starting Firebase Collection Migration (dry_run={dry_run})")
        logger.info("=" * 60)
        
        await self.initialize()
        
        # Check what collections exist
        existing_collections = await self.check_collections_exist()
        
        if not existing_collections:
            logger.info("✅ No collections found that need migration!")
            return
        
        logger.info(f"\n📋 Collections requiring migration:")
        for col in existing_collections:
            logger.info(f"   📁 {col['name']}: {col['count']} documents")
        
        if dry_run:
            logger.info(f"\n🔍 DRY RUN MODE - No changes will be made")
            logger.info("To execute migration, run with --execute flag")
            return
        
        logger.info(f"\n⚠️ EXECUTING MIGRATION - This will modify the database!")
        
        # Migrate invite links
        if any(col['name'] == 'kickai_invite_links' for col in existing_collections):
            await self.migrate_invite_links()
        
        # Migrate activation logs
        for col in existing_collections:
            if col['name'] in ['kickai_activation_logs', 'kickai_team_member_activation_logs']:
                collection_suffix = col['name'].replace('kickai_', '')
                await self.migrate_activation_logs(collection_suffix)
        
        logger.info(f"\n🎉 Migration completed successfully!")
        logger.info("Please verify the migrated data before deleting source collections.")


async def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate Firebase collections to proper naming')
    parser.add_argument('--execute', action='store_true', help='Execute the migration (default is dry-run)')
    args = parser.parse_args()
    
    migrator = CollectionMigrator()
    
    try:
        await migrator.run_migration(dry_run=not args.execute)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Set environment variable for testing
    os.environ.setdefault('KICKAI_INVITE_SECRET_KEY', 'test-migration-key')
    
    asyncio.run(main())