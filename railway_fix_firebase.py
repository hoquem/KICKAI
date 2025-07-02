#!/usr/bin/env python3
"""
Railway script to fix Firebase credentials with corrupted URLs
"""

import json
import os
import subprocess

def fix_firebase_credentials():
    """Fix Firebase credentials by ensuring all URLs have proper scheme"""
    
    # Get the Firebase credentials from environment
    credentials_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    
    if not credentials_json:
        print("❌ FIREBASE_CREDENTIALS_JSON not found in environment")
        return False
    
    try:
        # Parse the JSON
        credentials = json.loads(credentials_json)
        
        # Fix URLs in the credentials
        fixed = False
        
        # Fix token_uri if it exists and is corrupted
        if 'token_uri' in credentials:
            token_uri = credentials['token_uri']
            if token_uri and not token_uri.startswith('http'):
                credentials['token_uri'] = f"https://{token_uri}"
                fixed = True
                print(f"✅ Fixed token_uri: {token_uri} -> {credentials['token_uri']}")
        
        # Fix auth_uri if it exists and is corrupted
        if 'auth_uri' in credentials:
            auth_uri = credentials['auth_uri']
            if auth_uri and not auth_uri.startswith('http'):
                credentials['auth_uri'] = f"https://{auth_uri}"
                fixed = True
                print(f"✅ Fixed auth_uri: {auth_uri} -> {credentials['auth_uri']}")
        
        # Fix auth_provider_x509_cert_url if it exists and is corrupted
        if 'auth_provider_x509_cert_url' in credentials:
            cert_url = credentials['auth_provider_x509_cert_url']
            if cert_url and not cert_url.startswith('http'):
                credentials['auth_provider_x509_cert_url'] = f"https://{cert_url}"
                fixed = True
                print(f"✅ Fixed auth_provider_x509_cert_url: {cert_url} -> {credentials['auth_provider_x509_cert_url']}")
        
        # Fix client_x509_cert_url if it exists and is corrupted
        if 'client_x509_cert_url' in credentials:
            client_cert_url = credentials['client_x509_cert_url']
            if client_cert_url and not client_cert_url.startswith('http'):
                credentials['client_x509_cert_url'] = f"https://{client_cert_url}"
                fixed = True
                print(f"✅ Fixed client_x509_cert_url: {client_cert_url} -> {credentials['client_x509_cert_url']}")
        
        if fixed:
            # Convert back to JSON string
            fixed_credentials_json = json.dumps(credentials, indent=2)
            
            # Update Railway environment variable
            result = subprocess.run([
                'railway', 'variables', 'set', 
                'FIREBASE_CREDENTIALS_JSON', fixed_credentials_json
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Successfully updated FIREBASE_CREDENTIALS_JSON in Railway")
                return True
            else:
                print(f"❌ Failed to update Railway variable: {result.stderr}")
                return False
        else:
            print("ℹ️  No URL fixes needed - credentials look good")
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in FIREBASE_CREDENTIALS_JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error fixing Firebase credentials: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Firebase credentials...")
    success = fix_firebase_credentials()
    if success:
        print("✅ Firebase credentials fixed successfully!")
    else:
        print("❌ Failed to fix Firebase credentials") 