#!/usr/bin/env python3
"""
Comprehensive Agent and Tool Configuration Audit

This script audits the current agent configuration, tool registry, and identifies
issues that need to be fixed for a clean 5-agent setup following CrewAI best practices.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set required environment variable
os.environ["KICKAI_INVITE_SECRET_KEY"] = "test_secret_key_for_debugging_only_32_chars_long"

def audit_agent_configuration():
    """Audit the current agent configuration."""
    print("🔍 AUDITING AGENT CONFIGURATION")
    print("=" * 60)
    
    try:
        from kickai.config.agents import get_agent_config_manager
        from kickai.core.enums import AgentRole
        
        # Get agent config manager
        config_manager = get_agent_config_manager()
        
        # Test context
        context = {"team_id": "TEST1"}
        
        print("\n1. AGENT CONFIGURATION ANALYSIS:")
        print("-" * 40)
        
        # Check all agent configs
        all_configs = config_manager.get_all_agent_configs(context)
        enabled_configs = config_manager.get_enabled_agent_configs(context)
        
        print(f"✅ Total agent configs loaded: {len(all_configs)}")
        print(f"✅ Enabled agent configs: {len(enabled_configs)}")
        
        # Analyze each agent
        for role in AgentRole:
            config = all_configs.get(role)
            if config:
                print(f"\n📋 {role.value.upper()}:")
                print(f"   - Enabled: {config.enabled}")
                print(f"   - Tools: {len(config.tools)} tools")
                print(f"   - Temperature: {config.temperature}")
                print(f"   - Max Tokens: {config.max_tokens}")
                print(f"   - Primary Entity Type: {config.primary_entity_type}")
                print(f"   - Entity Types: {[et for et in config.entity_types]}")
                
                # Check for issues
                issues = []
                if not config.tools:
                    issues.append("No tools assigned")
                if config.temperature > 0.7:
                    issues.append("High temperature may cause hallucinations")
                if config.max_tokens < 200:
                    issues.append("Low max tokens may truncate responses")
                
                if issues:
                    print(f"   ⚠️  Issues: {', '.join(issues)}")
                else:
                    print(f"   ✅ No issues detected")
            else:
                print(f"\n❌ {role.value.upper()}: No configuration found")
        
        return all_configs, enabled_configs
        
    except Exception as e:
        print(f"❌ Error auditing agent configuration: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

def audit_tool_registry():
    """Audit the current tool registry."""
    print("\n\n🔧 AUDITING TOOL REGISTRY")
    print("=" * 60)
    
    try:
        from kickai.agents.tool_registry import get_tool_registry
        
        # Get tool registry
        registry = get_tool_registry()
        
        print("\n2. TOOL REGISTRY ANALYSIS:")
        print("-" * 40)
        
        # Get all tools
        all_tools = registry.list_all_tools()
        enabled_tools = registry.get_enabled_tools()
        
        print(f"✅ Total tools registered: {len(all_tools)}")
        print(f"✅ Enabled tools: {len(enabled_tools)}")
        
        # Analyze tools by category
        tools_by_category = {}
        tools_by_type = {}
        
        for tool in all_tools:
            # By category
            category = tool.category.value
            if category not in tools_by_category:
                tools_by_category[category] = []
            tools_by_category[category].append(tool)
            
            # By type
            tool_type = tool.tool_type.value
            if tool_type not in tools_by_type:
                tools_by_type[tool_type] = []
            tools_by_type[tool_type].append(tool)
        
        print(f"\n📊 Tools by Category:")
        for category, tools in tools_by_category.items():
            print(f"   - {category}: {len(tools)} tools")
        
        print(f"\n📊 Tools by Type:")
        for tool_type, tools in tools_by_type.items():
            print(f"   - {tool_type}: {len(tools)} tools")
        
        # Check for issues
        issues = []
        if len(all_tools) == 0:
            issues.append("No tools registered")
        if len(enabled_tools) == 0:
            issues.append("No enabled tools")
        
        # Check for duplicate tool names
        tool_names = [tool.name for tool in all_tools]
        duplicates = [name for name in set(tool_names) if tool_names.count(name) > 1]
        if duplicates:
            issues.append(f"Duplicate tool names: {duplicates}")
        
        if issues:
            print(f"\n⚠️  Tool Registry Issues: {', '.join(issues)}")
        else:
            print(f"\n✅ No tool registry issues detected")
        
        return all_tools, enabled_tools
        
    except Exception as e:
        print(f"❌ Error auditing tool registry: {e}")
        import traceback
        traceback.print_exc()
        return [], []

def audit_agent_tool_mapping():
    """Audit the mapping between agents and tools."""
    print("\n\n🔗 AUDITING AGENT-TOOL MAPPING")
    print("=" * 60)
    
    try:
        from kickai.config.agents import get_enabled_agent_configs
        from kickai.agents.tool_registry import get_tool_registry
        from kickai.core.enums import AgentRole
        
        # Get configurations
        context = {"team_id": "TEST1"}
        enabled_configs = get_enabled_agent_configs(context)
        registry = get_tool_registry()
        
        print("\n3. AGENT-TOOL MAPPING ANALYSIS:")
        print("-" * 40)
        
        # Check each agent's tools
        for role, config in enabled_configs.items():
            print(f"\n🤖 {role.value.upper()}:")
            print(f"   - Assigned tools: {config.tools}")
            
            # Check if tools exist in registry
            missing_tools = []
            for tool_name in config.tools:
                tool_metadata = registry.get_tool(tool_name)
                if not tool_metadata:
                    missing_tools.append(tool_name)
            
            if missing_tools:
                print(f"   ❌ Missing tools: {missing_tools}")
            else:
                print(f"   ✅ All tools found in registry")
        
        # Check for unused tools
        all_tool_names = [tool.name for tool in registry.list_all_tools()]
        used_tool_names = []
        for config in enabled_configs.values():
            used_tool_names.extend(config.tools)
        
        unused_tools = [name for name in all_tool_names if name not in used_tool_names]
        if unused_tools:
            print(f"\n⚠️  Unused tools: {unused_tools}")
        else:
            print(f"\n✅ All tools are assigned to agents")
        
        return enabled_configs
        
    except Exception as e:
        print(f"❌ Error auditing agent-tool mapping: {e}")
        import traceback
        traceback.print_exc()
        return {}

def audit_langgpt_prompts():
    """Audit the LangGPT prompt structure."""
    print("\n\n📝 AUDITING LANGGPT PROMPT STRUCTURE")
    print("=" * 60)
    
    try:
        from kickai.config.agents import get_enabled_agent_configs
        
        context = {"team_id": "TEST1"}
        enabled_configs = get_enabled_agent_configs(context)
        
        print("\n4. LANGGPT PROMPT ANALYSIS:")
        print("-" * 40)
        
        for role, config in enabled_configs.items():
            print(f"\n📋 {role.value.upper()} Prompt Analysis:")
            
            # Check backstory structure
            backstory = config.backstory
            issues = []
            
            if not backstory:
                issues.append("No backstory defined")
            else:
                # Check for LangGPT structure indicators
                if "CORE PRINCIPLES:" not in backstory:
                    issues.append("Missing CORE PRINCIPLES section")
                if "SPECIALIZED RESPONSIBILITIES:" not in backstory:
                    issues.append("Missing SPECIALIZED RESPONSIBILITIES section")
                if "TOOL USAGE RULES:" not in backstory:
                    issues.append("Missing TOOL USAGE RULES section")
                if "RESPONSE FORMAT:" not in backstory:
                    issues.append("Missing RESPONSE FORMAT section")
                
                # Check for performance optimizations
                if "ANTI-HALLUCINATION" not in backstory:
                    issues.append("Missing anti-hallucination rules")
                if "tool output" not in backstory.lower():
                    issues.append("Missing tool output validation rules")
            
            if issues:
                print(f"   ⚠️  Issues: {', '.join(issues)}")
            else:
                print(f"   ✅ LangGPT structure looks good")
        
    except Exception as e:
        print(f"❌ Error auditing LangGPT prompts: {e}")
        import traceback
        traceback.print_exc()

def generate_recommendations():
    """Generate recommendations for fixing issues."""
    print("\n\n💡 RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n5. RECOMMENDED FIXES:")
    print("-" * 40)
    
    print("""
