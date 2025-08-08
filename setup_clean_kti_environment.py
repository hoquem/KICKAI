#!/usr/bin/env python3
"""
Setup Clean KTI Environment

This script cleans up all existing Firestore collections and initializes
only team KTI with the correct collection structure.
"""

import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from loguru import logger

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def setup_clean_kti_environment():
    """Clean up Firestore and initialize only team KTI."""
    
    # Initialize Firebase
    try:
        # Get credentials from environment
        cred_file = os.getenv('FIREBASE_CREDENTIALS_FILE', './credentials/firebase_credentials_testing.json')
        
        if not os.path.exists(cred_file):
            logger.error(f"❌ Firebase credentials file not found: {cred_file}")
            return False
            
        cred = credentials.Certificate(cred_file)
        
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            logger.info("✅ Firebase app initialized")
        else:
            logger.info("✅ Using existing Firebase app")
            
        db = firestore.client()
        logger.info("✅ Firestore client created")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Firebase: {e}")
        return False
    
    # Define the correct collection structure for team KTI
    kti_collections = {
        'kickai_KTI_players': 'Player documents for team KTI',
        'kickai_KTI_team_members': 'Team member documents for team KTI',
        'kickai_KTI_matches': 'Match documents for team KTI',
        'kickai_KTI_payments': 'Payment documents for team KTI',
        'kickai_KTI_attendance': 'Attendance documents for team KTI',
        'kickai_KTI_daily_status': 'Daily status documents for team KTI',
        'kickai_teams': 'Team configuration documents (global)'
    }
    
    # Collections to clean up (remove all existing collections)
    collections_to_clean = [
        'kickai_KTI_matches',
        'kickai_KTI_players', 
        'kickai_KTI_team_members',
        'kickai_TEST1_players',
        'kickai_TEST2_players',
        'kickai_attendance',
        'kickai_daily_status',
        'kickai_matches',
        'kickai_payments',
        'kickai_players',
        'kickai_team_members',
        'kickai_teams'
    ]
    
    logger.info("🧹 Cleaning up existing collections...")
    
    # Clean up existing collections
    for collection_name in collections_to_clean:
        try:
            collection_ref = db.collection(collection_name)
            docs = collection_ref.stream()
            
            # Delete all documents in the collection
            deleted_count = 0
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"🗑️ Deleted {deleted_count} documents from {collection_name}")
            else:
                logger.info(f"📭 Collection {collection_name} was already empty")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not clean collection {collection_name}: {e}")
    
    logger.info("✅ Cleanup completed")
    
    # Initialize KTI team configuration
    logger.info("🏗️ Initializing team KTI configuration...")
    
    try:
        # Create team KTI document
        team_data = {
            'team_id': 'KTI',
            'team_name': 'KickAI Testing',
            'created_at': firestore.SERVER_TIMESTAMP,
            'status': 'active',
            'settings': {
                'main_chat_id': '2001',
                'leadership_chat_id': '2002',
                'invite_secret_key': os.getenv('KICKAI_INVITE_SECRET_KEY', 'test_secret_key_for_debugging_only_32_chars_long')
            }
        }
        
        db.collection('kickai_teams').document('KTI').set(team_data)
        logger.info("✅ Team KTI configuration created")
        
        # Create sample test data for KTI team
        logger.info("📝 Creating sample test data for team KTI...")
        
        # Sample players
        sample_players = [
            {
                'player_id': 'JS001',
                'name': 'John Smith',
                'phone': '+1234567890',
                'position': 'Forward',
                'team_id': 'KTI',
                'status': 'active',
                'registration_date': firestore.SERVER_TIMESTAMP,
                'telegram_id': '1001',  # Mock Telegram user ID (as string)
                'username': 'john_smith'
            },
            {
                'player_id': 'JD002', 
                'name': 'Jane Doe',
                'phone': '+1234567891',
                'position': 'Midfielder',
                'team_id': 'KTI',
                'status': 'active',
                'registration_date': firestore.SERVER_TIMESTAMP,
                'telegram_id': '1002',  # Mock Telegram user ID (as string)
                'username': 'jane_doe'
            }
        ]
        
        for player in sample_players:
            db.collection('kickai_KTI_players').document(player['player_id']).set(player)
        
        # Sample team members
        sample_members = [
            {
                'member_id': 'COACH001',
                'name': 'Coach Wilson',
                'phone': '+1234567892',
                'role': 'Coach',
                'team_id': 'KTI',
                'status': 'active',
                'registration_date': firestore.SERVER_TIMESTAMP,
                'telegram_id': '1003',  # Mock Telegram user ID (as string)
                'username': 'coach_wilson'
            }
        ]
        
        for member in sample_members:
            db.collection('kickai_KTI_team_members').document(member['member_id']).set(member)
        
        # Sample match
        sample_match = {
            'match_id': 'MATCH001',
            'team_id': 'KTI',
            'date': '2025-08-15',
            'time': '14:00',
            'location': 'Central Park',
            'status': 'scheduled',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        db.collection('kickai_KTI_matches').document('MATCH001').set(sample_match)
        
        logger.info("✅ Sample test data created for team KTI")
        
        # Verify the setup
        logger.info("🔍 Verifying setup...")
        
        # Check collections exist and have data
        verification_results = {}
        
        for collection_name in kti_collections.keys():
            try:
                docs = list(db.collection(collection_name).stream())
                verification_results[collection_name] = len(docs)
                logger.info(f"✅ {collection_name}: {len(docs)} documents")
            except Exception as e:
                verification_results[collection_name] = 0
                logger.warning(f"⚠️ {collection_name}: Error checking - {e}")
        
        # Summary
        logger.info("\n📊 SETUP SUMMARY:")
        logger.info("=" * 50)
        logger.info("Team KTI Environment Initialized Successfully!")
        logger.info("=" * 50)
        
        for collection_name, doc_count in verification_results.items():
            status = "✅" if doc_count > 0 or collection_name == 'kickai_teams' else "⚠️"
            logger.info(f"{status} {collection_name}: {doc_count} documents")
        
        logger.info("\n🎯 Ready for E2E Testing!")
        logger.info("Team ID: KTI")
        logger.info("Main Chat ID: 2001")
        logger.info("Leadership Chat ID: 2002")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize KTI environment: {e}")
        return False

def main():
    """Main function."""
    logger.info("🚀 Setting up clean KTI environment...")
    
    success = setup_clean_kti_environment()
    
    if success:
        logger.info("✅ KTI environment setup completed successfully!")
        return 0
    else:
        logger.error("❌ KTI environment setup failed!")
        return 1

if __name__ == "__main__":
    exit(main())
