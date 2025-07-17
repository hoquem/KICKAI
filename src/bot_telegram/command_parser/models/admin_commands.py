"""
Admin Command Models

This module contains Pydantic models for admin-related commands.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BroadcastCommand(BaseModel):
    """Model for /broadcast command parameters."""
    message: str = Field(..., description="Message to broadcast")
    target: Optional[str] = Field("all", description="Target audience (all, players, admins)")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class PromoteUserCommand(BaseModel):
    """Model for /promote_user command parameters."""
    user_id: str = Field(..., description="User ID to promote")
    role: str = Field(..., description="New role (admin, moderator, etc.)")
    
    @field_validator('user_id', 'role')
    @classmethod
    def validate_fields(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class DemoteUserCommand(BaseModel):
    """Model for /demote_user command parameters."""
    user_id: str = Field(..., description="User ID to demote")
    reason: Optional[str] = Field(None, description="Reason for demotion")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError('User ID cannot be empty')
        return v.strip()


class SystemStatusCommand(BaseModel):
    """Model for /system_status command parameters."""
    detailed: bool = Field(False, description="Show detailed status information") 