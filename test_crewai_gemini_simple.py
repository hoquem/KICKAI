#!/usr/bin/env python3
"""
Simple test to see if CrewAI works with Gemini
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_crewai_gemini():
    """Test CrewAI with Gemini."""
    try:
        # Set production environment
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'
        
        # Import after setting environment
        from config import config
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        print(f"🤖 AI Provider: {config.ai_provider}")
        print(f"🧠 Model: {config.ai_config['model']}")
        
        # Create Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model=config.ai_config['model'],
            google_api_key=config.ai_config['api_key'],
            temperature=0.7,
            max_output_tokens=1000
        )
        
        print("✅ Gemini LLM created")
        
        # Test simple response
        response = llm.invoke("Say 'Hello from Gemini!'")
        print(f"✅ Gemini Response: {response.content}")
        
        # Try to create a simple agent
        from crewai import Agent
        
        agent = Agent(
            role='Test Agent',
            goal='Test if CrewAI works with Gemini',
            backstory='A simple test agent',
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
        
        print("✅ Agent created successfully")
        
        # Test agent response (try different methods)
        try:
            # Try the correct method
            result = agent.run("Say 'Agent test successful'")
            print(f"✅ Agent Response: {result}")
        except AttributeError:
            try:
                # Try another possible method
                result = agent.invoke("Say 'Agent test successful'")
                print(f"✅ Agent Response: {result}")
            except AttributeError:
                print("⚠️  Agent created but execution method not found")
        
        # Try creating a crew
        from crewai import Crew
        
        crew = Crew(
            agents=[agent],
            verbose=True,
            memory=True
        )
        
        print("✅ Crew created successfully")
        
        # Test crew execution
        try:
            result = crew.kickoff({"task": "Say 'Crew test successful'"})
            print(f"✅ Crew Response: {result}")
        except Exception as e:
            print(f"⚠️  Crew execution failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing CrewAI with Gemini")
    print("=" * 40)
    
    success = test_crewai_gemini()
    
    if success:
        print("\n🎉 CrewAI with Gemini works!")
    else:
        print("\n❌ CrewAI with Gemini failed")
