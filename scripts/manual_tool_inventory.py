#!/usr/bin/env python3
"""
Manual Tool Inventory Script

This script manually examines tool files to create a comprehensive inventory
without relying on the tool registry discovery mechanism.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass


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


@dataclass
class AgentInfo:
    """Information about an agent."""
    name: str
    role: str
    assigned_tools: List[str]
    missing_tools: List[str]


class ManualToolInventory:
    """Manual tool inventory analyzer."""
    
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
    
    def discover_tools_manually(self):
        """Manually discover tools by examining tool files."""
        print("🔍 Manually discovering tools...")
        
        # Define tool directories to search
        tool_directories = [
            "kickai/features/player_registration/domain/tools",
            "kickai/features/team_administration/domain/tools", 
            "kickai/features/match_management/domain/tools",
            "kickai/features/communication/domain/tools",
            "kickai/features/system_infrastructure/domain/tools",
            "kickai/features/shared/domain/tools"
        ]
        
        total_tools = 0
        
        for tool_dir in tool_directories:
            if not os.path.exists(tool_dir):
                continue
                
            feature_name = tool_dir.split('/')[2]  # Extract feature name
            print(f"  📁 Scanning {feature_name}...")
            
            for file_path in Path(tool_dir).glob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                    
                tools_found = self._extract_tools_from_file(file_path, feature_name)
                total_tools += len(tools_found)
                
                for tool_name, tool_info in tools_found.items():
                    self.tools[tool_name] = tool_info
        
        print(f"✅ Manual discovery complete: {total_tools} tools found")
        return True
    
    def _extract_tools_from_file(self, file_path: Path, feature_name: str) -> Dict[str, ToolInfo]:
        """Extract tool information from a file."""
        tools = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all @tool decorators
            tool_pattern = r'@tool\([\'"]([^\'"]+)[\'"]\)'
            matches = re.findall(tool_pattern, content)
            print(f"    🔍 Found {len(matches)} tool decorators in {file_path.name}")
            
            for tool_name in matches:
                # Try to find the function definition - handle both sync and async functions
                func_patterns = [
                    rf'@tool\([\'"]({re.escape(tool_name)})[\'"]\)\s*\ndef\s+\w+\s*\(',
                    rf'@tool\([\'"]({re.escape(tool_name)})[\'"]\)\s*\nasync\s+def\s+\w+\s*\(',
                ]
                
                func_found = False
                for pattern in func_patterns:
                    func_match = re.search(pattern, content)
                    if func_match:
                        func_found = True
                        break
                
                if func_found:
                    # Try to extract docstring - more flexible pattern
                    docstring_patterns = [
                        rf'@tool\([\'"]({re.escape(tool_name)})[\'"]\)\s*\n(?:async\s+)?def\s+\w+\s*\([^)]*\):\s*"""(.*?)"""',
                        rf'@tool\([\'"]({re.escape(tool_name)})[\'"]\)\s*\n(?:async\s+)?def\s+\w+\s*\([^)]*\):\s*\n\s*"""(.*?)"""',
                    ]
                    
                    description = f"Tool: {tool_name}"
                    for pattern in docstring_patterns:
                        docstring_match = re.search(pattern, content, re.DOTALL)
                        if docstring_match:
                            description = docstring_match.group(1).strip()
                            break
                    
                    tool_info = ToolInfo(
                        name=tool_name,
                        file_path=str(file_path),
                        feature_module=feature_name,
                        description=description,
                        is_implemented=True,
                        is_assigned=False,
                        assigned_agents=[]
                    )
                    
                    tools[tool_name] = tool_info
                    print(f"    ✅ Found tool: {tool_name}")
                else:
                    print(f"    ⚠️  Could not find function definition for tool: {tool_name}")
            
        except Exception as e:
            print(f"    ⚠️  Error reading {file_path}: {e}")
        
        return tools
    
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
                missing_tools=[]
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
        print("🔍 MANUAL TOOL INVENTORY AUDIT REPORT")
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
            categories[tool.feature_module] = categories.get(tool.feature_module, 0) + 1
        for category, count in sorted(categories.items()):
            print(f"   {category}: {count} tools")
        
        # All Tools
        print(f"\n🔧 ALL DISCOVERED TOOLS:")
        for tool_name, tool in sorted(self.tools.items()):
            status = "✅ ASSIGNED" if tool.is_assigned else "❌ UNUSED"
            print(f"   {status} {tool_name} ({tool.feature_module})")
            print(f"     Description: {tool.description[:80]}...")
            if tool.assigned_agents:
                print(f"     Assigned to: {', '.join(tool.assigned_agents)}")
        
        # Unused Tools
        unused_tools = [name for name, tool in self.tools.items() if not tool.is_assigned]
        if unused_tools:
            print(f"\n🗑️  UNUSED TOOLS (can be deleted):")
            for tool_name in sorted(unused_tools):
                tool = self.tools[tool_name]
                print(f"   - {tool_name} ({tool.feature_module})")
                print(f"     File: {tool.file_path}")
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
                    print(f"     ✅ {tool_name} ({tool.feature_module})")
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
Generated by manual_tool_inventory.py
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
    
    # List of unused tools to remove with their file paths
    unused_tools_with_files = [
'''
        
        for tool_name in unused_tools:
            tool = self.tools[tool_name]
            script += f'        ("{tool_name}", "{tool.file_path}"),\n'
        
        script += '''    ]
    
    # Remove each unused tool
    removed_count = 0
    for tool_name, file_path in unused_tools_with_files:
        if remove_tool_from_file(file_path, tool_name):
            removed_count += 1
    
    print(f"✅ Cleanup complete. Removed {removed_count} unused tools.")

if __name__ == "__main__":
    main()
'''
        return script


def main():
    """Main audit function."""
    print("🔍 Starting Manual Tool Inventory Audit...")
    
    auditor = ManualToolInventory()
    
    # Load agents configuration
    if not auditor.load_agents_config():
        return False
    
    # Discover tools manually
    if not auditor.discover_tools_manually():
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
    
    print(f"\n✅ Manual tool inventory audit complete!")
    return True


if __name__ == "__main__":
    main()
