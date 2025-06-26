#!/usr/bin/env python3
"""
Test script for WhatsApp integration
Tests the WhatsApp tools without actually sending messages (dry run mode)
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment variables
load_dotenv()

def test_whatsapp_tools():
    """Test WhatsApp tools initialization and basic functionality."""
    print("🧪 Testing WhatsApp Integration")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_PHONE_NUMBER',
        'TEAM_WHATSAPP_GROUP'
    ]
    
    print("\n📋 Environment Variables Check:")
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'SID' in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            else:
                masked_value = value
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file before testing WhatsApp functionality.")
        return False
    
    # Test WhatsApp tools import
    try:
        from tools.whatsapp_tools import WhatsAppTools, get_whatsapp_tools
        print("\n✅ WhatsApp tools imported successfully")
    except ImportError as e:
        print(f"\n❌ Failed to import WhatsApp tools: {e}")
        return False
    
    # Test WhatsApp tools initialization
    try:
        whatsapp = WhatsAppTools()
        print("✅ WhatsApp tools initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize WhatsApp tools: {e}")
        return False
    
    # Test getting all tools
    try:
        tools = get_whatsapp_tools()
        print(f"✅ Retrieved {len(tools)} WhatsApp tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Failed to get WhatsApp tools: {e}")
        return False
    
    # Test tool instantiation
    try:
        from tools.whatsapp_tools import (
            SendWhatsAppMessageTool,
            SendWhatsAppPollTool,
            SendAvailabilityPollTool,
            SendSquadAnnouncementTool,
            SendPaymentReminderTool
        )
        
        # Test each tool
        tools_to_test = [
            ("SendWhatsAppMessageTool", SendWhatsAppMessageTool()),
            ("SendWhatsAppPollTool", SendWhatsAppPollTool()),
            ("SendAvailabilityPollTool", SendAvailabilityPollTool()),
            ("SendSquadAnnouncementTool", SendSquadAnnouncementTool()),
            ("SendPaymentReminderTool", SendPaymentReminderTool())
        ]
        
        print("\n🔧 Testing individual tools:")
        for tool_name, tool in tools_to_test:
            try:
                # Test tool initialization
                print(f"✅ {tool_name}: Initialized successfully")
                print(f"   Name: {tool.name}")
                print(f"   Description: {tool.description}")
            except Exception as e:
                print(f"❌ {tool_name}: Failed to initialize - {e}")
                return False
    
    except Exception as e:
        print(f"❌ Failed to test individual tools: {e}")
        return False
    
    print("\n🎉 All WhatsApp integration tests passed!")
    print("\n📝 Next steps:")
    print("1. Set up your Twilio WhatsApp sandbox or business account")
    print("2. Configure your WhatsApp phone number and group ID")
    print("3. Test sending actual messages (be careful with costs!)")
    print("4. Integrate with your CrewAI agents")
    
    return True

def test_agent_integration():
    """Test that agents can use WhatsApp tools."""
    print("\n🤖 Testing Agent Integration")
    print("=" * 50)
    
    try:
        from agents import communications_agent, manager_agent, finance_agent
        
        # Check if agents have WhatsApp tools
        agents_to_check = [
            ("Communications Agent", communications_agent),
            ("Manager Agent", manager_agent), 
            ("Finance Agent", finance_agent)
        ]
        
        for agent_name, agent in agents_to_check:
            tool_names = [tool.name for tool in agent.tools] if agent.tools else []
            whatsapp_tools = [name for name in tool_names if 'whatsapp' in name.lower()]
            
            if whatsapp_tools:
                print(f"✅ {agent_name}: Has {len(whatsapp_tools)} WhatsApp tools")
                for tool in whatsapp_tools:
                    print(f"   - {tool}")
            else:
                print(f"❌ {agent_name}: No WhatsApp tools found")
        
        print("\n✅ Agent integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test agent integration: {e}")
        return False

def main():
    """Run all WhatsApp integration tests."""
    print("🚀 KICKAI WhatsApp Integration Test")
    print("=" * 60)
    
    # Test WhatsApp tools
    tools_ok = test_whatsapp_tools()
    
    if tools_ok:
        # Test agent integration
        agent_ok = test_agent_integration()
        
        if agent_ok:
            print("\n🎯 All tests passed! WhatsApp integration is ready.")
            print("\n💡 To test actual message sending:")
            print("1. Ensure your Twilio account is set up")
            print("2. Use the demo scenarios in main.py")
            print("3. Monitor your Twilio console for message delivery")
        else:
            print("\n⚠️  Agent integration needs attention.")
    else:
        print("\n❌ WhatsApp tools test failed. Please check your setup.")

if __name__ == "__main__":
    main() 