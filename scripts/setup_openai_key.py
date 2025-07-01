#!/usr/bin/env python3
"""
OpenAI API Key Setup Script
Securely sets up OpenAI API keys for all Railway environments
"""

import os
import subprocess
import getpass
import sys

def run_railway_command(command):
    """Run a Railway CLI command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def set_openai_key_for_service(service_name, api_key):
    """Set OpenAI API key for a specific Railway service"""
    print(f"🔧 Setting OpenAI API key for {service_name}...")
    
    success, stdout, stderr = run_railway_command(
        f'railway variables --service {service_name} --set OPENAI_API_KEY="{api_key}"'
    )
    
    if success:
        print(f"✅ Successfully set OpenAI API key for {service_name}")
        return True
    else:
        print(f"❌ Failed to set OpenAI API key for {service_name}")
        print(f"Error: {stderr}")
        return False

def verify_openai_key_for_service(service_name):
    """Verify that OpenAI API key is set for a service"""
    print(f"🔍 Verifying OpenAI API key for {service_name}...")
    
    success, stdout, stderr = run_railway_command(
        f'railway variables --service {service_name} | grep OPENAI_API_KEY'
    )
    
    if success and "OPENAI_API_KEY" in stdout:
        print(f"✅ OpenAI API key verified for {service_name}")
        return True
    else:
        print(f"❌ OpenAI API key not found for {service_name}")
        return False

def main():
    print("🤖 OpenAI API Key Setup")
    print("=" * 50)
    print("This script will set up OpenAI API keys for all Railway environments.")
    print()
    
    # Get API key from user
    print("Please provide your OpenAI API key:")
    print("(You can get it from https://platform.openai.com/api-keys)")
    print()
    
    # Try to get from environment first
    api_key = os.getenv('OPENAI_API_KEY')
    
    if api_key:
        print("📋 Found OpenAI API key in environment variable")
        use_env = input("Use environment variable? (y/n): ").lower().strip()
        if use_env != 'y':
            api_key = None
    
    if not api_key:
        # Get from user input
        api_key = getpass.getpass("Enter your OpenAI API key: ").strip()
        
        if not api_key:
            print("❌ No API key provided. Exiting.")
            sys.exit(1)
        
        if not api_key.startswith('sk-'):
            print("⚠️  Warning: API key doesn't start with 'sk-'. Are you sure this is correct?")
            confirm = input("Continue anyway? (y/n): ").lower().strip()
            if confirm != 'y':
                print("❌ Setup cancelled.")
                sys.exit(1)
    
    print()
    print("🚀 Setting up OpenAI API keys for all environments...")
    print()
    
    # Services to configure
    services = ['kickai-testing', 'kickai-staging', 'kickai-production']
    
    success_count = 0
    for service in services:
        if set_openai_key_for_service(service, api_key):
            success_count += 1
        print()
    
    print("🔍 Verifying setup...")
    print()
    
    verify_count = 0
    for service in services:
        if verify_openai_key_for_service(service):
            verify_count += 1
        print()
    
    print("=" * 50)
    print("📊 Setup Summary:")
    print(f"✅ Successfully configured: {success_count}/{len(services)} services")
    print(f"✅ Verified: {verify_count}/{len(services)} services")
    
    if success_count == len(services) and verify_count == len(services):
        print()
        print("🎉 All environments are now configured with OpenAI API keys!")
        print()
        print("Next steps:")
        print("1. Set up Telegram bot tokens for staging and production")
        print("2. Deploy an environment to test the setup")
        print("3. Configure Firestore collections")
    else:
        print()
        print("⚠️  Some services may not be properly configured.")
        print("Please check the Railway dashboard or run the verification again.")

if __name__ == "__main__":
    main() 