#!/usr/bin/env python3
"""
Team Administration Domain Types

Type definitions for team administration operations to ensure consistency
across the system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Type aliases for better type safety
TelegramUserId = int  # Standard type for Telegram user IDs (always integer)
TeamId = str  # Team identifier
MemberId = str  # Team member identifier
PhoneNumber = str  # Phone number in normalized format


class MemberRole(Enum):
    """Standard team member roles."""

    TEAM_MANAGER = "team manager"
    COACH = "coach"
    ASSISTANT_COACH = "assistant coach"
    HEAD_COACH = "head coach"
    CLUB_ADMINISTRATOR = "club administrator"
    TREASURER = "treasurer"
    SECRETARY = "secretary"
    VOLUNTEER_COORDINATOR = "volunteer coordinator"
    VOLUNTEER = "volunteer"
    PARENT_HELPER = "parent helper"
    FIRST_AID_COORDINATOR = "first aid coordinator"
    EQUIPMENT_MANAGER = "equipment manager"
    TRANSPORT_COORDINATOR = "transport coordinator"


class MemberStatus(Enum):
    """Team member status values."""

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class TeamMemberCreationRequest:
    """Request to create a new team member with type safety."""

    telegram_id: TelegramUserId
    team_id: TeamId
    member_name: str
    phone_number: PhoneNumber
    chat_type: str
    role: str | None = None
    email: str | None = None


@dataclass
class TeamMemberCreationResult:
    """Result of team member creation operation."""

    success: bool
    member: Optional["TeamMember"] = None
    invite_link: str | None = None
    error_message: str | None = None
    member_id: MemberId | None = None


@dataclass
class InviteLinkCreationRequest:
    """Request to create an invite link for a team member."""

    team_id: TeamId
    member_name: str
    member_phone: PhoneNumber
    member_role: str
    leadership_chat_id: str


@dataclass
class InviteLinkCreationResult:
    """Result of invite link creation."""

    success: bool
    invite_link: str | None = None
    member_id: MemberId | None = None
    expires_at: str | None = None
    error_message: str | None = None


@dataclass
class TeamMemberLookupRequest:
    """Request to lookup a team member."""

    telegram_id: TelegramUserId
    team_id: TeamId


@dataclass
class TeamMemberUpdateRequest:
    """Request to update team member information."""

    telegram_id: TelegramUserId
    team_id: TeamId
    field: str
    value: str
    username: str
