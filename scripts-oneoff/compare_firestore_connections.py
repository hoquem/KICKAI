#!/usr/bin/env python3
"""
Compare Firestore Connections Script

This script clearly shows which Firestore project both the bot and test scripts
are connecting to, and compares their configurations.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.settings import initialize_settings, get_settings
from database.firebase_client import initialize_firebase_client, get_firebase_client
from loguru import logger

async def compare_firestore_connections():
    """Compare Firestore connections between bot and test scripts."""
    
    logger.info("🔍 Comparing Firestore connections...")
    
    # Test 1: Bot's exact initialization process
    logger.info("\n🤖 Test 1: Bot's exact initialization process")
    logger.info("=" * 60)
    
    try:
        # Initialize settings exactly like the bot
        initialize_settings()
        config = get_settings()
        logger.info(f"✅ Settings initialized")
        logger.info(f"   Firebase Project ID: {config.firebase_project_id}")
        logger.info(f"   Firebase Credentials Path: {config.firebase_credentials_path}")
        logger.info(f"   Environment: {config.environment}")
        
        # Initialize Firebase client exactly like the bot
        initialize_firebase_client(config)
        client = get_firebase_client()
        logger.info(f"✅ Firebase client initialized")
        logger.info(f"   Project ID: {client.config.firebase_project_id}")
        
        # Test queries
        collections = await client.list_collections()
        logger.info(f"   Available collections: {collections}")
        
        # Test kickai_teams collection
        from core.constants import get_collection_name, COLLECTION_TEAMS
        teams_collection = get_collection_name(COLLECTION_TEAMS)
        results = await client.query_documents(teams_collection, [])
        logger.info(f"   {teams_collection}: {len(results)} documents")
        
        # Test kickai_KTI_team_members collection
        from core.constants import get_team_members_collection
        team_members_collection = get_team_members_collection("KTI")
        results = await client.query_documents(team_members_collection, [])
        logger.info(f"   {team_members_collection}: {len(results)} documents")
        
    except Exception as e:
        logger.error(f"❌ Error in bot initialization: {e}")
    
    # Test 2: Manual environment variable approach (like our test scripts)
    logger.info("\n📝 Test 2: Manual environment variable approach")
    logger.info("=" * 60)
    
    try:
        # Load environment variables manually
        from dotenv import load_dotenv
        load_dotenv('../.env')
        
        # Set Firebase credentials path manually
        project_root = Path(__file__).parent.parent
        credentials_path = project_root / "credentials" / "firebase_credentials_testing.json"
        os.environ['FIREBASE_CREDENTIALS_FILE'] = str(credentials_path)
        
        logger.info(f"✅ Environment variables loaded")
        logger.info(f"   FIREBASE_PROJECT_ID: {os.environ.get('FIREBASE_PROJECT_ID')}")
        logger.info(f"   FIREBASE_CREDENTIALS_FILE: {os.environ.get('FIREBASE_CREDENTIALS_FILE')}")
        
        # Initialize Firebase client manually
        client = get_firebase_client()
        logger.info(f"✅ Firebase client initialized")
        logger.info(f"   Project ID: {client.config.firebase_project_id}")
        
        # Test queries
        collections = await client.list_collections()
        logger.info(f"   Available collections: {collections}")
        
        # Test kickai_teams collection
        from core.constants import get_collection_name, COLLECTION_TEAMS
        teams_collection = get_collection_name(COLLECTION_TEAMS)
        results = await client.query_documents(teams_collection, [])
        logger.info(f"   {teams_collection}: {len(results)} documents")
        
        # Test kickai_KTI_team_members collection
        from core.constants import get_team_members_collection
        team_members_collection = get_team_members_collection("KTI")
        results = await client.query_documents(team_members_collection, [])
        logger.info(f"   {team_members_collection}: {len(results)} documents")
        
    except Exception as e:
        logger.error(f"❌ Error in manual initialization: {e}")
    
    # Test 3: Check credentials file content
    logger.info("\n📁 Test 3: Check credentials file content")
    logger.info("=" * 60)
    
    try:
        credentials_path = Path(__file__).parent.parent / "credentials" / "firebase_credentials_testing.json"
        if credentials_path.exists():
            import json
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
            logger.info(f"✅ Credentials file exists: {credentials_path}")
            logger.info(f"   Project ID in credentials: {creds.get('project_id')}")
            logger.info(f"   Client email: {creds.get('client_email')}")
            logger.info(f"   Private key length: {len(creds.get('private_key', ''))}")
        else:
            logger.error(f"❌ Credentials file not found: {credentials_path}")
    except Exception as e:
        logger.error(f"❌ Error reading credentials file: {e}")
    
    # Test 4: Summary comparison
    logger.info("\n📊 Summary Comparison")
    logger.info("=" * 60)
    
    logger.info("🔍 Key Findings:")
    logger.info("   1. Both approaches should connect to the SAME Firebase project")
    logger.info("   2. Both approaches should use the SAME credentials file")
    logger.info("   3. Both approaches should see the SAME data")
    logger.info("   4. Any differences indicate configuration issues")

async def main():
    """Main function."""
    logger.info("🚀 Starting Firestore connection comparison...")
    await compare_firestore_connections()
    logger.info("✅ Firestore connection comparison completed")

if __name__ == "__main__":
    asyncio.run(main()) 