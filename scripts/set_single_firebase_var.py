#!/usr/bin/env python3
"""
Set a single Firebase credentials variable in Railway.
This avoids the size limit issues by using base64 encoding.

# NOTE: This script is for local setup only. Do not use file-based credential loading at runtime.
# All runtime Firebase credential loading must use environment variables only.
"""

import os
import json
import base64
import subprocess
import sys

def set_single_firebase_variable(environment):
    """Set a single FIREBASE_CREDENTIALS variable using base64 encoding."""
    
    # Read credentials file
    creds_file = f"firebase-credentials-{environment}.json"
    
    if not os.path.exists(creds_file):
        print(f"❌ Credentials file not found: {creds_file}")
        return False
    
    try:
        with open(creds_file, 'r') as f:
            creds_json = f.read()
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False
    
    # Convert to base64
    creds_b64 = base64.b64encode(creds_json.encode('utf-8')).decode('utf-8')
    
    print(f"🔐 Setting single Firebase credentials variable for {environment}")
    print(f"📏 Original size: {len(creds_json)} characters")
    print(f"📏 Base64 size: {len(creds_b64)} characters")
    
    # Set the variable using Railway CLI
    try:
        cmd = [
            'railway', 'variables', 
            '--service', f'kickai-{environment}',
            '--set', f'FIREBASE_CREDENTIALS={creds_b64}'
        ]
        
        print(f"🔧 Running: {' '.join(cmd[:4])} --set FIREBASE_CREDENTIALS=...")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Successfully set FIREBASE_CREDENTIALS variable")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set variable: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python set_single_firebase_var.py <environment>")
        print("Environments: testing, staging, production")
        sys.exit(1)
    
    environment = sys.argv[1].lower()
    
    if environment not in ['testing', 'staging', 'production']:
        print("❌ Invalid environment. Use: testing, staging, or production")
        sys.exit(1)
    
    success = set_single_firebase_variable(environment)
    
    if success:
        print(f"\n🎉 Firebase credentials set successfully for {environment}!")
        print("🔧 Now update your Firebase client to use this variable:")
        print("   FIREBASE_CREDENTIALS (base64 encoded)")
    else:
        print(f"\n💥 Failed to set Firebase credentials for {environment}.")
        sys.exit(1)

if __name__ == "__main__":
    main() 