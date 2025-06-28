#!/usr/bin/env python3
"""
Test script to demonstrate hybrid configuration
Shows how KICKAI switches between Ollama (local) and Google AI (production)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import config

def test_configuration():
    """Test the hybrid configuration system."""
    print("🔄 KICKAI Hybrid Configuration Test")
    print("=" * 50)
    
    # Test environment detection
    print(f"🌍 Environment: {config.environment}")
    print(f"🏭 Production Mode: {config.is_production}")
    print()
    
    # Test AI provider selection
    print(f"🤖 AI Provider: {config.ai_provider}")
    ai_config = config.ai_config
    print(f"   Model: {ai_config['model']}")
    print(f"   Base URL: {ai_config['base_url']}")
    print()
    
    # Test database configuration
    db_config = config.database_config
    print(f"🗄️ Database Type: {db_config['type']}")
    print(f"   URL: {db_config['url'][:50]}..." if db_config['url'] else "   URL: Not set")
    print(f"   Key: {'Set' if db_config['key'] else 'Not set'}")
    print()
    
    # Test configuration validation
    print("🔍 Validating Configuration...")
    is_valid = config.validate_config()
    print(f"✅ Configuration Valid: {is_valid}")
    print()
    
    # Test LLM configuration
    print("🧠 LLM Configuration:")
    llm_config = config.get_llm_config()
    for key, value in llm_config.items():
        if key == 'api_key' and value:
            print(f"   {key}: {'Set' if value else 'Not set'}")
        else:
            print(f"   {key}: {value}")
    print()
    
    # Show usage recommendations
    print("💡 Usage Recommendations:")
    if config.is_production:
        print("   🚀 Production Mode: Using Google AI")
        print("   📊 Monitor usage in Google AI Console")
        print("   💰 Set up cost alerts")
        print("   🔒 Environment variables are encrypted")
    else:
        print("   🏠 Development Mode: Using Ollama")
        print("   🆓 No API costs")
        print("   🔒 All data stays local")
        print("   ⚡ Fast local processing")
    
    print()
    print("🎯 Next Steps:")
    if config.is_production:
        print("   1. Deploy to Railway")
        print("   2. Test with real users")
        print("   3. Monitor performance")
    else:
        print("   1. Start Ollama: ollama serve")
        print("   2. Run bot: python run_telegram_bot.py")
        print("   3. Test AI commands")

if __name__ == "__main__":
    test_configuration() 