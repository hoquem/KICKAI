#!/usr/bin/env python3
"""
Test script to verify Telegram bot with Gemini and CrewAI
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_bot_status():
    """Test if the bot is running and accessible."""
    try:
        from src.tools.telegram_tools import get_bot_info
        
        # Get bot info
        bot_info = get_bot_info()
        if bot_info:
            print("✅ Bot is accessible")
            print(f"   Name: {bot_info.get('name', 'Unknown')}")
            print(f"   Username: @{bot_info.get('username', 'Unknown')}")
            print(f"   ID: {bot_info.get('id', 'Unknown')}")
            return True
        else:
            print("❌ Bot not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        return False

def test_gemini_integration():
    """Test Gemini integration."""
    try:
        # Set production environment
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'
        
        from config import config
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        print(f"🤖 Testing Gemini integration...")
        print(f"   Model: {config.ai_config['model']}")
        
        # Create Gemini instance
        llm = ChatGoogleGenerativeAI(
            model=config.ai_config['model'],
            google_api_key=config.ai_config['api_key'],
            temperature=0.7,
            max_output_tokens=1000
        )
        
        # Test response
        response = llm.invoke("Say 'Gemini is working with Telegram bot!'")
        print(f"✅ Gemini Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini integration failed: {e}")
        return False

def test_crewai_agents():
    """Test CrewAI agents creation."""
    try:
        os.environ['RAILWAY_ENVIRONMENT'] = 'production'
        
        from src.agents import create_agents_for_team, create_llm
        
        print("🧠 Testing CrewAI agents...")
        
        # Create LLM
        llm = create_llm()
        
        # Create agents for BP Hatters team
        team_id = "0854829d-445c-4138-9fd3-4db562ea46ee"
        agents = create_agents_for_team(llm, team_id)
        
        print("✅ CrewAI agents created successfully")
        print(f"   Team Manager: {agents[0].role}")
        print(f"   Player Coordinator: {agents[1].role}")
        print(f"   Match Analyst: {agents[2].role}")
        print(f"   Communication Specialist: {agents[3].role}")
        
        return True
        
    except Exception as e:
        print(f"❌ CrewAI agents failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Telegram Bot with Gemini and CrewAI")
    print("=" * 55)
    
    # Test bot status
    print("\n🔍 Testing Bot Status...")
    bot_ok = test_bot_status()
    
    # Test Gemini integration
    print("\n🔍 Testing Gemini Integration...")
    gemini_ok = test_gemini_integration()
    
    # Test CrewAI agents
    print("\n🔍 Testing CrewAI Agents...")
    crewai_ok = test_crewai_agents()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Bot Status: {'✅ PASS' if bot_ok else '❌ FAIL'}")
    print(f"Gemini Integration: {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    print(f"CrewAI Agents: {'✅ PASS' if crewai_ok else '❌ FAIL'}")
    
    if bot_ok and gemini_ok and crewai_ok:
        print("\n🎉 All tests passed! Ready for Telegram testing.")
        print("\n📱 Telegram Testing Instructions:")
        print("=" * 40)
        print("1. Open your Telegram app")
        print("2. Find your bot: @BPHatters_bot")
        print("3. Send these test messages:")
        print("   - 'Hello' (basic response)")
        print("   - 'List all players' (database query)")
        print("   - 'Add a new player named John Smith' (AI command)")
        print("   - 'What should a team manager focus on?' (CrewAI analysis)")
        print("   - 'Schedule a match for Sunday' (fixture management)")
        print("   - 'Show team status' (team management)")
        print("\n💡 The bot should respond using Google Gemini AI!")
        print("💡 CrewAI agents will handle complex tasks!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
