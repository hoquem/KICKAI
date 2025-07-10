#!/usr/bin/env python3
"""
Firestore Collection Cleaner and Standardizer for KICKAI

This script:
1. Lists all current Firestore collections
2. Deletes all documents from collections used for E2E testing
3. Ensures consistent naming with 'kickai_' prefix
4. Provides a clean dataset for end-to-end testing
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load credentials and initialize Firebase app
cred_file = os.getenv('FIREBASE_CREDENTIALS_FILE', './credentials/firebase_credentials_testing.json')
cred = credentials.Certificate(cred_file)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Define the collections that should exist with kickai_ prefix
EXPECTED_COLLECTIONS = {
    'kickai_players': 'Player documents for E2E testing',
    'kickai_teams': 'Team documents for E2E testing', 
    'kickai_team_members': 'Team member documents for E2E testing',
    'kickai_matches': 'Match documents for E2E testing',
    'kickai_bot_mappings': 'Bot mapping documents for E2E testing',
    'kickai_payments': 'Payment documents for E2E testing',
    'kickai_daily_status': 'Daily status documents for E2E testing',
    'kickai_fixtures': 'Fixture documents for FA registration testing'
}

def list_current_collections():
    """List all current collections in Firestore."""
    logger.info("🔍 Listing current Firestore collections...")
    collections = list(db.collections())
    collection_names = [col.id for col in collections]
    
    logger.info(f"Found {len(collection_names)} collections:")
    for name in sorted(collection_names):
        logger.info(f"  - {name}")
    
    return collection_names

def delete_all_documents_in_collection(collection_name: str):
    """Delete all documents in a collection."""
    try:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        
        # Get all document IDs
        doc_ids = [doc.id for doc in docs]
        
        if not doc_ids:
            logger.info(f"  📭 Collection '{collection_name}' is already empty")
            return 0
        
        # Delete documents in batches (Firestore limit is 500 per batch)
        batch_size = 500
        deleted_count = 0
        
        for i in range(0, len(doc_ids), batch_size):
            batch = db.batch()
            batch_doc_ids = doc_ids[i:i + batch_size]
            
            for doc_id in batch_doc_ids:
                doc_ref = collection_ref.document(doc_id)
                batch.delete(doc_ref)
            
            batch.commit()
            deleted_count += len(batch_doc_ids)
            logger.info(f"  🗑️  Deleted batch {i//batch_size + 1}: {len(batch_doc_ids)} documents")
        
        logger.info(f"  ✅ Deleted {deleted_count} documents from '{collection_name}'")
        return deleted_count
        
    except Exception as e:
        logger.error(f"  ❌ Error deleting documents from '{collection_name}': {e}")
        return 0

def clean_e2e_collections():
    """Clean all collections used for E2E testing."""
    logger.info("🧹 Cleaning collections for E2E testing...")
    
    total_deleted = 0
    
    # Clean expected collections
    for collection_name, description in EXPECTED_COLLECTIONS.items():
        logger.info(f"Cleaning {collection_name}: {description}")
        deleted = delete_all_documents_in_collection(collection_name)
        total_deleted += deleted
    
    # Also clean any collections without kickai_ prefix that might exist
    current_collections = list_current_collections()
    legacy_collections = [
        'players', 'teams', 'team_members', 'matches', 
        'bot_mappings', 'payments', 'daily_status', 'fixtures'
    ]
    
    for legacy_name in legacy_collections:
        if legacy_name in current_collections:
            logger.info(f"Cleaning legacy collection '{legacy_name}' (should be 'kickai_{legacy_name}')")
            deleted = delete_all_documents_in_collection(legacy_name)
            total_deleted += deleted
    
    logger.info(f"🎯 Total documents deleted: {total_deleted}")
    return total_deleted

def validate_collection_consistency():
    """Validate that collections follow the expected naming convention."""
    logger.info("🔍 Validating collection naming consistency...")
    
    current_collections = list_current_collections()
    issues = []
    
    # Check for expected collections
    for expected_name in EXPECTED_COLLECTIONS.keys():
        if expected_name not in current_collections:
            issues.append(f"Missing expected collection: {expected_name}")
    
    # Check for legacy collections
    legacy_collections = [
        'players', 'teams', 'team_members', 'matches', 
        'bot_mappings', 'payments', 'daily_status', 'fixtures'
    ]
    
    for legacy_name in legacy_collections:
        if legacy_name in current_collections:
            issues.append(f"Legacy collection found (should be 'kickai_{legacy_name}'): {legacy_name}")
    
    # Check for unexpected collections
    expected_and_legacy = list(EXPECTED_COLLECTIONS.keys()) + legacy_collections
    for collection_name in current_collections:
        if collection_name not in expected_and_legacy and not collection_name.startswith('kickai_'):
            issues.append(f"Unexpected collection: {collection_name}")
    
    if issues:
        logger.warning("⚠️  Collection consistency issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("✅ All collections follow expected naming convention")
    
    return issues

def create_empty_collections_if_missing():
    """Create empty collections if they don't exist."""
    logger.info("📁 Creating empty collections if missing...")
    
    for collection_name in EXPECTED_COLLECTIONS.keys():
        try:
            # Try to get the collection (this will create it if it doesn't exist)
            collection_ref = db.collection(collection_name)
            # Add a temporary document and immediately delete it to ensure collection exists
            temp_doc = collection_ref.document('_temp')
            temp_doc.set({'created': True})
            temp_doc.delete()
            logger.info(f"  ✅ Ensured collection exists: {collection_name}")
        except Exception as e:
            logger.error(f"  ❌ Error ensuring collection '{collection_name}': {e}")

def main():
    """Main function to clean and standardize Firestore collections."""
    logger.info("🚀 Starting Firestore collection cleanup and standardization...")
    
    # Step 1: List current collections
    current_collections = list_current_collections()
    
    # Step 2: Validate consistency
    issues = validate_collection_consistency()
    
    # Step 3: Clean E2E collections
    total_deleted = clean_e2e_collections()
    
    # Step 4: Create missing collections
    create_empty_collections_if_missing()
    
    # Step 5: Final validation
    logger.info("🔍 Final collection validation...")
    final_collections = list_current_collections()
    final_issues = validate_collection_consistency()
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 CLEANUP SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📁 Collections before cleanup: {len(current_collections)}")
    logger.info(f"📁 Collections after cleanup: {len(final_collections)}")
    logger.info(f"🗑️  Total documents deleted: {total_deleted}")
    logger.info(f"⚠️  Consistency issues: {len(final_issues)}")
    
    if final_issues:
        logger.warning("⚠️  Remaining issues to address:")
        for issue in final_issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("✅ All collections are clean and consistent!")
    
    logger.info("🎯 Firestore is ready for end-to-end testing!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 