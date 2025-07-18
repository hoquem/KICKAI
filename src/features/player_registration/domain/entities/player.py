#!/usr/bin/env python3
"""
Player Entity

This module defines the Player entity for the player registration domain.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Player:
    """Player entity for the player registration domain."""
    
    id: str
    name: str
    phone: str
    position: str
    team_id: str
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set default timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def approve(self):
        """Approve the player."""
        self.status = "approved"
        self.updated_at = datetime.utcnow()
    
    def reject(self):
        """Reject the player."""
        self.status = "rejected"
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate the player."""
        self.status = "active"
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the player."""
        self.status = "inactive"
        self.updated_at = datetime.utcnow()
    
    def is_approved(self) -> bool:
        """Check if player is approved."""
        return self.status == "approved"
    
    def is_active(self) -> bool:
        """Check if player is active."""
        return self.status == "active"
    
    def is_pending(self) -> bool:
        """Check if player is pending."""
        return self.status == "pending" 