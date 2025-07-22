#!/usr/bin/env python3
"""
Cleanup E2E Test Data for KICKAI

This script removes all test data from Firestore collections to provide
a clean slate for end-to-end testing. It preserves the collection structure
but removes all test documents.
"""

import os
import sys
import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load credentials and initialize Firebase app
cred_file = os.getenv('FIREBASE_CREDENTIALS_FILE', './credentials/firebase_credentials_testing.json')
cred = credentials.Certificate(cred_file)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Collections to clean
COLLECTIONS_TO_CLEAN = [
    'kickai_players',
    'kickai_teams', 
    'kickai_team_members',
    'kickai_matches',
    'kickai_payments',
    'kickai_daily_status',
    'kickai_expenses',
    'kickai_reminders',
    'kickai_onboarding'
]

# Test data identifiers to remove
TEST_PLAYER_IDS = ['JS', 'SJ', 'MW', 'ED', 'AB', 'LT', 'DC']
TEST_TEAM_IDS = ['KAI']
TEST_MATCH_IDS = ['MATCH001', 'MATCH002']
TEST_PAYMENT_IDS = ['PAY001', 'PAY002']
TEST_TEAM_MEMBER_IDS = [
    'TM_JS', 'TM_SJ', 'TM_MW', 'TM_ED', 'TM_AB', 'TM_LT', 'TM_DC',
    'TM_LEADER_admin_user', 'TM_LEADER_team_secretary'
]

async def clean_collection(collection_name: str, specific_ids: List[str] = None) -> int:
    """Clean a specific collection, optionally removing specific document IDs."""
    logger.info(f"🧹 Cleaning collection: {collection_name}")
    
    try:
        collection_ref = db.collection(collection_name)
        deleted_count = 0
        
        if specific_ids:
            # Delete specific documents
            for doc_id in specific_ids:
                try:
                    doc_ref = collection_ref.document(doc_id)
                    doc = doc_ref.get()
                    if doc.exists:
                        doc_ref.delete()
                        deleted_count += 1
                        logger.debug(f"    ✅ Deleted document: {doc_id}")
                    else:
                        logger.debug(f"    ⚠️  Document not found: {doc_id}")
                except Exception as e:
                    logger.warning(f"    ⚠️  Error deleting document {doc_id}: {e}")
        else:
            # Delete all documents in collection
            docs = collection_ref.stream()
            batch = db.batch()
            batch_count = 0
            
            for doc in docs:
                # Skip initialization documents
                if doc.id == '_initialization':
                    continue
                    
                batch.delete(doc.reference)
                batch_count += 1
                
                # Commit batch when it gets large
                if batch_count >= 500:
                    batch.commit()
                    deleted_count += batch_count
                    batch_count = 0
                    batch = db.batch()
            
            # Commit remaining documents
            if batch_count > 0:
                batch.commit()
                deleted_count += batch_count
        
        logger.info(f"  ✅ Cleaned {collection_name}: {deleted_count} documents deleted")
        return deleted_count
        
    except Exception as e:
        logger.error(f"  ❌ Error cleaning collection {collection_name}: {e}")
        return 0

async def clean_all_test_data():
    """Clean all test data from Firestore."""
    logger.info("🚀 Starting E2E test data cleanup...")
    
    total_deleted = 0
    
    try:
        # Clean collections with specific test data
        specific_cleanups = [
            ('kickai_players', TEST_PLAYER_IDS),
            ('kickai_teams', TEST_TEAM_IDS),
            ('kickai_team_members', TEST_TEAM_MEMBER_IDS),
            ('kickai_matches', TEST_MATCH_IDS),
            ('kickai_payments', TEST_PAYMENT_IDS)
        ]
        
        for collection_name, specific_ids in specific_cleanups:
            deleted = await clean_collection(collection_name, specific_ids)
            total_deleted += deleted
        
        # Clean other collections completely
        other_collections = [
            'kickai_daily_status',
            'kickai_expenses',
            'kickai_reminders',
            'kickai_onboarding'
        ]
        
        for collection_name in other_collections:
            deleted = await clean_collection(collection_name)
            total_deleted += deleted
        
        logger.info("🎉 E2E test data cleanup completed successfully!")
        logger.info(f"📊 Total documents deleted: {total_deleted}")
        logger.info("🎯 Firestore is now clean and ready for fresh testing!")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        raise

async def verify_cleanup():
    """Verify that cleanup was successful."""
    logger.info("🔍 Verifying cleanup...")
    
    try:
        for collection_name in COLLECTIONS_TO_CLEAN:
            collection_ref = db.collection(collection_name)
            docs = list(collection_ref.stream())
            
            # Count non-initialization documents
            actual_docs = [doc for doc in docs if doc.id != '_initialization']
            
            if actual_docs:
                logger.warning(f"  ⚠️  Collection {collection_name} still has {len(actual_docs)} documents")
                for doc in actual_docs[:5]:  # Show first 5
                    logger.warning(f"    - {doc.id}")
                if len(actual_docs) > 5:
                    logger.warning(f"    - ... and {len(actual_docs) - 5} more")
            else:
                logger.info(f"  ✅ Collection {collection_name} is clean")
        
        logger.info("✅ Cleanup verification completed!")
        
    except Exception as e:
        logger.error(f"❌ Error during verification: {e}")

def list_current_collections():
    """List all current collections in Firestore."""
    logger.info("📋 Current Firestore collections:")
    try:
        collections = list(db.collections())
        collection_names = [col.id for col in collections]
        
        for name in sorted(collection_names):
            # Count documents in each collection
            try:
                docs = list(db.collection(name).stream())
                doc_count = len([doc for doc in docs if doc.id != '_initialization'])
                logger.info(f"  - {name}: {doc_count} documents")
            except Exception as e:
                logger.warning(f"  - {name}: Error counting documents ({e})")
        
        return collection_names
        
    except Exception as e:
        logger.error(f"❌ Error listing collections: {e}")
        return []

def main():
    """Main function to clean test data."""
    logger.info("🎯 Starting E2E test data cleanup...")
    
    # Show current state
    logger.info("📊 Current Firestore state:")
    list_current_collections()
    
    # Run the cleanup
    asyncio.run(clean_all_test_data())
    
    # Verify cleanup
    asyncio.run(verify_cleanup())
    
    # Show final state
    logger.info("📊 Final Firestore state:")
    list_current_collections()
    
    logger.info("✅ Test data cleanup completed!")

if __name__ == "__main__":
    main() 