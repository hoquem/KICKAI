import unittest
from unittest.mock import Mock
from .test_utils import MockLLM, MockAgent


class BaseTestCase(unittest.TestCase):
    """Base class for synchronous test cases."""
    
    def setup_method(self, method=None):
        """Set up test environment."""
        pass
    
    def create_mock_llm(self, responses=None):
        """Create a mock LLM for testing."""
        return MockLLM(responses)
    
    def create_mock_agent(self, name="mock_agent", role="general"):
        """Create a mock agent for testing."""
        return MockAgent(name, role)
    
    def create_mock_service(self, service_name):
        """Create a mock service for testing."""
        return Mock(name=service_name)


class AsyncBaseTestCase(unittest.IsolatedAsyncioTestCase):
    """Base class for asynchronous test cases (Python 3.8+)."""
    
    def setup_method(self, method=None):
        """Set up test environment."""
        pass
    
    def create_mock_llm(self, responses=None):
        """Create a mock LLM for testing."""
        return MockLLM(responses)
    
    def create_mock_agent(self, name="mock_agent", role="general"):
        """Create a mock agent for testing."""
        return MockAgent(name, role)
    
    def create_mock_service(self, service_name):
        """Create a mock service for testing."""
        return Mock(name=service_name) 