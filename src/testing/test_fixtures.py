"""
Test Fixtures for KICKAI

This module provides comprehensive test fixtures and sample data
for reliable and consistent testing across the KICKAI system.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

from src.database.models import Player, Team, PlayerPosition, PlayerRole, OnboardingStatus, TeamStatus
from src.testing.test_utils import MockAgent, MockTool, MockLLM


@dataclass
class TestData:
    """Base test data class."""
    id: str
    created_at: datetime
    updated_at: datetime


@dataclass
class PlayerTestData(TestData):
    """Test data for player-related tests."""
    name: str
    phone: str
    team_id: str
    position: PlayerPosition
    role: PlayerRole
    onboarding_status: OnboardingStatus
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_conditions: Optional[str] = None
    is_active: bool = True


@dataclass
class TeamTestData(TestData):
    """Test data for team-related tests."""
    name: str
    status: TeamStatus
    description: Optional[str] = None
    home_ground: Optional[str] = None
    manager_name: Optional[str] = None
    manager_phone: Optional[str] = None
    bot_token: Optional[str] = None
    admin_chat_id: Optional[str] = None


@dataclass
class AgentTestData(TestData):
    """Test data for agent-related tests."""
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    response_pattern: str


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_player_data(
        name: str = "John Smith",
        phone: str = "07123456789",
        team_id: str = "test-team-1",
        position: PlayerPosition = PlayerPosition.FORWARD,
        role: PlayerRole = PlayerRole.PLAYER,
        onboarding_status: OnboardingStatus = OnboardingStatus.COMPLETED,
        **kwargs
    ) -> PlayerTestData:
        """Create player test data."""
        now = datetime.now()
        return PlayerTestData(
            id=str(uuid.uuid4()),
            created_at=now,
            updated_at=now,
            name=name,
            phone=phone,
            team_id=team_id,
            position=position,
            role=role,
            onboarding_status=onboarding_status,
            **kwargs
        )
    
    @staticmethod
    def create_team_data(
        name: str = "Test Team",
        status: TeamStatus = TeamStatus.ACTIVE,
        **kwargs
    ) -> TeamTestData:
        """Create team test data."""
        now = datetime.now()
        return TeamTestData(
            id=str(uuid.uuid4()),
            created_at=now,
            updated_at=now,
            name=name,
            status=status,
            **kwargs
        )
    
    @staticmethod
    def create_agent_data(
        name: str = "Test Agent",
        role: str = "Test Role",
        goal: str = "Test Goal",
        backstory: str = "Test Backstory",
        tools: Optional[List[str]] = None,
        response_pattern: str = "Test response"
    ) -> AgentTestData:
        """Create agent test data."""
        now = datetime.now()
        return AgentTestData(
            id=str(uuid.uuid4()),
            created_at=now,
            updated_at=now,
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools or ["test_tool"],
            response_pattern=response_pattern
        )


class SampleData:
    """Predefined sample data for common test scenarios."""
    
    # Player samples
    PLAYERS = {
        "john_smith": PlayerTestData(
            id="player-1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="John Smith",
            phone="07123456789",
            team_id="team-1",
            position=PlayerPosition.FORWARD,
            role=PlayerRole.CAPTAIN,
            onboarding_status=OnboardingStatus.COMPLETED,
            telegram_id="123456789",
            telegram_username="johnsmith",
            email="john.smith@example.com"
        ),
        "jane_doe": PlayerTestData(
            id="player-2",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="Jane Doe",
            phone="07987654321",
            team_id="team-1",
            position=PlayerPosition.MIDFIELDER,
            role=PlayerRole.PLAYER,
            onboarding_status=OnboardingStatus.PENDING,
            telegram_id="987654321",
            telegram_username="janedoe"
        ),
        "bob_wilson": PlayerTestData(
            id="player-3",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="Bob Wilson",
            phone="07555123456",
            team_id="team-1",
            position=PlayerPosition.DEFENDER,
            role=PlayerRole.PLAYER,
            onboarding_status=OnboardingStatus.IN_PROGRESS,
            telegram_id="555123456",
            telegram_username="bobwilson"
        )
    }
    
    # Team samples
    TEAMS = {
        "team_1": TeamTestData(
            id="team-1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="Red Dragons",
            status=TeamStatus.ACTIVE,
            description="A competitive football team",
            home_ground="Central Park",
            manager_name="Mike Johnson",
            manager_phone="07111222333",
            bot_token="test_bot_token_1",
            admin_chat_id="admin_chat_1"
        ),
        "team_2": TeamTestData(
            id="team-2",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="Blue Eagles",
            status=TeamStatus.ACTIVE,
            description="Another competitive team",
            home_ground="Sports Complex",
            manager_name="Sarah Williams",
            manager_phone="07444555666",
            bot_token="test_bot_token_2",
            admin_chat_id="admin_chat_2"
        )
    }
    
    # Agent samples
    AGENTS = {
        "player_manager": AgentTestData(
            id="agent-1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="Player Manager",
            role="Player Management Specialist",
            goal="Manage player registrations and team rosters",
            backstory="Expert in player management and team coordination",
            tools=["player_tools", "team_tools"],
            response_pattern="Player management response"
        ),
        "fixture_coordinator": AgentTestData(
            id="agent-2",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="Fixture Coordinator",
            role="Fixture Management Specialist",
            goal="Coordinate match schedules and fixture management",
            backstory="Specialist in scheduling and fixture coordination",
            tools=["fixture_tools", "team_tools"],
            response_pattern="Fixture coordination response"
        )
    }
    
    # Telegram message samples
    TELEGRAM_MESSAGES = {
        "player_registration": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "first_name": "John",
                "last_name": "Smith",
                "username": "johnsmith"
            },
            "chat": {
                "id": 123456789,
                "type": "private"
            },
            "text": "/register John Smith 07123456789",
            "date": int(datetime.now().timestamp())
        },
        "team_command": {
            "message_id": 2,
            "from": {
                "id": 123456789,
                "first_name": "John",
                "last_name": "Smith",
                "username": "johnsmith"
            },
            "chat": {
                "id": -1001234567890,
                "type": "group",
                "title": "Red Dragons Team Chat"
            },
            "text": "/team",
            "date": int(datetime.now().timestamp())
        },
        "fixture_command": {
            "message_id": 3,
            "from": {
                "id": 123456789,
                "first_name": "John",
                "last_name": "Smith",
                "username": "johnsmith"
            },
            "chat": {
                "id": -1001234567890,
                "type": "group",
                "title": "Red Dragons Team Chat"
            },
            "text": "/fixtures",
            "date": int(datetime.now().timestamp())
        }
    }
    
    # Task samples
    TASKS = {
        "player_registration": {
            "description": "Register a new player",
            "expected_output": "Player registration completed",
            "agent_role": "player_manager"
        },
        "team_info": {
            "description": "Get team information",
            "expected_output": "Team details retrieved",
            "agent_role": "player_manager"
        },
        "fixture_creation": {
            "description": "Create a new fixture",
            "expected_output": "Fixture created successfully",
            "agent_role": "fixture_coordinator"
        }
    }


class MockDataBuilder:
    """Builder class for creating complex mock data structures."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the builder state."""
        self._players = []
        self._teams = []
        self._agents = []
        self._tools = []
        
    def add_player(self, **kwargs) -> 'MockDataBuilder':
        """Add a player to the builder."""
        player_data = TestDataFactory.create_player_data(**kwargs)
        self._players.append(player_data)
        return self
    
    def add_team(self, **kwargs) -> 'MockDataBuilder':
        """Add a team to the builder."""
        team_data = TestDataFactory.create_team_data(**kwargs)
        self._teams.append(team_data)
        return self
    
    def add_agent(self, **kwargs) -> 'MockDataBuilder':
        """Add an agent to the builder."""
        agent_data = TestDataFactory.create_agent_data(**kwargs)
        self._agents.append(agent_data)
        return self
    
    def add_tool(self, name: str, return_value: str = "mock_result") -> 'MockDataBuilder':
        """Add a tool to the builder."""
        tool = MockTool(name=name, return_value=return_value)
        self._tools.append(tool)
        return self
    
    def build_players(self) -> List[PlayerTestData]:
        """Build and return the list of players."""
        return self._players.copy()
    
    def build_teams(self) -> List[TeamTestData]:
        """Build and return the list of teams."""
        return self._teams.copy()
    
    def build_agents(self) -> List[AgentTestData]:
        """Build and return the list of agents."""
        return self._agents.copy()
    
    def build_tools(self) -> List[MockTool]:
        """Build and return the list of tools."""
        return self._tools.copy()
    
    def build_all(self) -> Dict[str, List]:
        """Build and return all data structures."""
        return {
            'players': self.build_players(),
            'teams': self.build_teams(),
            'agents': self.build_agents(),
            'tools': self.build_tools()
        }


