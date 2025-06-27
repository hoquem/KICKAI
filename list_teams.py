#!/usr/bin/env python3
"""
List Teams for KICKAI
Shows all teams and their IDs for easy reference.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def list_teams():
    """List all teams with their IDs."""
    print("📋 Listing All Teams")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # List all teams
        result = tool._run(command="list_teams")
        print(result)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_team_details(team_id):
    """Get detailed information about a specific team."""
    print(f"\n🔍 Team Details for ID: {team_id}")
    print("=" * 50)
    
    try:
        from tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # Get team info
        result = tool._run(command="get_team_info", team_id=team_id)
        print(result)
        
        # Get team members
        result = tool._run(command="get_team_members", team_id=team_id)
        print(f"\n{result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Choose an option:")
    print("1. List all teams")
    print("2. Get details for a specific team")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        list_teams()
    elif choice == "2":
        team_id = input("Enter team ID: ").strip()
        if team_id:
            get_team_details(team_id)
        else:
            print("No team ID provided")
    else:
        print("Invalid choice!") 