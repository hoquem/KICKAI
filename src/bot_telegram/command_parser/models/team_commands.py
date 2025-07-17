"""
Team Command Models

This module contains Pydantic models for team-related commands.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from utils.validation_utils import validate_team_name


class AddTeamCommand(BaseModel):
    """Model for /add_team command parameters."""
    team_name: str = Field(..., min_length=2, max_length=100, description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    
    @field_validator('team_name')
    @classmethod
    def validate_team_name(cls, v):
        if not validate_team_name(v):
            raise ValueError('Team name cannot be empty and must be at least 3 characters')
        return v.strip()


class RemoveTeamCommand(BaseModel):
    """Model for /remove_team command parameters."""
    team_id: str = Field(..., description="Team ID or name")
    
    @field_validator('team_id')
    @classmethod
    def validate_team_id(cls, v):
        if not v.strip():
            raise ValueError('Team ID cannot be empty')
        return v.strip()


class ListTeamsCommand(BaseModel):
    """Model for /list_teams command parameters."""
    filter: Optional[str] = Field(None, description="Filter type (active, inactive, etc.)")


class UpdateTeamInfoCommand(BaseModel):
    """Model for /update_team_info command parameters."""
    team_id: str = Field(..., description="Team ID or name")
    field: str = Field(..., description="Field to update (name, description, etc.)")
    value: str = Field(..., description="New value")
    
    @field_validator('team_id', 'field', 'value')
    @classmethod
    def validate_fields(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip() 