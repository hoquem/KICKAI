#!/usr/bin/env python3
"""
Tool Inventory Audit Script

This script performs a comprehensive audit of all tools in the KICKAI system:
1. Discovers all tool implementations
2. Validates tool assignments in agents.yaml
3. Identifies unused tools
4. Provides cleanup recommendations
"""

import os
import sys
import yaml
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kickai.agents.tool_registry import initialize_tool_registry, get_tool_registry


@dataclass
class ToolInfo:
    """Information about a tool."""
    name: str
    file_path: str
    feature_module: str
    description: str
    is_implemented: bool
    is_assigned: bool
    assigned_agents: List[str]
    tool_type: str
    category: str


@dataclass
class AgentInfo:
    """Information about an agent."""
    name: str
    role: str
    assigned_tools: List[str]
    missing_tools: List[str]
    unused_tools: List[str]


class ToolInventoryAuditor:
    """Auditor for tool inventory and assignments."""
    
    def __init__(self):
        self.tools: Dict[str, ToolInfo] = {}
        self.agents: Dict[str, AgentInfo] = {}
        self.agents_config = {}
        
    def load_agents_config(self, config_path: str = "kickai/config/agents.yaml"):
        """Load agents configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                self.agents_config = yaml.safe_load(f)
            print(f"✅ Loaded agents configuration from {config_path}")
        except Exception as e:
            print(f"❌ Failed to load agents configuration: {e}")
            return False
        return True
    
    def discover_tools(self):
        """Discover all tools in the codebase."""
        try:
            # Initialize tool registry to discover tools
            registry = initialize_tool_registry("kickai")
            all_tools = registry.list_all_tools()
            
            print(f"🔍 Discovered {len(all_tools)} tools from registry")
            
            for tool_metadata in all_tools:
                tool_info = ToolInfo(
                    name=tool_metadata.tool_id,
                    file_path="",  # Will be filled from registry
                    feature_module=tool_metadata.feature_module,
                    description=tool_metadata.description,
                    is_implemented=True,
                    is_assigned=False,
                    assigned_agents=[],
                    tool_type=tool_metadata.tool_type.value,
                    category=tool_metadata.category.value
                )
                self.tools[tool_metadata.tool_id] = tool_info
            
            print(f"✅ Tool discovery complete: {len(self.tools)} tools found")
            
        except Exception as e:
            print(f"❌ Tool discovery failed: {e}")
            return False
        return True
    
    def analyze_agent_assignments(self):
        """Analyze tool assignments in agents configuration."""
        if not self.agents_config or 'agents' not in self.agents_config:
            print("❌ No agents configuration found")
            return False
        
        print(f"🔍 Analyzing {len(self.agents_config['agents'])} agents...")
        
        for agent_config in self.agents_config['agents']:
            agent_name = agent_config['name']
            agent_role = agent_config.get('role', 'Unknown')
            assigned_tools = agent_config.get('tools', [])
            
            # Track tool assignments
            for tool_name in assigned_tools:
                if tool_name in self.tools:
                    self.tools[tool_name].is_assigned = True
                    self.tools[tool_name].assigned_agents.append(agent_name)
                else:
                    print(f"⚠️  Agent {agent_name} references non-existent tool: {tool_name}")
            
            # Create agent info
            agent_info = AgentInfo(
                name=agent_name,
                role=agent_role,
                assigned_tools=assigned_tools,
                missing_tools=[],
                unused_tools=[]
            )
            
            self.agents[agent_name] = agent_info
        
        print(f"✅ Agent assignment analysis complete")
        return True
    
    def identify_missing_and_unused_tools(self):
        """Identify missing and unused tools."""
        # Find missing tools (assigned but not implemented)
        for agent_name, agent_info in self.agents.items():
            for tool_name in agent_info.assigned_tools:
                if tool_name not in self.tools:
                    agent_info.missing_tools.append(tool_name)
        
        # Find unused tools (implemented but not assigned)
        unused_tools = [name for name, tool in self.tools.items() if not tool.is_assigned]
        
        print(f"📊 Analysis Results:")
        print(f"   - Total tools: {len(self.tools)}")
        print(f"   - Assigned tools: {len([t for t in self.tools.values() if t.is_assigned])}")
        print(f"   - Unused tools: {len(unused_tools)}")
        
        return unused_tools
    
    def generate_report(self):
        """Generate comprehensive audit report."""
        print("\n" + "="*80)
        print("🔍 TOOL INVENTORY AUDIT REPORT")
        print("="*80)
        
        # Tool Summary
        print(f"\n📊 TOOL SUMMARY:")
        print(f"   Total Tools: {len(self.tools)}")
        print(f"   Assigned Tools: {len([t for t in self.tools.values() if t.is_assigned])}")
        print(f"   Unused Tools: {len([t for t in self.tools.values() if not t.is_assigned])}")
        
        # Agent Summary
        print(f"\n🤖 AGENT SUMMARY:")
        for agent_name, agent_info in self.agents.items():
            print(f"   {agent_name}: {len(agent_info.assigned_tools)} tools assigned")
            if agent_info.missing_tools:
                print(f"     ⚠️  Missing: {agent_info.missing_tools}")
        
        # Tool Categories
        print(f"\n📁 TOOL CATEGORIES:")
        categories = {}
        for tool in self.tools.values():
            categories[tool.category] = categories.get(tool.category, 0) + 1
        for category, count in sorted(categories.items()):
            print(f"   {category}: {count} tools")
        
        # Unused Tools
        unused_tools = [name for name, tool in self.tools.items() if not tool.is_assigned]
        if unused_tools:
            print(f"\n🗑️  UNUSED TOOLS (can be deleted):")
            for tool_name in sorted(unused_tools):
                tool = self.tools[tool_name]
                print(f"   - {tool_name} ({tool.category}/{tool.tool_type})")
                print(f"     Description: {tool.description[:80]}...")
        
        # Missing Tools
        missing_tools = set()
        for agent_info in self.agents.values():
            missing_tools.update(agent_info.missing_tools)
        
        if missing_tools:
            print(f"\n❌ MISSING TOOLS (referenced but not implemented):")
            for tool_name in sorted(missing_tools):
                print(f"   - {tool_name}")
        
        # Tool Assignments by Agent
        print(f"\n🔗 TOOL ASSIGNMENTS BY AGENT:")
        for agent_name, agent_info in self.agents.items():
            print(f"\n   {agent_name} ({agent_info.role}):")
            for tool_name in agent_info.assigned_tools:
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    print(f"     ✅ {tool_name} ({tool.category}/{tool.tool_type})")
                else:
                    print(f"     ❌ {tool_name} (MISSING)")
        
        return unused_tools
    
    def generate_cleanup_script(self, unused_tools: List[str]):
        """Generate cleanup script for unused tools."""
        if not unused_tools:
            print("\n✅ No unused tools to clean up!")
            return
        
        print(f"\n🧹 CLEANUP RECOMMENDATIONS:")
        print(f"   The following {len(unused_tools)} tools can be safely deleted:")
        
        # Group by file for easier cleanup
        tools_by_file = {}
        for tool_name in unused_tools:
            tool = self.tools[tool_name]
            if tool.file_path not in tools_by_file:
                tools_by_file[tool.file_path] = []
            tools_by_file[tool.file_path].append(tool_name)
        
        for file_path, tools in tools_by_file.items():
            if file_path:  # Skip if no file path
                print(f"\n   File: {file_path}")
                for tool_name in tools:
                    print(f"     - Remove @tool('{tool_name}')")
        
        # Generate actual cleanup script
        cleanup_script = self._create_cleanup_script(unused_tools)
        
        with open("scripts/cleanup_unused_tools.py", "w") as f:
            f.write(cleanup_script)
        
        print(f"\n📝 Cleanup script generated: scripts/cleanup_unused_tools.py")
    
    def _create_cleanup_script(self, unused_tools: List[str]) -> str:
        """Create a cleanup script for unused tools."""
        script = '''#!/usr/bin/env python3
"""
Cleanup script for unused tools.

