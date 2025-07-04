#!/usr/bin/env python3
"""
List all players in the database.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.player_service import PlayerService
from src.database.firebase_client import FirebaseClient
from src.core.config import get_config

async def list_all_players():
    """List all players in the database."""
    print("👥 All Players in Database")
    print("=" * 30)
    
    # Setup
    config = get_config()
    firebase_client = FirebaseClient(config.database)
    player_service = PlayerService(firebase_client)
    
    team_id = "test_team_001"
    
    # Get all players
    players = await player_service.get_team_players(team_id)
    
    if not players:
        print("❌ No players found in database!")
        return
    
    print(f"✅ Found {len(players)} players:")
    print()
    
    for i, player in enumerate(players, 1):
        print(f"{i}. {player.name}")
        print(f"   Player ID: {player.player_id}")
        print(f"   Phone: {player.phone}")
        print(f"   Position: {player.position.value}")
        print(f"   Telegram ID: {player.telegram_id or 'Not set'}")
        print(f"   Status: {player.onboarding_status}")
        print(f"   Step: {player.onboarding_step}")
        print()

if __name__ == "__main__":
    asyncio.run(list_all_players()) 