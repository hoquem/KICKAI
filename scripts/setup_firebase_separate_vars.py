#!/usr/bin/env python3
"""
Setup Firebase Separate Environment Variables for Railway
This script extracts Firebase credentials from JSON files and sets them as separate environment variables.
This avoids Railway's environment variable size limits and JSON truncation issues.
"""

import json
import subprocess
import sys
import os
from typing import Dict, Optional

def read_firebase_credentials(file_path: str) -> Optional[Dict]:
    """Read Firebase credentials from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def set_railway_variable(service: str, key: str, value: str) -> bool:
    """Set Railway environment variable."""
    try:
        # Escape the value properly for shell
        escaped_value = value.replace('"', '\\"').replace("'", "\\'")
        cmd = f'railway variables --set "{key}={escaped_value}" --service {service}'
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Set {key} for {service}")
            return True
        else:
            print(f"❌ Failed to set {key} for {service}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting {key} for {service}: {e}")
        return False

def extract_firebase_variables(creds: Dict) -> Dict[str, str]:
    """Extract Firebase credentials into separate variables."""
    variables = {}
    
    # Required fields
    required_fields = {
        'project_id': 'FIREBASE_PROJECT_ID',
        'private_key': 'FIREBASE_PRIVATE_KEY',
        'client_email': 'FIREBASE_CLIENT_EMAIL'
    }
    
    # Optional fields
    optional_fields = {
        'private_key_id': 'FIREBASE_PRIVATE_KEY_ID',
        'client_id': 'FIREBASE_CLIENT_ID',
        'auth_uri': 'FIREBASE_AUTH_URI',
        'token_uri': 'FIREBASE_TOKEN_URI',
        'auth_provider_x509_cert_url': 'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
        'client_x509_cert_url': 'FIREBASE_CLIENT_X509_CERT_URL'
    }
    
    # Extract required fields
    for json_key, env_key in required_fields.items():
        if json_key in creds:
            variables[env_key] = str(creds[json_key])
        else:
            print(f"⚠️ Missing required field: {json_key}")
    
    # Extract optional fields
    for json_key, env_key in optional_fields.items():
        if json_key in creds:
            variables[env_key] = str(creds[json_key])
    
    return variables

def setup_environment(environment: str, service: str, credentials_file: str):
    """Setup Firebase environment variables for a specific environment."""
    print(f"\n🔥 Setting up Firebase separate variables for {environment}")
    print("=" * 60)
    
    # Read credentials
    creds = read_firebase_credentials(credentials_file)
    if not creds:
        print(f"❌ Failed to read credentials from {credentials_file}")
        return False
    
    # Extract variables
    variables = extract_firebase_variables(creds)
    
    if not variables:
        print("❌ No variables extracted from credentials")
        return False
    
    # Set variables in Railway
    success_count = 0
    total_count = len(variables)
    
    for key, value in variables.items():
        if set_railway_variable(service, key, value):
            success_count += 1
    
    print(f"\n📊 Results for {environment}:")
    print(f"   ✅ Successfully set: {success_count}/{total_count} variables")
    
    if success_count == total_count:
        print(f"✅ All Firebase variables set for {environment}")
        return True
    else:
        print(f"⚠️ Some variables failed to set for {environment}")
        return False

def main():
    """Main function to setup Firebase separate variables."""
    print("🔧 Setting up Firebase Separate Environment Variables for Railway")
    print("=" * 70)
    print("This script extracts Firebase credentials from JSON files and sets them")
    print("as separate environment variables to avoid Railway size limits.")
    print()
    
    # Check for Firebase credential files
    firebase_files = {
        'testing': 'firebase_creds_testing.json',
        'staging': 'firebase_creds_staging.json', 
        'production': 'firebase_creds_production.json'
    }
    
    success_environments = []
    
    for environment, filename in firebase_files.items():
        print(f"\n📁 Processing {environment} environment...")
        
        if not os.path.exists(filename):
            print(f"⚠️  {filename} not found, skipping {environment}")
            continue
            
        service_name = f"kickai-{environment}"
        
        if setup_environment(environment, service_name, filename):
            success_environments.append(environment)
    
    print(f"\n🎯 Setup Summary:")
    print(f"   ✅ Successful: {', '.join(success_environments) if success_environments else 'None'}")
    print(f"   ❌ Failed: {', '.join(set(firebase_files.keys()) - set(success_environments)) if success_environments else ', '.join(firebase_files.keys())}")
    
    if success_environments:
        print(f"\n✅ Firebase separate variables setup completed!")
        print(f"\nNext steps:")
        print(f"1. Deploy the services again")
        print(f"2. Check the logs to verify Firebase connection")
        print(f"3. The system will now use separate environment variables instead of JSON")
        print(f"\n📋 Variables set for each environment:")
        print(f"   - FIREBASE_PROJECT_ID")
        print(f"   - FIREBASE_PRIVATE_KEY")
        print(f"   - FIREBASE_CLIENT_EMAIL")
        print(f"   - FIREBASE_PRIVATE_KEY_ID (optional)")
        print(f"   - FIREBASE_CLIENT_ID (optional)")
        print(f"   - FIREBASE_AUTH_URI (optional)")
        print(f"   - FIREBASE_TOKEN_URI (optional)")
        print(f"   - FIREBASE_AUTH_PROVIDER_X509_CERT_URL (optional)")
        print(f"   - FIREBASE_CLIENT_X509_CERT_URL (optional)")
    else:
        print(f"\n❌ No environments were successfully configured")
        print(f"Please check your Firebase credential files and try again")

if __name__ == "__main__":
    main() 