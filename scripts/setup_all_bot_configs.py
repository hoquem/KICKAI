#!/usr/bin/env python3
"""
Comprehensive Bot Configuration Setup Script

This script sets up bot configurations for all environments:
- Testing: Use existing bot token with team name "kickai-testing"
- Staging: Use environment variables with team name "kickai-staging"  
- Production: Move testing config to production Firestore with team name "BP Hatters FC"
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def run_railway_command(command):
    """Run a Railway CLI command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def get_railway_variable(service_name, variable_name):
    """Get a Railway environment variable"""
    success, stdout, stderr = run_railway_command(
        f'railway variables --service {service_name} | grep {variable_name}'
    )
    
    if success and variable_name in stdout:
        # Extract the value from the Railway output
        lines = stdout.strip().split('\n')
        for line in lines:
            if variable_name in line:
                # Parse the Railway table format
                parts = line.split('│')
                if len(parts) >= 2:
                    return parts[1].strip()
    return None

def set_railway_variable(service_name, variable_name, value):
    """Set a Railway environment variable"""
    print(f"🔧 Setting {variable_name} for {service_name}...")
    
    success, stdout, stderr = run_railway_command(
        f'railway variables --service {service_name} --set {variable_name}="{value}"'
    )
    
    if success:
        print(f"✅ Successfully set {variable_name} for {service_name}")
        return True
    else:
        print(f"❌ Failed to set {variable_name} for {service_name}")
        print(f"Error: {stderr}")
        return False

