#!/usr/bin/env python3
"""
Deploy with Firebase Credentials
This script copies Firebase credentials files to the correct location during Railway deployment.

# NOTE: This script is for local setup only. Do not use file-based credential loading at runtime.
# All runtime Firebase credential loading must use environment variables only.
"""

import json
import os
import shutil
import sys

def copy_firebase_credentials():
    """Copy Firebase credentials file to the correct location."""
    environment = os.getenv('ENVIRONMENT', 'testing')
    credentials_file = f"firebase-credentials-{environment}.json"
    target_path = f"/app/firebase-credentials-{environment}.json"
    
    print(f"🔧 Setting up Firebase credentials for {environment}")
    print(f"📁 Source: {credentials_file}")
    print(f"📁 Target: {target_path}")
    
    # Check if source file exists
    if not os.path.exists(credentials_file):
        print(f"❌ Source file {credentials_file} not found")
        return False
    
    try:
        # Copy the file to the target location
        shutil.copy2(credentials_file, target_path)
        print(f"✅ Successfully copied {credentials_file} to {target_path}")
        
        # Verify the file was copied correctly
        if os.path.exists(target_path):
            print(f"✅ Target file exists and is accessible")
            
            # Read and validate the JSON
            with open(target_path, 'r') as f:
                creds = json.load(f)
            
            if 'private_key' in creds and 'client_email' in creds:
                print(f"✅ Firebase credentials file is valid")
                return True
            else:
                print(f"❌ Firebase credentials file is missing required fields")
                return False
        else:
            print(f"❌ Target file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error copying Firebase credentials: {e}")
        return False

def main():
    """Main function to setup Firebase credentials for deployment."""
    print("🚀 Deploying with Firebase credentials")
    print("=" * 50)
    
    if copy_firebase_credentials():
        print("✅ Firebase credentials setup completed successfully")
        return 0
    else:
        print("❌ Firebase credentials setup failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 