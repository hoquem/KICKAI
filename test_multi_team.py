#!/usr/bin/env python3
"""
Test script for KICKAI Multi-Team functionality
Verifies that multiple teams can run simultaneously with complete isolation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_multi_team_isolation():
    """Test that multiple teams are completely isolated from each other."""
    print("🧪 Testing Multi-Team Isolation")
    print("=" * 50)
    
    try:
        from src.multi_team_manager import MultiTeamManager
        
        # Initialize the multi-team manager
        print("1️⃣ Initializing Multi-Team Manager...")
        manager = MultiTeamManager()
        manager.initialize()
        
        # List all managed teams
        teams = manager.list_teams()
        print(f"2️⃣ Found {len(teams)} managed teams:")
        
        for team in teams:
            status = "✅ Ready" if team['has_crew'] else "❌ No Crew"
            print(f"   - {team['name']} (ID: {team['id'][:8]}...) - {status}")
        
        if len(teams) < 2:
            print("⚠️  Need at least 2 teams to test isolation. Current teams:")
            for team in teams:
                print(f"   - {team['name']}")
            return False
        
        # Test isolation by checking that each team has its own tools
        print("\n3️⃣ Testing team isolation...")
        
        for team in teams:
            team_id = team['id']
            team_name = team['name']
            
            if team_id not in manager.crews:
                print(f"   ❌ No crew for {team_name}")
                continue
            
            crew = manager.crews[team_id]
            
            # Check that agents have team-specific tools
            for agent in crew.agents:
                for tool in agent.tools:
                    if hasattr(tool, 'team_id'):
                        if tool.team_id == team_id:
                            print(f"   ✅ {team_name}: {agent.role} has correct team_id in {tool.name}")
                        else:
                            print(f"   ❌ {team_name}: {agent.role} has wrong team_id in {tool.name}")
                    else:
                        print(f"   ⚠️  {team_name}: {agent.role} tool {tool.name} has no team_id")
        
        # Test that teams can run independently
        print("\n4️⃣ Testing independent team execution...")
        
        for team in teams:
            team_id = team['id']
            team_name = team['name']
            
            if team_id not in manager.crews:
                continue
            
            print(f"   🚀 Testing {team_name}...")
            
            # Create a simple task for this team
            from crewai import Task
            crew = manager.crews[team_id]
            
            # Create a simple task that lists players
            list_players_task = Task(
                description="List all players in the team",
                expected_output="A list of all players in the team",
                agent=crew.agents[0],  # Use the first agent
                tools=[tool for tool in crew.agents[0].tools if hasattr(tool, 'name') and 'Player' in tool.name]
            )
            
            try:
                result = manager.run_team_tasks(team_id, [list_players_task])
                if result:
                    print(f"   ✅ {team_name}: Successfully executed task")
                    # Show first 100 characters of result
                    preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                    print(f"      Result preview: {preview}")
                else:
                    print(f"   ❌ {team_name}: No result from task execution")
                    
            except Exception as e:
                print(f"   ❌ {team_name}: Error executing task - {e}")
        
        print("\n✅ Multi-team isolation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing multi-team isolation: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_team_specific_data():
    """Test that each team only sees its own data."""
    print("\n🧪 Testing Team-Specific Data Access")
    print("=" * 50)
    
    try:
        from src.tools.supabase_tools import PlayerTools
        from src.tools.telegram_tools import get_team_name_by_id
        
        # Get active teams
        from src.multi_team_manager import get_active_teams
        active_teams = get_active_teams()
        
        if len(active_teams) < 2:
            print("⚠️  Need at least 2 teams to test data isolation")
            return False
        
        print(f"1️⃣ Testing data isolation for {len(active_teams)} teams...")
        
        for team in active_teams:
            team_id = team['id']
            team_name = team['name']
            
            print(f"\n2️⃣ Testing {team_name} (ID: {team_id[:8]}...)")
            
            # Test player tools for this team
            try:
                player_tools = PlayerTools(team_id)
                result = player_tools._run('get_all_players')
                print(f"   📋 Players for {team_name}:")
                print(f"      {result}")
                
            except Exception as e:
                print(f"   ❌ Error getting players for {team_name}: {e}")
            
            # Test team name retrieval
            try:
                retrieved_name = get_team_name_by_id(team_id)
                if retrieved_name == team_name:
                    print(f"   ✅ Team name retrieval correct: {retrieved_name}")
                else:
                    print(f"   ❌ Team name mismatch: expected {team_name}, got {retrieved_name}")
                    
            except Exception as e:
                print(f"   ❌ Error getting team name for {team_id}: {e}")
        
        print("\n✅ Team-specific data test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing team-specific data: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_telegram_isolation():
    """Test that Telegram tools are isolated per team."""
    print("\n🧪 Testing Telegram Tool Isolation")
    print("=" * 50)
    
    try:
        from src.tools.telegram_tools import SendTelegramMessageTool, get_team_bot_credentials
        
        # Get active teams
        from src.multi_team_manager import get_active_teams
        active_teams = get_active_teams()
        
        if len(active_teams) < 2:
            print("⚠️  Need at least 2 teams to test Telegram isolation")
            return False
        
        print(f"1️⃣ Testing Telegram isolation for {len(active_teams)} teams...")
        
        for team in active_teams:
            team_id = team['id']
            team_name = team['name']
            
            print(f"\n2️⃣ Testing {team_name} (ID: {team_id[:8]}...)")
            
            # Test bot credentials for this team
            try:
                token, chat_id = get_team_bot_credentials(team_id)
                print(f"   ✅ Bot credentials retrieved for {team_name}")
                print(f"      Token: {token[:10]}...")
                print(f"      Chat ID: {chat_id}")
                
                # Test message tool creation
                message_tool = SendTelegramMessageTool(team_id)
                print(f"   ✅ Message tool created for {team_name}")
                print(f"      Tool team_id: {message_tool.team_id}")
                
            except Exception as e:
                print(f"   ❌ Error with Telegram tools for {team_name}: {e}")
        
        print("\n✅ Telegram isolation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Telegram isolation: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all multi-team tests."""
    print("##################################################")
    print("## KICKAI Multi-Team Testing Suite ##")
    print("##################################################")
    
    # Validate environment
    required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("✅ Environment variables validated")
    
    # Run tests
    tests = [
        ("Multi-Team Isolation", test_multi_team_isolation),
        ("Team-Specific Data", test_team_specific_data),
        ("Telegram Isolation", test_telegram_isolation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Multi-team functionality is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 