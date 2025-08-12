#!/usr/bin/env python3
"""
LLM Response Issue Diagnostic Script

This script tests the exact flow that's causing "None or empty response" errors
by isolating and testing each component.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from loguru import logger
from kickai.core.config import get_settings
from kickai.config.llm_config import get_llm_config
from kickai.agents.crew_agents import TeamManagementSystem
from kickai.core.types import TelegramMessage
from kickai.core.enums import ChatType

def test_groq_direct():
    """Test Groq API directly to confirm it's working."""
    logger.info("🧪 Testing Groq API directly...")
    
    try:
        llm_config = get_llm_config()
        llm = llm_config.main_llm
        
        # Test with simple prompt
        simple_prompt = "Hello! Please respond with 'Test successful!'"
        
        logger.debug(f"📤 Sending prompt: {simple_prompt}")
        
        # Try to invoke the LLM directly
        if hasattr(llm, 'invoke'):
            response = llm.invoke(simple_prompt)
            logger.info(f"✅ Direct LLM Response: {response}")
            return True
        else:
            logger.warning("⚠️ LLM doesn't have invoke method")
            return False
            
    except Exception as e:
        logger.error(f"❌ Direct LLM test failed: {e}")
        return False

def test_tool_output_format():
    """Test different tool output formats to see if formatting causes issues."""
    logger.info("🧪 Testing tool output formats...")
    
    test_outputs = [
        # Simple string
        "Player: John Smith - Active",
        
        # With emojis
        "👥 Players:\n• Jane Doe - Midfielder ✅ Active (ID: 01JD)\n• John Smith - Forward ✅ Active (ID: JS001)",
        
        # Complex formatted output (like the actual tool returns)
        """📋 Team Overview for KTI

👔 Team Members:
• Coach Wilson - Coach

👥 Players:
• Jane Doe - Midfielder ✅ Active (ID: 01JD)
• John Smith - Forward ✅ Active (ID: JS001)

""",
    ]
    
    try:
        llm_config = get_llm_config()
        llm = llm_config.main_llm
        
        for i, test_output in enumerate(test_outputs, 1):
            logger.info(f"🧪 Testing format {i}...")
            
            # Create a prompt that includes the tool output (similar to what CrewAI does)
            prompt = f"""You are a helpful assistant. A tool returned this information:

{test_output}

Please provide a clear response based on this tool output. Return the tool output exactly as provided.
"""
            
            logger.debug(f"📤 Test prompt {i}: {prompt}")
            
            if hasattr(llm, 'invoke'):
                response = llm.invoke(prompt)
                logger.info(f"✅ Response {i}: {response}")
                
                if not response or str(response).strip() == "":
                    logger.warning(f"⚠️ Empty response for format {i}")
                    return False
            else:
                logger.warning("⚠️ LLM doesn't have invoke method")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool output format test failed: {e}")
        return False

def test_complex_prompt():
    """Test the actual complex prompt used in the system."""
    logger.info("🧪 Testing complex agent prompt...")
    
    # This is similar to the actual structured prompt used in crew_agents.py
    complex_prompt = """
User Request: /list

Context Information:
- Team ID: KTI
- User Telegram ID: 1003
- Username: coach_wilson
- Chat Type: leadership

Instructions: Use the provided context information to call tools with the appropriate parameters.
Pass team_id, telegram_id, username, and chat_type as direct parameters to tools that require them.

IMPORTANT: For get_my_status tool, ALWAYS pass chat_type parameter to determine whether to look up player status (main chat) or team member status (leadership chat).

🚨 CRITICAL ANTI-HALLUCINATION RULE 🚨: 
Return tool outputs EXACTLY as provided - NEVER add, modify, or invent data.
- Tool output is final - DO NOT add extra players, team members, or any data
- DO NOT reformat, summarize, or remove emojis, symbols, or formatting
- If tool returns 2 players, your response must have EXACTLY 2 players
- NEVER add fictional players like "Saim", "Ahmed", etc.

MANDATORY TOOL USAGE: You MUST call the appropriate tool for data requests:
- /list: MUST call list_team_members_and_players(team_id) for leadership chat or get_active_players(team_id, telegram_id) for main chat
- /info: MUST call get_my_status(telegram_id, team_id, chat_type) 
- NEVER provide made-up or fabricated data - if no tool is called, return "Error: No tool was used to retrieve data"

Please respond with "I understand the instructions" if you can process this prompt.
"""
    
    try:
        llm_config = get_llm_config()
        llm = llm_config.main_llm
        
        logger.debug(f"📤 Complex prompt (length: {len(complex_prompt)}): {complex_prompt}")
        
        if hasattr(llm, 'invoke'):
            response = llm.invoke(complex_prompt)
            logger.info(f"✅ Complex prompt response: {response}")
            
            if not response or str(response).strip() == "":
                logger.warning("⚠️ Empty response for complex prompt - this might be the issue!")
                return False
            
            return True
        else:
            logger.warning("⚠️ LLM doesn't have invoke method")
            return False
            
    except Exception as e:
        logger.error(f"❌ Complex prompt test failed: {e}")
        return False