def update_testing_config():
    """Update testing configuration with existing bot token"""
    print("\n🔧 Setting up Testing Environment")
    print("=" * 50)
    
    # Get the existing bot token from Railway
    bot_token = get_railway_variable('kickai-testing', 'TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ No bot token found in testing environment")
        return False
    
    print(f"📋 Found bot token: {bot_token[:10]}...")
    
    # Update the testing configuration file
    config_path = Path("config/bot_config.json")
    
    if not config_path.exists():
        print("❌ Testing configuration file not found")
        return False
    
    # Read current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Update team name and bot token
    config['teams']['test-team']['name'] = 'kickai-testing'
    config['teams']['test-team']['description'] = 'Testing environment for KICKAI'
    config['teams']['test-team']['bots']['main']['token'] = bot_token
    config['teams']['test-team']['bots']['main']['username'] = 'kickai_testing_bot'
    config['teams']['test-team']['bots']['main']['chat_id'] = '-1001234567890'  # Placeholder
    
    # Update Firebase project ID
    firebase_project = get_railway_variable('kickai-testing', 'FIREBASE_PROJECT_ID')
    if firebase_project:
        config['firebase_config']['project_id'] = firebase_project
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Testing configuration updated")
    print(f"   Team Name: kickai-testing")
    print(f"   Bot Token: {bot_token[:10]}...")
    print(f"   Firebase Project: {firebase_project}")
    
    return True

def update_staging_config():
    """Update staging configuration with environment variables"""
    print("\n🔧 Setting up Staging Environment")
    print("=" * 50)
    
    # Get bot token from Railway
    bot_token = get_railway_variable('kickai-staging', 'TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("⚠️  No bot token found in staging environment")
        print("   You'll need to set it manually later")
        bot_token = "YOUR_STAGING_BOT_TOKEN_HERE"
    
    # Update the staging configuration file
    config_path = Path("config/bot_config.staging.json")
    
    if not config_path.exists():
        print("❌ Staging configuration file not found")
        return False
    
    # Read current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Update team name and bot token
    config['teams']['staging-team']['name'] = 'kickai-staging'
    config['teams']['staging-team']['description'] = 'Staging environment for KICKAI'
    config['teams']['staging-team']['bots']['main']['token'] = bot_token
    config['teams']['staging-team']['bots']['main']['username'] = 'kickai_staging_bot'
    config['teams']['staging-team']['bots']['main']['chat_id'] = '-1001234567890'  # Placeholder
    
    # Update Firebase project ID
    firebase_project = get_railway_variable('kickai-staging', 'FIREBASE_PROJECT_ID')
    if firebase_project:
        config['firebase_config']['project_id'] = firebase_project
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Staging configuration updated")
    print(f"   Team Name: kickai-staging")
    print(f"   Bot Token: {bot_token[:10]}...")
    print(f"   Firebase Project: {firebase_project}")
    
    return True

def setup_production_firestore():
    """Set up production Firestore with BP Hatters FC team"""
    print("\n🔧 Setting up Production Environment (Firestore)")
    print("=" * 50)
    
    # Get the testing bot token to move to production
    testing_bot_token = get_railway_variable('kickai-testing', 'TELEGRAM_BOT_TOKEN')
    
    if not testing_bot_token:
        print("❌ No testing bot token found to move to production")
        return False
    
    print(f"📋 Moving bot token {testing_bot_token[:10]}... to production")
    
    # Create a script to set up the production Firestore
    firestore_script = """
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Initialize Firebase Admin SDK for production
cred = credentials.Certificate('firebase_creds_production.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'kickai-production'
})

db = firestore.client()

# Create BP Hatters FC team
team_data = {
    'name': 'BP Hatters FC',
    'description': 'Production team for BP Hatters FC',
    'is_active': True,
    'created_at': firestore.SERVER_TIMESTAMP,
    'settings': {
        'ai_provider': 'openai',
        'ai_model': 'gpt-4',
        'max_members': 200,
        'allow_public_join': False
    }
}

# Add team to Firestore
team_ref = db.collection('teams').document('bp-hatters-fc')
team_ref.set(team_data)

# Create main bot configuration
main_bot_data = {
    'team_id': 'bp-hatters-fc',
    'bot_type': 'main',
    'bot_token': '""" + testing_bot_token + """',
    'bot_username': 'kickai_bp_hatters_main_bot',
    'chat_id': '-1001234567890',  # You'll need to update this
    'is_active': True,
    'created_at': firestore.SERVER_TIMESTAMP
}

# Add main bot to Firestore
main_bot_ref = db.collection('team_bots').document('bp-hatters-fc-main')
main_bot_ref.set(main_bot_data)

# Create leadership bot configuration (placeholder)
leadership_bot_data = {
    'team_id': 'bp-hatters-fc',
    'bot_type': 'leadership',
    'bot_token': 'YOUR_LEADERSHIP_BOT_TOKEN_HERE',  # You'll need to set this
    'bot_username': 'kickai_bp_hatters_leadership_bot',
    'chat_id': '-1001234567890',  # You'll need to update this
    'is_active': True,
    'created_at': firestore.SERVER_TIMESTAMP
}

# Add leadership bot to Firestore
leadership_bot_ref = db.collection('team_bots').document('bp-hatters-fc-leadership')
leadership_bot_ref.set(leadership_bot_data)

print("✅ Production Firestore setup completed!")
print("   Team: BP Hatters FC")
print("   Main Bot: kickai_bp_hatters_main_bot")
print("   Leadership Bot: kickai_bp_hatters_leadership_bot")
print("   Note: You'll need to update chat IDs and leadership bot token")
"""
    
    # Save the script
    script_path = Path("scripts/setup_production_firestore.py")
    with open(script_path, 'w') as f:
        f.write(firestore_script)
    
    print("✅ Production Firestore setup script created")
    print(f"   Script: {script_path}")
    print("   Team: BP Hatters FC")
    print("   Main Bot: Using testing bot token")
    print("   Leadership Bot: Placeholder (needs token)")
    
    return True

def create_environment_variables_script():
    """Create a script to set up environment variables for staging"""
    print("\n🔧 Creating Environment Variables Setup Script")
    print("=" * 50)
    
    script_content = """#!/bin/bash
# Environment Variables Setup Script for Staging

echo "🔧 Setting up environment variables for staging..."

# Set bot token for staging (you'll need to provide this)
echo "Please provide the staging bot token:"
read -s STAGING_BOT_TOKEN

if [ -z "$STAGING_BOT_TOKEN" ]; then
    echo "❌ No bot token provided"
    exit 1
fi

# Set the bot token in Railway
railway variables --service kickai-staging --set TELEGRAM_BOT_TOKEN="$STAGING_BOT_TOKEN"

if [ $? -eq 0 ]; then
    echo "✅ Staging bot token set successfully"
else
    echo "❌ Failed to set staging bot token"
    exit 1
fi

echo "🎉 Staging environment variables setup completed!"
"""
    
    script_path = Path("scripts/setup_staging_env.sh")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    print("✅ Environment variables setup script created")
    print(f"   Script: {script_path}")
    print("   Run: ./scripts/setup_staging_env.sh")
    
    return True

def main():
    print("🤖 Comprehensive Bot Configuration Setup")
    print("=" * 60)
    print("This script will set up bot configurations for all environments:")
    print("• Testing: Use existing bot token with team name 'kickai-testing'")
    print("• Staging: Use environment variables with team name 'kickai-staging'")
    print("• Production: Move testing config to production Firestore with team 'BP Hatters FC'")
    print()
    
    # Check if we're in the right directory
    if not Path("config").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    success_count = 0
    
    # Update testing configuration
    if update_testing_config():
        success_count += 1
    
    # Update staging configuration
    if update_staging_config():
        success_count += 1
    
    # Set up production Firestore
    if setup_production_firestore():
        success_count += 1
    
    # Create environment variables script
    if create_environment_variables_script():
        success_count += 1
    
    print("\n" + "=" * 60)
    print("📊 Setup Summary:")
    print(f"✅ Completed: {success_count}/4 tasks")
    
    if success_count == 4:
        print("\n🎉 All bot configurations have been set up!")
        print("\n📋 Next Steps:")
        print("1. Update chat IDs in configuration files")
        print("2. Create and configure staging bot token:")
        print("   ./scripts/setup_staging_env.sh")
        print("3. Set up production Firestore:")
        print("   python scripts/setup_production_firestore.py")
        print("4. Create leadership bot for production")
        print("5. Test the configurations")
    else:
        print("\n⚠️  Some tasks may need manual completion")
        print("Please check the output above for any errors")

if __name__ == "__main__":
    main() 