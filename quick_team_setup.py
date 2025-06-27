#!/usr/bin/env python3
"""
Quick Team Setup for KICKAI
Quickly create a new team with minimal input.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def quick_team_setup():
    """Quick team setup with minimal input."""
    print("🚀 KICKAI Quick Team Setup")
    print("=" * 40)
    
    try:
        from src.tools.team_management_tools import TeamManagementTools
        
        tool = TeamManagementTools()
        
        # Get minimal input with defaults
        team_name = input("Team name: ").strip() or "My Sunday League Team"
        admin_phone = input("Your phone number: ").strip() or "+1234567890"
        admin_name = input("Your name: ").strip() or "Team Admin"
        telegram_group = input("Telegram group ID: ").strip() or "test_group"
        
        print(f"\n📋 Team Details:")
        print(f"Name: {team_name}")
        print(f"Admin: {admin_name} ({admin_phone})")
        print(f"📱 Telegram Group: {telegram_group}")
        
        # Confirm
        confirm = input("\nCreate this team? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Team creation cancelled.")
            return False
        
        # Create team
        print(f"\nCreating team '{team_name}'...")
        result = tool._run('create_team',
                          name=team_name,
                          admin_phone=admin_phone,
                          admin_name=admin_name,
                          telegram_group=telegram_group,
                          description="Team created via quick setup")
        
        print(f"✅ {result}")
        
        # Show next steps
        print(f"\n📋 Next Steps:")
        print(f"1. Update your .env file: TELEGRAM_CHAT_ID={telegram_group}")
        print(f"2. Test Telegram messaging: python test_telegram_features.py")
        print(f"3. Invite team members to your Telegram group")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating team: {e}")
        return False


if __name__ == "__main__":
    quick_team_setup() 