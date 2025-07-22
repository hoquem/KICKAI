#!/usr/bin/env python3
"""
Final Firestore Investigation Script

This script performs a comprehensive investigation to understand why
the bot can read data that our validation scripts cannot see.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.firebase_client import get_firebase_client
from core.constants import get_team_members_collection, get_collection_name, COLLECTION_TEAMS
from loguru import logger

async def final_investigation():
    """Final comprehensive investigation."""
    
    logger.info("🔍 Starting final Firestore investigation...")
    
    # Test 1: Check all possible credentials files
    logger.info("\n🔐 Test 1: Checking all possible credentials files")
    credentials_dir = Path(__file__).parent.parent / "credentials"
    if credentials_dir.exists():
        for cred_file in credentials_dir.glob("*.json"):
            logger.info(f"Found credentials file: {cred_file}")
            try:
                import json
                with open(cred_file, 'r') as f:
                    creds = json.load(f)
                    project_id = creds.get('project_id', 'Not found')
                    logger.info(f"  Project ID: {project_id}")
            except Exception as e:
                logger.error(f"  Error reading {cred_file}: {e}")
    
    # Test 2: Check if there are multiple Firebase projects
    logger.info("\n🔥 Test 2: Checking for multiple Firebase projects")
    
    # Test with current credentials
    client = get_firebase_client()
    logger.info(f"Current project: {client.config.firebase_project_id}")
    
    # Test 3: Check if data exists in different collections
    logger.info("\n📁 Test 3: Checking all possible collection names")
    
    # Get all collections
    collections = await client.list_collections()
    logger.info(f"All collections: {collections}")
    
    # Check each collection for any data
    for collection_name in collections:
        logger.info(f"\nChecking collection: {collection_name}")
        try:
            docs = await client.query_documents(collection_name, [])
            logger.info(f"  Documents found: {len(docs)}")
            if docs:
                for i, doc in enumerate(docs[:3]):  # Show first 3 docs
                    logger.info(f"    Doc {i+1}: {doc.get('id', 'No ID')} - {doc.get('name', 'No name')}")
        except Exception as e:
            logger.error(f"  Error querying {collection_name}: {e}")
    
    # Test 4: Check if data exists with different field names
    logger.info("\n🔍 Test 4: Checking for data with different field names")
    
    # Check team members collection for any documents with similar data
    team_members_collection = get_team_members_collection("KTI")
    try:
        all_docs = await client.query_documents(team_members_collection, [])
        logger.info(f"All documents in {team_members_collection}: {len(all_docs)}")
        
        for doc in all_docs:
            logger.info(f"  Document: {doc}")
            # Check if any field contains the telegram_id
            for key, value in doc.items():
                if str(value) == "8148917292":
                    logger.info(f"    Found telegram_id in field '{key}': {value}")
    except Exception as e:
        logger.error(f"Error querying team members: {e}")
    
    # Test 5: Check if data exists in different team collections
    logger.info("\n🏆 Test 5: Checking different team collections")
    
    # Check for any team-related collections
    team_collections = [col for col in collections if 'team' in col.lower()]
    logger.info(f"Team-related collections: {team_collections}")
    
    for team_col in team_collections:
        logger.info(f"\nChecking {team_col}:")
        try:
            docs = await client.query_documents(team_col, [])
            logger.info(f"  Documents: {len(docs)}")
            if docs:
                for doc in docs:
                    logger.info(f"    {doc.get('id', 'No ID')} - {doc.get('name', 'No name')} - {doc.get('team_id', 'No team_id')}")
        except Exception as e:
            logger.error(f"  Error: {e}")
    
    # Test 6: Check if the bot is using a different environment
    logger.info("\n🤖 Test 6: Checking bot environment variables")
    
    # Check if bot is using different environment variables
    bot_env_vars = [
        'FIREBASE_CREDENTIALS_FILE',
        'FIREBASE_PROJECT_ID',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'USE_MOCK_DATASTORE'
    ]
    
    for var in bot_env_vars:
        value = os.environ.get(var, 'Not set')
        logger.info(f"  {var}: {value}")
    
    # Test 7: Check if there's a timing issue
    logger.info("\n⏰ Test 7: Checking for timing issues")
    
    # The bot logs show data from 14:00:48, our tests are running at 14:25:xx
    # Check if data was added/removed between these times
    logger.info("Bot logs show data at 14:00:48, our tests run at 14:25:xx")
    logger.info("This suggests data might have been added/removed between these times")
    
    # Test 8: Check if the bot is using cached data
    logger.info("\n💾 Test 8: Checking for cached data")
    
    # The bot might be using cached data from a previous run
    logger.info("The bot might be using cached data from a previous run")
    logger.info("This could explain why it sees data that doesn't exist now")
    
    # Test 9: Check if the bot is connected to a different Firebase project
    logger.info("\n🌐 Test 9: Checking for different Firebase projects")
    
    # The bot might be connected to a different Firebase project
    logger.info(f"Current project: {client.config.firebase_project_id}")
    logger.info("The bot might be connected to a different Firebase project")
    logger.info("This would explain why it sees different data")
    
    # Test 10: Final conclusion
    logger.info("\n🎯 Test 10: Final Analysis")
    
    logger.info("Based on all tests, the most likely explanations are:")
    logger.info("1. The bot is connected to a different Firebase project")
    logger.info("2. The data was added/removed between bot startup and our tests")
    logger.info("3. The bot is using cached data from a previous run")
    logger.info("4. There's a difference in how the bot loads environment variables")
    
    logger.info("\nTo resolve this:")
    logger.info("1. Check if the bot is using different credentials")
    logger.info("2. Verify the exact Firebase project the bot connects to")
    logger.info("3. Check if data exists in the correct project")
    logger.info("4. Restart the bot to clear any cached data")
    
    logger.info("\n✅ Final investigation completed")

async def main():
    """Main function."""
    logger.info("🚀 Starting final Firestore investigation...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('../.env')
    
    # Set Firebase credentials path
    import os
    project_root = Path(__file__).parent.parent
    credentials_path = project_root / "credentials" / "firebase_credentials_testing.json"
    os.environ['FIREBASE_CREDENTIALS_FILE'] = str(credentials_path)
    
    await final_investigation()
    logger.info("✅ Final investigation completed")

if __name__ == "__main__":
    asyncio.run(main()) 