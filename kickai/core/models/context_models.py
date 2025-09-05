"""
Pydantic context models for CrewAI native context passing.

This module defines the context models used throughout the system to ensure
proper validation and type safety when passing context to CrewAI tools.
"""

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, validator


class BaseContext(BaseModel):
    """Base context model for all operations."""

    team_id: str = Field(..., description="Team identifier")
    telegram_id: str = Field(..., description="User identifier (telegram ID)")  # Fixed: was user_id
    timestamp: datetime = Field(default_factory=datetime.now, description="Context timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("team_id", "telegram_id")
    def validate_required_fields(cls, v):
        """Validate that required fields are not empty."""
        if not v or not str(v).strip():
            raise ValueError("Field cannot be empty")
        return str(v).strip()

    @validator("team_id")
    def validate_team_id_format(cls, v):
        """Validate team ID format."""
        if not v:
            raise ValueError("Team ID is required")
        return v.upper()

    class Config:
        """Pydantic model configuration."""
        
        extra = "allow"  # Allow additional fields for flexibility
        validate_assignment = True


def validate_context_data(context_data: dict[str, Any], context_type: str) -> bool:
    """
    Validate context data against basic requirements.
    
    Args:
        context_data: Context data to validate
        context_type: Type of context for validation
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Basic required fields
        required_fields = ["team_id", "telegram_id"]
        
        for field in required_fields:
            if field not in context_data or not context_data[field]:
                logger.warning(f"Missing required field '{field}' in context")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Context validation error: {e}")
        return False