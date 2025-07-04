#!/usr/bin/env python3
"""
Find Alima by phone number and show her details.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.player_service import PlayerService
from src.database.firebase_client import FirebaseClient
from src.core.config import get_config

async def find_alima():
    """Find Alima by phone number."""
    print("🔍 Finding Alima by Phone Number")
    print("=" * 35)
    
    # Setup
    config = get_config()
    firebase_client = FirebaseClient(config.database)
    player_service = PlayerService(firebase_client)
    
    team_id = "test_team_001"
    
    # Try different phone numbers
    phone_numbers = [
        "07871521581",  # Correct phone number
        "07987654321",  # Old phone number
    ]
    
    for phone in phone_numbers:
        print(f"🔍 Searching for phone: {phone}")
        try:
            player = await player_service.get_player_by_phone(phone, team_id)
            if player:
                print(f"✅ Found Alima!")
                print(f"   Name: {player.name}")
                print(f"   Player ID: {player.player_id}")
                print(f"   Phone: {player.phone}")
                print(f"   Position: {player.position.value}")
                print(f"   Telegram ID: {player.telegram_id or 'Not set'}")
                print(f"   Username: {player.telegram_username or 'Not set'}")
                print(f"   Status: {player.onboarding_status}")
                print(f"   Step: {player.onboarding_step}")
                print()
                return player
            else:
                print(f"❌ No player found with phone {phone}")
        except Exception as e:
            print(f"❌ Error searching for {phone}: {e}")
        print()
    
    # Try searching all players
    print("🔍 Searching all players...")
    try:
        players = await player_service.get_team_players(team_id)
        print(f"Found {len(players)} players:")
        for player in players:
            if "alima" in player.name.lower():
                print(f"   {player.name} - {player.phone} - {player.player_id}")
    except Exception as e:
        print(f"❌ Error getting players: {e}")
    
    return None

if __name__ == "__main__":
    asyncio.run(find_alima()) 