#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.firebase_client import FirebaseClient
from loguru import logger

async def get_bot_token():
    """Get bot token from database"""
    client = FirebaseClient()
    teams = await client.query_documents('teams', [])
    
    if teams:
        team = teams[0]  # Get first team
        bot_token = team.get('bot_token')
        logger.info(f"Bot token: {bot_token}")
        return bot_token
    else:
        logger.warning("No teams found")
        return None

if __name__ == "__main__":
    token = asyncio.run(get_bot_token())
    if token:
        # Set environment variable for the test script
        os.environ['TELEGRAM_BOT_TOKEN'] = token
        logger.info("Set TELEGRAM_BOT_TOKEN environment variable") 