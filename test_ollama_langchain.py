#!/usr/bin/env python3
"""
Test Ollama with LangChain for CrewAI integration
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_ollama_langchain():
    """Test Ollama with LangChain."""
    print("🤖 Testing Ollama with LangChain")
    print("=" * 50)
    
    try:
        from langchain_ollama import OllamaLLM
        
        # Initialize Ollama LLM
        print("🧪 Initializing Ollama LLM...")
        llm = OllamaLLM(
            model="llama3.1:8b-instruct-q4_0",
            temperature=0.5
        )
        
        print("✅ LLM initialized successfully")
        
        # Test simple call
        print("\n🧪 Testing LLM call...")
        response = llm.invoke("Say 'Hello from KICKAI!' and add a football emoji.")
        
        print(f"✅ LLM call successful!")
        print(f"📝 Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ollama_langchain() 