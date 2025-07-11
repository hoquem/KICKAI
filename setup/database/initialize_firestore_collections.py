#!/usr/bin/env python3
"""
Initialize Firestore Collections for KICKAI

This script creates the expected collections with kickai_ prefix
for end-to-end testing.
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

def initialize_collections():
    """Initialize all expected collections."""
    logger.info("🚀 Initializing Firestore collections...")
    
    for collection_name, description in EXPECTED_COLLECTIONS.items():
        try:
            # Create collection by adding an initialization document
            collection_ref = db.collection(collection_name)
            init_doc = collection_ref.document('_initialization')
            init_doc.set({
                'type': 'initialization',
                'description': description,
                'created_at': firestore.SERVER_TIMESTAMP,
                'version': '1.0.0',
                'note': 'This document keeps the collection alive. Safe to ignore in queries.'
            })
            
            logger.info(f"  ✅ Created collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"  ❌ Error creating collection '{collection_name}': {e}")

def verify_collections():
    """Verify that all expected collections exist."""
    logger.info("🔍 Verifying collections...")
    
    collections = list(db.collections())
    collection_names = [col.id for col in collections]
    
    logger.info(f"Found {len(collection_names)} collections:")
    for name in sorted(collection_names):
        logger.info(f"  - {name}")
    
    # Check for missing collections
    missing = []
    for expected_name in EXPECTED_COLLECTIONS.keys():
        if expected_name not in collection_names:
            missing.append(expected_name)
    
    if missing:
        logger.warning(f"⚠️  Missing collections: {missing}")
        return False
    else:
        logger.info("✅ All expected collections are present!")
        return True

def main():
    """Main function to initialize Firestore collections."""
    logger.info("🎯 Starting Firestore collection initialization...")
    
    # Initialize collections
    initialize_collections()
    
    # Verify collections
    success = verify_collections()
    
    if success:
        logger.info("🎉 Firestore collections initialized successfully!")
        logger.info("🎯 Ready for end-to-end testing!")
        logger.info("📝 Note: Each collection has an '_initialization' document to keep it alive.")
    else:
        logger.error("❌ Some collections are missing!")

if __name__ == "__main__":
    main() 