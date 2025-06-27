#!/usr/bin/env python3
"""
Update WhatsApp Group Settings for KICKAI
Help configure WhatsApp group for real testing.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def update_whatsapp_group():
    """Update WhatsApp group settings."""
    print("📱 WhatsApp Group Configuration")
    print("=" * 50)
    
    print("\n📋 Current Settings:")
    current_group = os.getenv('TEAM_WHATSAPP_GROUP', 'Not set')
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER', 'Not set')
    
    print(f"Current WhatsApp Group: {current_group}")
    print(f"Twilio Number: {twilio_number}")
    
    print("\n🔧 Setup Instructions:")
    print("1. Create a WhatsApp group with your real team members")
    print("2. Add your Twilio number to the group")
    print("3. Get the group ID (usually your phone number)")
    print("4. Update the settings below")
    
    print("\n📝 Update Settings:")
    new_group = input("New WhatsApp Group ID (or press Enter to keep current): ").strip()
    
    if new_group:
        # Update .env file
        env_file = '.env'
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update or add TEAM_WHATSAPP_GROUP
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('TEAM_WHATSAPP_GROUP='):
                    lines[i] = f'TEAM_WHATSAPP_GROUP={new_group}\n'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'TEAM_WHATSAPP_GROUP={new_group}\n')
            
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            print(f"✅ Updated .env file with TEAM_WHATSAPP_GROUP={new_group}")
        else:
            print(f"⚠️  .env file not found. Please add manually:")
            print(f"TEAM_WHATSAPP_GROUP={new_group}")
    
    print("\n🎯 Next Steps:")
    print("1. ✅ Add real members using: python add_real_members.py")
    print("2. ✅ Test WhatsApp messaging: python test_whatsapp_features.py")
    print("3. ✅ Send messages to your real team!")

def show_whatsapp_instructions():
    """Show detailed WhatsApp setup instructions."""
    print("📱 WhatsApp Setup Instructions")
    print("=" * 50)
    
    print("\n🔧 For Twilio Sandbox (Testing):")
    print("1. Create a WhatsApp group with your team")
    print("2. Add your Twilio number to the group")
    print("3. Use your phone number as the group ID:")
    print("   Format: whatsapp:+<country_code><number>")
    print("   Example: whatsapp:+447123456789")
    
    print("\n🔧 For WhatsApp Business API (Production):")
    print("1. Request group messaging approval from Twilio")
    print("2. Get the group JID from WhatsApp")
    print("3. Use the provided group identifier")
    
    print("\n⚠️  Important Notes:")
    print("- Twilio Sandbox only supports individual messaging")
    print("- For group messaging, you need WhatsApp Business API approval")
    print("- Test with individual numbers first")
    print("- Contact Twilio support for group messaging setup")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Update WhatsApp group settings")
    print("2. Show WhatsApp setup instructions")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == "1":
        update_whatsapp_group()
    elif choice == "2":
        show_whatsapp_instructions()
    else:
        print("Invalid choice!") 