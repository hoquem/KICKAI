#!/usr/bin/env python3
"""
Script to validate Google API key using Google AI SDK
"""

import os
import subprocess

def test_google_ai_import():
    """Test if Google AI packages are available"""
    try:
        import google.generativeai as genai
        return True, genai
    except ImportError:
        return False, None

def validate_google_api_key_sdk(api_key: str) -> bool:
    """Validate Google API key using Google AI SDK"""
    try:
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test with a simple model call - try different model versions
        try:
            # Try gemini-1.5-flash first (newer version)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello, this is a test.")
        except:
            try:
                # Try gemini-pro (older version)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Hello, this is a test.")
            except:
                # Try gemini-1.0-pro (alternative version)
                model = genai.GenerativeModel('gemini-1.0-pro')
                response = model.generate_content("Hello, this is a test.")
        
        if response and response.text:
            print(f"✅ API key works! Response: {response.text[:50]}...")
            return True
        else:
            print("❌ No response from API")
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
    print("🔍 Validating Google API key using Google AI SDK...")
    
    # Check if Google AI packages are available
    available, genai = test_google_ai_import()
    if not available:
        print("❌ Google AI packages not available. Installing...")
        subprocess.run(['pip', 'install', 'google-generativeai'])
        available, genai = test_google_ai_import()
        if not available:
            print("❌ Failed to install Google AI packages")
            return
    
    # Get current API key from Railway
    current_api_key = os.getenv('GOOGLE_API_KEY')
    if not current_api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    print(f"Current API key length: {len(current_api_key)} characters")
    print(f"Current API key starts with: {current_api_key[:10]}...")
    
    # Validate the current API key
    print("\n🔍 Testing current API key...")
    if validate_google_api_key_sdk(current_api_key):
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
    if validate_google_api_key_sdk(new_api_key):
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