async def test_crewai_basic_task():
    """Test a basic CrewAI task to see where the failure occurs."""
    logger.info("🧪 Testing basic CrewAI task...")
    
    try:
        from crewai import Agent, Task, Crew, Process
        
        # Create a simple agent
        llm_config = get_llm_config()
        llm = llm_config.main_llm
        
        agent = Agent(
            role="Test Agent",
            goal="Respond to simple requests",
            backstory="A simple test agent for debugging purposes",
            llm=llm,
            verbose=True
        )
        
        # Create a simple task
        task = Task(
            description="Please respond with 'CrewAI task successful!'",
            agent=agent,
            expected_output="A simple success message"
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("🚀 Executing basic CrewAI task...")
        result = crew.kickoff()
        
        logger.info(f"✅ CrewAI result type: {type(result)}")
        logger.info(f"✅ CrewAI result: {result}")
        
        # Try to extract the actual response
        if hasattr(result, 'raw'):
            logger.info(f"✅ Result.raw: {result.raw}")
            if hasattr(result.raw, 'output'):
                logger.info(f"✅ Result.raw.output: {result.raw.output}")
        
        if hasattr(result, 'output'):
            logger.info(f"✅ Result.output: {result.output}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ CrewAI basic task failed: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

async def test_team_management_system():
    """Test the actual TeamManagementSystem to isolate the issue."""
    logger.info("🧪 Testing TeamManagementSystem directly...")
    
    try:
        # Create team management system
        system = TeamManagementSystem("TEST_TEAM")
        
        # Create execution context
        execution_context = {
            'team_id': 'TEST_TEAM',
            'telegram_id': 1003,
            'username': 'test_user',
            'chat_type': 'leadership',
            'user_role': 'admin'
        }
        
        logger.info("🚀 Executing simple task through TeamManagementSystem...")
        result = await system.execute_task("/list", execution_context)
        
        logger.info(f"✅ TeamManagementSystem result: {result}")
        
        if not result or result.strip() == "":
            logger.warning("⚠️ Empty result from TeamManagementSystem!")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ TeamManagementSystem test failed: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Run all diagnostic tests."""
    logger.info("🚀 LLM Response Issue Diagnostic Starting...")
    logger.info("=" * 60)
    
    # Initialize environment and dependency container like the real system
    os.environ["PYTHONPATH"] = str(project_root)
    
    try:
        logger.info("🔧 Initializing dependency container for diagnostics...")
        from kickai.core.dependency_container import ensure_container_initialized
        from kickai.core.config import get_settings
        from kickai.database.firebase_client import initialize_firebase_client
        from dotenv import load_dotenv
        
        # Load environment
        load_dotenv()
        
        # Initialize Firebase and container like the real bot does
        config = get_settings()
        initialize_firebase_client(config)
        ensure_container_initialized()
        logger.info("✅ Dependency container initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize dependency container: {e}")
        logger.info("Continuing with basic tests that don't require container...")
    
    test_results = {}
    
    # Test 1: Direct Groq API
    logger.info("\n📋 TEST 1: Direct Groq API")
    test_results['groq_direct'] = test_groq_direct()
    
    # Test 2: Tool output formats
    logger.info("\n📋 TEST 2: Tool Output Formats")
    test_results['tool_formats'] = test_tool_output_format()
    
    # Test 3: Complex prompt handling
    logger.info("\n📋 TEST 3: Complex Prompt")
    test_results['complex_prompt'] = test_complex_prompt()
    
    # Test 4: Basic CrewAI task
    logger.info("\n📋 TEST 4: Basic CrewAI Task")
    test_results['crewai_basic'] = await test_crewai_basic_task()
    
    # Test 5: TeamManagementSystem
    logger.info("\n📋 TEST 5: TeamManagementSystem")
    test_results['team_system'] = await test_team_management_system()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<20}: {status}")
    
    # Analysis
    logger.info("\n📋 ANALYSIS:")
    
    if test_results['groq_direct'] and not test_results['crewai_basic']:
        logger.info("🎯 Issue is with CrewAI integration, not Groq API")
    elif test_results['groq_direct'] and not test_results['complex_prompt']:
        logger.info("🎯 Issue is with complex prompt overwhelming the LLM")
    elif test_results['tool_formats'] and not test_results['team_system']:
        logger.info("🎯 Issue is in TeamManagementSystem execution flow")
    else:
        logger.info("🎯 Need to investigate further based on test results")

if __name__ == "__main__":
    asyncio.run(main())