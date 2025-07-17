import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio
from database.firebase_client import get_firebase_client

async def print_teams():
    client = get_firebase_client()
    teams = await client.query_documents('teams')
    print(f"Found {len(teams)} teams in Firestore:")
    for team in teams:
        print("-" * 60)
        print(f"Team ID: {team.get('id')}")
        print(f"Name: {team.get('name')}")
        print(f"Status: {team.get('status')}")
        print(f"Description: {team.get('description')}")
        print(f"Settings: {team.get('settings')}")
        print(f"Full Document: {team}")

if __name__ == "__main__":
    asyncio.run(print_teams()) 