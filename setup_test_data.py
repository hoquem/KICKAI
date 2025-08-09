#!/usr/bin/env python3
"""
Setup Test Data for KICKAI End-to-End Testing

This script creates a comprehensive set of test users, team members, and players
in Firestore for testing all system commands with the Mock Telegram interface.
"""

import os
import sys
from datetime import datetime, timedelta
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set required environment variables
os.environ["KICKAI_INVITE_SECRET_KEY"] = "test_secret_key_for_debugging_only_32_chars_long"
os.environ["USE_MOCK_DATASTORE"] = "false"
os.environ["FIREBASE_PROJECT_ID"] = "kickai-954c2"
os.environ["FIREBASE_CREDENTIALS_FILE"] = "credentials/firebase_credentials_testing.json"

def setup_test_data():
    """Set up comprehensive test data in Firestore."""
    print("🔧 SETTING UP TEST DATA IN FIRESTORE")
    print("=" * 70)
    
    try:
        from kickai.database.firebase_client import get_firebase_client
        from kickai.utils.simple_id_generator import generate_simple_player_id, generate_simple_team_member_id
        from kickai.utils.user_id_generator import generate_user_id
        
        # Get Firebase client
        client = get_firebase_client()
        db = client.client
        
        # Team ID (using existing team)
        team_id = "KTI"
        
        # Test data summary
        created_players = []
        created_members = []
        created_matches = []
        
        print("\n📋 CREATING TEST PLAYERS")
        print("-" * 50)
        
        # Test Players with various states
        test_players = [
            # Active approved players
            {
                "telegram_id": 1001,
                "name": "John Smith",
                "username": "john_smith",
                "phone": "+447700900001",
                "position": "striker",
                "status": "active",
                "approval_status": "approved",
                "jersey_number": 9
            },
            {
                "telegram_id": 1002,
                "name": "Mike Johnson",
                "username": "mike_j",
                "phone": "+447700900002",
                "position": "midfielder",
                "status": "active",
                "approval_status": "approved",
                "jersey_number": 8
            },
            {
                "telegram_id": 1003,
                "name": "David Wilson",
                "username": "d_wilson",
                "phone": "+447700900003",
                "position": "defender",
                "status": "active",
                "approval_status": "approved",
                "jersey_number": 4
            },
            {
                "telegram_id": 1004,
                "name": "James Brown",
                "username": "james_b",
                "phone": "+447700900004",
                "position": "goalkeeper",
                "status": "active",
                "approval_status": "approved",
                "jersey_number": 1
            },
            # Pending approval players
            {
                "telegram_id": 1005,
                "name": "Tom Anderson",
                "username": "tom_a",
                "phone": "+447700900005",
                "position": "striker",
                "status": "pending",
                "approval_status": "pending",
                "jersey_number": None
            },
            {
                "telegram_id": 1006,
                "name": "Charlie White",
                "username": "charlie_w",
                "phone": "+447700900006",
                "position": "midfielder",
                "status": "pending",
                "approval_status": "pending",
                "jersey_number": None
            },
            # Inactive player
            {
                "telegram_id": 1007,
                "name": "William Davis",
                "username": "will_d",
                "phone": "+447700900007",
                "position": "defender",
                "status": "inactive",
                "approval_status": "approved",
                "jersey_number": 5
            },
            # Rejected player
            {
                "telegram_id": 1008,
                "name": "Harry Martin",
                "username": "harry_m",
                "phone": "+447700900008",
                "position": "defender",
                "status": "rejected",
                "approval_status": "rejected",
                "rejection_reason": "Not eligible for team",
                "jersey_number": None
            }
        ]
        
        # Create players in Firestore
        for player_data in test_players:
            player_id = generate_simple_player_id(player_data["name"], team_id)
            
            player_doc = {
                "id": player_id,
                "telegram_id": player_data["telegram_id"],
                "team_id": team_id,
                "name": player_data["name"],
                "username": player_data.get("username"),
                "phone": player_data.get("phone"),
                "position": player_data.get("position"),
                "status": player_data.get("status", "pending"),
                "approval_status": player_data.get("approval_status", "pending"),
                "jersey_number": player_data.get("jersey_number"),
                "rejection_reason": player_data.get("rejection_reason"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "matches_played": 0,
                "goals_scored": 0,
                "assists": 0
            }
            
            # Store in both collections
            db.collection("kickai_players").document(player_id).set(player_doc)
            db.collection(f"kickai_{team_id}_players").document(player_id).set(player_doc)
            
            created_players.append(player_doc)
            print(f"✅ Created player: {player_id} - {player_data['name']} ({player_data['status']})")
        
        print(f"\n📋 CREATING TEST TEAM MEMBERS")
        print("-" * 50)
        
        # Test Team Members (Leadership)
        test_members = [
            {
                "telegram_id": 2001,
                "name": "Alex Manager",
                "username": "alex_manager",
                "phone": "+447700900101",
                "role": "manager",
                "status": "active",
                "permissions": ["all"]
            },
            {
                "telegram_id": 2002,
                "name": "Sam Coach",
                "username": "sam_coach",
                "phone": "+447700900102",
                "role": "coach",
                "status": "active",
                "permissions": ["squad_selection", "training"]
            },
            {
                "telegram_id": 2003,
                "name": "Pat Secretary",
                "username": "pat_secretary",
                "phone": "+447700900103",
                "role": "secretary",
                "status": "active",
                "permissions": ["admin", "communications"]
            },
            {
                "telegram_id": 2004,
                "name": "Chris Treasurer",
                "username": "chris_treasurer",
                "phone": "+447700900104",
                "role": "treasurer",
                "status": "active",
                "permissions": ["finance", "payments"]
            },
            # Pending member
            {
                "telegram_id": 2005,
                "name": "Jordan Assistant",
                "username": "jordan_assistant",
                "phone": "+447700900105",
                "role": "assistant",
                "status": "pending",
                "permissions": []
            }
        ]
        
        # Create team members in Firestore
        for member_data in test_members:
            member_id = generate_simple_team_member_id(member_data["name"], team_id)
            
            member_doc = {
                "id": member_id,
                "telegram_id": member_data["telegram_id"],
                "team_id": team_id,
                "name": member_data["name"],
                "username": member_data.get("username"),
                "phone": member_data.get("phone"),
                "role": member_data.get("role", "member"),
                "status": member_data.get("status", "active"),
                "permissions": member_data.get("permissions", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_active": datetime.utcnow()
            }
            
            # Store in both collections
            db.collection("kickai_team_members").document(member_id).set(member_doc)
            db.collection(f"kickai_{team_id}_team_members").document(member_id).set(member_doc)
            
            created_members.append(member_doc)
            print(f"✅ Created team member: {member_id} - {member_data['name']} ({member_data['role']})")
        
        # Create a dual-role user (both player and team member)
        print(f"\n📋 CREATING DUAL-ROLE USER")
        print("-" * 50)
        
        dual_user = {
            "telegram_id": 3001,
            "name": "Captain Leader",
            "username": "captain_leader",
            "phone": "+447700900201"
        }
        
        # Create as player
        player_id = generate_simple_player_id(dual_user["name"], team_id)
        player_doc = {
            "id": player_id,
            "telegram_id": dual_user["telegram_id"],
            "team_id": team_id,
            "name": dual_user["name"],
            "username": dual_user["username"],
            "phone": dual_user["phone"],
            "position": "midfielder",
            "status": "active",
            "approval_status": "approved",
            "jersey_number": 10,
            "is_captain": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        db.collection("kickai_players").document(player_id).set(player_doc)
        db.collection(f"kickai_{team_id}_players").document(player_id).set(player_doc)
        created_players.append(player_doc)
        print(f"✅ Created dual-role as player: {player_id}")
        
        # Create as team member
        member_id = generate_simple_team_member_id(dual_user["name"], team_id)
        member_doc = {
            "id": member_id,
            "telegram_id": dual_user["telegram_id"],
            "team_id": team_id,
            "name": dual_user["name"],
            "username": dual_user["username"],
            "phone": dual_user["phone"],
            "role": "captain",
            "status": "active",
            "permissions": ["squad_selection", "team_leadership"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        db.collection("kickai_team_members").document(member_id).set(member_doc)
        db.collection(f"kickai_{team_id}_team_members").document(member_id).set(member_doc)
        created_members.append(member_doc)
        print(f"✅ Created dual-role as team member: {member_id}")
        
        print(f"\n⚽ CREATING TEST MATCHES")
        print("-" * 50)
        
        # Create test matches
        test_matches = [
            {
                "match_id": f"MATCH_{uuid.uuid4().hex[:8].upper()}",
                "team_id": team_id,
                "opponent": "Test FC",
                "date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "time": "14:00",
                "location": "Home Ground",
                "type": "league",
                "status": "scheduled",
                "home_team": team_id,
                "away_team": "Test FC"
            },
            {
                "match_id": f"MATCH_{uuid.uuid4().hex[:8].upper()}",
                "team_id": team_id,
                "opponent": "United Test",
                "date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "time": "15:30",
                "location": "Away Stadium",
                "type": "cup",
                "status": "scheduled",
                "home_team": "United Test",
                "away_team": team_id
            },
            {
                "match_id": f"MATCH_{uuid.uuid4().hex[:8].upper()}",
                "team_id": team_id,
                "opponent": "City Test",
                "date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "time": "14:00",
                "location": "Home Ground",
                "type": "league",
                "status": "completed",
                "home_team": team_id,
                "away_team": "City Test",
                "result": "3-2",
                "home_score": 3,
                "away_score": 2
            }
        ]
        
        for match_data in test_matches:
            match_data["created_at"] = datetime.utcnow()
            match_data["updated_at"] = datetime.utcnow()
            
            db.collection("kickai_matches").document(match_data["match_id"]).set(match_data)
            db.collection(f"kickai_{team_id}_matches").document(match_data["match_id"]).set(match_data)
            
            created_matches.append(match_data)
            print(f"✅ Created match: {match_data['match_id']} vs {match_data['opponent']} ({match_data['status']})")
        
        # Create attendance records for upcoming matches
        print(f"\n📝 CREATING TEST ATTENDANCE RECORDS")
        print("-" * 50)
        
        attendance_statuses = ["yes", "no", "maybe", "unknown"]
        attendance_count = 0
        
        for match in created_matches[:2]:  # Only for future matches
            for i, player in enumerate(created_players[:4]):  # First 4 players
                attendance_doc = {
                    "attendance_id": f"ATT_{uuid.uuid4().hex[:8].upper()}",
                    "match_id": match["match_id"],
                    "player_id": player["id"],
                    "team_id": team_id,
                    "status": attendance_statuses[i % 4],
                    "responded_at": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                db.collection("kickai_attendance").document(attendance_doc["attendance_id"]).set(attendance_doc)
                attendance_count += 1
        
        print(f"✅ Created {attendance_count} attendance records")
        
        print("\n" + "="*70)
        print("TEST DATA SETUP COMPLETE")
        print("="*70)
        print(f"\n✅ Team: {team_id} (existing team)")
        print(f"✅ Created {len(created_players)} test players")
        print(f"✅ Created {len(created_members)} test team members")
        print(f"✅ Created {len(created_matches)} test matches")
        print(f"✅ Created {attendance_count} attendance records")
        
        print("\n📋 TEST USER TELEGRAM IDs:")
        print("-"*50)
        print("\n🏃 PLAYERS:")
        for player in created_players:
            status_emoji = "✅" if player["status"] == "active" else "⏳" if player["status"] == "pending" else "❌"
            print(f"  {status_emoji} {player['telegram_id']:4d} - {player['name']:20s} ({player['status']})")
        
        print("\n👔 TEAM MEMBERS:")
        for member in created_members:
            status_emoji = "✅" if member["status"] == "active" else "⏳"
            print(f"  {status_emoji} {member['telegram_id']:4d} - {member['name']:20s} ({member['role']})")
        
        print("\n⚽ MATCHES:")
        for match in created_matches:
            status_emoji = "📅" if match["status"] == "scheduled" else "✅"
            date_str = match["date"][:10] if isinstance(match["date"], str) else match["date"].strftime("%Y-%m-%d")
            print(f"  {status_emoji} {match['match_id']} vs {match['opponent']} on {date_str}")
        
        print("\n" + "="*70)
        print("✅ Test data is ready for E2E testing with Mock Telegram!")
        print("📝 Use the telegram_id values above to test as different users")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to set up test data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    success = setup_test_data()
    if success:
        print("\n🚀 Test data setup successful! Ready for comprehensive testing.")
    else:
        print("\n❌ Test data setup failed! Please check the errors above.")

if __name__ == "__main__":
    main()