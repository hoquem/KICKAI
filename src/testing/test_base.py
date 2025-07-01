"""
Test Base Classes for KICKAI

This module provides base classes for different types of tests,
including unit tests, integration tests, and async tests.
"""

import asyncio
import pytest
import unittest
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, AsyncMock, patch
from abc import ABC, abstractmethod

from src.testing.test_utils import (
    MockTool, MockLLM, MockAgent, MockService, AsyncMockService,
    MockDatabase, MockTelegramBot, TestContext
)
from src.testing.test_fixtures import (
    TestDataFactory, SampleData, MockDataBuilder,
    create_sample_team_with_players, create_sample_agent_with_tools,
    create_complete_test_scenario
)


class BaseTestCase(unittest.TestCase):
    """
    Base test case class for all KICKAI tests.
    
    Provides common setup, teardown, and utility methods
    for consistent test behavior across the system.
    """
    
    def setup_method(self, method=None):
        """Set up test method."""
        self.test_context = TestContext()
        self.mock_data = {}
        self.setup_mocks()
        self.setup_test_data()
    
    def teardown_method(self, method=None):
        """Tear down test method."""
        self.test_context.cleanup()
        self.cleanup_test_data()
    
    def setup_mocks(self):
        """Set up mock objects for the test."""
        # Override in subclasses to set up specific mocks
        pass
    
    def setup_test_data(self):
        """Set up test data for the test."""
        # Override in subclasses to set up specific test data
        pass
    
    def cleanup_test_data(self):
        """Clean up test data after the test."""
        # Override in subclasses to clean up specific test data
        pass
    
    def create_mock_tool(self, name: str = "test_tool", return_value: str = "test_result") -> MockTool:
        """Create a mock tool for testing."""
        tool = MockTool(name=name, return_value=return_value)
        self.test_context.add_mock(tool)
        return tool
    
    def create_mock_llm(self, responses: Optional[List[str]] = None) -> MockLLM:
        """Create a mock LLM for testing."""
        llm = MockLLM(responses=responses)
        self.test_context.add_mock(llm)
        return llm
    
    def create_mock_agent(self, name: str = "test_agent", role: str = "Mock Agent", response: str = "test response") -> MockAgent:
        """Create a mock agent for testing."""
        agent = MockAgent(name=name, role=role, response=response)
        self.test_context.add_mock(agent)
        return agent
    
    def create_mock_service(self, service_name: str = "test_service") -> AsyncMockService:
        """Create a mock service for testing."""
        service = AsyncMockService(service_name=service_name)
        self.test_context.add_mock(service)
        return service
    
    def create_mock_database(self) -> MockDatabase:
        """Create a mock database for testing."""
        db = MockDatabase()
        self.test_context.add_mock(db)
        return db
    
    def create_mock_telegram_bot(self, bot_token: str = "test_token") -> MockTelegramBot:
        """Create a mock Telegram bot for testing."""
        bot = MockTelegramBot(bot_token=bot_token)
        self.test_context.add_mock(bot)
        return bot
    
    def assert_mock_called(self, mock, expected_calls: int = 1):
        """Assert that a mock was called the expected number of times."""
        assert mock.call_count == expected_calls, f"Expected {expected_calls} calls, got {mock.call_count}"
    
    def assert_mock_not_called(self, mock):
        """Assert that a mock was not called."""
        assert mock.call_count == 0, f"Expected 0 calls, got {mock.call_count}"
    
    def assert_mock_called_with(self, mock, *args, **kwargs):
        """Assert that a mock was called with specific arguments."""
        mock.assert_called_with(*args, **kwargs)
    
    def assert_mock_called_once_with(self, mock, *args, **kwargs):
        """Assert that a mock was called exactly once with specific arguments."""
        mock.assert_called_once_with(*args, **kwargs)


