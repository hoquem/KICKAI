#!/usr/bin/env python3
"""
Add Mock Data to Railway Testing Environment

This script adds realistic test data to the KICKAI Railway testing environment.
It uses the Railway CLI to trigger the mock data generation in the deployed environment.
"""

import subprocess
import sys
import os
import time
import json

def check_railway_cli():
    """Check if Railway CLI is installed and configured."""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
        else:
            print("❌ Railway CLI is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI is not installed")
        print("📝 Install it with: npm install -g @railway/cli")
        return False

def list_railway_services():
    """List available Railway services."""
    try:
        result = subprocess.run(['railway', 'service', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("🚂 Available Railway services:")
            print(result.stdout)
            return result.stdout
        else:
            print("❌ Failed to list Railway services")
            return None
    except Exception as e:
        print(f"❌ Error listing services: {e}")
        return None

def select_testing_service():
    """Select the testing service."""
    try:
        # Try to select the testing service
        result = subprocess.run(['railway', 'service', 'select', 'kickai-testing'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Selected kickai-testing service")
            return True
        else:
            print("⚠️  Could not select kickai-testing service, trying to list available services...")
            list_railway_services()
            return False
    except Exception as e:
        print(f"❌ Error selecting service: {e}")
        return False

def trigger_mock_data_generation():
    """Trigger mock data generation in the Railway environment."""
    try:
        print("🚀 Triggering mock data generation in Railway...")
        
        # Create a simple script to run in Railway
        script_content = """
import os
import sys
sys.path.insert(0, '/app/src')

# Set environment to testing
os.environ['ENVIRONMENT'] = 'testing'

# Import and run the mock data generator
from generate_mock_data import MockDataGenerator
import asyncio

async def main():
    generator = MockDataGenerator()
    await generator.generate_all_data()

if __name__ == "__main__":
    asyncio.run(main())
"""
        
        # Write the script to a temporary file
        with open('railway_mock_data.py', 'w') as f:
            f.write(script_content)
        
        # Run the script in Railway
        result = subprocess.run(['railway', 'run', 'python', 'railway_mock_data.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Mock data generation completed successfully!")
            print("📊 Output:")
            print(result.stdout)
        else:
            print("❌ Mock data generation failed")
            print("Error:")
            print(result.stderr)
        
        # Clean up
        os.remove('railway_mock_data.py')
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error triggering mock data generation: {e}")
        return False

def check_railway_status():
    """Check the status of Railway services."""
    try:
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("📊 Railway Status:")
            print(result.stdout)
            return True
        else:
            print("❌ Failed to get Railway status")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def main():
    """Main function."""
    print("🚀 KICKAI Mock Data Generator for Railway")
    print("=" * 50)
    
    # Check Railway CLI
    if not check_railway_cli():
        print("\n📝 Please install and configure Railway CLI first:")
        print("   1. npm install -g @railway/cli")
        print("   2. railway login")
        print("   3. railway link")
        return
    
    # Check Railway status
    print("\n🔍 Checking Railway status...")
    check_railway_status()
    
    # Select testing service
    print("\n🎯 Selecting testing service...")
    if not select_testing_service():
        print("❌ Could not select testing service")
        print("📝 Please manually select the correct service:")
        print("   railway service select <service-name>")
        return
    
    # Trigger mock data generation
    print("\n🚀 Starting mock data generation...")
    if trigger_mock_data_generation():
        print("\n✅ Mock data has been added to the Railway testing environment!")
        print("\n📊 You can now test the bot with realistic data:")
        print("   - Teams with human-readable IDs (BH, LL, ME, etc.)")
        print("   - Players with proper registration data")
        print("   - Matches with scheduling information")
        print("   - Team members and bot mappings")
    else:
        print("\n❌ Failed to add mock data to Railway")
        print("📝 You can still test with the sample data generator:")
        print("   python generate_mock_data_simple.py")

if __name__ == "__main__":
    main() 