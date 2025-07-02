#!/usr/bin/env python3
"""
Script to validate Google API key and update Railway variables if needed
"""

import os
import requests
import subprocess
import json

def validate_google_api_key(api_key: str) -> bool:
    """Validate Google API key by making a test request to Gemini API"""
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "contents": [{
                "parts": [{
                    "text": "Hello, this is a test message."
                }]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ API key validation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating API key: {e}")
        return False

def update_railway_variable(variable_name: str, value: str) -> bool:
    """Update a Railway environment variable"""
    try:
        result = subprocess.run([
            'railway', 'variables', '--set', f"{variable_name}={value}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully updated {variable_name} in Railway")
            return True
        else:
            print(f"❌ Failed to update {variable_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating Railway variable: {e}")
        return False

def main():
    """Main function to validate and update Google API key"""
    print("🔍 Validating Google API key...")
    
    # Get current API key from Railway
    current_api_key = os.getenv('GOOGLE_API_KEY')
    if not current_api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    print(f"Current API key length: {len(current_api_key)} characters")
    print(f"Current API key starts with: {current_api_key[:10]}...")
    
    # Validate the current API key
    print("\n🔍 Testing current API key...")
    if validate_google_api_key(current_api_key):
        print("✅ Current Google API key is valid!")
        return
    else:
        print("❌ Current Google API key is invalid or expired")
    
    # Ask user for new API key
    print("\n🔧 Please provide a new Google API key:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Copy the API key (starts with 'AIza...')")
    
    new_api_key = input("\nEnter new Google API key: ").strip()
    
    if not new_api_key:
        print("❌ No API key provided")
        return
    
    if not new_api_key.startswith('AIza'):
        print("❌ Invalid API key format. Should start with 'AIza'")
        return
    
    # Validate the new API key
    print("\n🔍 Testing new API key...")
    if validate_google_api_key(new_api_key):
        print("✅ New Google API key is valid!")
        
        # Update Railway variable
        print("\n🔄 Updating Railway environment variable...")
        if update_railway_variable('GOOGLE_API_KEY', new_api_key):
            print("✅ Google API key updated successfully!")
            print("🔄 Railway will redeploy automatically with the new key")
        else:
            print("❌ Failed to update Railway variable")
    else:
        print("❌ New API key is invalid. Please check the key and try again")

if __name__ == "__main__":
    main() 