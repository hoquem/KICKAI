#!/usr/bin/env python3
"""
Fix Firebase Credentials for Railway
This script reads Firebase credentials from local JSON files and sets them properly in Railway.
"""

import json
import subprocess
import sys
import os

def read_firebase_credentials(file_path):
    """Read Firebase credentials from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def set_railway_variable(service, key, value):
    """Set Railway environment variable."""
    try:
        # Escape the JSON string properly for shell
        escaped_value = json.dumps(value).replace('"', '\\"')
        cmd = f'railway variables --set "{key}={escaped_value}" --service {service}'
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Set {key} for {service}")
        else:
            print(f"❌ Failed to set {key} for {service}: {result.stderr}")
    except Exception as e:
        print(f"❌ Error setting {key} for {service}: {e}")

def main():
    """Main function to fix Firebase credentials."""
    print("🔧 Fixing Firebase Credentials for Railway")
    print("=" * 50)
    
    # Check for Firebase credential files
    firebase_files = {
        'testing': 'firebase_creds_testing.json',
        'staging': 'firebase_creds_staging.json', 
        'production': 'firebase_creds_production.json'
    }
    
    for environment, filename in firebase_files.items():
        print(f"\n📁 Processing {environment} environment...")
        
        if not os.path.exists(filename):
            print(f"⚠️  {filename} not found, skipping {environment}")
            continue
            
        # Read credentials
        creds = read_firebase_credentials(filename)
        if not creds:
            print(f"❌ Failed to read credentials from {filename}")
            continue
            
        # Set in Railway
        service_name = f"kickai-{environment}"
        set_railway_variable(service_name, "FIREBASE_CREDENTIALS", creds)
        
        # Also set project ID
        project_id = creds.get('project_id', '')
        if project_id:
            set_railway_variable(service_name, "FIREBASE_PROJECT_ID", project_id)
    
    print("\n✅ Firebase credentials fix completed!")
    print("\nNext steps:")
    print("1. Deploy the services again")
    print("2. Check the logs to verify Firebase connection")

if __name__ == "__main__":
    main() 