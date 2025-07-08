"""
Task definitions for KICKAI.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task definition."""
    id: str
    name: str
    description: str
    status: TaskStatus
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    template_name: Optional[str] = None


class MessageProcessingTasks:
    """Message processing task definitions."""
    
    @staticmethod
    def process_user_message(message: str, user_id: str) -> Task:
        """Create a task for processing user messages."""
        return Task(
            id=f"msg_{user_id}_{datetime.utcnow().timestamp()}",
            name="Process User Message",
            description=f"Process message from user {user_id}",
            status=TaskStatus.PENDING,
            parameters={"message": message, "user_id": user_id},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


class PlayerManagementTasks:
    """Player management task definitions."""
    
    @staticmethod
    def register_player(player_data: Dict[str, Any]) -> Task:
        """Create a task for player registration."""
        return Task(
            id=f"reg_{datetime.utcnow().timestamp()}",
            name="Register Player",
            description="Register a new player",
            status=TaskStatus.PENDING,
            parameters=player_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


class FixtureManagementTasks:
    """Fixture management task definitions."""
    
    @staticmethod
    def create_fixture(fixture_data: Dict[str, Any]) -> Task:
        """Create a task for fixture creation."""
        return Task(
            id=f"fix_{datetime.utcnow().timestamp()}",
            name="Create Fixture",
            description="Create a new fixture",
            status=TaskStatus.PENDING,
            parameters=fixture_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


class TeamManagementTasks:
    """Team management task definitions."""
    
    @staticmethod
    def create_team(team_data: Dict[str, Any]) -> Task:
        """Create a task for team creation."""
        return Task(
            id=f"team_{datetime.utcnow().timestamp()}",
            name="Create Team",
            description="Create a new team",
            status=TaskStatus.PENDING,
            parameters=team_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


class BotManagementTasks:
    """Bot management task definitions."""
    
    @staticmethod
    def configure_bot(bot_data: Dict[str, Any]) -> Task:
        """Create a task for bot configuration."""
        return Task(
            id=f"bot_{datetime.utcnow().timestamp()}",
            name="Configure Bot",
            description="Configure a bot instance",
            status=TaskStatus.PENDING,
            parameters=bot_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )


class CommandLoggingTasks:
    """Command logging task definitions."""
    
    @staticmethod
    def log_command(command_data: Dict[str, Any]) -> Task:
        """Create a task for command logging."""
        return Task(
            id=f"cmd_{datetime.utcnow().timestamp()}",
            name="Log Command",
            description="Log a command execution",
            status=TaskStatus.PENDING,
            parameters=command_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ) 