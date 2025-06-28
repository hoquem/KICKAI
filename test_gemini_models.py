#!/usr/bin/env python3
"""
Test to find available Gemini models
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_available_models():
    """List available Gemini models."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json()
            print("✅ Available Gemini models:")
            for model in models.get('models', []):
                print(f"   - {model['name']}")
                if 'description' in model:
                    print(f"     Description: {model['description']}")
                print()
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_specific_model(model_name):
    """Test a specific model."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    data = {
        "contents": [{
            "parts": [{
                "text": "Hello! Say 'Model test successful'"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Model {model_name} works!")
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"Response: {text}")
        else:
            print(f"❌ Model {model_name} failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception with {model_name}: {e}")

if __name__ == "__main__":
    print("�� Checking available Gemini models...")
    print("=" * 50)
    
    list_available_models()
    
    print("\n🧪 Testing specific models...")
    print("=" * 30)
    
    # Test common model names
    models_to_test = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-1.0-pro",
        "gemini-1.0-flash"
    ]
    
    for model in models_to_test:
        print(f"\nTesting {model}...")
        test_specific_model(model)