# Convenience functions for common test scenarios
def create_sample_team_with_players(team_name: str = "Test Team", player_count: int = 5) -> Dict[str, Any]:
    """Create a sample team with multiple players."""
    builder = MockDataBuilder()
    
    # Add team
    builder.add_team(name=team_name)
    
    # Add players
    positions = list(PlayerPosition)
    for i in range(player_count):
        builder.add_player(
            name=f"Player {i+1}",
            phone=f"07{i:08d}",
            team_id="team-1",
            position=positions[i % len(positions)],
            role=PlayerRole.PLAYER if i > 0 else PlayerRole.CAPTAIN
        )
    
    return builder.build_all()


def create_sample_agent_with_tools(agent_name: str = "Test Agent", tool_count: int = 3) -> Dict[str, Any]:
    """Create a sample agent with multiple tools."""
    builder = MockDataBuilder()
    
    # Add agent
    builder.add_agent(name=agent_name)
    
    # Add tools
    for i in range(tool_count):
        builder.add_tool(name=f"tool_{i+1}", return_value=f"result_{i+1}")
    
    return builder.build_all()


def create_complete_test_scenario() -> Dict[str, Any]:
    """Create a complete test scenario with teams, players, agents, and tools."""
    builder = MockDataBuilder()
    
    # Add teams
    builder.add_team(name="Red Dragons", status=TeamStatus.ACTIVE)
    builder.add_team(name="Blue Eagles", status=TeamStatus.ACTIVE)
    
    # Add players for Red Dragons
    builder.add_player(name="John Smith", team_id="team-1", role=PlayerRole.CAPTAIN)
    builder.add_player(name="Jane Doe", team_id="team-1", role=PlayerRole.PLAYER)
    builder.add_player(name="Bob Wilson", team_id="team-1", role=PlayerRole.PLAYER)
    
    # Add players for Blue Eagles
    builder.add_player(name="Alice Brown", team_id="team-2", role=PlayerRole.CAPTAIN)
    builder.add_player(name="Charlie Davis", team_id="team-2", role=PlayerRole.PLAYER)
    
    # Add agents
    builder.add_agent(name="Player Manager", role="Player Management")
    builder.add_agent(name="Fixture Coordinator", role="Fixture Management")
    
    # Add tools
    builder.add_tool(name="player_tools", return_value="Player management result")
    builder.add_tool(name="team_tools", return_value="Team management result")
    builder.add_tool(name="fixture_tools", return_value="Fixture management result")
    
    return builder.build_all() 