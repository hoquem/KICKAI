import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio
from database.firebase_client import get_firebase_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def print_teams():
    client = get_firebase_client()
    teams = await client.query_documents('teams')
    logger.info(f"Found {len(teams)} teams in Firestore:")
    for team in teams:
        logger.info("-" * 60)
        logger.info(f"Team ID: {team.get('id')}")
        logger.info(f"Name: {team.get('name')}")
        logger.info(f"Status: {team.get('status')}")
        logger.info(f"Description: {team.get('description')}")
        logger.info(f"Settings: {team.get('settings')}")
        logger.info(f"Full Document: {team}")

if __name__ == "__main__":
    asyncio.run(print_teams()) 