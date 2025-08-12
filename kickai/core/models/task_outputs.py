"""
Pydantic Output Models for CrewAI Tasks

This module defines structured output models for different KICKAI operations,
following CrewAI 2025 best practices for typed responses.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Union

from pydantic import BaseModel, Field, validator


class PlayerStatus(str, Enum):
    """Player registration and activity status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


class TeamMemberRole(str, Enum):
    """Team member roles."""
    ADMIN = "admin"
    LEADERSHIP = "leadership"
    PLAYER = "player"
    PUBLIC = "public"


class MatchAvailability(str, Enum):
    """Match availability status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAYBE = "maybe"
    NOT_RESPONDED = "not_responded"


# Player-related output models
class PlayerInfo(BaseModel):
    """Individual player information."""
    telegram_id: int = Field(description="Player's Telegram ID")
    username: str = Field(description="Player's username")
    full_name: str | None = Field(None, description="Player's full name")
    status: PlayerStatus = Field(description="Current player status")
    registration_date: datetime | None = Field(None, description="When player registered")
    position: str | None = Field(None, description="Player's position")
    jersey_number: int | None = Field(None, description="Player's jersey number")
    matches_played: int = Field(0, description="Total matches played")
    last_active: datetime | None = Field(None, description="Last activity date")


class PlayerStatusOutput(BaseModel):
    """Output model for player status queries."""
    success: bool = Field(description="Whether the query was successful")
    player: PlayerInfo | None = Field(None, description="Player information")
    error_message: str | None = Field(None, description="Error message if failed")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }


class PlayersListOutput(BaseModel):
    """Output model for player lists."""
    success: bool = Field(description="Whether the query was successful")
    players: list[PlayerInfo] = Field(default_factory=list, description="List of players")
    total_count: int = Field(0, description="Total number of players")
    active_count: int = Field(0, description="Number of active players")
    filter_applied: str | None = Field(None, description="Filter applied to the list")
    error_message: str | None = Field(None, description="Error message if failed")

    @validator('total_count', always=True)
    def calculate_total_count(cls, v, values):
        return len(values.get('players', []))

    @validator('active_count', always=True)
    def calculate_active_count(cls, v, values):
        players = values.get('players', [])
        return len([p for p in players if p.status == PlayerStatus.ACTIVE])


# Team-related output models
class TeamMemberInfo(BaseModel):
    """Individual team member information."""
    telegram_id: int = Field(description="Member's Telegram ID")
    username: str = Field(description="Member's username")
    full_name: str | None = Field(None, description="Member's full name")
    role: TeamMemberRole = Field(description="Member's role in team")
    is_admin: bool = Field(False, description="Whether member is admin")
    join_date: datetime | None = Field(None, description="When member joined")
    permissions: list[str] = Field(default_factory=list, description="Member permissions")


class TeamMembersOutput(BaseModel):
    """Output model for team member lists."""
    success: bool = Field(description="Whether the query was successful")
    members: list[TeamMemberInfo] = Field(default_factory=list, description="List of team members")
    total_count: int = Field(0, description="Total number of members")
    admin_count: int = Field(0, description="Number of admin members")
    leadership_count: int = Field(0, description="Number of leadership members")
    error_message: str | None = Field(None, description="Error message if failed")

    @validator('total_count', always=True)
    def calculate_total_count(cls, v, values):
        return len(values.get('members', []))

    @validator('admin_count', always=True)
    def calculate_admin_count(cls, v, values):
        members = values.get('members', [])
        return len([m for m in members if m.is_admin])

    @validator('leadership_count', always=True)
    def calculate_leadership_count(cls, v, values):
        members = values.get('members', [])
        return len([m for m in members if m.role == TeamMemberRole.LEADERSHIP])


# Match-related output models
class MatchInfo(BaseModel):
    """Individual match information."""
    match_id: str = Field(description="Unique match identifier")
    opponent: str = Field(description="Opponent team name")
    date: datetime = Field(description="Match date and time")
    location: str = Field(description="Match location")
    type: str = Field(description="Match type (league, friendly, etc.)")
    status: str = Field(description="Match status")
    home_away: str = Field(description="Home or away match")
    result: str | None = Field(None, description="Match result if played")


class MatchListOutput(BaseModel):
    """Output model for match lists."""
    success: bool = Field(description="Whether the query was successful")
    matches: list[MatchInfo] = Field(default_factory=list, description="List of matches")
    total_count: int = Field(0, description="Total number of matches")
    upcoming_count: int = Field(0, description="Number of upcoming matches")
    completed_count: int = Field(0, description="Number of completed matches")
    error_message: str | None = Field(None, description="Error message if failed")


class PlayerAvailabilityInfo(BaseModel):
    """Player availability for a match."""
    telegram_id: int = Field(description="Player's Telegram ID")
    username: str = Field(description="Player's username")
    availability: MatchAvailability = Field(description="Player's availability status")
    response_date: datetime | None = Field(None, description="When player responded")
    notes: str | None = Field(None, description="Additional notes from player")


class MatchAvailabilityOutput(BaseModel):
    """Output model for match availability."""
    success: bool = Field(description="Whether the query was successful")
    match_id: str = Field(description="Match identifier")
    match_date: datetime = Field(description="Match date")
    availability: list[PlayerAvailabilityInfo] = Field(default_factory=list, description="Player availability")
    available_count: int = Field(0, description="Number of available players")
    unavailable_count: int = Field(0, description="Number of unavailable players")
    no_response_count: int = Field(0, description="Number of players who haven't responded")
    error_message: str | None = Field(None, description="Error message if failed")

    @validator('available_count', always=True)
    def calculate_available_count(cls, v, values):
        availability = values.get('availability', [])
        return len([a for a in availability if a.availability == MatchAvailability.AVAILABLE])


# Help and system output models
class CommandInfo(BaseModel):
    """Information about a command."""
    name: str = Field(description="Command name")
    description: str = Field(description="Command description")
    usage: str = Field(description="Command usage example")
    permissions: list[str] = Field(default_factory=list, description="Required permissions")
    chat_types: list[str] = Field(default_factory=list, description="Applicable chat types")


class HelpOutput(BaseModel):
    """Output model for help responses."""
    success: bool = Field(description="Whether the help query was successful")
    commands: list[CommandInfo] = Field(default_factory=list, description="Available commands")
    category: str | None = Field(None, description="Command category")
    user_role: str = Field(description="User's role")
    chat_type: str = Field(description="Chat type context")
    total_commands: int = Field(0, description="Total number of commands")
    welcome_message: str | None = Field(None, description="Welcome message for new users")
    error_message: str | None = Field(None, description="Error message if failed")

    @validator('total_commands', always=True)
    def calculate_total_commands(cls, v, values):
        return len(values.get('commands', []))


class SystemStatusOutput(BaseModel):
    """Output model for system status."""
    success: bool = Field(description="Whether status check was successful")
    version: str = Field(description="System version")
    status: str = Field(description="Overall system status")
    uptime: str = Field(description="System uptime")
    database_status: str = Field(description="Database connectivity status")
    api_status: str = Field(description="API status")
    active_users: int = Field(0, description="Number of active users")
    total_teams: int = Field(0, description="Total number of teams")
    error_message: str | None = Field(None, description="Error message if failed")


# Communication output models
class MessageDeliveryInfo(BaseModel):
    """Information about message delivery."""
    recipient_id: int = Field(description="Recipient's Telegram ID")
    recipient_username: str = Field(description="Recipient's username")
    delivered: bool = Field(description="Whether message was delivered")
    delivery_time: datetime = Field(description="When message was delivered")
    error: str | None = Field(None, description="Delivery error if any")


class CommunicationOutput(BaseModel):
    """Output model for communication operations."""
    success: bool = Field(description="Whether communication was successful")
    message_sent: bool = Field(description="Whether message was sent")
    recipients: list[MessageDeliveryInfo] = Field(default_factory=list, description="Delivery information")
    total_recipients: int = Field(0, description="Total number of recipients")
    successful_deliveries: int = Field(0, description="Number of successful deliveries")
    failed_deliveries: int = Field(0, description="Number of failed deliveries")
    broadcast_id: str | None = Field(None, description="Broadcast identifier for tracking")
    error_message: str | None = Field(None, description="Error message if failed")

    @validator('total_recipients', always=True)
    def calculate_total_recipients(cls, v, values):
        return len(values.get('recipients', []))

    @validator('successful_deliveries', always=True)
    def calculate_successful_deliveries(cls, v, values):
        recipients = values.get('recipients', [])
        return len([r for r in recipients if r.delivered])

    @validator('failed_deliveries', always=True)
    def calculate_failed_deliveries(cls, v, values):
        recipients = values.get('recipients', [])
        return len([r for r in recipients if not r.delivered])


# Generic operation output model
class OperationResult(BaseModel):
    """Generic operation result model."""
    success: bool = Field(description="Whether operation was successful")
    operation: str = Field(description="Operation that was performed")
    data: dict[str, Any] | None = Field(None, description="Operation data")
    message: str = Field(description="Result message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Operation timestamp")
    execution_time_ms: int | None = Field(None, description="Execution time in milliseconds")
    error_message: str | None = Field(None, description="Error message if failed")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }


# Task execution monitoring models
class TaskExecutionMetrics(BaseModel):
    """Metrics for task execution monitoring."""
    task_id: str = Field(description="Unique task identifier")
    agent_role: str = Field(description="Agent role that executed the task")
    start_time: datetime = Field(description="Task start time")
    end_time: datetime | None = Field(None, description="Task end time")
    duration_ms: int | None = Field(None, description="Task duration in milliseconds")
    success: bool = Field(description="Whether task completed successfully")
    tokens_used: int | None = Field(None, description="Number of tokens used")
    tools_called: list[str] = Field(default_factory=list, description="Tools called during execution")
    error_type: str | None = Field(None, description="Type of error if failed")
    error_message: str | None = Field(None, description="Error message if failed")

    @validator('duration_ms', always=True)
    def calculate_duration(cls, v, values):
        start = values.get('start_time')
        end = values.get('end_time')
        if start and end:
            return int((end - start).total_seconds() * 1000)
        return None


# Union types for different output categories
PlayerOutput = Union[PlayerStatusOutput, PlayersListOutput]
TeamOutput = Union[TeamMembersOutput]
MatchOutput = Union[MatchListOutput, MatchAvailabilityOutput]
SystemOutput = Union[HelpOutput, SystemStatusOutput]
CommunicationOutputType = Union[CommunicationOutput]

# All output types for type hints
TaskOutput = Union[
    PlayerStatusOutput,
    PlayersListOutput,
    TeamMembersOutput,
    MatchListOutput,
    MatchAvailabilityOutput,
    HelpOutput,
    SystemStatusOutput,
    CommunicationOutput,
    OperationResult,
    TaskExecutionMetrics
]
