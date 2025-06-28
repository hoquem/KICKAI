#!/usr/bin/env python3
"""
Test Google Gemini with CrewAI agents locally
This script tests the Google AI integration before Railway deployment
"""

import os
import sys
import logging
import importlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_gemini_connection():
    """Test basic Google Gemini connection."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Try different model names
        model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        
        for model_name in model_names:
            try:
                print(f"🔍 Trying model: {model_name}")
                
                # Create Gemini instance
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0.7,
                    max_output_tokens=1000
                )
                
                # Test simple response
                response = llm.invoke("Hello! Can you respond with 'Gemini is working!'?")
                print(f"✅ Gemini Response with {model_name}: {response.content}")
                
                return True
                
            except Exception as e:
                print(f"❌ Model {model_name} failed: {e}")
                continue
        
        raise Exception("All Gemini models failed")
        
    except Exception as e:
        logger.error(f"❌ Gemini connection failed: {e}")
        return False

def test_crewai_with_gemini():
    """Test CrewAI agents with Google Gemini."""
    try:
        # Temporarily set production environment
        original_env = os.getenv('RAILWAY_ENVIRONMENT')
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'
        
        # Reload config module to pick up new environment
        if 'config' in sys.modules:
            importlib.reload(sys.modules['config'])
        
        # Import config after setting environment
        from config import config
        
        # Validate configuration
        if not config.validate_config():
            raise ValueError("Configuration validation failed")
        
        print(f"🤖 Using AI Provider: {config.ai_provider}")
        print(f"🧠 Model: {config.ai_config['model']}")
        
        # Create LLM
        from src.agents import create_llm
        llm = create_llm()
        print("✅ LLM created successfully")
        
        # Create agents for BP Hatters team
        team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
        from src.agents import create_agents_for_team, create_crew_for_team
        
        agents = create_agents_for_team(llm, team_id)
        print("✅ CrewAI agents created successfully")
        
        # Create crew
        crew = create_crew_for_team(agents)
        print("✅ CrewAI crew created successfully")
        
        # Test with a simple task
        task_description = """
        Analyze the current team situation and provide a brief summary of what a football team manager should focus on.
        Keep the response under 100 words.
        """
        
        print(f"\n🎯 Testing CrewAI with Gemini...")
        print(f"Task: {task_description}")
        
        # Run the crew
        result = crew.kickoff({"task": task_description})
        
        print(f"\n✅ CrewAI Result:")
        print(f"{result}")
        
        # Restore original environment
        if original_env:
            os.environ['RAILWAY_ENVIRONMENT'] = original_env
        else:
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CrewAI with Gemini failed: {e}")
        # Restore original environment on error
        if original_env:
            os.environ['RAILWAY_ENVIRONMENT'] = original_env
        else:
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
        return False

def test_gemini_tools():
    """Test Gemini with our custom tools."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from src.tools.supabase_tools import PlayerTools
        
        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Create Gemini instance
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=1000
        )
        
        # Test with a tool
        team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"  # BP Hatters FC
        player_tools = PlayerTools(team_id)
        
        # Test tool functionality
        print("🔧 Testing Gemini with PlayerTools...")
        
        # Check available methods
        methods = [method for method in dir(player_tools) if not method.startswith('_')]
        print(f"Available methods: {methods}")
        
        # Test getting players using the _run method
        result = player_tools._run("get_all_players")
        
        print(f"✅ PlayerTools test: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Gemini with tools failed: {e}")
        return False

def test_hybrid_configuration():
    """Test that configuration switches correctly."""
    try:
        # Test development mode
        os.environ['RAILWAY_ENVIRONMENT'] = 'development'
        
        # Reload config module
        if 'config' in sys.modules:
            importlib.reload(sys.modules['config'])
        
        from config import config as dev_config
        print(f"🏠 Development Mode: {dev_config.ai_provider}")
        
        # Test production mode
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'
        
        # Reload config module
        if 'config' in sys.modules:
            importlib.reload(sys.modules['config'])
        
        from config import config as prod_config
        print(f"🚀 Production Mode: {prod_config.ai_provider}")
        
        # Verify they're different
        if dev_config.ai_provider != prod_config.ai_provider:
            print("✅ Configuration switching works correctly")
            return True
        else:
            print("❌ Configuration switching failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_simple_gemini():
    """Test simple Gemini without CrewAI."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        print(f"🔑 API Key: {api_key[:10]}...")
        
        # Create Gemini instance
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=1000
        )
        
        # Test simple response
        response = llm.invoke("Say 'Hello from Gemini!'")
        print(f"✅ Simple Gemini Response: {response.content}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Simple Gemini test failed: {e}")
        return False

def main():
    """Run all Gemini tests."""
    print("🧪 Testing Google Gemini Integration")
    print("=" * 50)
    
    tests = [
        ("Simple Gemini Test", test_simple_gemini),
        ("Basic Gemini Connection", test_gemini_connection),
        ("Hybrid Configuration", test_hybrid_configuration),
        ("Gemini with Tools", test_gemini_tools),
        ("CrewAI with Gemini", test_crewai_with_gemini),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini is ready for Railway deployment.")
        print("\n🚀 Next steps:")
        print("   1. Deploy to Railway")
        print("   2. Set RAILWAY_ENVIRONMENT=production")
        print("   3. Add GOOGLE_API_KEY to Railway environment")
        print("   4. Test with real users")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify GOOGLE_API_KEY is set correctly")
        print("   2. Check internet connection")
        print("   3. Verify Google AI API is enabled")
        print("   4. Check billing is set up for Google AI")

if __name__ == "__main__":
    main()
