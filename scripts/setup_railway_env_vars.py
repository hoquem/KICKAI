#!/usr/bin/env python3
"""
Interactive Railway Environment Variables Setup

This script helps set up environment variables for Railway services.
"""

import os
import subprocess
import sys
from typing import Dict, List

def run_command(command: str) -> str:
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error running command: {command}")
            print(f"Error: {result.stderr}")
            return ""
    except Exception as e:
        print(f"Exception running command: {e}")
        return ""

def get_input(prompt: str, required: bool = True, default: str = "") -> str:
    """Get user input with validation."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and required:
            print("❌ This field is required")
            continue
        
        return user_input

def set_railway_variable(service: str, key: str, value: str) -> bool:
    """Set a Railway environment variable."""
    command = f'railway variables --service {service} --set "{key}={value}"'
    print(f"Setting {key} for {service}...")
    
    result = run_command(command)
    if result or "error" not in result.lower():
        print(f"✅ Set {key} for {service}")
        return True
    else:
        print(f"❌ Failed to set {key} for {service}")
        return False

def setup_service_variables(service: str, environment: str):
    """Set up all variables for a service."""
    print(f"\n🔧 Setting up {service} ({environment})")
    print("=" * 50)
    
    # Get bot token
    bot_token = get_input(f"Enter Telegram Bot Token for {environment}")
    if bot_token:
        set_railway_variable(service, f"TELEGRAM_BOT_TOKEN_{environment.upper()}", bot_token)
        set_railway_variable(service, "TELEGRAM_BOT_TOKEN", bot_token)
    
    # Get Google AI API Key
    google_api_key = get_input(f"Enter Google AI API Key for {environment}")
    if google_api_key:
        set_railway_variable(service, f"GOOGLE_AI_API_KEY_{environment.upper()}", google_api_key)
        set_railway_variable(service, "GOOGLE_AI_API_KEY", google_api_key)
    
    # Get Firebase Credentials
    print(f"\n📄 Firebase Credentials for {environment}:")
    print("1. Paste the JSON content directly")
    print("2. Provide a path to the JSON file")
    print("3. Skip for now and set later")
    
    firebase_option = get_input("Choose option (1/2/3)", required=False, default="3")
    
    if firebase_option == "1":
        print("Paste the Firebase JSON content (press Ctrl+D when done):")
        firebase_creds = ""
        try:
            while True:
                line = input()
                firebase_creds += line + "\n"
        except EOFError:
            pass
        
        if firebase_creds.strip():
            set_railway_variable(service, f"FIREBASE_CREDENTIALS_{environment.upper()}", firebase_creds.strip())
            set_railway_variable(service, "FIREBASE_CREDENTIALS", firebase_creds.strip())
    
    elif firebase_option == "2":
        firebase_file = get_input("Path to Firebase JSON file")
        if os.path.exists(firebase_file):
            with open(firebase_file, 'r') as f:
                firebase_creds = f.read()
            set_railway_variable(service, f"FIREBASE_CREDENTIALS_{environment.upper()}", firebase_creds)
            set_railway_variable(service, "FIREBASE_CREDENTIALS", firebase_creds)
        else:
            print(f"❌ File not found: {firebase_file}")
    
    else:
        print(f"⚠️ Skipping Firebase credentials for {environment}")

def verify_service_variables(service: str):
    """Verify that variables are set correctly."""
    print(f"\n🔍 Verifying {service} variables...")
    
    result = run_command(f"railway variables --service {service}")
    if result:
        print("✅ Variables set successfully")
        print(result)
    else:
        print("❌ Failed to verify variables")

def main():
    """Main setup function."""
    print("🚀 Railway Environment Variables Setup")
    print("=" * 50)
    
    # Check if Railway CLI is available
    if not run_command("railway --version"):
        print("❌ Railway CLI not found. Please install it first.")
        return
    
    # Check current project
    project_status = run_command("railway status")
    if project_status:
        print(f"Current project: {project_status}")
    else:
        print("❌ No Railway project linked")
        return
    
    # Setup options
    print("\n📋 Setup Options:")
    print("1. Setup Testing Environment")
    print("2. Setup Staging Environment")
    print("3. Setup Production Environment")
    print("4. Setup All Environments")
    print("5. Verify All Variables")
    
    choice = get_input("Choose option (1-5)", required=False, default="1")
    
    if choice == "1":
        setup_service_variables("kickai-testing", "testing")
        verify_service_variables("kickai-testing")
    
    elif choice == "2":
        setup_service_variables("kickai-staging", "staging")
        verify_service_variables("kickai-staging")
    
    elif choice == "3":
        setup_service_variables("kickai-production", "production")
        verify_service_variables("kickai-production")
    
    elif choice == "4":
        setup_service_variables("kickai-testing", "testing")
        setup_service_variables("kickai-staging", "staging")
        setup_service_variables("kickai-production", "production")
        
        print("\n🔍 Verifying all services...")
        verify_service_variables("kickai-testing")
        verify_service_variables("kickai-staging")
        verify_service_variables("kickai-production")
    
    elif choice == "5":
        print("\n🔍 Verifying all services...")
        verify_service_variables("kickai-testing")
        verify_service_variables("kickai-staging")
        verify_service_variables("kickai-production")
    
    else:
        print("❌ Invalid choice")
        return
    
    print("\n✅ Setup completed!")
    print("\nNext steps:")
    print("1. Deploy services: railway up")
    print("2. Check logs: railway logs --service <service-name>")
    print("3. Test health: curl https://<service>.railway.app/health")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 