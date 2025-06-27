#!/usr/bin/env python3
"""
Test Team Setup for KICKAI
Creates a new team and tests the multi-team functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_team_creation():
    """Test creating a new team."""
    print("🏗️ Testing Team Creation...")
    
    try:
        from src.tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # Test data
        team_name = "Test Team Alpha"
        admin_phone = "+1234567890"
        admin_name = "Test Admin"
        telegram_group = "test_team_alpha_group"
        description = "Test team for KICKAI development"
        
        result = tool._run('create_team', 
                          name=team_name,
                          admin_phone=admin_phone,
                          admin_name=admin_name,
                          telegram_group=telegram_group,
                          description=description)
        
        print(f"✅ Team creation result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating team: {e}")
        return False


def test_team_member_addition():
    """Test adding members to the team."""
    print("\n👥 Testing Team Member Addition...")
    
    try:
        from src.tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # Test data
        team_id = "test-team-id"  # You'll need to get this from the team creation
        phone_number = "+1987654321"
        name = "Test Player"
        role = "player"
        
        result = tool._run('add_team_member',
                          team_id=team_id,
                          phone_number=phone_number,
                          name=name,
                          role=role)
        
        print(f"✅ Member addition result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error adding team member: {e}")
        return False


def test_team_listing():
    """Test listing all teams."""
    print("\n📋 Testing Team Listing...")
    
    try:
        from src.tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        result = tool._run('list_teams')
        
        print(f"✅ Team listing result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error listing teams: {e}")
        return False


def interactive_team_setup():
    """Interactive team setup for real testing."""
    print("\n🎯 Interactive Team Setup")
    print("=" * 40)
    
    try:
        from src.tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # Get user input
        print("Enter team details:")
        team_name = input("Team name: ").strip()
        admin_phone = input("Admin phone number: ").strip()
        admin_name = input("Admin name: ").strip()
        telegram_group = input("Telegram group ID: ").strip()
        description = input("Description (optional): ").strip() or "Team created via interactive setup"
        
        # Validate input
        if not all([team_name, admin_phone, admin_name, telegram_group]):
            print("❌ All fields are required!")
            return False
        
        # Create team
        print(f"\nCreating team '{team_name}'...")
        result = tool._run('create_team',
                          name=team_name,
                          admin_phone=admin_phone,
                          admin_name=admin_name,
                          telegram_group=telegram_group,
                          description=description)
        
        print(f"✅ {result}")
        
        # Show next steps
        print(f"\n📋 Next Steps:")
        print(f"1. Update your .env file with the new Telegram group: {telegram_group}")
        print(f"2. Test Telegram messaging with the new team")
        print(f"3. Invite real people to join the Telegram group")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in interactive setup: {e}")
        return False


def main():
    """Run all team setup tests."""
    print("🚀 KICKAI Team Setup Test")
    print("=" * 50)
    
    # Run automated tests
    tests = [
        test_team_creation,
        test_team_member_addition,
        test_team_listing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Automated Tests: {passed}/{total} passed")
    
    # Ask if user wants interactive setup
    print("\n" + "=" * 50)
    response = input("Would you like to create a real team? (y/n): ").strip().lower()
    
    if response == 'y':
        interactive_team_setup()
    else:
        print("Skipping interactive setup.")
    
    print("\n✅ Team setup test complete!")


if __name__ == "__main__":
    main() 