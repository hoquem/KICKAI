#!/usr/bin/env python3
"""
Setup Firebase Secrets for Railway
This script uses Railway secrets for Firebase credentials to avoid environment variable size limits.
Railway secrets are designed for large sensitive data like private keys.
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

def set_railway_secret(service: str, key: str, value: str) -> bool:
    """Set Railway secret."""
    try:
        # Create a temporary file with the secret value
        temp_file = f"/tmp/{key}_{service}.tmp"
        with open(temp_file, 'w') as f:
            f.write(value)
        
        # Use Railway secrets command
        cmd = f'railway secrets set {key} --file {temp_file} --service {service}'
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass
        
        if result.returncode == 0:
            print(f"✅ Set secret {key} for {service}")
            return True
        else:
            print(f"❌ Failed to set secret {key} for {service}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting secret {key} for {service}: {e}")
        return False

def set_railway_variable(service: str, key: str, value: str) -> bool:
    """Set Railway environment variable for non-sensitive data."""
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
    """Setup Firebase secrets and variables for a specific environment."""
    print(f"\n🔥 Setting up Firebase secrets for {environment}")
    print("=" * 60)
    
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
    
    # Set private key as secret (sensitive and large)
    if 'private_key' in creds:
        if set_railway_secret(service, 'FIREBASE_PRIVATE_KEY', str(creds['private_key'])):
            success_count += 1
        total_count += 1
    
    # Set client email as environment variable (not sensitive)
    if 'client_email' in creds:
        if set_railway_variable(service, 'FIREBASE_CLIENT_EMAIL', str(creds['client_email'])):
            success_count += 1
        total_count += 1
    
    # Set other fields as environment variables
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
    print(f"   ✅ Successfully set: {success_count}/{total_count} variables/secrets")
    
    if success_count == total_count:
        print(f"✅ All Firebase variables/secrets set for {environment}")
        return True
    else:
        print(f"⚠️ Some variables/secrets failed to set for {environment}")
        return False

def main():
    """Main function to setup Firebase secrets."""
    print("🔧 Setting up Firebase Secrets for Railway")
    print("=" * 60)
    print("This script uses Railway secrets for sensitive data like private keys")
    print("to avoid environment variable size limits.")
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
        print(f"\n✅ Firebase secrets setup completed!")
        print(f"\nNext steps:")
        print(f"1. Update the Firebase client to use secrets")
        print(f"2. Deploy the services again")
        print(f"3. Check the logs to verify Firebase connection")
        print(f"\n📋 Variables/Secrets set for each environment:")
        print(f"   🔐 FIREBASE_PRIVATE_KEY (as secret)")
        print(f"   📝 FIREBASE_PROJECT_ID (as variable)")
        print(f"   📝 FIREBASE_CLIENT_EMAIL (as variable)")
        print(f"   📝 Other fields (as variables)")
    else:
        print(f"\n❌ No environments were successfully configured")
        print(f"Please check your Firebase credential files and try again")

if __name__ == "__main__":
    main() 