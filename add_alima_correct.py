#!/usr/bin/env python3
"""
Add Alima with the correct phone number.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.player_service import PlayerService
from src.database.firebase_client import FirebaseClient
from src.core.config import get_config
from src.database.models import PlayerPosition, PlayerRole

async def add_alima_correct():
    """Add Alima with the correct phone number."""
    print("👤 Adding Alima with Correct Phone Number")
    print("=" * 45)
    
    # Setup
    config = get_config()
    firebase_client = FirebaseClient(config.database)
    player_service = PlayerService(firebase_client)
    
    team_id = "test_team_001"
    
    # Alima's correct details
    alima_name = "Alima Begum"
    alima_phone = "07871521581"  # Correct phone number
    alima_position = PlayerPosition.FORWARD
    
    print(f"📝 Adding player:")
    print(f"   Name: {alima_name}")
    print(f"   Phone: {alima_phone}")
    print(f"   Position: {alima_position.value}")
    print(f"   Team: {team_id}")
    print()
    
    try:
        # Create Alima
        alima = await player_service.create_player(
            name=alima_name,
            phone=alima_phone,
            team_id=team_id,
            position=alima_position,
            role=PlayerRole.PLAYER,
            fa_registered=False
        )
        
        print(f"✅ Successfully added Alima!")
        print(f"   Player ID: {alima.player_id}")
        print(f"   Internal ID: {alima.id}")
        print()
        
        # Update with additional details
        updated_alima = await player_service.update_player(
            alima.id,
            fa_eligible=True,
            onboarding_status="PENDING",
            onboarding_step="welcome"
        )
        
        print(f"📊 Updated Alima's status:")
        print(f"   FA Eligible: {updated_alima.fa_eligible}")
        print(f"   Onboarding Status: {updated_alima.onboarding_status}")
        print(f"   Onboarding Step: {updated_alima.onboarding_step}")
        print()
        
        print("🎯 Next Steps:")
        print("1. Admin generates invitation: /invite 07871521581")
        print("2. Alima clicks invitation link and joins group")
        print("3. System automatically starts onboarding")
        print("4. Alima responds to questions naturally")
        print()
        
        print("💡 Alternative manual onboarding:")
        print(f"   Alima can type: /register {alima.player_id}")
        
    except Exception as e:
        print(f"❌ Error adding Alima: {e}")
        print()
        print("💡 If player already exists, try updating the phone number instead.")

if __name__ == "__main__":
    asyncio.run(add_alima_correct()) 