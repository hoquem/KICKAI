#!/usr/bin/env python3
"""
Detailed test for Google Gemini API with better error reporting
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_detailed():
    """Test Google Gemini API with detailed error reporting."""
    print("🔍 Detailed Google Gemini API Test")
    print("=" * 50)
    
    # Check environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        return False
    
    print(f"✅ Found API key: {api_key[:15]}...")
    print(f"📏 Key length: {len(api_key)} characters")
    
    # Check key format
    if not api_key.startswith("AIza"):
        print("❌ API key doesn't start with 'AIza' - this might be incorrect")
        return False
    
    print("✅ API key format looks correct")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        print("\n🧪 Initializing LLM...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest",
            verbose=False,
            temperature=0.5,
            google_api_key=api_key
        )
        
        print("✅ LLM initialized successfully")
        
        print("\n🧪 Testing API call...")
        response = llm.invoke("Say 'Hello from KICKAI!' and add a football emoji.")
        
        print(f"✅ API call successful!")
        print(f"📝 Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error occurred: {type(e).__name__}")
        print(f"📝 Error message: {str(e)}")
        
        # Provide specific guidance based on error
        if "API key not valid" in str(e):
            print("\n🔧 Troubleshooting steps:")
            print("1. Enable billing: https://console.cloud.google.com/billing")
            print("2. Enable Gemini API: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
            print("3. Check API key permissions: https://console.cloud.google.com/apis/credentials")
            print("4. Make sure you're using the correct project")
        
        return False

if __name__ == "__main__":
    success = test_gemini_detailed()
    if success:
        print("\n🎉 Gemini API is working! Ready for CrewAI integration.")
    else:
        print("\n❌ Please follow the troubleshooting steps above.") 