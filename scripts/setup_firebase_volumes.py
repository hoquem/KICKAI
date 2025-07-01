#!/usr/bin/env python3
"""
Setup Firebase Credentials using Railway Volumes
This script uses Railway volumes to store Firebase credentials files.
This is the official Railway solution for storing large sensitive data like private keys.
"""

import json
import subprocess
import sys
import os
import tempfile
from typing import Dict, Optional

def read_firebase_credentials(file_path: str) -> Optional[Dict]:
    """Read Firebase credentials from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def create_volume(service: str, volume_name: str) -> bool:
    """Create a Railway volume."""
    try:
        cmd = f'railway volume add {volume_name} --service {service}'
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created volume {volume_name} for {service}")
            return True
        else:
            print(f"❌ Failed to create volume {volume_name} for {service}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating volume {volume_name} for {service}: {e}")
        return False

def list_volumes(service: str) -> list:
    """List volumes for a service."""
    try:
        cmd = f'railway volume list --service {service}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        else:
            print(f"❌ Failed to list volumes for {service}: {result.stderr}")
            return []
    except Exception as e:
        print(f"❌ Error listing volumes for {service}: {e}")
        return []

def setup_environment(environment: str, service: str, credentials_file: str):
    """Setup Firebase credentials using Railway volumes."""
    print(f"\n🔥 Setting up Firebase volumes for {environment}")
    print("=" * 60)
    
    # Read credentials
    creds = read_firebase_credentials(credentials_file)
    if not creds:
        print(f"❌ Failed to read credentials from {credentials_file}")
        return False
    
    # Create volume name
    volume_name = f"firebase-creds-{environment}"
    
    # Check if volume already exists
    existing_volumes = list_volumes(service)
    volume_exists = any(volume_name in volume for volume in existing_volumes)
    
    if volume_exists:
        print(f"✅ Volume {volume_name} already exists for {service}")
    else:
        # Create volume
        if not create_volume(service, volume_name):
            print(f"❌ Failed to create volume for {environment}")
            return False
    
    # Set environment variables for volume path
    success_count = 0
    total_count = 0
    
    # Set project ID as environment variable
    if 'project_id' in creds:
        if set_railway_variable(service, 'FIREBASE_PROJECT_ID', str(creds['project_id'])):
            success_count += 1
        total_count += 1
    
    # Set client email as environment variable
    if 'client_email' in creds:
        if set_railway_variable(service, 'FIREBASE_CLIENT_EMAIL', str(creds['client_email'])):
            success_count += 1
        total_count += 1
    
    # Set volume path as environment variable
    volume_path = f"/app/volumes/{volume_name}/firebase-credentials.json"
    if set_railway_variable(service, 'FIREBASE_CREDENTIALS_PATH', volume_path):
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
    print(f"   ✅ Successfully set: {success_count}/{total_count} variables")
    print(f"   📁 Volume: {volume_name}")
    print(f"   📂 Credentials path: {volume_path}")
    
    if success_count == total_count:
        print(f"✅ All Firebase variables set for {environment}")
        return True
    else:
        print(f"⚠️ Some variables failed to set for {environment}")
        return False

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

def create_credentials_file(environment: str, credentials_file: str):
    """Create a credentials file that will be uploaded to the volume."""
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
    """Main function to setup Firebase volumes."""
    print("🔧 Setting up Firebase Credentials using Railway Volumes")
    print("=" * 70)
    print("This script uses Railway volumes to store Firebase credentials files.")
    print("This is the official Railway solution for storing large sensitive data.")
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
        print(f"\n✅ Firebase volumes setup completed!")
        print(f"\n📋 Next steps:")
        print(f"1. Upload credentials files to Railway volumes:")
        for env in success_environments:
            print(f"   - Upload firebase-credentials-{env}.json to volume firebase-creds-{env}")
        print(f"2. Update the Firebase client to use volume paths")
        print(f"3. Deploy the services again")
        print(f"4. Check the logs to verify Firebase connection")
        print(f"\n📋 Variables set for each environment:")
        print(f"   📂 FIREBASE_CREDENTIALS_PATH (volume path)")
        print(f"   📝 FIREBASE_PROJECT_ID")
        print(f"   📝 FIREBASE_CLIENT_EMAIL")
        print(f"   📝 Other fields")
        print(f"\n🔧 Manual upload required:")
        print(f"   Use Railway dashboard to upload credentials files to volumes")
        print(f"   Or use Railway CLI to copy files to volumes")
    else:
        print(f"\n❌ No environments were successfully configured")
        print(f"Please check your Firebase credential files and try again")

if __name__ == "__main__":
    main() 