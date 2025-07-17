"""
Player Command Models

This module contains Pydantic models for player-related commands.
"""

import logging
from typing import Optional
from enum import Enum

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
    from pydantic.types import constr
except ImportError as e:
    raise ImportError(f"Required libraries missing: {e}\nInstall with: pip install pydantic")

import phonenumbers
from utils.phone_utils import normalize_phone
from utils.validation_utils import validate_name

logger = logging.getLogger(__name__)


class PlayerPosition(str, Enum):
    """Player positions with validation."""
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    STRIKER = "striker"
    UTILITY = "utility"
    ANY = "any"  # Added for flexibility


class UKPhoneNumber(str):
    """UK phone number with validation using phonenumbers."""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.str_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(
            type="string",
            pattern=r"^(\+44|0)7\d{9}$",
            description="UK mobile number in 07xxx or +447xxx format (validated with phonenumbers)"
        )
        return json_schema

    @classmethod
    def validate(cls, v, info):
        if not isinstance(v, str):
            raise ValueError('Phone number must be a string')
        normalized = normalize_phone(v, region="GB")
        if not normalized:
            raise ValueError('Invalid UK mobile number. Use 07xxx or +447xxx format')
        return normalized


class AddPlayerCommand(BaseModel):
    """Model for /add command parameters."""
    name: str = Field(..., min_length=2, max_length=100, description="Player's full name")
    phone: UKPhoneNumber = Field(..., description="UK mobile number")
    position: PlayerPosition = Field(..., description="Player position")
    admin_approved: bool = Field(False, description="Admin approval status")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not validate_name(v):
            raise ValueError('Name cannot be empty and must be at least 2 characters')
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Smith",
                "phone": "+447123456789",
                "position": "midfielder",
                "admin_approved": True
            }
        }
    }


class RegisterCommand(BaseModel):
    """Model for /register command parameters."""
    player_id: Optional[str] = Field(None, description="Player ID for simple registration")
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Your full name")
    phone: Optional[UKPhoneNumber] = Field(None, description="Your UK mobile number")
    position: Optional[PlayerPosition] = Field(PlayerPosition.UTILITY, description="Your preferred position")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not validate_name(v):
            raise ValueError('Name cannot be empty and must be at least 2 characters')
        return v.strip() if v else v
    
    @model_validator(mode='before')
    @classmethod
    def validate_registration_format(cls, values):
        """Validate that either player_id OR (name, phone, position) are provided."""
        if isinstance(values, dict):
            player_id = values.get('player_id')
            name = values.get('name')
            phone = values.get('phone')
            
            if player_id and (name or phone):
                raise ValueError('Cannot provide both player_id and registration details')
            
            if not player_id and not (name and phone):
                raise ValueError('Must provide either player_id or registration details (name, phone)')
        
        return values


class RemovePlayerCommand(BaseModel):
    """Model for /remove command parameters."""
    identifier: str = Field(..., description="Phone number or player name")
    
    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v):
        if not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()


class ApprovePlayerCommand(BaseModel):
    """Model for /approve command parameters."""
    player_id: str = Field(..., description="Player ID or name")
    
    @field_validator('player_id')
    @classmethod
    def validate_player_id(cls, v):
        if not v.strip():
            raise ValueError('Player ID cannot be empty')
        return v.strip()


class RejectPlayerCommand(BaseModel):
    """Model for /reject command parameters."""
    player_id: str = Field(..., description="Player ID or name")
    reason: Optional[str] = Field("No reason provided", description="Reason for rejection")
    
    @field_validator('player_id')
    @classmethod
    def validate_player_id(cls, v):
        if not v.strip():
            raise ValueError('Player ID cannot be empty')
        return v.strip()


class InvitePlayerCommand(BaseModel):
    """Model for /invitelink command parameters."""
    identifier: str = Field(..., description="Phone number or player name")
    
    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v):
        if not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()


class StatusCommand(BaseModel):
    """Model for /status command parameters."""
    identifier: str = Field(..., description="Phone number or player name")
    
    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v):
        if not v.strip():
            raise ValueError('Identifier cannot be empty')
        return v.strip()


class ListCommand(BaseModel):
    """Model for /list command parameters."""
    filter: Optional[str] = Field(None, description="Filter type (pending, active, etc.)")


class HelpCommand(BaseModel):
    """Model for /help command parameters."""
    command: Optional[str] = Field(None, description="Specific command to get help for") 