This script removes unused tool implementations from the codebase.
Generated by tool_inventory_audit.py
"""

import os
import re
from pathlib import Path

def remove_tool_from_file(file_path: str, tool_name: str) -> bool:
    """Remove a tool implementation from a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the tool function
        pattern = rf'@tool\("{re.escape(tool_name)}"\)\s*\ndef\s+(\w+)\s*\([^)]*\):.*?(?=\\n\\n|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Remove the entire function
            function_name = match.group(1)
            function_pattern = rf'def\s+{re.escape(function_name)}\s*\([^)]*\):.*?(?=\\n\\n|$)'
            new_content = re.sub(function_pattern, '', content, flags=re.DOTALL)
            
            # Also remove the @tool decorator if it's on a separate line
            decorator_pattern = rf'@tool\("{re.escape(tool_name)}"\)\s*\\n'
            new_content = re.sub(decorator_pattern, '', new_content)
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Removed tool '{tool_name}' from {file_path}")
            return True
        else:
            print(f"⚠️  Could not find tool '{tool_name}' in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error removing tool '{tool_name}' from {file_path}: {e}")
        return False

def main():
    """Main cleanup function."""
    print("🧹 Starting unused tool cleanup...")
    
    # List of unused tools to remove
    unused_tools = [
'''
        
        for tool_name in unused_tools:
            script += f'        "{tool_name}",\n'
        
        script += '''    ]
    
    # Remove each unused tool
    removed_count = 0
    for tool_name in unused_tools:
        # You'll need to manually specify the file path for each tool
        # This is a template - update the file paths as needed
        print(f"🔍 Looking for tool: {tool_name}")
        # Example: remove_tool_from_file("path/to/file.py", tool_name)
    
    print(f"✅ Cleanup complete. Removed {removed_count} unused tools.")

if __name__ == "__main__":
    main()
'''
        return script


def main():
    """Main audit function."""
    print("🔍 Starting Tool Inventory Audit...")
    
    auditor = ToolInventoryAuditor()
    
    # Load agents configuration
    if not auditor.load_agents_config():
        return False
    
    # Discover tools
    if not auditor.discover_tools():
        return False
    
    # Analyze assignments
    if not auditor.analyze_agent_assignments():
        return False
    
    # Identify unused tools
    unused_tools = auditor.identify_missing_and_unused_tools()
    
    # Generate report
    auditor.generate_report()
    
    # Generate cleanup script
    auditor.generate_cleanup_script(unused_tools)
    
    print(f"\n✅ Tool inventory audit complete!")
    return True


if __name__ == "__main__":
    main()
