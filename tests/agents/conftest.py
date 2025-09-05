"""
Test configuration for CrewAI Agents Tests

This module provides fixtures and configuration for the agent testing categories
implemented from CREWAI_AGENTS_TEST_SPECIFICATION.md.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List

from kickai.agents.agent_types import AgentRole, AgentContext
from kickai.agents.configurable_agent import ConfigurableAgent
from kickai.agents.crew_agents import TeamManagementSystem
from kickai.core.team_system_manager import get_team_system
# Removed entity_specific_agents import - using simplified 5-agent architecture
# Removed old Ollama imports - using new SimpleLLMFactory instead


# Test configuration from specification
TEST_CONFIG = {
    "ollama_base_url": "http://macmini1.local:11434",
    "ollama_model": "llama3.1:8b-instruct-q4_0",
    "test_team_id": "test_team_alpha",
    "test_user_id": "test_user_123",
    "mock_services": True,
    "isolated_database": True
}

# Test data setup
TEST_DATA = {
    "teams": [
        {"id": "test_team_alpha", "name": "Test Team Alpha"},
        {"id": "test_team_beta", "name": "Test Team Beta"}
    ],
    "users": [
        {"id": "test_user_123", "name": "Test User", "phone": "+1234567890"},
        {"id": "test_user_456", "name": "Another User", "phone": "+0987654321"}
    ],
    "players": [
        {"id": "player_001", "name": "John Doe", "position": "Forward"},
        {"id": "player_002", "name": "Jane Smith", "position": "Midfielder"}
    ]
}


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return TEST_CONFIG


@pytest.fixture(scope="session")
def test_data():
    """Provide test data."""
    return TEST_DATA


@pytest.fixture(scope="function")
def mock_llm():
    """Create mock LLM for testing using new SimpleLLMFactory pattern."""
    mock_llm = Mock()
    mock_llm.invoke = Mock(return_value="Mock response")
    mock_llm.ainvoke = AsyncMock(return_value="Mock response")
    mock_llm.__call__ = Mock(return_value="Mock response")
    return mock_llm


@pytest.fixture(scope="function")
def mock_llm_config():
    """Create mock LLM configuration for testing."""
    return {
        "base_url": TEST_CONFIG["ollama_base_url"],
        "model": TEST_CONFIG["ollama_model"],
        "temperature": 0.7,
        "max_tokens": 800
    }


@pytest.fixture(scope="function")
def test_agent_context():
    """Create test agent context."""
    return AgentContext(
        role=AgentRole.PLAYER_COORDINATOR,
        team_id=TEST_CONFIG["test_team_id"],
        llm=Mock(),
        tool_registry=Mock(),
        config=None,
        team_memory=None
    )


@pytest.fixture(scope="function")
def coordinator_agent(test_agent_context):
    """Create player coordinator agent for testing."""
    # Use the new ConfigurableAgent approach
    return ConfigurableAgent(
        role=AgentRole.PLAYER_COORDINATOR,
        team_id=TEST_CONFIG["test_team_id"]
    )


@pytest.fixture(scope="function")
def manager_agent(test_agent_context):
    """Create team manager agent for testing."""
    # Use the new ConfigurableAgent approach
    return ConfigurableAgent(
        role=AgentRole.TEAM_MANAGER,
        team_id=TEST_CONFIG["test_team_id"]
    )


@pytest.fixture(scope="function")
def configurable_agent(test_agent_context):
    """Create configurable agent for testing."""
    return ConfigurableAgent(
        role=AgentRole.PLAYER_COORDINATOR,
        context=test_agent_context
    )


@pytest.fixture(scope="function")
def mock_tool():
    """Create mock tool for testing."""
    tool = Mock()
    tool.name = "test_tool"
    tool.description = "A test tool for validation"
    tool.execute = AsyncMock(return_value="test_result")
    return tool


@pytest.fixture(scope="function")
def mock_tools():
    """Create multiple mock tools for testing."""
    tools = []
    for i in range(3):
        tool = Mock()
        tool.name = f"test_tool_{i}"
        tool.description = f"Test tool {i}"
        tool.execute = AsyncMock(return_value=f"result_{i}")
        tools.append(tool)
    return tools


@pytest.fixture(scope="function")
def failing_tool():
    """Create mock tool that fails."""
    tool = Mock()
    tool.name = "failing_tool"
    tool.description = "A tool that fails"
    tool.execute = AsyncMock(side_effect=Exception("Tool failed"))
    return tool


@pytest.fixture(scope="function")
def mock_telegram_service():
    """Create mock Telegram service for testing."""
    service = Mock()
    service.sent_messages = []
    service.received_messages = []
    
    async def send_message(chat_id: str, text: str):
        service.sent_messages.append({"chat_id": chat_id, "text": text})
        return {"message_id": len(service.sent_messages)}
    
    async def get_updates():
        return service.received_messages
    
    service.send_message = send_message
    service.get_updates = get_updates
    return service


@pytest.fixture(scope="function")
def mock_database_service():
    """Create mock database service for testing."""
    service = Mock()
    service.data = {}
    
    async def get_player(player_id: str):
        return service.data.get(f"player_{player_id}")
    
    async def save_player(player_data: dict):
        player_id = player_data.get("id")
        service.data[f"player_{player_id}"] = player_data
        return player_data
    
    async def update_player(player_id: str, player_data: dict):
        service.data[f"player_{player_id}"] = player_data
        return player_data
    
    service.get_player = get_player
    service.save_player = save_player
    service.update_player = update_player
    return service


@pytest.fixture(scope="function")
def reasoning_validator():
    """Create reasoning validator for testing."""
    from tests.agents.reasoning.test_reasoning_validation import OllamaReasoningValidator
    return OllamaReasoningValidator()


@pytest.fixture(scope="function")
def test_workflow_data():
    """Provide test workflow data."""
    return {
        "registration_flow": [
            "I want to register as a player",
            "My phone number is +1234567890",
            "My position is Forward"
        ],
        "team_management_flow": [
            "Show me the current team roster",
            "Add player Jane Smith to the roster",
            "Change Jane Smith's position to Defender"
        ],
        "help_flow": [
            "Help me understand what I can do",
            "How do I register for matches?",
            "What are the team rules?"
        ],
        "error_recovery_flow": [
            "Invalid command that doesn't exist",
            "What went wrong?",
            "How do I fix this?"
        ]
    }


@pytest.fixture(scope="function")
def performance_metrics():
    """Track performance metrics during tests."""
    return {
        "response_times": [],
        "memory_usage": [],
        "error_counts": 0,
        "success_counts": 0
    }


@pytest.fixture(scope="function")
def test_scenarios():
    """Provide test scenarios for comprehensive testing."""
    return {
        "player_registration": {
            "valid": {
                "name": "John Doe",
                "phone": "+1234567890",
                "position": "Forward"
            },
            "invalid": {
                "name": "",
                "phone": "123",
                "position": ""
            }
        },
        "team_management": {
            "roster_operations": [
                "add_player",
                "remove_player", 
                "update_position"
            ],
            "schedule_operations": [
                "add_training",
                "schedule_match",
                "update_schedule"
            ]
        },
        "error_scenarios": [
            "network_failure",
            "invalid_data",
            "permission_denied",
            "timeout_error"
        ]
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test (Groq-only)."""
    import os
    os.environ.update({
        'ENVIRONMENT': 'testing',
        'TESTING': 'true',
        'AI_PROVIDER': 'groq'
    })

    yield

    # Cleanup after test
    pass


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestDataProvider:
    """Provide test data for various scenarios."""
    
    @staticmethod
    def get_player_registration_data():
        """Get player registration test data."""
        return {
            "valid_players": [
                {"name": "Alice Johnson", "phone": "+1234567890", "position": "Forward"},
                {"name": "Bob Smith", "phone": "+0987654321", "position": "Midfielder"},
                {"name": "Carol Davis", "phone": "+1122334455", "position": "Defender"}
            ],
            "invalid_players": [
                {"name": "", "phone": "123", "position": ""},
                {"name": "Test", "phone": "invalid", "position": "Unknown"},
                {"name": "A" * 100, "phone": "+1234567890", "position": "Forward"}
            ]
        }
    
    @staticmethod
    def get_team_management_data():
        """Get team management test data."""
        return {
            "teams": [
                {"id": "team_alpha", "name": "Team Alpha", "level": "competitive"},
                {"id": "team_beta", "name": "Team Beta", "level": "recreational"},
                {"id": "team_gamma", "name": "Team Gamma", "level": "training"}
            ],
            "policies": [
                {"type": "attendance", "requirement": "80%"},
                {"type": "payment", "requirement": "$50/month"},
                {"type": "conduct", "requirement": "sportsmanship"}
            ]
        }
    
    @staticmethod
    def get_error_scenarios():
        """Get error scenario test data."""
        return {
            "network_errors": [
                "Connection timeout",
                "DNS resolution failed",
                "Server unavailable"
            ],
            "validation_errors": [
                "Invalid phone number format",
                "Missing required field",
                "Invalid position value"
            ],
            "permission_errors": [
                "Unauthorized access",
                "Insufficient privileges",
                "Role-based restriction"
            ]
        }


@pytest.fixture
def test_data_provider():
    """Provide test data provider."""
    return TestDataProvider() 