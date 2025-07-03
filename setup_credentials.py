#!/usr/bin/env python3
"""
Firebase Credentials Setup Script

This script helps you set up Firebase credentials for local development.
It will guide you through the process of placing your credentials file in the right location.
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("🔐 Firebase Credentials Setup")
    print("=" * 40)
    
    # Check if credentials directory exists
    credentials_dir = Path("credentials")
    if not credentials_dir.exists():
        print("❌ Credentials directory not found. Creating it...")
        credentials_dir.mkdir(exist_ok=True)
    
    # Check for existing credentials
    possible_credential_files = [
        "firebase_credentials_testing.json",
        "firebase_creds_testing.json", 
        "firebase-credentials-testing.json",
        "firebase_creds.json",
        "firebase_credentials.json"
    ]
    
    existing_files = []
    for filename in possible_credential_files:
        if Path(filename).exists():
            existing_files.append(filename)
        if Path(credentials_dir / filename).exists():
            existing_files.append(f"credentials/{filename}")
    
    if existing_files:
        print("✅ Found existing credential files:")
        for file in existing_files:
            print(f"   📄 {file}")
        
        choice = input("\n🤔 Would you like to move them to the credentials directory? (y/n): ").lower()
        if choice == 'y':
            for file in existing_files:
                if not file.startswith("credentials/"):
                    source = Path(file)
                    destination = credentials_dir / source.name
                    try:
                        shutil.move(str(source), str(destination))
                        print(f"   ✅ Moved {file} to credentials/{source.name}")
                    except Exception as e:
                        print(f"   ❌ Failed to move {file}: {e}")
    
    # Check if we have credentials in the right place
    target_file = credentials_dir / "firebase_credentials_testing.json"
    
    if target_file.exists():
        print(f"\n✅ Firebase credentials found at: {target_file}")
        print("   You're all set for local development!")
    else:
        print(f"\n❌ Firebase credentials not found at: {target_file}")
        print("\n📋 To set up your credentials:")
        print("1. Go to Firebase Console: https://console.firebase.google.com")
        print("2. Select your project")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Download the JSON file")
        print(f"6. Rename it to 'firebase_credentials_testing.json'")
        print(f"7. Place it in the 'credentials/' directory")
        print(f"\n📁 Expected location: {target_file}")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"\n✅ Environment file found: {env_file}")
        with open(env_file, 'r') as f:
            content = f.read()
            if "FIREBASE_CREDENTIALS_FILE" in content:
                print("   ✅ FIREBASE_CREDENTIALS_FILE is configured")
            else:
                print("   ⚠️  FIREBASE_CREDENTIALS_FILE not found in .env")
                print("   💡 Add this line to your .env file:")
                print("   FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials_testing.json")
    else:
        print(f"\n❌ Environment file not found: {env_file}")
        print("   💡 Create a .env file with:")
        print("   FIREBASE_CREDENTIALS_FILE=credentials/firebase_credentials_testing.json")
    
    print("\n🔒 Security Notes:")
    print("   • The 'credentials/' directory is gitignored")
    print("   • Never commit your actual Firebase credentials")
    print("   • Keep your credentials file secure")
    print("   • Use different credentials for different environments")

if __name__ == "__main__":
    main() 