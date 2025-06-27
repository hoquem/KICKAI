#!/usr/bin/env python3
"""
Test alternative Gemini models
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_alternative_models():
    """Test different Gemini models."""
    print("🧪 Testing Alternative Gemini Models")
    print("=" * 50)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found")
            return False
        
        print(f"✅ Using API key: {api_key[:15]}...")
        
        # Test different models
        models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]
        
        for model in models:
            print(f"\n🧪 Testing model: {model}")
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model,
                    verbose=False,
                    temperature=0.5,
                    google_api_key=api_key
                )
                
                response = llm.invoke("Say 'Hello from KICKAI!'")
                print(f"✅ {model} - Success!")
                print(f"📝 Response: {response.content}")
                return True
                
            except Exception as e:
                print(f"❌ {model} - Failed: {str(e)[:100]}...")
                continue
        
        print("\n❌ All models failed. Please check billing setup.")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_alternative_models() 