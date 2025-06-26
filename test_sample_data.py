#!/usr/bin/env python3
"""
Test script to add sample data to the KICKAI Supabase database
This will create test players, fixtures, and availability records for testing.
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add the src directory to the path so we can import our tools
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from tools.supabase_tools import PlayerTools, FixtureTools, AvailabilityTools

# Load environment variables
load_dotenv()

def test_sample_data():
    """Add sample data to the database for testing"""
    print("🧪 Adding Sample Data to KICKAI Database")
    print("========================================")
    
    # Initialize tools
    player_tool = PlayerTools()
    fixture_tool = FixtureTools()
    availability_tool = AvailabilityTools()
    
    # Sample player data
    sample_players = [
        {"name": "John Smith", "phone_number": "+447123456789"},
        {"name": "Mike Johnson", "phone_number": "+447123456790"},
        {"name": "David Wilson", "phone_number": "+447123456791"},
        {"name": "Chris Brown", "phone_number": "+447123456792"},
        {"name": "Alex Davis", "phone_number": "+447123456793"},
        {"name": "Tom Miller", "phone_number": "+447123456794"},
        {"name": "James Garcia", "phone_number": "+447123456795"},
        {"name": "Rob Martinez", "phone_number": "+447123456796"},
        {"name": "Dan Anderson", "phone_number": "+447123456797"},
        {"name": "Sam Taylor", "phone_number": "+447123456798"},
        {"name": "Luke Thomas", "phone_number": "+447123456799"},
        {"name": "Ben Jackson", "phone_number": "+447123456800"},
        {"name": "Ryan White", "phone_number": "+447123456801"},
        {"name": "Matt Harris", "phone_number": "+447123456802"},
    ]
    
    # Sample fixture data
    sample_fixtures = [
        {
            "opponent": "Red Lions FC",
            "match_date": (datetime.now() + timedelta(days=7)).isoformat() + "Z",
            "location": "Home Ground",
            "is_home_game": True
        },
        {
            "opponent": "Blue Eagles",
            "match_date": (datetime.now() + timedelta(days=14)).isoformat() + "Z",
            "location": "Away Stadium",
            "is_home_game": False
        },
        {
            "opponent": "Green Dragons",
            "match_date": (datetime.now() + timedelta(days=21)).isoformat() + "Z",
            "location": "Home Ground",
            "is_home_game": True
        }
    ]
    
    print("\n1️⃣  Adding Sample Players...")
    player_ids = []
    
    for player_data in sample_players:
        try:
            result = player_tool._run('add_player', **player_data)
            print(f"   ✅ {result}")
            # Extract player ID from the result for later use
            if "ID:" in result:
                player_id = result.split("ID: ")[1].split(")")[0]
                player_ids.append(player_id)
        except Exception as e:
            print(f"   ❌ Error adding player {player_data['name']}: {e}")
    
    print(f"\n   📊 Added {len(player_ids)} players")
    
    print("\n2️⃣  Adding Sample Fixtures...")
    fixture_ids = []
    
    for fixture_data in sample_fixtures:
        try:
            result = fixture_tool._run('add_fixture', **fixture_data)
            print(f"   ✅ {result}")
            # Extract fixture ID from the result for later use
            if "ID:" in result:
                fixture_id = result.split("ID: ")[1].split(")")[0]
                fixture_ids.append(fixture_id)
        except Exception as e:
            print(f"   ❌ Error adding fixture {fixture_data['opponent']}: {e}")
    
    print(f"\n   📊 Added {len(fixture_ids)} fixtures")
    
    print("\n3️⃣  Setting Sample Availability...")
    
    # Set availability for the first fixture
    if fixture_ids and player_ids:
        first_fixture = fixture_ids[0]
        
        # Set different availability statuses
        availability_statuses = ['Available', 'Unavailable', 'Maybe', 'Available', 'Available', 
                               'Maybe', 'Available', 'Unavailable', 'Available', 'Available',
                               'Available', 'Maybe', 'Available', 'Available']
        
        for i, player_id in enumerate(player_ids):
            if i < len(availability_statuses):
                status = availability_statuses[i]
                try:
                    result = availability_tool._run('set_availability', 
                                                   player_id=player_id, 
                                                   fixture_id=first_fixture, 
                                                   status=status)
                    print(f"   ✅ Player {i+1}: {status}")
                except Exception as e:
                    print(f"   ❌ Error setting availability for player {i+1}: {e}")
    
    print("\n4️⃣  Setting Sample Squad Selection...")
    
    if fixture_ids and player_ids:
        first_fixture = fixture_ids[0]
        
        # Set squad status for available players
        squad_assignments = [
            ('Starter', 0), ('Starter', 1), ('Starter', 2), ('Starter', 3), ('Starter', 4),
            ('Starter', 5), ('Starter', 6), ('Starter', 7), ('Starter', 8), ('Starter', 9),
            ('Starter', 10), ('Substitute', 11), ('Substitute', 12), ('Substitute', 13)
        ]
        
        for squad_status, player_index in squad_assignments:
            if player_index < len(player_ids):
                try:
                    result = availability_tool._run('set_squad_status',
                                                   player_id=player_ids[player_index],
                                                   fixture_id=first_fixture,
                                                   squad_status=squad_status)
                    print(f"   ✅ Player {player_index+1}: {squad_status}")
                except Exception as e:
                    print(f"   ❌ Error setting squad status for player {player_index+1}: {e}")
    
    print("\n5️⃣  Marking Sample Payments...")
    
    if fixture_ids and player_ids:
        first_fixture = fixture_ids[0]
        
        # Mark some players as paid
        paid_players = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # First 10 players paid
        
        for player_index in paid_players:
            if player_index < len(player_ids):
                try:
                    result = availability_tool._run('mark_payment',
                                                   player_id=player_ids[player_index],
                                                   fixture_id=first_fixture,
                                                   has_paid=True)
                    print(f"   ✅ Player {player_index+1}: Paid")
                except Exception as e:
                    print(f"   ❌ Error marking payment for player {player_index+1}: {e}")
    
    print("\n6️⃣  Testing Data Retrieval...")
    
    print("\n   📋 All Players:")
    try:
        players_result = player_tool._run('get_all_players')
        print(players_result)
    except Exception as e:
        print(f"   ❌ Error getting players: {e}")
    
    print("\n   📅 All Fixtures:")
    try:
        fixtures_result = fixture_tool._run('get_fixtures', upcoming_only=False)
        print(fixtures_result)
    except Exception as e:
        print(f"   ❌ Error getting fixtures: {e}")
    
    if fixture_ids:
        print(f"\n   👥 Availability for Fixture {fixture_ids[0]}:")
        try:
            availability_result = availability_tool._run('get_availability', fixture_id=fixture_ids[0])
            print(availability_result)
        except Exception as e:
            print(f"   ❌ Error getting availability: {e}")
        
        print(f"\n   ⚽ Squad for Fixture {fixture_ids[0]}:")
        try:
            squad_result = availability_tool._run('get_squad', fixture_id=fixture_ids[0])
            print(squad_result)
        except Exception as e:
            print(f"   ❌ Error getting squad: {e}")
    
    print("\n✅ Sample data creation completed!")
    print(f"📊 Summary:")
    print(f"   - Players: {len(player_ids)}")
    print(f"   - Fixtures: {len(fixture_ids)}")
    print(f"   - Availability records: {len(player_ids)}")
    print(f"   - Squad selections: {len(player_ids)}")
    print(f"   - Payment records: {len(paid_players)}")
    
    print("\n🎯 You can now test all the KICKAI tools with this sample data!")

if __name__ == "__main__":
    test_sample_data() 