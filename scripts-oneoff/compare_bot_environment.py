#!/usr/bin/env python3
"""
Compare Bot Environment Script

This script compares the bot's exact environment configuration with our validation script
to identify why they're getting different Firestore results.
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

async def compare_environments():
    """Compare bot environment with validation script environment."""
    
    logger.info("🔍 Comparing bot environment with validation script environment...")
    
    # Test 1: Check environment variables
    logger.info("\n📋 Test 1: Environment Variables")
    logger.info(f"FIREBASE_CREDENTIALS_FILE: {os.environ.get('FIREBASE_CREDENTIALS_FILE', 'Not set')}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Test 2: Check if credentials file exists
    logger.info("\n🔐 Test 2: Credentials File")
    credentials_file = os.environ.get('FIREBASE_CREDENTIALS_FILE')
    if credentials_file:
        if os.path.exists(credentials_file):
            logger.info(f"✅ Credentials file exists: {credentials_file}")
            # Check file size
            file_size = os.path.getsize(credentials_file)
            logger.info(f"   File size: {file_size} bytes")
            
            # Check project ID in credentials
            import json
            try:
                with open(credentials_file, 'r') as f:
                    creds = json.load(f)
                    project_id = creds.get('project_id', 'Not found')
                    logger.info(f"   Project ID in credentials: {project_id}")
            except Exception as e:
                logger.error(f"   Error reading credentials: {e}")
        else:
            logger.error(f"❌ Credentials file does not exist: {credentials_file}")
    else:
        logger.error("❌ FIREBASE_CREDENTIALS_FILE not set")
    
    # Test 3: Initialize Firebase client and check project
    logger.info("\n🔥 Test 3: Firebase Client Initialization")
    try:
        client = get_firebase_client()
        logger.info(f"✅ Firebase client initialized successfully")
        logger.info(f"   Project ID: {client.config.firebase_project_id}")
        # Remove database_url check as it's not available
    except Exception as e:
        logger.error(f"❌ Error initializing Firebase client: {e}")
        return
    
    # Test 4: Check collections
    logger.info("\n📁 Test 4: Collections")
    try:
        collections = await client.list_collections()
        logger.info(f"Found collections: {collections}")
    except Exception as e:
        logger.error(f"❌ Error listing collections: {e}")
        return
    
    # Test 5: Check teams collection (bot can read this)
    logger.info("\n🏟️ Test 5: Teams Collection (Bot can read this)")
    teams_collection = get_collection_name(COLLECTION_TEAMS)
    logger.info(f"Teams collection path: {teams_collection}")
    
    try:
        teams = await client.query_documents(teams_collection, [])
        logger.info(f"Teams found: {len(teams)}")
        if teams:
            for i, team in enumerate(teams):
                logger.info(f"  Team {i+1}: {team.get('id', 'No ID')} - {team.get('name', 'No name')}")
        else:
            logger.warning("❌ No teams found (different from bot logs)")
    except Exception as e:
        logger.error(f"❌ Error querying teams: {e}")
    
    # Test 6: Check team members collection
    logger.info("\n👥 Test 6: Team Members Collection")
    team_members_collection = get_team_members_collection("KTI")
    logger.info(f"Team members collection path: {team_members_collection}")
    
    try:
        members = await client.query_documents(team_members_collection, [])
        logger.info(f"Team members found: {len(members)}")
        if members:
            for i, member in enumerate(members):
                logger.info(f"  Member {i+1}: {member.get('id', 'No ID')} - {member.get('name', 'No name')}")
        else:
            logger.warning("❌ No team members found (screenshot shows document exists)")
    except Exception as e:
        logger.error(f"❌ Error querying team members: {e}")
    
    # Test 7: Check if we're using the same credentials as the bot
    logger.info("\n🤖 Test 7: Bot Environment Comparison")
    
    # Check if we're running from the same directory as the bot
    bot_script = Path(__file__).parent.parent / "run_bot_local.py"
    if bot_script.exists():
        logger.info(f"✅ Bot script exists: {bot_script}")
        
        # Read bot script to see how it loads environment
        try:
            with open(bot_script, 'r') as f:
                bot_content = f.read()
                if 'FIREBASE_CREDENTIALS_FILE' in bot_content:
                    logger.info("✅ Bot script references FIREBASE_CREDENTIALS_FILE")
                if 'load_dotenv' in bot_content:
                    logger.info("✅ Bot script uses load_dotenv")
        except Exception as e:
            logger.error(f"❌ Error reading bot script: {e}")
    else:
        logger.error(f"❌ Bot script not found: {bot_script}")
    
    # Test 8: Check .env file
    logger.info("\n📄 Test 8: .env File")
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        logger.info(f"✅ .env file exists: {env_file}")
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
                if 'FIREBASE_CREDENTIALS_FILE' in env_content:
                    logger.info("✅ .env file contains FIREBASE_CREDENTIALS_FILE")
                    # Extract the value
                    for line in env_content.split('\n'):
                        if line.startswith('FIREBASE_CREDENTIALS_FILE='):
                            env_value = line.split('=', 1)[1].strip()
                            logger.info(f"   Value in .env: {env_value}")
                            break
                else:
                    logger.warning("❌ .env file does not contain FIREBASE_CREDENTIALS_FILE")
        except Exception as e:
            logger.error(f"❌ Error reading .env file: {e}")
    else:
        logger.error(f"❌ .env file not found: {env_file}")
    
    logger.info("\n✅ Environment comparison completed")

async def main():
    """Main function."""
    logger.info("🚀 Starting environment comparison script...")
    
    # Load environment variables (same as bot)
    from dotenv import load_dotenv
    load_dotenv('../.env')
    
    # Set Firebase credentials path (same as validation script)
    import os
    project_root = Path(__file__).parent.parent
    credentials_path = project_root / "credentials" / "firebase_credentials_testing.json"
    os.environ['FIREBASE_CREDENTIALS_FILE'] = str(credentials_path)
    
    await compare_environments()
    logger.info("✅ Environment comparison script completed")

if __name__ == "__main__":
    asyncio.run(main()) 