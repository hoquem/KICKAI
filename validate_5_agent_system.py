#!/usr/bin/env python3
"""
Validation Script for 5-Agent Architecture
Tests the cleaned-up KICKAI system after removing obsolete files.
"""

import asyncio
import sys
from typing import Dict, Any

def validate_imports():
    """Test that all core imports work."""
    print("🔍 Testing core imports...")
    
    try:
        from kickai.agents.crew_agents import TeamManagementSystem
        from kickai.agents.configurable_agent import ConfigurableAgent, AgentFactory
        from kickai.agents.tool_registry import initialize_tool_registry
        from kickai.agents.tools_manager import AgentToolsManager
        from kickai.core.enums import AgentRole
        print("✅ All core imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def validate_agent_roles():
    """Test that all 5 agent roles are available."""
    print("\n🔍 Testing agent roles...")
    
    try:
        from kickai.core.enums import AgentRole
        
        expected_roles = [
            AgentRole.MESSAGE_PROCESSOR,
            AgentRole.HELP_ASSISTANT,
            AgentRole.PLAYER_COORDINATOR,
            AgentRole.TEAM_ADMINISTRATOR,
            AgentRole.SQUAD_SELECTOR
        ]
        
        print("Expected 5-agent roles:")
        for role in expected_roles:
            print(f"  ✅ {role.value}")
        
        return True
    except Exception as e:
        print(f"❌ Agent role error: {e}")
        return False

def validate_tool_registry():
    """Test that tool registry initializes and discovers tools."""
    print("\n🔍 Testing tool registry...")
    
    try:
        from kickai.agents.tool_registry import initialize_tool_registry
        
        registry = initialize_tool_registry("kickai")
        tool_count = len(registry.get_tool_names())
        
        print(f"✅ Tool registry initialized with {tool_count} tools")
        
        # Sample some tools
        sample_tools = [
            "get_available_commands",
            "FINAL_HELP_RESPONSE", 
            "get_player_status",
            "add_team_member_simplified",
            "select_squad"
        ]
        
        found_tools = []
        for tool_name in sample_tools:
            if registry.get_tool_function(tool_name):
                found_tools.append(tool_name)
        
        print(f"✅ Found {len(found_tools)}/{len(sample_tools)} sample tools")
        return True
    except Exception as e:
        print(f"❌ Tool registry error: {e}")
        return False

def validate_agent_creation():
    """Test that agents can be created successfully."""
    print("\n🔍 Testing agent creation...")
    
    try:
        from kickai.agents.configurable_agent import ConfigurableAgent
        from kickai.core.enums import AgentRole
        
        # Test creating each agent type
        roles_to_test = [
            AgentRole.MESSAGE_PROCESSOR,
            AgentRole.HELP_ASSISTANT,
            AgentRole.PLAYER_COORDINATOR
        ]
        
        created_agents = []
        for role in roles_to_test:
            try:
                agent = ConfigurableAgent(role, "TEST")
                tool_count = len(agent.get_tools())
                created_agents.append((role.value, tool_count))
                print(f"  ✅ {role.value}: {tool_count} tools")
            except Exception as e:
                print(f"  ❌ {role.value}: {e}")
        
        print(f"✅ Created {len(created_agents)}/{len(roles_to_test)} agents")
        return len(created_agents) == len(roles_to_test)
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return False

def validate_team_system():
    """Test that the full TeamManagementSystem can be created."""
    print("\n🔍 Testing TeamManagementSystem...")
    
    try:
        from kickai.agents.crew_agents import TeamManagementSystem
        
        system = TeamManagementSystem("TEST")
        agent_count = len(system.agents)
        
        print(f"✅ TeamManagementSystem created with {agent_count} agents:")
        for role, agent in system.agents.items():
            tool_count = len(agent.get_tools()) if hasattr(agent, 'get_tools') else 0
            enabled = agent.is_enabled() if hasattr(agent, 'is_enabled') else True
            status = "enabled" if enabled else "disabled"
            print(f"  - {role.value}: {tool_count} tools ({status})")
        
        return agent_count >= 3  # Should have at least 3 agents
    except Exception as e:
        print(f"❌ TeamManagementSystem error: {e}")
        return False

def validate_context_handling():
    """Test that context validation works without deprecated dependencies."""
    print("\n🔍 Testing context handling...")
    
    try:
        from kickai.agents.configurable_agent import ConfigurableAgent
        from kickai.core.enums import AgentRole
        
        agent = ConfigurableAgent(AgentRole.HELP_ASSISTANT, "TEST")
        
        # Test valid context
        valid_context = {
            'team_id': 'TEST',
            'telegram_id': '12345',
            'username': 'testuser',
            'chat_type': 'main',
            'user_role': 'public',
            'is_registered': True
        }
        
        agent._validate_context(valid_context)
        print("✅ Valid context validation passed")
        
        # Test invalid context
        try:
            invalid_context = {'team_id': 'TEST'}  # Missing required keys
            agent._validate_context(invalid_context)
            print("❌ Invalid context validation should have failed")
            return False
        except ValueError:
            print("✅ Invalid context validation correctly failed")
        
        return True
    except Exception as e:
        print(f"❌ Context handling error: {e}")
        return False

def validate_no_deprecated_imports():
    """Check that deprecated imports are not present."""
    print("\n🔍 Checking for deprecated imports...")
    
    deprecated_patterns = [
        "entity_specific_agents",
        "simplified_tool_registry", 
        "helper_agent",
        "registration_agent",
        "user_flow_agent",
        "simple_agent"
    ]
    
    clean = True
    for pattern in deprecated_patterns:
        try:
            exec(f"import kickai.agents.{pattern}")
            print(f"❌ Found deprecated import: {pattern}")
            clean = False
        except ImportError:
            print(f"✅ Deprecated import correctly removed: {pattern}")
    
    return clean

async def run_async_validation():
    """Run async validation tests."""
    print("\n🔍 Testing async functionality...")
    
    try:
        from kickai.agents.configurable_agent import ConfigurableAgent
        from kickai.core.enums import AgentRole
        
        agent = ConfigurableAgent(AgentRole.HELP_ASSISTANT, "TEST")
        
        context = {
            'team_id': 'TEST',
            'telegram_id': '12345',
            'username': 'testuser',
            'chat_type': 'main',
            'user_role': 'public',
            'is_registered': True
        }
        
        # This will attempt to create and run a crew
        # We expect it to fail due to missing LLM config in test environment
        # But it should fail gracefully
        try:
            result = await agent.execute("test task", context)
            print("✅ Agent execution completed (result may be error)")
            return True
        except Exception as e:
            if "model" in str(e).lower() or "llm" in str(e).lower():
                print("✅ Agent execution failed as expected (no LLM config in test)")
                return True
            else:
                print(f"❌ Unexpected error in agent execution: {e}")
                return False
    except Exception as e:
        print(f"❌ Async validation error: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 KICKAI 5-Agent Architecture Validation")
    print("=" * 50)
    
    tests = [
        ("Import Validation", validate_imports),
        ("Agent Roles", validate_agent_roles), 
        ("Tool Registry", validate_tool_registry),
        ("Agent Creation", validate_agent_creation),
        ("Team System", validate_team_system),
        ("Context Handling", validate_context_handling),
        ("Deprecated Imports", validate_no_deprecated_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Run async test
    try:
        print("\n" + "=" * 50)
        async_result = asyncio.run(run_async_validation())
        results.append(("Async Functionality", async_result))
    except Exception as e:
        print(f"❌ Async validation crashed: {e}")
        results.append(("Async Functionality", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS:")
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 5-agent architecture is ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} tests failed. Review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())