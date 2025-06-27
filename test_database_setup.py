#!/usr/bin/env python3
"""
Test Database Setup for KICKAI
Verifies that the multi-team schema is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test basic database connection."""
    print("🔌 Testing Database Connection")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import get_supabase_client
        
        client = get_supabase_client()
        print("✅ Supabase client created successfully")
        
        # Test basic query
        response = client.table('teams').select('*').limit(1).execute()
        print("✅ Teams table query successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_team_creation():
    """Test creating a team."""
    print("\n🏗️ Testing Team Creation")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # Test team creation
        print("\n3️⃣ Testing team creation...")
        result = tool._run(
            command="create_team",
            name="Test Beta Team",
            admin_phone="+1234567890",
            admin_name="Beta Admin",
            telegram_group="test_beta_group",
            description="Test team for database validation"
        )
        print(f"✅ Team creation: {result}")
        
        # Test member addition
        print("\n4️⃣ Testing member addition...")
        result = tool._run(
            command="add_team_member",
            team_id="test-team-id",  # You'll need to get this from the team creation
            phone_number="+1987654321",
            name="Test Member",
            role="player"
        )
        print(f"✅ Member addition: {result}")
        
        # Test team listing
        print("\n5️⃣ Testing team listing...")
        result = tool._run(command="list_teams")
        print(f"✅ Team listing: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Team creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_tables():
    """Test that existing tables still work."""
    print("\n📊 Testing Existing Tables")
    print("=" * 50)
    
    try:
        from tools.supabase_tools import PlayerTools
        
        player_tool = PlayerTools()
        
        # Test getting all players
        result = player_tool._run(command="get_all_players")
        print(f"✅ Players query: {result[:100]}...")  # Show first 100 chars
        
        return True
        
    except Exception as e:
        print(f"❌ Existing tables test failed: {e}")
        return False

def check_schema_changes():
    """Check if schema changes were applied."""
    print("\n🔍 Checking Schema Changes")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import get_supabase_client
        
        client = get_supabase_client()
        
        # Check if teams table exists
        response = client.table('teams').select('*').limit(1).execute()
        print("✅ Teams table exists and accessible")
        
        # Check if team_members table exists
        response = client.table('team_members').select('*').limit(1).execute()
        print("✅ Team members table exists and accessible")
        
        # Check if players table has team_id column
        response = client.table('players').select('team_id').limit(1).execute()
        print("✅ Players table has team_id column")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False

def main():
    """Run all database tests."""
    print("🧪 KICKAI Database Setup Verification")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Schema Changes", check_schema_changes),
        ("Existing Tables", test_existing_tables),
        ("Team Creation", test_team_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database setup is complete.")
        print("\n📋 Next steps:")
        print("1. ✅ Database schema updated successfully")
        print("2. 🔄 Test team creation: python quick_team_setup.py")
        print("3. 📱 Test Telegram integration: python test_telegram_features.py")
        print("4. 🤖 Test CrewAI agents: python test_crewai_ollama_correct.py")
        print("5. 📊 Add sample data: python test_sample_data.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify Supabase credentials in .env file")
        print("2. Check that SQL schema was executed in Supabase")
        print("3. Ensure all tables exist in your database")

if __name__ == "__main__":
    main() 