class AsyncBaseTestCase(BaseTestCase):
    """
    Base test case class for async tests.
    
    Provides async setup, teardown, and utility methods
    for testing async functionality.
    """
    
    @pytest.mark.asyncio
    async def async_setup_method(self):
        """Async set up test method."""
        self.test_context = TestContext()
        self.mock_data = {}
        await self.async_setup_mocks()
        await self.async_setup_test_data()
    
    @pytest.mark.asyncio
    async def async_teardown_method(self):
        """Async tear down test method."""
        await self.async_cleanup_test_data()
        self.test_context.cleanup()
    
    async def async_setup_mocks(self):
        """Set up async mock objects for the test."""
        # Override in subclasses to set up specific async mocks
        pass
    
    async def async_setup_test_data(self):
        """Set up async test data for the test."""
        # Override in subclasses to set up specific async test data
        pass
    
    async def async_cleanup_test_data(self):
        """Clean up async test data after the test."""
        # Override in subclasses to clean up specific async test data
        pass
    
    async def create_async_mock_service(self, service_name: str = "test_service") -> AsyncMockService:
        """Create an async mock service for testing."""
        service = AsyncMockService(service_name=service_name)
        self.test_context.add_mock(service)
        return service
    
    async def run_async_function(self, func, *args, **kwargs):
        """Run an async function and return the result."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    async def assert_async_mock_called(self, mock, expected_calls: int = 1):
        """Assert that an async mock was called the expected number of times."""
        # Wait a bit for async operations to complete
        await asyncio.sleep(0.1)
        assert mock.call_count == expected_calls, f"Expected {expected_calls} calls, got {mock.call_count}"
    
    async def assert_async_mock_not_called(self, mock):
        """Assert that an async mock was not called."""
        # Wait a bit for async operations to complete
        await asyncio.sleep(0.1)
        assert mock.call_count == 0, f"Expected 0 calls, got {mock.call_count}"


class IntegrationTestCase(AsyncBaseTestCase):
    """
    Base test case class for integration tests.
    
    Provides integration test setup, teardown, and utility methods
    for testing system-wide functionality.
    """
    
    def setup_method(self):
        """Set up integration test method."""
        super().setup_method()
        self.integration_mocks = {}
        self.setup_integration_mocks()
    
    def teardown_method(self):
        """Tear down integration test method."""
        self.cleanup_integration_mocks()
        super().teardown_method()
    
    def setup_integration_mocks(self):
        """Set up mocks for integration testing."""
        # Mock external services
        self.integration_mocks['firebase'] = self.create_mock_database()
        self.integration_mocks['telegram'] = self.create_mock_telegram_bot()
        
        # Mock AI services
        self.integration_mocks['llm'] = self.create_mock_llm()
        
        # Mock agent services
        self.integration_mocks['player_agent'] = self.create_mock_agent("Player Manager")
        self.integration_mocks['fixture_agent'] = self.create_mock_agent("Fixture Coordinator")
        
        # Mock tools
        self.integration_mocks['player_tools'] = self.create_mock_tool("player_tools")
        self.integration_mocks['team_tools'] = self.create_mock_tool("team_tools")
        self.integration_mocks['fixture_tools'] = self.create_mock_tool("fixture_tools")
    
    def cleanup_integration_mocks(self):
        """Clean up integration test mocks."""
        for mock in self.integration_mocks.values():
            if hasattr(mock, 'reset_mock'):
                mock.reset_mock()
        self.integration_mocks.clear()
    
    def create_integration_test_scenario(self) -> Dict[str, Any]:
        """Create a complete integration test scenario."""
        return create_complete_test_scenario()
    
    def assert_integration_flow_complete(self, flow_result: Dict[str, Any]):
        """Assert that an integration flow completed successfully."""
        assert flow_result is not None
        assert 'status' in flow_result
        assert flow_result['status'] in ['success', 'completed']
    
    def assert_service_interaction(self, service_mock, expected_method: str, expected_calls: int = 1):
        """Assert that a service was called with the expected method."""
        assert hasattr(service_mock, expected_method)
        method_mock = getattr(service_mock, expected_method)
        assert method_mock.call_count == expected_calls


class UnitTestCase(BaseTestCase):
    """
    Base test case class for unit tests.
    
    Provides unit test setup, teardown, and utility methods
    for testing individual components in isolation.
    """
    
    def setup_method(self):
        """Set up unit test method."""
        super().setup_method()
        self.unit_mocks = {}
        self.setup_unit_mocks()
    
    def teardown_method(self):
        """Tear down unit test method."""
        self.cleanup_unit_mocks()
        super().teardown_method()
    
    def setup_unit_mocks(self):
        """Set up mocks for unit testing."""
        # Override in subclasses to set up specific unit test mocks
        pass
    
    def cleanup_unit_mocks(self):
        """Clean up unit test mocks."""
        for mock in self.unit_mocks.values():
            if hasattr(mock, 'reset_mock'):
                mock.reset_mock()
        self.unit_mocks.clear()
    
    def assert_component_behavior(self, component, expected_behavior: Dict[str, Any]):
        """Assert that a component behaves as expected."""
        for behavior, expected_value in expected_behavior.items():
            if hasattr(component, behavior):
                actual_value = getattr(component, behavior)
                assert actual_value == expected_value, f"Expected {behavior}={expected_value}, got {actual_value}"
    
    def assert_method_returns(self, obj, method_name: str, expected_return: Any, *args, **kwargs):
        """Assert that a method returns the expected value."""
        method = getattr(obj, method_name)
        result = method(*args, **kwargs)
        assert result == expected_return, f"Expected {expected_return}, got {result}"


class PerformanceTestCase(AsyncBaseTestCase):
    """
    Base test case class for performance tests.
    
    Provides performance test setup, teardown, and utility methods
    for testing system performance and scalability.
    """
    
    def setup_method(self):
        """Set up performance test method."""
        super().setup_method()
        self.performance_metrics = {}
        self.setup_performance_mocks()
    
    def teardown_method(self):
        """Tear down performance test method."""
        self.cleanup_performance_mocks()
        super().teardown_method()
    
    def setup_performance_mocks(self):
        """Set up mocks for performance testing."""
        # Override in subclasses to set up specific performance test mocks
        pass
    
    def cleanup_performance_mocks(self):
        """Clean up performance test mocks."""
        # Override in subclasses to clean up specific performance test mocks
        pass
    
    async def measure_execution_time(self, func, *args, **kwargs) -> float:
        """Measure the execution time of a function."""
        import time
        start_time = time.time()
        
        if asyncio.iscoroutinefunction(func):
            await func(*args, **kwargs)
        else:
            func(*args, **kwargs)
        
        end_time = time.time()
        return end_time - start_time
    
    def assert_performance_threshold(self, execution_time: float, max_time: float):
        """Assert that execution time is within acceptable threshold."""
        assert execution_time <= max_time, f"Execution time {execution_time}s exceeds threshold {max_time}s"
    
    def record_performance_metric(self, metric_name: str, value: float):
        """Record a performance metric for analysis."""
        self.performance_metrics[metric_name] = value
    
    def get_performance_summary(self) -> Dict[str, float]:
        """Get a summary of recorded performance metrics."""
        return self.performance_metrics.copy()


class SecurityTestCase(BaseTestCase):
    """
    Base test case class for security tests.
    
    Provides security test setup, teardown, and utility methods
    for testing system security and vulnerability assessment.
    """
    
    def setup_method(self):
        """Set up security test method."""
        super().setup_method()
        self.security_vulnerabilities = []
        self.setup_security_mocks()
    
    def teardown_method(self):
        """Tear down security test method."""
        self.cleanup_security_mocks()
        super().teardown_method()
    
    def setup_security_mocks(self):
        """Set up mocks for security testing."""
        # Override in subclasses to set up specific security test mocks
        pass
    
    def cleanup_security_mocks(self):
        """Clean up security test mocks."""
        # Override in subclasses to clean up specific security test mocks
        pass
    
    def assert_input_validation(self, validator_func, valid_inputs: List[Any], invalid_inputs: List[Any]):
        """Assert that input validation works correctly."""
        # Test valid inputs
        for valid_input in valid_inputs:
            try:
                result = validator_func(valid_input)
                assert result is not None, f"Validator should accept {valid_input}"
            except Exception as e:
                assert False, f"Validator should accept {valid_input}, but raised {e}"
        
        # Test invalid inputs
        for invalid_input in invalid_inputs:
            try:
                result = validator_func(invalid_input)
                assert result is None or result is False, f"Validator should reject {invalid_input}"
            except Exception:
                # Expected behavior for invalid input
                pass
    
    def assert_authentication_required(self, protected_func, *args, **kwargs):
        """Assert that a function requires authentication."""
        try:
            protected_func(*args, **kwargs)
            assert False, "Function should require authentication"
        except Exception as e:
            # Expected behavior - function should raise an authentication error
            assert "auth" in str(e).lower() or "unauthorized" in str(e).lower()
    
    def assert_authorization_required(self, protected_func, *args, **kwargs):
        """Assert that a function requires proper authorization."""
        try:
            protected_func(*args, **kwargs)
            assert False, "Function should require authorization"
        except Exception as e:
            # Expected behavior - function should raise an authorization error
            assert "permission" in str(e).lower() or "forbidden" in str(e).lower()
    
    def record_security_vulnerability(self, vulnerability_type: str, description: str, severity: str = "medium"):
        """Record a security vulnerability for analysis."""
        self.security_vulnerabilities.append({
            'type': vulnerability_type,
            'description': description,
            'severity': severity
        })
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get a security test report."""
        return {
            'vulnerabilities': self.security_vulnerabilities,
            'total_vulnerabilities': len(self.security_vulnerabilities),
            'high_severity': len([v for v in self.security_vulnerabilities if v['severity'] == 'high']),
            'medium_severity': len([v for v in self.security_vulnerabilities if v['severity'] == 'medium']),
            'low_severity': len([v for v in self.security_vulnerabilities if v['severity'] == 'low'])
        }


# Convenience decorators for common test patterns
def mock_external_service(service_name: str):
    """Decorator to mock external services for tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch(f'src.services.{service_name}') as mock_service:
                return func(*args, **kwargs, mock_service=mock_service)
        return wrapper
    return decorator


def mock_database_operations():
    """Decorator to mock database operations for tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch('src.database.firebase_client.FirebaseClient') as mock_db:
                return func(*args, **kwargs, mock_db=mock_db)
        return wrapper
    return decorator


def mock_telegram_api():
    """Decorator to mock Telegram API calls for tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch('src.telegram.player_registration_handler.TelegramBot') as mock_bot:
                return func(*args, **kwargs, mock_bot=mock_bot)
        return wrapper
    return decorator


def mock_ai_services():
    """Decorator to mock AI services for tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with patch('src.intelligent_router.MockLLM') as mock_llm:
                with patch('src.agents.MockAgent') as mock_agent:
                    return func(*args, **kwargs, mock_llm=mock_llm, mock_agent=mock_agent)
        return wrapper
    return decorator 