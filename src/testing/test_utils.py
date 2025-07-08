"""
Test utilities and mock objects for KICKAI tests.
"""

from typing import List, Optional
from unittest.mock import Mock


class MockTool:
    """Mock tool for testing."""
    
    def __init__(self, name: str = "mock_tool", description: str = "A mock tool for testing"):
        self.name = name
        self.description = description
        self.mock = Mock()
    
    def __call__(self, *args, **kwargs):
        """Make the tool callable."""
        return self.mock(*args, **kwargs)
    
    def reset_mock(self):
        """Reset the mock."""
        self.mock.reset_mock()


class MockAgent:
    """Mock agent for testing."""
    
    def __init__(self, name: str = "mock_agent", role: str = "general"):
        self.name = name
        self.role = role
        self.mock = Mock()
        self.tools = []
        self.call_count = 0
        self.last_input = None
    
    def add_tool(self, tool: MockTool):
        """Add a tool to the agent."""
        self.tools.append(tool)
    
    def execute(self, task: str, **kwargs):
        """Mock execute method."""
        self.call_count += 1
        self.last_input = task
        return self.mock(task, **kwargs)
    
    async def aexecute(self, task: str, **kwargs):
        """Mock async execute method."""
        return self.execute(task, **kwargs)
    
    def reset(self):
        """Reset the mock agent."""
        self.call_count = 0
        self.last_input = None
        self.mock.reset_mock()


class MockLLM(Mock):
    """Mock LLM for testing."""
    
    def __init__(self, responses: Optional[List[str]] = None):
        super().__init__()
        self.responses = responses or ["Mock LLM response"]
        self.response_index = 0
        self.call_count = 0
        self.last_input = None
        
        # Create a mock for the invoke method
        self.invoke = Mock()
        self.ainvoke = Mock()
        
        # Set up default behavior
        if responses:
            self.invoke.return_value = responses[0]
            self.ainvoke.return_value = responses[0]
        else:
            self.invoke.return_value = "Mock LLM response"
            self.ainvoke.return_value = "Mock LLM response"
    
    def reset(self):
        """Reset the mock LLM."""
        self.response_index = 0
        self.call_count = 0
        self.last_input = None
        super().reset_mock()
    
    def set_responses(self, responses: List[str]):
        """Set custom responses."""
        self.responses = responses
        self.reset() 