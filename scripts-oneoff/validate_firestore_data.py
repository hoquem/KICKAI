#!/usr/bin/env python3
"""
Validate Firestore Data Script

This script comprehensively tests the Firestore data to understand why
the bot can read from kickai_teams but not from kickai_KTI_team_members,
even though the team member document exists in the screenshot.

This script does NOT modify any data - it only reads and validates.
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.firebase_client import get_firebase_client
from core.constants import get_team_members_collection, get_team_players_collection, get_collection_name, COLLECTION_TEAMS
from loguru import logger

# Constants from the codebase
TEAM_ID = "KTI"
TELEGRAM_ID = "8148917292"  # doods2000
USER_ID = "TMMH"  # From the screenshot

async def validate_firestore_data():
    """Comprehensive validation of Firestore data."""
    
    logger.info("🔍 Starting comprehensive Firestore data validation...")
    
    # Initialize Firebase client
    client = get_firebase_client()
    logger.info(f"✅ Connected to Firebase project: {client.config.firebase_project_id}")
    
    # Test 1: List all collections
    logger.info("\n📋 Test 1: Listing all collections")
    collections = await client.list_collections()
    logger.info(f"Found collections: {collections}")
    
    # Test 2: Validate team members collection
    logger.info("\n👥 Test 2: Validating team members collection")
    team_members_collection = get_team_members_collection(TEAM_ID)
    logger.info(f"Expected collection path: {team_members_collection}")
    
    # Get all team members
    all_team_members = await client.query_documents(team_members_collection, [])
    logger.info(f"Total team members found: {len(all_team_members)}")
    
    if all_team_members:
        for i, member in enumerate(all_team_members):
            logger.info(f"  Member {i+1}:")
            logger.info(f"    ID: {member.get('id', 'No ID')}")
            logger.info(f"    Name: {member.get('name', 'No name')}")
            logger.info(f"    Telegram ID: {member.get('telegram_id', 'No telegram_id')}")
            logger.info(f"    Team ID: {member.get('team_id', 'No team_id')}")
            logger.info(f"    Roles: {member.get('roles', 'No roles')}")
            logger.info(f"    Document keys: {list(member.keys())}")
    else:
        logger.warning("❌ No team members found in collection")
    
    # Test 3: Search for specific team member by telegram_id
    logger.info(f"\n🔍 Test 3: Searching for team member with telegram_id={TELEGRAM_ID}")
    
    # Try string telegram_id
    members_by_telegram_string = await client.query_documents(
        team_members_collection, 
        [{'field': 'telegram_id', 'operator': '==', 'value': TELEGRAM_ID}]
    )
    logger.info(f"Found {len(members_by_telegram_string)} members with telegram_id='{TELEGRAM_ID}' (string)")
    
    # Try integer telegram_id
    members_by_telegram_int = await client.query_documents(
        team_members_collection, 
        [{'field': 'telegram_id', 'operator': '==', 'value': int(TELEGRAM_ID)}]
    )
    logger.info(f"Found {len(members_by_telegram_int)} members with telegram_id={int(TELEGRAM_ID)} (integer)")
    
    # Test 4: Search by team_id
    logger.info(f"\n🏆 Test 4: Searching for team members with team_id={TEAM_ID}")
    members_by_team = await client.query_documents(
        team_members_collection, 
        [{'field': 'team_id', 'operator': '==', 'value': TEAM_ID}]
    )
    logger.info(f"Found {len(members_by_team)} members with team_id='{TEAM_ID}'")
    
    # Test 5: Search by user_id
    logger.info(f"\n👤 Test 5: Searching for team member with user_id={USER_ID}")
    members_by_user_id = await client.query_documents(
        team_members_collection, 
        [{'field': 'user_id', 'operator': '==', 'value': USER_ID}]
    )
    logger.info(f"Found {len(members_by_user_id)} members with user_id='{USER_ID}'")
    
    # Test 6: Validate teams collection (bot can read this)
    logger.info("\n🏟️ Test 6: Validating teams collection (bot can read this)")
    teams_collection = get_collection_name(COLLECTION_TEAMS)
    logger.info(f"Teams collection path: {teams_collection}")
    
    all_teams = await client.query_documents(teams_collection, [])
    logger.info(f"Total teams found: {len(all_teams)}")
    
    if all_teams:
        for i, team in enumerate(all_teams):
            logger.info(f"  Team {i+1}:")
            logger.info(f"    ID: {team.get('id', 'No ID')}")
            logger.info(f"    Name: {team.get('name', 'No name')}")
            logger.info(f"    Team ID: {team.get('team_id', 'No team_id')}")
            logger.info(f"    First User: {team.get('settings', {}).get('first_user', 'No first_user')}")
            logger.info(f"    Document keys: {list(team.keys())}")
    
    # Test 7: Check if collection exists but is empty
    logger.info("\n📁 Test 7: Checking collection existence and structure")
    try:
        # Try to get a single document to see if collection exists
        test_query = await client.query_documents(team_members_collection, [], limit=1)
        logger.info(f"Collection {team_members_collection} exists and is accessible")
        logger.info(f"Collection contains {len(test_query)} documents")
    except Exception as e:
        logger.error(f"❌ Error accessing collection {team_members_collection}: {e}")
    
    # Test 8: Compare with bot's exact query
    logger.info("\n🤖 Test 8: Replicating bot's exact query")
    bot_query_filters = [
        {'field': 'team_id', 'operator': '==', 'value': TEAM_ID},
        {'field': 'telegram_id', 'operator': '==', 'value': TELEGRAM_ID}
    ]
    bot_query_result = await client.query_documents(team_members_collection, bot_query_filters)
    logger.info(f"Bot query result: {len(bot_query_result)} documents found")
    logger.info(f"Bot query filters: {bot_query_filters}")
    
    # Test 9: Check for any documents with similar data
    logger.info("\n🔎 Test 9: Searching for any documents with similar data")
    
    # Search for any document with the telegram_id (any field)
    all_docs = await client.query_documents(team_members_collection, [])
    matching_docs = []
    
    for doc in all_docs:
        # Check if any field contains the telegram_id
        for key, value in doc.items():
            if str(value) == TELEGRAM_ID:
                matching_docs.append((doc, key))
                break
    
    logger.info(f"Found {len(matching_docs)} documents containing telegram_id '{TELEGRAM_ID}' in any field")
    for doc, field in matching_docs:
        logger.info(f"  Document ID: {doc.get('id', 'No ID')}, Field: {field}, Value: {doc.get(field)}")
    
    # Test 10: Check collection permissions and structure
    logger.info("\n🔐 Test 10: Checking collection permissions and structure")
    try:
        # Try to get collection metadata
        logger.info(f"Collection path: {team_members_collection}")
        logger.info(f"Firebase project: {client.config.firebase_project_id}")
        logger.info(f"Firebase credentials file: {os.environ.get('FIREBASE_CREDENTIALS_FILE', 'Not set')}")
    except Exception as e:
        logger.error(f"❌ Error checking collection metadata: {e}")
    
    logger.info("\n✅ Firestore data validation completed")

async def main():
    """Main function."""
    logger.info("🚀 Starting Firestore data validation script...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('../.env')
    
    # Set Firebase credentials path
    import os
    project_root = Path(__file__).parent.parent
    credentials_path = project_root / "credentials" / "firebase_credentials_testing.json"
    os.environ['FIREBASE_CREDENTIALS_FILE'] = str(credentials_path)
    
    await validate_firestore_data()
    logger.info("✅ Validation script completed")

if __name__ == "__main__":
    asyncio.run(main()) 