#!/usr/bin/env python3
"""
Test Google Gemini API connection
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_api():
    """Test Google Gemini API connection."""
    print("🔍 Testing Google Gemini API Connection")
    print("=" * 50)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            return False
        
        print(f"✅ Found GOOGLE_API_KEY: {api_key[:10]}...")
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest",
            verbose=True,
            temperature=0.5,
            google_api_key=api_key
        )
        
        print("✅ LLM initialized successfully")
        
        # Test a simple call
        print("\n🧪 Testing simple API call...")
        response = llm.invoke("Say 'Hello from KICKAI!' in a friendly way.")
        
        print(f"✅ API call successful!")
        print(f"📝 Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_google_api() 