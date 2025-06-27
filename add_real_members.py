#!/usr/bin/env python3
"""
Add Real Members to KICKAI Team
Add real people with their actual phone numbers and names.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def add_real_member(team_id):
    """Add a real member to the team."""
    print("👥 Adding Real Team Member")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # Get member details
        print("\n📝 Enter member details:")
        name = input("Full name: ").strip()
        phone = input("Phone number (with country code, e.g., +447123456789): ").strip()
        
        print("\n🎭 Choose role:")
        print("1. admin - Full system access")
        print("2. manager - Squad selection, match coordination")
        print("3. captain - On-field leadership")
        print("4. secretary - Communication, documentation")
        print("5. player - Basic interactions")
        
        role_choice = input("Enter role number (1-5): ").strip()
        
        role_map = {
            "1": "admin",
            "2": "manager", 
            "3": "captain",
            "4": "secretary",
            "5": "player"
        }
        
        role = role_map.get(role_choice, "player")
        
        # Add the member
        result = tool._run(
            command="add_team_member",
            team_id=team_id,
            phone_number=phone,
            name=name,
            role=role,
            invited_by="system"
        )
        
        print(f"\n✅ {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def add_multiple_members(team_id):
    """Add multiple members at once."""
    print("👥 Adding Multiple Real Members")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        members = []
        print("\n📝 Enter member details (press Enter with empty name to finish):")
        
        while True:
            name = input("\nFull name (or press Enter to finish): ").strip()
            if not name:
                break
                
            phone = input("Phone number (+country code): ").strip()
            
            print("Role: 1=admin, 2=manager, 3=captain, 4=secretary, 5=player")
            role_choice = input("Role (1-5): ").strip()
            
            role_map = {
                "1": "admin",
                "2": "manager", 
                "3": "captain",
                "4": "secretary",
                "5": "player"
            }
            
            role = role_map.get(role_choice, "player")
            
            members.append((name, phone, role))
        
        if not members:
            print("No members to add.")
            return True
        
        # Add all members
        print(f"\n🔄 Adding {len(members)} members...")
        
        for name, phone, role in members:
            result = tool._run(
                command="add_team_member",
                team_id=team_id,
                phone_number=phone,
                name=name,
                role=role,
                invited_by="system"
            )
            print(f"✅ {name} ({role}): {result}")
        
        print(f"\n🎉 Successfully added {len(members)} members!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_team_members(team_id):
    """Show current team members."""
    print("📋 Current Team Members")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        result = tool._run(command="get_team_members", team_id=team_id)
        print(result)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Use the team ID from your setup
    team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"
    
    print("🎯 KICKAI Team Member Management")
    print("=" * 50)
    print(f"Team ID: {team_id}")
    
    print("\nChoose an option:")
    print("1. Add single real member")
    print("2. Add multiple real members")
    print("3. Show current team members")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        add_real_member(team_id)
    elif choice == "2":
        add_multiple_members(team_id)
    elif choice == "3":
        show_team_members(team_id)
    else:
        print("Invalid choice!") 