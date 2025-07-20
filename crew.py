#!/usr/bin/env python3
"""
KICKAI YAML-based CrewAI Configuration

This module loads agent and task configurations from YAML files
and creates a CrewAI crew for processing user requests.
"""

import os
import yaml
from typing import List, Dict, Any
from pathlib import Path

from crewai import Agent, Task, Crew
from src.agents.tool_registry import ToolRegistry
from src.config.llm_config import get_llm_config


class KICKAICrew:
    """KICKAI CrewAI crew with YAML-based configuration."""
    
    def __init__(self):
        """Initialize the KICKAI crew with YAML configuration."""
        self.llm = get_llm_config()
        self.tool_registry = ToolRegistry()
        self.agents = {}
        self.tasks = {}
        self.crew = None
        
        # Load configurations
        self._load_configurations()
        self._create_agents()
        self._create_tasks()
        self._create_crew()
    
    def _load_configurations(self):
        """Load agent and task configurations from YAML files."""
        config_dir = Path(__file__).parent / "src" / "config"
        
        # Load agents configuration
        agents_file = config_dir / "agents.yaml"
        with open(agents_file, 'r') as f:
            self.agents_config = yaml.safe_load(f)
        
        # Load tasks configuration
        tasks_file = config_dir / "tasks.yaml"
        with open(tasks_file, 'r') as f:
            self.tasks_config = yaml.safe_load(f)
        
        print(f"✅ Loaded {len(self.agents_config['agents'])} agents from {agents_file}")
        print(f"✅ Loaded {len(self.tasks_config['tasks'])} tasks from {tasks_file}")
    
    def _create_agents(self):
        """Create CrewAI agents from YAML configuration."""
        for agent_config in self.agents_config['agents']:
            agent_name = agent_config['name']
            
            # Get tools for this agent
            tool_names = agent_config.get('tools', [])
            tools = self._get_tools_for_agent(tool_names)
            
            # Create agent
            agent = Agent(
                role=agent_config['role'],
                goal=agent_config['goal'],
                backstory=agent_config['backstory'],
                tools=tools,
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            self.agents[agent_name] = agent
            print(f"✅ Created agent: {agent_name} with {len(tools)} tools")
    
    def _get_tools_for_agent(self, tool_names: List[str]) -> List[Any]:
        """Get tool objects for agent based on tool names."""
        tools = []
        for tool_name in tool_names:
            tool_metadata = self.tool_registry.get_tool(tool_name)
            if tool_metadata and hasattr(tool_metadata, 'tool_function') and tool_metadata.tool_function:
                tools.append(tool_metadata.tool_function)
                print(f"✅ Found tool '{tool_name}' for agent")
            else:
                print(f"Warning: Tool '{tool_name}' not found in registry or has no function")
        return tools
    
    def _create_tasks(self):
        """Create CrewAI tasks from YAML configuration."""
        for task_config in self.tasks_config['tasks']:
            task_name = task_config['name']
            agent_name = task_config['agent']
            
            if agent_name not in self.agents:
                print(f"Warning: Agent '{agent_name}' not found for task '{task_name}'")
                continue
            
            # Create task
            task = Task(
                description=task_config['description'],
                expected_output=task_config['expected_output'],
                agent=self.agents[agent_name]
            )
            
            self.tasks[task_name] = task
            print(f"✅ Created task: {task_name} assigned to {agent_name}")
    
    def _create_crew(self):
        """Create the CrewAI crew with all agents and tasks."""
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            verbose=True,
            memory=True
        )
        print(f"✅ Created crew with {len(self.agents)} agents and {len(self.tasks)} tasks")
    
    def process_request(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Process a user request through the CrewAI crew.
        
        Args:
            user_input: The user's input text
            context: Additional context for processing
            
        Returns:
            The processed response
        """
        try:
            # For now, use the first task as default
            # In a real implementation, you'd route to appropriate tasks based on input
            default_task = list(self.tasks.values())[0] if self.tasks else None
            
            if default_task:
                result = self.crew.kickoff({
                    "user_input": user_input,
                    "context": context or {}
                })
                return result
            else:
                return "No tasks available for processing."
                
        except Exception as e:
            print(f"Error processing request: {e}")
            return f"Error processing request: {str(e)}"


def get_kickai_crew() -> KICKAICrew:
    """Get the KICKAI crew instance."""
    return KICKAICrew()


if __name__ == "__main__":
    # Test the crew
    print("🧪 Testing KICKAI YAML-based CrewAI configuration...")
    
    crew = get_kickai_crew()
    
    # Test processing
    test_input = "What commands are available?"
    result = crew.process_request(test_input)
    
    print(f"\n📝 Test Result:")
    print(f"Input: {test_input}")
    print(f"Output: {result}")
    
    print("\n✅ Crew test completed successfully!") 