🔧 AGENT CONFIGURATION FIXES:
1. Ensure all 5 agents have proper LangGPT structure
2. Add missing anti-hallucination rules to all agents
3. Optimize temperature settings (0.1-0.3 for data-critical agents)
4. Set appropriate max_tokens (500-1000 for complex responses)
5. Add primary_entity_type to all agents

🔧 TOOL REGISTRY FIXES:
1. Remove unused/legacy tools
2. Ensure all agent-assigned tools exist in registry
3. Add proper tool descriptions and metadata
4. Implement tool access control by agent role

🔧 LANGGPT PROMPT OPTIMIZATIONS:
1. Add structured sections: CORE PRINCIPLES, SPECIALIZED RESPONSIBILITIES, TOOL USAGE RULES
2. Include anti-hallucination rules in all agents
3. Add performance optimization guidelines
4. Include context-aware tool usage rules
5. Add response formatting standards

🔧 CREWAI BEST PRACTICES:
1. Use sequential process for predictable execution
2. Implement proper error handling in tools
3. Add tool validation and context checking
4. Use appropriate memory configuration
5. Implement proper agent delegation rules
    """)

def main():
    """Run the complete audit."""
    print("🚀 KICKAI AGENT & TOOL CONFIGURATION AUDIT")
    print("=" * 80)
    
    # Run all audits
    agent_configs, enabled_configs = audit_agent_configuration()
    all_tools, enabled_tools = audit_tool_registry()
    agent_tool_mapping = audit_agent_tool_mapping()
    audit_langgpt_prompts()
    generate_recommendations()
    
    print("\n\n📊 AUDIT SUMMARY")
    print("=" * 60)
    print(f"✅ Agents configured: {len(enabled_configs)}")
    print(f"✅ Tools registered: {len(enabled_tools)}")
    print(f"✅ Agent-tool mappings: {len(agent_tool_mapping)}")
    
    print("\n🎯 Next Steps:")
    print("1. Fix agent configuration issues identified above")
    print("2. Clean up tool registry and remove unused tools")
    print("3. Implement LangGPT-optimized prompts")
    print("4. Test agent creation and tool assignment")
    print("5. Validate CrewAI integration")

if __name__ == "__main__":
    main()
