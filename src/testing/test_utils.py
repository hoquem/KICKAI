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
from crewai.tools import BaseTool

from ..core.config import DatabaseConfig, AIConfig, TelegramConfig, AIProvider
from ..core.exceptions import KICKAIError
from ..database.models import Player, Team, PlayerPosition, PlayerRole, OnboardingStatus, TeamStatus


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


class MockLLM:
    """Mock LLM for testing."""
    
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        self.responses = responses or {}
        self._call_count = 0
    
    async def ainvoke(self, prompt: str) -> str:
        """Mock async invoke."""
        self._call_count += 1
        
        # Return predefined response based on prompt content
        for key, response in self.responses.items():
            if key.lower() in prompt.lower():
                return response
        
        # Default responses
        if "complexity" in prompt.lower():
            return '{"complexity": 5, "intent": "player_management", "reasoning": "Test reasoning"}'
        elif "capabilities" in prompt.lower():
            return '["player_management", "messaging"]'
        else:
            return '{"result": "success", "message": "Test response"}'


class CrewAICompatibleTool(BaseTool):
    """CrewAI-compatible tool for testing."""
    
    name: str = "test_tool"
    description: str = "A test tool for CrewAI compatibility"
    
    def __init__(self, name: str = "test_tool", description: str = "Test tool", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        self._mock_function = None
    
    def set_mock_function(self, func: Callable):
        """Set a mock function for this tool."""
        self._mock_function = func
    
    def _run(self, *args, **kwargs) -> str:
        """Run the tool."""
        if self._mock_function:
            result = self._mock_function(*args, **kwargs)
            return str(result)
        return "Mock tool executed"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async run the tool."""
        if self._mock_function:
            if asyncio.iscoroutinefunction(self._mock_function):
                result = await self._mock_function(*args, **kwargs)
            else:
                result = self._mock_function(*args, **kwargs)
            return str(result)
        return "Mock tool executed"


class MockAgent(Agent):
    """Mock CrewAI agent for testing."""
    
    def __init__(self, name: str = "test_agent", role: str = "Test Agent", 
                 goal: str = "Test goal", backstory: str = "Test backstory", **kwargs):
        super().__init__(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            **kwargs
        )
        self._mock_tools = []
        self._execution_history = []
    
    def add_mock_tool(self, tool: CrewAICompatibleTool):
        """Add a mock tool to the agent."""
        self._mock_tools.append(tool)
        self.tools = self._mock_tools
    
    def execute_task(self, task: str) -> str:
        """Mock task execution."""
        self._execution_history.append(task)
        return f"Mock execution result for: {task}"
    
    def get_execution_history(self) -> List[str]:
        """Get execution history."""
        return self._execution_history


class MockTask(Task):
    """Mock CrewAI task for testing."""
    
    def __init__(self, description: str = "Test task", **kwargs):
        super().__init__(
            description=description,
            **kwargs
        )
        self._execution_result = None
    
    def set_execution_result(self, result: str):
        """Set the execution result."""
        self._execution_result = result
    
    def execute(self, agent: Agent) -> str:
        """Mock task execution."""
        if self._execution_result:
            return self._execution_result
        return f"Mock task executed: {self.description}"


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


def create_mock_agent_with_tools(name: str = "test_agent", tools: Optional[List[CrewAICompatibleTool]] = None) -> MockAgent:
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


def create_mock_tool(name: str = "test_tool", description: str = "Test tool") -> CrewAICompatibleTool:
    """Create a mock tool."""
    return CrewAICompatibleTool(name=name, description=description)


def create_mock_task(description: str = "Test task") -> MockTask:
    """Create a mock task."""
    return MockTask(description=description)


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