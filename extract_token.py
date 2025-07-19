#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up environment
os.environ['PYTHONPATH'] = 'src'

from database.firebase_client import FirebaseClient
from loguru import logger

async def extract_token():
    """Extract bot token from database"""
    # Initialize Firebase client
    client = FirebaseClient()
    
    # Query teams collection
    teams = await client.query_documents('teams', [])
    
    if teams:
        team = teams[0]  # Get first team
        settings = team.get('settings', {})
        bot_token = settings.get('bot_token')
        
        if bot_token:
            logger.info(f"Full bot token: {bot_token}")
            return bot_token
        else:
            logger.warning("No bot_token found in team settings")
            return None
    else:
        logger.warning("No teams found in database")
        return None

if __name__ == "__main__":
    token = asyncio.run(extract_token()) 