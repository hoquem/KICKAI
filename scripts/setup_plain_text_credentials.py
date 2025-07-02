#!/usr/bin/env python3
"""
Simple script to set up Firebase credentials as plain text JSON in Railway.
This avoids all base64 encoding issues.
"""

import os
import json
import subprocess
import sys

def main():
    print("🔧 Setting up Firebase Credentials as Plain Text JSON")
    print("=" * 60)
    print("This will set FIREBASE_CREDENTIALS_JSON in Railway")
    print("No base64 encoding - just plain text JSON")
    print()
    
    # Get credentials file path
    credentials_file = input("Enter path to your Firebase credentials JSON file: ").strip()
    
    if not os.path.exists(credentials_file):
        print(f"❌ File not found: {credentials_file}")
        sys.exit(1)
    
    # Read and validate JSON
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        # Convert to compact JSON string
        creds_json = json.dumps(creds, separators=(',', ':'))
        
        print(f"✅ Loaded credentials for project: {creds.get('project_id', 'Unknown')}")
        print(f"📏 JSON size: {len(creds_json)} characters")
        print()
        
        # Set in Railway
        environment = input("Enter Railway environment (production/staging/testing): ").strip()
        
        # Use the correct Railway CLI syntax
        cmd = f'railway variables --set "FIREBASE_CREDENTIALS_JSON={creds_json}" --environment {environment}'
        
        print(f"🔄 Setting FIREBASE_CREDENTIALS_JSON for {environment}...")
        print(f"Command: {cmd[:100]}...")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully set FIREBASE_CREDENTIALS_JSON")
            
            # Also set project ID
            project_id = creds.get('project_id', '')
            if project_id:
                project_cmd = f'railway variables --set "FIREBASE_PROJECT_ID={project_id}" --environment {environment}'
                subprocess.run(project_cmd, shell=True)
                print("✅ Also set FIREBASE_PROJECT_ID")
            
            print(f"\n🎉 Firebase credentials set up successfully for {environment}!")
            print("The app will now use plain text JSON instead of base64 encoding.")
            
        else:
            print(f"❌ Failed to set credentials: {result.stderr}")
            sys.exit(1)
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
