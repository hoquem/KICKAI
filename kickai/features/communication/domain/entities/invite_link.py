#!/usr/bin/env python3
"""
InviteLink Domain Entity

This module defines the InviteLink entity for the communication domain.
InviteLinks represent secure invitation links for team members.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from kickai.core.enums import InviteLinkStatus


@dataclass
class InviteLink:
    """
    Invite Link entity representing secure invitation links for team members.
    
    This domain entity encapsulates all invite link data and business logic,
    providing a clean interface for invite link operations.
    """

    # Core identification
    invite_id: str
    team_id: str
    
    # Member information
    member_name: str
    member_phone: str
    member_id: Optional[str] = None
    
    # Link details
    invite_link: Optional[str] = None
    secure_data: Optional[str] = None
    
    # Status and timing
    status: InviteLinkStatus = InviteLinkStatus.ACTIVE
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    used_at: Optional[datetime] = None
    
    def _post_init_(self):
        """Set defaults and validate after initialization."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        # Ensure status is proper enum
        if isinstance(self.status, str):
            self.status = InviteLinkStatus(self.status)
        
        self._validate()
    
    def _validate(self):
        """Validate invite link data."""
        if not self.invite_id:
            raise ValueError("Invite ID cannot be empty")
        if not self.team_id:
            raise ValueError("Team ID cannot be empty")
        if not self.member_name:
            raise ValueError("Member name cannot be empty")
        if not self.member_phone:
            raise ValueError("Member phone cannot be empty")
        if not isinstance(self.status, InviteLinkStatus):
            raise ValueError(f"Invalid status type: {type(self.status)}. Must be InviteLinkStatus enum")
    
    def is_active(self) -> bool:
        """Check if the invite link is active and usable."""
        if self.status != InviteLinkStatus.ACTIVE:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def mark_as_used(self) -> None:
        """Mark the invite link as used."""
        self.status = InviteLinkStatus.USED
        self.used_at = datetime.utcnow()
    
    def revoke(self) -> None:
        """Revoke the invite link."""
        self.status = InviteLinkStatus.REVOKED
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "invite_id": self.invite_id,
            "team_id": self.team_id,
            "member_name": self.member_name,
            "member_phone": self.member_phone,
            "member_id": self.member_id,
            "invite_link": self.invite_link,
            "secure_data": self.secure_data,
            "status": self.status.value if isinstance(self.status, InviteLinkStatus) else self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "used_at": self.used_at.isoformat() if self.used_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InviteLink":
        """Create from dictionary."""
        return cls(
            invite_id=data.get("invite_id", ""),
            team_id=data.get("team_id", ""),
            member_name=data.get("member_name", ""),
            member_phone=data.get("member_phone", ""),
            member_id=data.get("member_id"),
            invite_link=data.get("invite_link"),
            secure_data=data.get("secure_data"),
            status=InviteLinkStatus(data.get("status", InviteLinkStatus.ACTIVE.value)),
            expires_at=cls._parse_datetime(data.get("expires_at")),
            created_at=cls._parse_datetime(data.get("created_at")),
            used_at=cls._parse_datetime(data.get("used_at")),
        )
    
    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        """Parse datetime from string or return existing datetime."""
        if isinstance(value, str):
            # Handle ISO format with or without timezone
            if value.endswith('Z'):
                value = value.replace('Z', '+00:00')
            return datetime.fromisoformat(value)
        return value
    
    def _str_(self) -> str:
        """String representation for debugging."""
        return f"InviteLink(invite_id={self.invite_id}, member_name={self.member_name}, status={self.status.value})"
    
    def _repr_(self) -> str:
        """Detailed representation for debugging."""
        return (f"InviteLink(invite_id='{self.invite_id}', team_id='{self.team_id}', "
                f"member_name='{self.member_name}', status={self.status.value})")