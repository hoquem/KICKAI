#!/usr/bin/env python3
"""
Setup Firebase Credentials using Railway's Official Secrets Management
This script follows Railway's official recommendations for storing large sensitive data.
Railway recommends using their dashboard for secrets management rather than environment variables.
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
            print(f"✅ Set variable {key} for {service}")
            return True
        else:
            print(f"❌ Failed to set variable {key} for {service}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting variable {key} for {service}: {e}")
        return False

def setup_environment(environment: str, service: str, credentials_file: str):
    """Setup Firebase environment variables following Railway's recommendations."""
    print(f"\n🔥 Setting up Firebase for {environment} using Railway's recommended approach")
    print("=" * 70)
    
    # Read credentials
    creds = read_firebase_credentials(credentials_file)
    if not creds:
        print(f"❌ Failed to read credentials from {credentials_file}")
        return False
    
    success_count = 0
    total_count = 0
    
    # Set project ID as environment variable (not sensitive)
    if 'project_id' in creds:
        if set_railway_variable(service, 'FIREBASE_PROJECT_ID', str(creds['project_id'])):
            success_count += 1
        total_count += 1
    
    # Set client email as environment variable (not sensitive)
    if 'client_email' in creds:
        if set_railway_variable(service, 'FIREBASE_CLIENT_EMAIL', str(creds['client_email'])):
            success_count += 1
        total_count += 1
    
    # Set other fields as environment variables (not sensitive)
    optional_fields = {
        'private_key_id': 'FIREBASE_PRIVATE_KEY_ID',
        'client_id': 'FIREBASE_CLIENT_ID',
        'auth_uri': 'FIREBASE_AUTH_URI',
        'token_uri': 'FIREBASE_TOKEN_URI',
        'auth_provider_x509_cert_url': 'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
        'client_x509_cert_url': 'FIREBASE_CLIENT_X509_CERT_URL'
    }
    
    for json_key, env_key in optional_fields.items():
        if json_key in creds:
            if set_railway_variable(service, env_key, str(creds[json_key])):
                success_count += 1
            total_count += 1
    
    print(f"\n📊 Results for {environment}:")
    print(f"   ✅ Successfully set: {success_count}/{total_count} variables")
    
    if success_count == total_count:
        print(f"✅ All Firebase variables set for {environment}")
        return True
    else:
        print(f"⚠️ Some variables failed to set for {environment}")
        return False

def create_credentials_file(environment: str, credentials_file: str):
    """Create a credentials file for manual upload to Railway dashboard."""
    print(f"\n📁 Creating credentials file for {environment}")
    
    # Read credentials
    creds = read_firebase_credentials(credentials_file)
    if not creds:
        print(f"❌ Failed to read credentials from {credentials_file}")
        return None
    
    # Create output file
    output_file = f"firebase-credentials-{environment}.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(creds, f, indent=2)
        print(f"✅ Created credentials file: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Failed to create credentials file: {e}")
        return None

def main():
    """Main function to setup Firebase following Railway's recommendations."""
    print("🔧 Setting up Firebase using Railway's Official Secrets Management")
    print("=" * 80)
    print("Railway's official recommendation for large sensitive data:")
    print("1. Store non-sensitive data as environment variables")
    print("2. Store sensitive data (like private keys) through Railway dashboard")
    print("3. Use Railway's built-in secrets management for large files")
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
            
            # Create credentials file for manual upload
            create_credentials_file(environment, filename)
    
    print(f"\n🎯 Setup Summary:")
    print(f"   ✅ Successful: {', '.join(success_environments) if success_environments else 'None'}")
    print(f"   ❌ Failed: {', '.join(set(firebase_files.keys()) - set(success_environments)) if success_environments else ', '.join(firebase_files.keys())}")
    
    if success_environments:
        print(f"\n✅ Firebase setup completed following Railway's recommendations!")
        print(f"\n📋 Next steps (MANUAL REQUIRED):")
        print(f"1. Open Railway dashboard for each environment")
        print(f"2. Go to Variables tab")
        print(f"3. Add the following secrets manually:")
        for env in success_environments:
            print(f"   - For {env}: Add FIREBASE_CREDENTIALS_JSON with the content of firebase-credentials-{env}.json")
        print(f"\n📋 Alternative approach:")
        print(f"1. Use Railway's file upload feature in the dashboard")
        print(f"2. Upload firebase-credentials-{env}.json files")
        print(f"3. Set FIREBASE_CREDENTIALS_PATH to point to uploaded files")
        print(f"\n📋 Variables already set:")
        print(f"   📝 FIREBASE_PROJECT_ID")
        print(f"   📝 FIREBASE_CLIENT_EMAIL")
        print(f"   📝 Other non-sensitive fields")
        print(f"\n🔧 Manual steps required:")
        print(f"   - Add FIREBASE_CREDENTIALS_JSON secret in Railway dashboard")
        print(f"   - Or upload credentials files and set FIREBASE_CREDENTIALS_PATH")
    else:
        print(f"\n❌ No environments were successfully configured")
        print(f"Please check your Firebase credential files and try again")

if __name__ == "__main__":
    main() 