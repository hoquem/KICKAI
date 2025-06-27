#!/usr/bin/env python3
"""
Test Ollama integration for KICKAI
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_ollama():
    """Test Ollama integration."""
    print("🤖 Testing Ollama Integration")
    print("=" * 40)
    
    try:
        import ollama
        
        # Test basic connection
        print("🧪 Testing Ollama connection...")
        response = ollama.chat(model='llama3.1:8b', messages=[
            {
                'role': 'user',
                'content': 'Say "Hello from KICKAI!" and add a football emoji.'
            }
        ])
        
        print(f"✅ Ollama connection successful!")
        print(f"📝 Response: {response['message']['content']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_ollama() 