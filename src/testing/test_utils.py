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


class MockLLM:
    """Mock LLM for testing."""
    
    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or ["Mock LLM response"]
        self.response_index = 0
        self.call_count = 0
        self.last_input = None
    
    def invoke(self, input_text: str, **kwargs) -> str:
        """Mock invoke method."""
        self.call_count += 1
        self.last_input = input_text
        
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response
        else:
            return "Default mock response"
    
    async def ainvoke(self, input_text: str, **kwargs) -> str:
        """Mock async invoke method."""
        return self.invoke(input_text, **kwargs)
    
    def reset(self):
        """Reset the mock LLM."""
        self.response_index = 0
        self.call_count = 0
        self.last_input = None
    
    def set_responses(self, responses: List[str]):
        """Set custom responses."""
        self.responses = responses
        self.reset() 