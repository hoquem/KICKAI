#!/usr/bin/env python3
"""
Simple test for Google Gemini API
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini():
    """Test Google Gemini API with a simple prompt."""
    print("🧪 Testing Google Gemini API")
    print("=" * 40)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            return False
        
        print(f"✅ Found API key: {api_key[:15]}...")
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest",
            verbose=False,
            temperature=0.5,
            google_api_key=api_key
        )
        
        print("✅ LLM initialized successfully")
        
        # Test simple call
        print("\n🧪 Testing API call...")
        response = llm.invoke("Say 'Hello from KICKAI!' and add a football emoji.")
        
        print(f"✅ API call successful!")
        print(f"📝 Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini()
    if success:
        print("\n🎉 Gemini API is working! Ready for CrewAI integration.")
    else:
        print("\n❌ Please check your API key and try again.") 