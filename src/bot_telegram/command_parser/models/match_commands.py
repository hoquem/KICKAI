"""
Match Command Models

This module contains Pydantic models for match-related commands.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from utils.validation_utils import validate_date_format, validate_time_format


class CreateMatchCommand(BaseModel):
    """Model for /create_match command parameters."""
    date: str = Field(..., description="Match date (YYYY-MM-DD)")
    time: str = Field(..., description="Match time (HH:MM)")
    location: str = Field(..., description="Match location")
    opponent: Optional[str] = Field(None, description="Opponent team name")
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if not validate_date_format(v):
            raise ValueError('Invalid date format. Use YYYY-MM-DD')
        return v
    
    @field_validator('time')
    @classmethod
    def validate_time(cls, v):
        if not validate_time_format(v):
            raise ValueError('Invalid time format. Use HH:MM')
        return v


class AttendMatchCommand(BaseModel):
    """Model for /attend_match command parameters."""
    match_id: str = Field(..., description="Match ID")
    availability: Optional[str] = Field("yes", description="Availability (yes/no/maybe)")


class UnattendMatchCommand(BaseModel):
    """Model for /unattend_match command parameters."""
    match_id: str = Field(..., description="Match ID")


class ListMatchesCommand(BaseModel):
    """Model for /list_matches command parameters."""
    filter: Optional[str] = Field(None, description="Filter type (upcoming, past, etc.)")


class RecordResultCommand(BaseModel):
    """Model for /record_result command parameters."""
    match_id: str = Field(..., description="Match ID")
    our_score: int = Field(..., ge=0, description="Our team's score")
    their_score: int = Field(..., ge=0, description="Opponent's score")
    notes: Optional[str] = Field(None, description="Additional notes") 