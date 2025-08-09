#!/usr/bin/env python3
"""
Update Player Telegram IDs for Testing

This script updates the test players in Firestore to include telegram_id fields
so the bot can properly match users to players.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set required environment variable
os.environ["KICKAI_INVITE_SECRET_KEY"] = "test_secret_key_for_debugging_only_32_chars_long"

async def update_player_telegram_ids():
    """Update test players with telegram IDs."""
    print("🔧 UPDATING PLAYER TELEGRAM IDS")
    print("=" * 60)
    
    try:
        from kickai.core.dependency_container import initialize_container, get_container
        from kickai.features.player_registration.domain.services.player_service import PlayerService
        
        # Initialize container
        initialize_container()
        container = get_container()
        
        # Get player service
        player_service = container.get_service("PlayerService")
        
        if not player_service:
            print("❌ Failed to get PlayerService")
            return False
        
        print("✅ PlayerService initialized successfully")
        
        # Map of phone numbers to telegram IDs for test users
        phone_to_telegram_id = {
            "+447123456789": "1001",  # John Smith
            "+447123456790": "1002",  # Sarah Johnson
            "+447123456791": "1003",  # Mike Wilson
            "+447123456792": "1004",  # Emma Davis
            "+447123456793": "1005",  # Alex Brown
        }
        
        # Get all players for TEST1
        players = player_service.get_all_players_sync("TEST1")
        
        if not players:
            print("❌ No players found for TEST1")
            return False
        
        print(f"✅ Found {len(players)} players for TEST1")
        
        updated_count = 0
        
        for player in players:
            phone = player.phone_number
            if phone in phone_to_telegram_id:
                telegram_id = phone_to_telegram_id[phone]
                
                # Update player with telegram_id
                try:
                    # Update the player's telegram_id
                    updated_player = await player_service.update_player(
                        player_id=player.player_id,
                        team_id="TEST1",
                        telegram_id=telegram_id
                    )
                    
                    print(f"✅ Updated player {player.name} ({phone}) with telegram_id: {telegram_id}")
                    updated_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to update player {player.name}: {e}")
            else:
                print(f"⚠️ No telegram_id mapping for phone: {phone}")
        
        print(f"\n🎉 UPDATED {updated_count} PLAYERS WITH TELEGRAM IDS")
        print("=" * 60)
        print("✅ Players now have telegram_id fields")
        print("✅ Bot can now match users to players")
        print("✅ Ready for comprehensive testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update player telegram IDs: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main async function."""
    success = await update_player_telegram_ids()
    if success:
        print("\n🚀 Player telegram ID update successful! Ready for testing.")
    else:
        print("\n❌ Player telegram ID update failed! Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
