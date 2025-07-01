"""
Test Utilities for KICKAI

This module provides comprehensive test utilities that are compatible with CrewAI
and provide proper mocking capabilities for all system components.
"""

import asyncio
from typing import Dict, Any, Optional, List, Union, Callable
from unittest.mock import Mock, AsyncMock, MagicMock
from dataclasses import dataclass
from datetime import datetime
import json

from crewai import Agent, Task, Crew
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from src.tools.firebase_tools import BaseTool
from pydantic import Field

from src.core.config import DatabaseConfig, AIConfig, TelegramConfig, AIProvider
from src.core.exceptions import KICKAIError
from src.database.models import Player, Team, PlayerPosition, PlayerRole, OnboardingStatus, TeamStatus


@dataclass
class MockConfig:
    """Mock configuration for testing."""
    database: DatabaseConfig
    ai: AIConfig
    telegram: TelegramConfig


class MockFirebaseClient:
    """Mock Firebase client for testing."""
    
    def __init__(self):
        self._players: Dict[str, Player] = {}
        self._teams: Dict[str, Team] = {}
        self._bot_mappings: Dict[str, Any] = {}
        self._team_members: Dict[str, Any] = {}
    
    async def create_player(self, player: Player) -> str:
        """Mock create player."""
        player_id = player.id or f"player_{len(self._players) + 1}"
        player.id = player_id
        self._players[player_id] = player
        return player_id
    
    async def get_player(self, player_id: str) -> Optional[Player]:
        """Mock get player."""
        return self._players.get(player_id)
    
    async def update_player(self, player: Player) -> bool:
        """Mock update player."""
        if player.id in self._players:
            self._players[player.id] = player
            return True
        return False
    
    async def delete_player(self, player_id: str) -> bool:
        """Mock delete player."""
        if player_id in self._players:
            del self._players[player_id]
            return True
        return False
    
    async def get_players_by_team(self, team_id: str) -> List[Player]:
        """Mock get players by team."""
        return [player for player in self._players.values() if player.team_id == team_id]
    
    async def get_player_by_phone(self, phone: str, team_id: str) -> Optional[Player]:
        """Mock get player by phone."""
        for player in self._players.values():
            if player.phone == phone and player.team_id == team_id:
                return player
        return None
    
    async def create_team(self, team: Team) -> str:
        """Mock create team."""
        team_id = team.id or f"team_{len(self._teams) + 1}"
        team.id = team_id
        self._teams[team_id] = team
        return team_id
    
    async def get_team(self, team_id: str) -> Optional[Team]:
        """Mock get team."""
        return self._teams.get(team_id)
    
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Mock get team by name."""
        for team in self._teams.values():
            if team.name == name:
                return team
        return None
    
    async def update_team(self, team: Team) -> bool:
        """Mock update team."""
        if team.id in self._teams:
            self._teams[team.id] = team
            return True
        return False
    
    async def delete_team(self, team_id: str) -> bool:
        """Mock delete team."""
        if team_id in self._teams:
            del self._teams[team_id]
            return True
        return False
    
    async def get_bot_mapping_by_team(self, team_name: str) -> Optional[Any]:
        """Mock get bot mapping by team."""
        return self._bot_mappings.get(team_name)
    
    async def create_document(self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None) -> str:
        """Mock create document."""
        doc_id = document_id or f"{collection}_doc_{len(self._team_members) + 1}"
        self._team_members[doc_id] = data
        return doc_id
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Mock delete document."""
        if document_id in self._team_members:
            del self._team_members[document_id]
            return True
        return False
    
    async def query_documents(self, collection: str, filters: Optional[List[Dict[str, Any]]] = None,
                            order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Mock query documents."""
        # Simple mock implementation
        if collection == 'team_members':
            return list(self._team_members.values())
        elif collection == 'teams':
            return [team.to_dict() for team in self._teams.values()]
        elif collection == 'players':
            return [player.to_dict() for player in self._players.values()]
        return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {
            'status': 'healthy',
            'collections_count': 4,
            'response_time_ms': 1.0,
            'timestamp': datetime.now().isoformat()
        }


class MockTool(BaseTool):
    """
    CrewAI-compatible mock tool for testing.
    
    This tool can be used in place of real tools during testing,
    providing predictable responses without external dependencies.
    """
    
    name: str = "mock_tool"
    description: str = "A mock tool for testing purposes"
    return_value: Any = Field(default="mock_result")
    call_count: int = Field(default=0)
    call_args: list = Field(default_factory=list)

    def __init__(self, name: str = "mock_tool", description: str = "Mock tool", return_value: Any = "mock_result", **kwargs):
        super().__init__(name=name, description=description)
        self.return_value = return_value
        self.call_count = 0
        self.call_args = []

    def _run(self, *args, **kwargs) -> str:
        """Synchronous run method."""
        self.call_count += 1
        self.call_args.append((args, kwargs))
        return str(self.return_value)
    
    async def _arun(self, *args, **kwargs) -> str:
        """Asynchronous run method."""
        self.call_count += 1
        self.call_args.append((args, kwargs))
        return str(self.return_value)

    class Config:
        extra = "allow"


class MockLLM:
    """
    Mock LLM for testing agent interactions.
    
    Provides predictable responses for testing without requiring
    actual LLM API calls.
    """
    
    def __init__(self, responses: Optional[Union[str, List[str]]] = None):
        self.responses = responses if responses else "Mock LLM response"
        self.call_count = 0
        self.call_history = []
        
    def bind(self, *args, **kwargs):
        """Bind method for compatibility with LangChain."""
        return self
    
    def invoke(self, *args, **kwargs) -> str:
        """Invoke method for LangChain compatibility."""
        self.call_count += 1
        self.call_history.append((args, kwargs))
        
        if isinstance(self.responses, list):
            response = self.responses[self.call_count - 1] if self.call_count <= len(self.responses) else self.responses[-1]
        else:
            response = self.responses
            
        return response
    
    def __call__(self, *args, **kwargs) -> str:
        """Call method for direct invocation."""
        return self.invoke(*args, **kwargs)


class MockAgent:
    """
    Mock agent for testing agent interactions.
    
    Simulates agent behavior without requiring full CrewAI agent initialization.
    """
    
    def __init__(self, name: str = "mock_agent", role: str = "Mock Agent", 
                 goal: str = "Mock goal", backstory: str = "Mock backstory",
                 response: str = "Mock agent response"):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.response = response
        self.call_count = 0
        self.call_history = []
        self.tools = []
        
    def add_mock_tool(self, tool: BaseTool):
        """Add a mock tool to the agent."""
        self.tools.append(tool)
        
    def execute_task(self, task: Task) -> str:
        """Execute a task and return a response."""
        self.call_count += 1
        self.call_history.append(task)
        return self.response
    
    async def execute_task_async(self, task: Task) -> str:
        """Execute a task asynchronously."""
        self.call_count += 1
        self.call_history.append(task)
        return self.response


class MockService:
    """
    Base mock service class for testing service layer interactions.
    
    Provides common functionality for mocking service classes.
    """
    
    def __init__(self, service_name: str = "mock_service"):
        self.service_name = service_name
        self.call_count = 0
        self.call_history = []
        
    def _record_call(self, method_name: str, *args, **kwargs):
        """Record a method call for testing verification."""
        self.call_count += 1
        self.call_history.append({
            'method': method_name,
            'args': args,
            'kwargs': kwargs,
            'call_number': self.call_count
        })


class AsyncMockService(MockService):
    """
    Async mock service for testing async service methods.
    
    Provides async-compatible mocking for service classes.
    """
    
    def __init__(self, service_name: str = "mock_service"):
        super().__init__(service_name)
        self._mock_methods = {}
        
    def mock_method(self, method_name: str, return_value: Any = None, 
                   side_effect: Optional[Exception] = None):
        """Mock a specific method with return value or side effect."""
        mock = AsyncMock()
        if side_effect:
            mock.side_effect = side_effect
        else:
            mock.return_value = return_value
        self._mock_methods[method_name] = mock
        setattr(self, method_name, mock)
        
    def __getattr__(self, name):
        """Auto-create async mocks for undefined methods."""
        if name not in self._mock_methods:
            self.mock_method(name)
        return self._mock_methods[name]


class MockDatabase:
    """
    Mock database for testing database operations.
    
    Provides in-memory storage for testing without requiring
    actual database connections.
    """
    
    def __init__(self):
        self.data = {}
        self.call_count = 0
        self.call_history = []
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the mock database."""
        self._record_call('get', key, default)
        return self.data.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set a value in the mock database."""
        self._record_call('set', key, value)
        self.data[key] = value
        
    def delete(self, key: str) -> bool:
        """Delete a value from the mock database."""
        self._record_call('delete', key)
        if key in self.data:
            del self.data[key]
            return True
        return False
        
    def exists(self, key: str) -> bool:
        """Check if a key exists in the mock database."""
        self._record_call('exists', key)
        return key in self.data
        
    def _record_call(self, method: str, *args, **kwargs):
        """Record a database call."""
        self.call_count += 1
        self.call_history.append({
            'method': method,
            'args': args,
            'kwargs': kwargs,
            'call_number': self.call_count
        })


class MockTelegramBot:
    """
    Mock Telegram bot for testing bot interactions.
    
    Simulates Telegram bot behavior without requiring
    actual Telegram API calls.
    """
    
    def __init__(self, bot_token: str = "mock_token"):
        self.bot_token = bot_token
        self.sent_messages = []
        self.call_count = 0
        
    async def send_message(self, chat_id: str, text: str, **kwargs) -> Dict[str, Any]:
        """Send a message and record it for testing."""
        self.call_count += 1
        message = {
            'chat_id': chat_id,
            'text': text,
            'kwargs': kwargs,
            'timestamp': asyncio.get_event_loop().time()
        }
        self.sent_messages.append(message)
        return {'message_id': self.call_count, 'chat': {'id': chat_id}, 'text': text}
        
    async def edit_message_text(self, chat_id: str, message_id: int, text: str, **kwargs) -> Dict[str, Any]:
        """Edit a message and record it for testing."""
        self.call_count += 1
        # Find and update the message
        for msg in self.sent_messages:
            if msg.get('message_id') == message_id:
                msg['text'] = text
                msg['edited'] = True
                break
        return {'message_id': message_id, 'chat': {'id': chat_id}, 'text': text}


class TestContext:
    """
    Test context manager for managing test state and cleanup.
    
    Provides a context for test execution with automatic cleanup.
    """
    
    def __init__(self):
        self.mocks = []
        self.temp_data = {}
        
    def add_mock(self, mock):
        """Add a mock to the context for cleanup."""
        self.mocks.append(mock)
        return mock
        
    def set_temp_data(self, key: str, value: Any):
        """Set temporary data for the test context."""
        self.temp_data[key] = value
        
    def get_temp_data(self, key: str, default: Any = None) -> Any:
        """Get temporary data from the test context."""
        return self.temp_data.get(key, default)
        
    def cleanup(self):
        """Clean up all mocks and temporary data."""
        for mock in self.mocks:
            if hasattr(mock, 'reset_mock'):
                mock.reset_mock()
        self.temp_data.clear()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class MockCrew(Crew):
    """Mock CrewAI crew for testing."""
    
    def __init__(self, agents: Optional[List[Agent]] = None, tasks: Optional[List[Task]] = None, **kwargs):
        super().__init__(
            agents=agents or [],
            tasks=tasks or [],
            **kwargs
        )
        self._execution_results = []
    
    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> str:
        """Mock crew kickoff."""
        result = f"Mock crew execution with {len(self.agents)} agents and {len(self.tasks)} tasks"
        self._execution_results.append(result)
        return result
    
    def get_execution_results(self) -> List[str]:
        """Get execution results."""
        return self._execution_results


def create_mock_config() -> MockConfig:
    """Create a mock configuration for testing."""
    return MockConfig(
        database=DatabaseConfig(
            project_id="test-project",
            collection_prefix="test",
            batch_size=100,
            timeout_seconds=10
        ),
        ai=AIConfig(
            provider=AIProvider.GOOGLE_GEMINI,
            api_key="test-api-key",
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000,
            timeout_seconds=30
        ),
        telegram=TelegramConfig(
            bot_token="test-bot-token",
            parse_mode="MarkdownV2",
            message_timeout=30
        )
    )


def create_mock_player(name: str = "John Smith", phone: str = "07123456789", 
                      team_id: str = "test-team-1") -> Player:
    """Create a mock player for testing."""
    return Player(
        name=name,
        phone=phone,
        email="john.smith@example.com",
        position=PlayerPosition.MIDFIELDER,
        role=PlayerRole.PLAYER,
        fa_registered=False,
        fa_eligible=True,
        player_id="JS1",
        team_id=team_id,
        onboarding_status=OnboardingStatus.PENDING
    )


def create_mock_team(name: str = "Test Team", team_id: str = "test-team-1") -> Team:
    """Create a mock team for testing."""
    return Team(
        name=name,
        description="A test team",
        status=TeamStatus.ACTIVE,
        settings={"max_players": 20},
        id=team_id
    )


def create_mock_agent_with_tools(name: str = "test_agent", tools: Optional[List[BaseTool]] = None) -> MockAgent:
    """Create a mock agent with tools."""
    agent = MockAgent(
        name=name,
        role="Test Agent",
        goal="Test goal",
        backstory="Test backstory"
    )
    
    if tools:
        for tool in tools:
            agent.add_mock_tool(tool)
    
    return agent


def create_mock_tool(name: str = "test_tool", return_value: Any = "test_result") -> MockTool:
    """Create a mock tool with default test values."""
    return MockTool(name=name, return_value=return_value)


def create_mock_task(description: str = "Test task") -> Task:
    """Create a mock task."""
    return Task(
        description=description
    )


def create_mock_crew(agents: Optional[List[Agent]] = None, tasks: Optional[List[Task]] = None) -> MockCrew:
    """Create a mock crew."""
    return MockCrew(agents=agents or [], tasks=tasks or [])


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_players(count: int = 5, team_id: str = "test-team-1") -> List[Player]:
        """Create multiple mock players."""
        names = ["John Smith", "Jane Doe", "Bob Johnson", "Alice Brown", "Charlie Wilson"]
        phones = ["07123456789", "07234567890", "07345678901", "07456789012", "07567890123"]
        
        players = []
        for i in range(min(count, len(names))):
            player = create_mock_player(
                name=names[i],
                phone=phones[i],
                team_id=team_id
            )
            player.id = f"player_{i+1}"
            players.append(player)
        
        return players
    
    @staticmethod
    def create_teams(count: int = 3) -> List[Team]:
        """Create multiple mock teams."""
        names = ["Test Team 1", "Test Team 2", "Test Team 3"]
        
        teams = []
        for i in range(min(count, len(names))):
            team = create_mock_team(name=names[i], team_id=f"team_{i+1}")
            teams.append(team)
        
        return teams
    
    @staticmethod
    def create_agents(count: int = 3) -> List[MockAgent]:
        """Create multiple mock agents."""
        agent_configs = [
            ("player_coordinator", "Player Coordinator", "Manage player operations"),
            ("team_manager", "Team Manager", "Manage team operations"),
            ("communication_specialist", "Communication Specialist", "Handle team communications")
        ]
        
        agents = []
        for i in range(min(count, len(agent_configs))):
            name, role, goal = agent_configs[i]
            agent = MockAgent(
                name=name,
                role=role,
                goal=goal,
                backstory=f"Test backstory for {name}"
            )
            agents.append(agent)
        
        return agents


# Utility functions for testing
def run_async_test(coro):
    """Run an async test coroutine."""
    return asyncio.run(coro)


def mock_async_function(func):
    """Decorator to mock an async function."""
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def create_error_response(error_type: str, message: str) -> Dict[str, Any]:
    """Create a mock error response."""
    return {
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    }


def create_success_response(data: Any) -> Dict[str, Any]:
    """Create a mock success response."""
    return {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }


def create_mock_llm(responses: Optional[Union[str, List[str]]] = None) -> MockLLM:
    """Create a mock LLM with default test values."""
    return MockLLM(responses=responses)


def create_mock_agent(name: str = "test_agent", role: str = "Mock Agent", response: str = "test response") -> MockAgent:
    """Create a mock agent with default test values."""
    return MockAgent(name=name, role=role, response=response)


def create_mock_service(service_name: str = "test_service") -> AsyncMockService:
    """Create a mock service with default test values."""
    return AsyncMockService(service_name=service_name)


def create_mock_database() -> MockDatabase:
    """Create a mock database for testing."""
    return MockDatabase()


def create_mock_telegram_bot(bot_token: str = "test_token") -> MockTelegramBot:
    """Create a mock Telegram bot for testing."""
    return MockTelegramBot(bot_token=bot_token) 