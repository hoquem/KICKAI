#!/usr/bin/env python3
"""
Test script to verify Railway-compatible imports
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all critical imports for Railway deployment."""
    
    print("🧪 Testing Railway-compatible imports...")
    print("=" * 50)
    
    # Test 1: Basic Python packages
    print("\n1. Testing basic packages...")
    try:
        import requests
        import json
        print("✅ Basic packages imported successfully")
    except ImportError as e:
        print(f"❌ Basic package import failed: {e}")
        return False
    
    # Test 2: Firebase
    print("\n2. Testing Firebase...")
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        print("✅ Firebase imported successfully")
    except ImportError as e:
        print(f"❌ Firebase import failed: {e}")
        return False
    
    # Test 3: Telegram
    print("\n3. Testing Telegram...")
    try:
        from telegram.ext import Application
        print("✅ Telegram imported successfully")
    except ImportError as e:
        print(f"❌ Telegram import failed: {e}")
        return False
    
    # Test 4: LangChain core
    print("\n4. Testing LangChain core...")
    try:
        import langchain
        import langchain_community
        import langchain_core
        print("✅ LangChain core imported successfully")
    except ImportError as e:
        print(f"❌ LangChain core import failed: {e}")
        return False
    
    # Test 5: Google AI (primary)
    print("\n5. Testing langchain_google_genai...")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai imported successfully")
        return True
    except ImportError as e:
        print(f"⚠️ langchain_google_genai import failed: {e}")
        
        # Test 6: Google AI (fallback)
        print("\n6. Testing google-generativeai fallback...")
        try:
            import google.generativeai as genai
            print("✅ google-generativeai fallback imported successfully")
            return True
        except ImportError as e:
            print(f"❌ google-generativeai fallback also failed: {e}")
            return False
    
    return True

def test_railway_environment():
    """Test if we're in a Railway-like environment."""
    print("\n🔍 Environment Analysis:")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Executable: {sys.executable}")
    
    # Check for Railway environment variables
    railway_vars = ['RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_ID', 'PORT']
    for var in railway_vars:
        value = os.getenv(var)
        print(f"{var}: {'✅ Set' if value else '❌ Not set'}")

if __name__ == "__main__":
    print("🚀 Railway Import Compatibility Test")
    print("=" * 50)
    
    # Test environment
    test_railway_environment()
    
    # Test imports
    success = test_imports()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All imports successful! Ready for Railway deployment.")
    else:
        print("❌ Some imports failed. Check requirements.txt and dependencies.")
    
    print("\n📋 Next steps:")
    print("1. If all tests pass, deploy to Railway")
    print("2. Monitor Railway build logs for any issues")
    print("3. Check that the fallback system works in production") 