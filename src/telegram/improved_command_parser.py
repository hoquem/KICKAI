#!/usr/bin/env python3
"""
Improved Command Parser using Popular Open-Source Libraries

This module uses Typer and Pydantic for robust command parsing and validation,
replacing the custom command parser with industry-standard libraries.

Dependencies:
- typer: Modern command-line interface library
- pydantic: Data validation using Python type annotations
"""

import re
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

try:
    import typer
    from typer import Typer
    from pydantic import BaseModel, Field, field_validator, ValidationError, model_validator
    from pydantic.types import constr
except ImportError as e:
    raise ImportError(
        f"Required libraries missing: {e}\n"
        "Install with: pip install typer pydantic"
    )

import phonenumbers
from utils.phone_utils import normalize_phone
from utils.validation_utils import validate_phone, validate_name, validate_team_name, validate_date_format, validate_time_format

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS FOR VALIDATION
# ============================================================================

class PlayerPosition(str, Enum):
    """Player positions with validation."""
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    STRIKER = "striker"
    UTILITY = "utility"
    ANY = "any" # Added for flexibility


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
    """Model for /invite command parameters."""
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


# ============================================================================
# ONBOARDING COMMAND MODELS
# ============================================================================

class StartOnboardingCommand(BaseModel):
    """Model for /start_onboarding command parameters."""
    user_id: Optional[str] = Field(None, description="User ID to start onboarding for")


class ProcessOnboardingResponseCommand(BaseModel):
    """Model for /process_onboarding_response command parameters."""
    response: str = Field(..., description="User's onboarding response")
    step: Optional[str] = Field(None, description="Current onboarding step")


class OnboardingStatusCommand(BaseModel):
    """Model for /onboarding_status command parameters."""
    user_id: Optional[str] = Field(None, description="User ID to check status for")


# ============================================================================
# TEAM MANAGEMENT COMMAND MODELS
# ============================================================================

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


# ============================================================================
# MATCH COMMAND MODELS
# ============================================================================

class CreateMatchCommand(BaseModel):
    """Model for /create_match command parameters."""
    date: str = Field(..., description="Match date (YYYY-MM-DD)")
    time: str = Field(..., description="Match time (HH:MM)")
    location: str = Field(..., description="Match location")
    opponent: Optional[str] = Field(None, description="Opponent team name")
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if not validate_date_format(v, "%Y-%m-%d"):
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v
    
    @field_validator('time')
    @classmethod
    def validate_time(cls, v):
        if not validate_time_format(v, "%H:%M"):
            raise ValueError('Time must be in HH:MM format')
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


# ============================================================================
# PAYMENT COMMAND MODELS
# ============================================================================

class CreatePaymentCommand(BaseModel):
    """Model for /create_payment command parameters."""
    amount: float = Field(..., gt=0, description="Payment amount")
    description: str = Field(..., description="Payment description")
    player_id: Optional[str] = Field(None, description="Player ID for player-specific payment")
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class PaymentStatusCommand(BaseModel):
    """Model for /payment_status command parameters."""
    payment_id: Optional[str] = Field(None, description="Payment ID to check")
    player_id: Optional[str] = Field(None, description="Player ID to check payments for")


class PendingPaymentsCommand(BaseModel):
    """Model for /pending_payments command parameters."""
    filter: Optional[str] = Field(None, description="Filter type (overdue, upcoming, etc.)")


class PaymentHistoryCommand(BaseModel):
    """Model for /payment_history command parameters."""
    player_id: Optional[str] = Field(None, description="Player ID to get history for")
    period: Optional[str] = Field(None, description="Time period (week, month, year)")


class FinancialDashboardCommand(BaseModel):
    """Model for /financial_dashboard command parameters."""
    period: Optional[str] = Field("month", description="Time period (week, month, year)")


# ============================================================================
# ADMIN COMMAND MODELS
# ============================================================================

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


# ============================================================================
# COMMAND PARSER USING TYPER
# ============================================================================

class CommandType(str, Enum):
    """Command types supported by the parser."""
    # Player Management Commands
    ADD_PLAYER = "add_player"
    REGISTER = "register"
    REMOVE_PLAYER = "remove_player"
    APPROVE = "approve"
    REJECT = "reject"
    INVITE = "invite"
    STATUS = "status"
    LIST = "list"
    HELP = "help"
    START = "start"
    PENDING = "pending"
    
    # Onboarding Commands
    START_ONBOARDING = "start_onboarding"
    PROCESS_ONBOARDING_RESPONSE = "process_onboarding_response"
    ONBOARDING_STATUS = "onboarding_status"
    
    # Team Management Commands
    ADD_TEAM = "add_team"
    REMOVE_TEAM = "remove_team"
    LIST_TEAMS = "list_teams"
    UPDATE_TEAM_INFO = "update_team_info"
    
    # Match Commands
    CREATE_MATCH = "create_match"
    ATTEND_MATCH = "attend_match"
    UNATTEND_MATCH = "unattend_match"
    LIST_MATCHES = "list_matches"
    RECORD_RESULT = "record_result"
    
    # Payment Commands
    CREATE_PAYMENT = "create_payment"
    PAYMENT_STATUS = "payment_status"
    PENDING_PAYMENTS = "pending_payments"
    PAYMENT_HISTORY = "payment_history"
    FINANCIAL_DASHBOARD = "financial_dashboard"
    
    # Admin Commands
    BROADCAST = "broadcast"
    PROMOTE_USER = "promote_user"
    DEMOTE_USER = "demote_user"
    SYSTEM_STATUS = "system_status"


@dataclass
class ParsedCommand:
    """Result of command parsing."""
    command_type: CommandType
    parameters: Dict[str, Any] = None
    raw_text: str = ""
    is_valid: bool = True
    error_message: str = ""
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.validation_errors is None:
            self.validation_errors = []
    
    def get_parameter(self, key: str) -> Any:
        """Get a parameter value by key."""
        return self.parameters.get(key)


class ImprovedCommandParser:
    """Command parser using Typer and Pydantic for robust parsing and validation."""
    
    def __init__(self):
        self.app = Typer(help="KICKAI Bot Commands")
        self._setup_commands()
    
    def _setup_commands(self):
        """Setup all command handlers using Typer."""
        
        @self.app.command("add")
        def add_player(
            name_and_phone: str = typer.Argument(..., help="Player's full name and phone number"),
            position: PlayerPosition = typer.Option(PlayerPosition.ANY, help="Player position (optional, default: Any)"),
            admin_approved: bool = typer.Option(False, "--admin-approved", help="Admin approval status")
        ):
            """Add a new player to the team."""
            pass
        
        @self.app.command("register")
        def register(
            player_id: str = typer.Argument(..., help="Player ID for simple registration"),
            name: str = typer.Option(None, help="Your full name (for full registration)"),
            phone: str = typer.Option(None, help="Your UK mobile number (for full registration)"),
            position: PlayerPosition = typer.Option(PlayerPosition.UTILITY, help="Your preferred position (for full registration)")
        ):
            """Register yourself as a player."""
            pass
        
        @self.app.command("remove")
        def remove_player(
            identifier: str = typer.Argument(..., help="Phone number or player name")
        ):
            """Remove a player from the team."""
            pass
        
        @self.app.command("approve")
        def approve_player(
            player_id: str = typer.Argument(..., help="Player ID or name")
        ):
            """Approve a pending player."""
            pass
        
        @self.app.command("reject")
        def reject_player(
            player_id: str = typer.Argument(..., help="Player ID or name"),
            reason: str = typer.Option("No reason provided", help="Reason for rejection")
        ):
            """Reject a pending player."""
            pass
        
        @self.app.command("invite")
        def invite_player(
            identifier: str = typer.Argument(..., help="Phone number or player name")
        ):
            """Generate invitation for a player."""
            pass
        
        @self.app.command("status")
        def status(
            identifier: str = typer.Argument(..., help="Phone number or player name")
        ):
            """Check player status."""
            pass
        
        @self.app.command("list")
        def list_players(
            filter: str = typer.Option(None, help="Filter type (pending, active, etc.)")
        ):
            """List players or other items."""
            pass
        
        @self.app.command("help")
        def help_command(
            command: str = typer.Option(None, help="Specific command to get help for")
        ):
            """Show help information."""
            pass
        
        @self.app.command("start")
        def start():
            """Start the bot."""
            pass
        
        @self.app.command("pending")
        def pending():
            """Show pending approvals."""
            pass
        
        # ============================================================================
        # ONBOARDING COMMANDS
        # ============================================================================
        
        @self.app.command("start_onboarding")
        def start_onboarding(
            user_id: str = typer.Option(None, help="User ID to start onboarding for")
        ):
            """Start the onboarding process for a user."""
            pass
        
        @self.app.command("process_onboarding_response")
        def process_onboarding_response(
            response: str = typer.Argument(..., help="User's onboarding response"),
            step: str = typer.Option(None, help="Current onboarding step")
        ):
            """Process a user's onboarding response."""
            pass
        
        @self.app.command("onboarding_status")
        def onboarding_status(
            user_id: str = typer.Option(None, help="User ID to check status for")
        ):
            """Check onboarding status for a user."""
            pass
        
        # ============================================================================
        # TEAM MANAGEMENT COMMANDS
        # ============================================================================
        
        @self.app.command("add_team")
        def add_team(
            team_name: str = typer.Argument(..., help="Team name"),
            description: str = typer.Option(None, help="Team description")
        ):
            """Add a new team."""
            pass
        
        @self.app.command("remove_team")
        def remove_team(
            team_id: str = typer.Argument(..., help="Team ID or name")
        ):
            """Remove a team."""
            pass
        
        @self.app.command("list_teams")
        def list_teams(
            filter: str = typer.Option(None, help="Filter type (active, inactive, etc.)")
        ):
            """List all teams."""
            pass
        
        @self.app.command("update_team_info")
        def update_team_info(
            team_id: str = typer.Argument(..., help="Team ID or name"),
            field: str = typer.Argument(..., help="Field to update (name, description, etc.)"),
            value: str = typer.Argument(..., help="New value")
        ):
            """Update team information."""
            pass
        
        # ============================================================================
        # MATCH COMMANDS
        # ============================================================================
        
        @self.app.command("create_match")
        def create_match(
            date: str = typer.Argument(..., help="Match date (YYYY-MM-DD)"),
            time: str = typer.Argument(..., help="Match time (HH:MM)"),
            location: str = typer.Argument(..., help="Match location"),
            opponent: str = typer.Option(None, help="Opponent team name")
        ):
            """Create a new match."""
            pass
        
        @self.app.command("attend_match")
        def attend_match(
            match_id: str = typer.Argument(..., help="Match ID"),
            availability: str = typer.Option("yes", help="Availability (yes/no/maybe)")
        ):
            """Mark attendance for a match."""
            pass
        
        @self.app.command("unattend_match")
        def unattend_match(
            match_id: str = typer.Argument(..., help="Match ID")
        ):
            """Remove attendance for a match."""
            pass
        
        @self.app.command("list_matches")
        def list_matches(
            filter: str = typer.Option(None, help="Filter type (upcoming, past, etc.)")
        ):
            """List all matches."""
            pass
        
        @self.app.command("record_result")
        def record_result(
            match_id: str = typer.Argument(..., help="Match ID"),
            our_score: int = typer.Argument(..., help="Our team's score"),
            their_score: int = typer.Argument(..., help="Opponent's score"),
            notes: str = typer.Option(None, help="Additional notes")
        ):
            """Record match result."""
            pass
        
        # ============================================================================
        # PAYMENT COMMANDS
        # ============================================================================
        
        @self.app.command("create_payment")
        def create_payment(
            amount: float = typer.Argument(..., help="Payment amount"),
            description: str = typer.Argument(..., help="Payment description"),
            player_id: str = typer.Option(None, help="Player ID for player-specific payment")
        ):
            """Create a new payment."""
            pass
        
        @self.app.command("payment_status")
        def payment_status(
            payment_id: str = typer.Option(None, help="Payment ID to check"),
            player_id: str = typer.Option(None, help="Player ID to check payments for")
        ):
            """Check payment status."""
            pass
        
        @self.app.command("pending_payments")
        def pending_payments(
            filter: str = typer.Option(None, help="Filter type (overdue, upcoming, etc.)")
        ):
            """List pending payments."""
            pass
        
        @self.app.command("payment_history")
        def payment_history(
            player_id: str = typer.Option(None, help="Player ID to get history for"),
            period: str = typer.Option(None, help="Time period (week, month, year)")
        ):
            """Get payment history."""
            pass
        
        @self.app.command("financial_dashboard")
        def financial_dashboard(
            period: str = typer.Option("month", help="Time period (week, month, year)")
        ):
            """Show financial dashboard."""
            pass
        
        # ============================================================================
        # ADMIN COMMANDS
        # ============================================================================
        
        @self.app.command("broadcast")
        def broadcast(
            message: str = typer.Argument(..., help="Message to broadcast"),
            target: str = typer.Option("all", help="Target audience (all, players, admins)")
        ):
            """Broadcast a message to users."""
            pass
        
        @self.app.command("promote_user")
        def promote_user(
            user_id: str = typer.Argument(..., help="User ID to promote"),
            role: str = typer.Argument(..., help="New role (admin, moderator, etc.)")
        ):
            """Promote a user to a higher role."""
            pass
        
        @self.app.command("demote_user")
        def demote_user(
            user_id: str = typer.Argument(..., help="User ID to demote"),
            reason: str = typer.Option(None, help="Reason for demotion")
        ):
            """Demote a user to a lower role."""
            pass
        
        @self.app.command("system_status")
        def system_status(
            detailed: bool = typer.Option(False, help="Show detailed status information")
        ):
            """Show system status."""
            pass
    
    def parse(self, text: str) -> ParsedCommand:
        """Parse a command from text using Typer and Pydantic validation."""
        text = text.strip()
        
        # Handle empty or invalid input
        if not text:
            return ParsedCommand(
                command_type=CommandType.START,
                raw_text=text,
                is_valid=False,
                error_message="Empty command"
            )
        
        # Extract command name
        parts = text.split()
        if not parts:
            return ParsedCommand(
                command_type=CommandType.START,
                raw_text=text,
                is_valid=False,
                error_message="No command found"
            )
        
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Map command names to types
        command_mapping = {
            # Player Management Commands
            "/add": CommandType.ADD_PLAYER,
            "/register": CommandType.REGISTER,
            "/remove": CommandType.REMOVE_PLAYER,
            "/approve": CommandType.APPROVE,
            "/reject": CommandType.REJECT,
            "/invite": CommandType.INVITE,
            "/status": CommandType.STATUS,
            "/list": CommandType.LIST,
            "/help": CommandType.HELP,
            "/start": CommandType.START,
            "/pending": CommandType.PENDING,
            
            # Onboarding Commands
            "/start_onboarding": CommandType.START_ONBOARDING,
            "/process_onboarding_response": CommandType.PROCESS_ONBOARDING_RESPONSE,
            "/onboarding_status": CommandType.ONBOARDING_STATUS,
            
            # Team Management Commands
            "/add_team": CommandType.ADD_TEAM,
            "/remove_team": CommandType.REMOVE_TEAM,
            "/list_teams": CommandType.LIST_TEAMS,
            "/update_team_info": CommandType.UPDATE_TEAM_INFO,
            
            # Match Commands
            "/create_match": CommandType.CREATE_MATCH,
            "/attend_match": CommandType.ATTEND_MATCH,
            "/unattend_match": CommandType.UNATTEND_MATCH,
            "/list_matches": CommandType.LIST_MATCHES,
            "/record_result": CommandType.RECORD_RESULT,
            
            # Payment Commands
            "/create_payment": CommandType.CREATE_PAYMENT,
            "/payment_status": CommandType.PAYMENT_STATUS,
            "/pending_payments": CommandType.PENDING_PAYMENTS,
            "/payment_history": CommandType.PAYMENT_HISTORY,
            "/financial_dashboard": CommandType.FINANCIAL_DASHBOARD,
            
            # Admin Commands
            "/broadcast": CommandType.BROADCAST,
            "/promote_user": CommandType.PROMOTE_USER,
            "/demote_user": CommandType.DEMOTE_USER,
            "/system_status": CommandType.SYSTEM_STATUS,
        }
        
        if command_name not in command_mapping:
            return ParsedCommand(
                command_type=CommandType.START,
                raw_text=text,
                is_valid=False,
                error_message=f"Unknown command: {command_name}"
            )
        
        command_type = command_mapping[command_name]
        
        # Validate parameters using Pydantic models
        try:
            parameters = self._validate_parameters(command_type, args, text)
            return ParsedCommand(
                command_type=command_type,
                parameters=parameters,
                raw_text=text,
                is_valid=True
            )
        except ValidationError as e:
            return ParsedCommand(
                command_type=command_type,
                raw_text=text,
                is_valid=False,
                error_message="Parameter validation failed",
                validation_errors=[str(error) for error in e.errors()]
            )
        except Exception as e:
            return ParsedCommand(
                command_type=command_type,
                raw_text=text,
                is_valid=False,
                error_message=f"Parsing error: {str(e)}"
            )
    
    def _validate_parameters(self, command_type: CommandType, args: List[str], raw_text: str) -> Dict[str, Any]:
        """Validate parameters using appropriate Pydantic model."""
        
        if command_type == CommandType.ADD_PLAYER:
            # Parse /add name phone [position] [admin_approved]
            # Find the phone number in the arguments
            import re
            phone_pattern = r'^((?:\+44|0)7\d{9})$'
            phone_index = None
            phone = None
            for i, arg in enumerate(args):
                if re.match(phone_pattern, arg):
                    phone_index = i
                    phone = arg
                    break
            if phone_index is None:
                raise ValueError("Could not find valid UK phone number in the input")
            name = " ".join(args[:phone_index])
            position = args[phone_index + 1] if phone_index + 1 < len(args) else PlayerPosition.ANY
            admin_approved = False
            if phone_index + 2 < len(args):
                admin_flag = args[phone_index + 2].lower()
                admin_approved = admin_flag in ['true', 'yes', 'y', '1']
            from utils.phone_utils import normalize_phone
            normalized_name = " ".join(word.capitalize() for word in name.strip().split())
            normalized_phone = normalize_phone(phone)
            normalized_position = position if isinstance(position, PlayerPosition) else position.lower().strip()
            if not normalized_position or normalized_position == "any":
                normalized_position = PlayerPosition.ANY
            model = AddPlayerCommand(
                name=normalized_name,
                phone=normalized_phone,
                position=normalized_position,
                admin_approved=admin_approved
            )
            return model.dict()
        
        elif command_type == CommandType.REGISTER:
            # Parse /register name phone [position]
            if len(args) < 2:
                raise ValueError("Register command requires: name phone [position]")
            
            name = args[0]
            phone = args[1]
            position = args[2] if len(args) > 2 else PlayerPosition.UTILITY
            
            model = RegisterCommand(
                name=name,
                phone=phone,
                position=position
            )
            return model.dict()
        
        elif command_type == CommandType.REMOVE_PLAYER:
            # Parse /remove identifier
            if len(args) < 1:
                raise ValueError("Remove command requires: identifier")
            
            model = RemovePlayerCommand(identifier=args[0])
            return model.dict()
        
        elif command_type == CommandType.APPROVE:
            # Parse /approve player_id
            if len(args) < 1:
                raise ValueError("Approve command requires: player_id")
            
            model = ApprovePlayerCommand(player_id=args[0])
            return model.dict()
        
        elif command_type == CommandType.REJECT:
            # Parse /reject player_id [reason]
            if len(args) < 1:
                raise ValueError("Reject command requires: player_id [reason]")
            
            player_id = args[0]
            reason = " ".join(args[1:]) if len(args) > 1 else "No reason provided"
            
            model = RejectPlayerCommand(player_id=player_id, reason=reason)
            return model.dict()
        
        elif command_type == CommandType.INVITE:
            # Parse /invite identifier
            if len(args) < 1:
                raise ValueError("Invite command requires: identifier")
            
            model = InvitePlayerCommand(identifier=args[0])
            return model.dict()
        
        elif command_type == CommandType.STATUS:
            # Parse /status identifier
            if len(args) < 1:
                raise ValueError("Status command requires: identifier")
            
            model = StatusCommand(identifier=args[0])
            return model.dict()
        
        elif command_type == CommandType.LIST:
            # Parse /list [filter]
            filter_type = args[0] if args else None
            
            model = ListCommand(filter=filter_type)
            return model.dict()
        
        elif command_type == CommandType.HELP:
            # Parse /help [command]
            command = args[0] if args else None
            
            model = HelpCommand(command=command)
            return model.dict()
        
        elif command_type in [CommandType.START, CommandType.PENDING]:
            # No parameters needed
            return {}
        
        # ============================================================================
        # ONBOARDING COMMANDS
        # ============================================================================
        
        elif command_type == CommandType.START_ONBOARDING:
            # Parse /start_onboarding [user_id]
            user_id = args[0] if args else None
            
            model = StartOnboardingCommand(user_id=user_id)
            return model.dict()
        
        elif command_type == CommandType.PROCESS_ONBOARDING_RESPONSE:
            # Parse /process_onboarding_response response [step]
            if len(args) < 1:
                raise ValueError("Process onboarding response requires: response [step]")
            
            response = args[0]
            step = args[1] if len(args) > 1 else None
            
            model = ProcessOnboardingResponseCommand(response=response, step=step)
            return model.dict()
        
        elif command_type == CommandType.ONBOARDING_STATUS:
            # Parse /onboarding_status [user_id]
            user_id = args[0] if args else None
            
            model = OnboardingStatusCommand(user_id=user_id)
            return model.dict()
        
        # ============================================================================
        # TEAM MANAGEMENT COMMANDS
        # ============================================================================
        
        elif command_type == CommandType.ADD_TEAM:
            # Parse /add_team team_name [description]
            if len(args) < 1:
                raise ValueError("Add team requires: team_name [description]")
            
            team_name = args[0]
            description = " ".join(args[1:]) if len(args) > 1 else None
            
            model = AddTeamCommand(team_name=team_name, description=description)
            return model.dict()
        
        elif command_type == CommandType.REMOVE_TEAM:
            # Parse /remove_team team_id
            if len(args) < 1:
                raise ValueError("Remove team requires: team_id")
            
            model = RemoveTeamCommand(team_id=args[0])
            return model.dict()
        
        elif command_type == CommandType.LIST_TEAMS:
            # Parse /list_teams [filter]
            filter_type = args[0] if args else None
            
            model = ListTeamsCommand(filter=filter_type)
            return model.dict()
        
        elif command_type == CommandType.UPDATE_TEAM_INFO:
            # Parse /update_team_info team_id field value
            if len(args) < 3:
                raise ValueError("Update team info requires: team_id field value")
            
            team_id = args[0]
            field = args[1]
            value = " ".join(args[2:])
            
            model = UpdateTeamInfoCommand(team_id=team_id, field=field, value=value)
            return model.dict()
        
        # ============================================================================
        # MATCH COMMANDS
        # ============================================================================
        
        elif command_type == CommandType.CREATE_MATCH:
            # Parse /create_match date time location [opponent]
            if len(args) < 3:
                raise ValueError("Create match requires: date time location [opponent]")
            
            date = args[0]
            time = args[1]
            location = args[2]
            opponent = " ".join(args[3:]) if len(args) > 3 else None
            
            model = CreateMatchCommand(date=date, time=time, location=location, opponent=opponent)
            return model.dict()
        
        elif command_type == CommandType.ATTEND_MATCH:
            # Parse /attend_match match_id [availability]
            if len(args) < 1:
                raise ValueError("Attend match requires: match_id [availability]")
            
            match_id = args[0]
            availability = args[1] if len(args) > 1 else "yes"
            
            model = AttendMatchCommand(match_id=match_id, availability=availability)
            return model.dict()
        
        elif command_type == CommandType.UNATTEND_MATCH:
            # Parse /unattend_match match_id
            if len(args) < 1:
                raise ValueError("Unattend match requires: match_id")
            
            model = UnattendMatchCommand(match_id=args[0])
            return model.dict()
        
        elif command_type == CommandType.LIST_MATCHES:
            # Parse /list_matches [filter]
            filter_type = args[0] if args else None
            
            model = ListMatchesCommand(filter=filter_type)
            return model.dict()
        
        elif command_type == CommandType.RECORD_RESULT:
            # Parse /record_result match_id our_score their_score [notes]
            if len(args) < 3:
                raise ValueError("Record result requires: match_id our_score their_score [notes]")
            
            match_id = args[0]
            our_score = int(args[1])
            their_score = int(args[2])
            notes = " ".join(args[3:]) if len(args) > 3 else None
            
            model = RecordResultCommand(match_id=match_id, our_score=our_score, their_score=their_score, notes=notes)
            return model.dict()
        
        # ============================================================================
        # PAYMENT COMMANDS
        # ============================================================================
        
        elif command_type == CommandType.CREATE_PAYMENT:
            # Parse /create_payment amount description [player_id]
            if len(args) < 2:
                raise ValueError("Create payment requires: amount description [player_id]")
            
            amount = float(args[0])
            description = args[1]
            player_id = args[2] if len(args) > 2 else None
            
            model = CreatePaymentCommand(amount=amount, description=description, player_id=player_id)
            return model.dict()
        
        elif command_type == CommandType.PAYMENT_STATUS:
            # Parse /payment_status [payment_id] [player_id]
            payment_id = args[0] if args else None
            player_id = args[1] if len(args) > 1 else None
            
            model = PaymentStatusCommand(payment_id=payment_id, player_id=player_id)
            return model.dict()
        
        elif command_type == CommandType.PENDING_PAYMENTS:
            # Parse /pending_payments [filter]
            filter_type = args[0] if args else None
            
            model = PendingPaymentsCommand(filter=filter_type)
            return model.dict()
        
        elif command_type == CommandType.PAYMENT_HISTORY:
            # Parse /payment_history [player_id] [period]
            player_id = args[0] if args else None
            period = args[1] if len(args) > 1 else None
            
            model = PaymentHistoryCommand(player_id=player_id, period=period)
            return model.dict()
        
        elif command_type == CommandType.FINANCIAL_DASHBOARD:
            # Parse /financial_dashboard [period]
            period = args[0] if args else "month"
            
            model = FinancialDashboardCommand(period=period)
            return model.dict()
        
        # ============================================================================
        # ADMIN COMMANDS
        # ============================================================================
        
        elif command_type == CommandType.BROADCAST:
            # Parse /broadcast message [target]
            if len(args) < 1:
                raise ValueError("Broadcast requires: message [target]")
            
            message = args[0]
            target = args[1] if len(args) > 1 else "all"
            
            model = BroadcastCommand(message=message, target=target)
            return model.dict()
        
        elif command_type == CommandType.PROMOTE_USER:
            # Parse /promote_user user_id role
            if len(args) < 2:
                raise ValueError("Promote user requires: user_id role")
            
            user_id = args[0]
            role = args[1]
            
            model = PromoteUserCommand(user_id=user_id, role=role)
            return model.dict()
        
        elif command_type == CommandType.DEMOTE_USER:
            # Parse /demote_user user_id [reason]
            if len(args) < 1:
                raise ValueError("Demote user requires: user_id [reason]")
            
            user_id = args[0]
            reason = " ".join(args[1:]) if len(args) > 1 else None
            
            model = DemoteUserCommand(user_id=user_id, reason=reason)
            return model.dict()
        
        elif command_type == CommandType.SYSTEM_STATUS:
            # Parse /system_status [detailed]
            detailed = len(args) > 0 and args[0].lower() in ['true', 'yes', 'y', '1', 'detailed']
            
            model = SystemStatusCommand(detailed=detailed)
            return model.dict()
        
        else:
            raise ValueError(f"Unsupported command type: {command_type}")
    
    def get_help_text(self, command_type: Optional[CommandType] = None) -> str:
        """Get help text using Typer's built-in help system."""
        if command_type:
            # Get help for specific command
            try:
                # This would need to be implemented with Typer's help system
                return f"Help for {command_type.value} command"
            except Exception:
                return f"Unknown command: {command_type.value}"
        else:
            # Get general help
            return """🤖 **KICKAI Bot Commands**

**Player Management:**
• `/add [name] [phone] [position] [admin_approved]` - Add a player
• `/register [name] [phone] [position]` - Self-registration
• `/remove [identifier]` - Remove a player
• `/approve [player_id]` - Approve a player
• `/reject [player_id] [reason]` - Reject a player

**Information:**
• `/status [identifier]` - Check player status
• `/list [filter]` - List players
• `/pending` - Show pending approvals
• `/invite [identifier]` - Generate invitation

**Onboarding:**
• `/start_onboarding [user_id]` - Start onboarding process
• `/process_onboarding_response [response] [step]` - Process onboarding response
• `/onboarding_status [user_id]` - Check onboarding status

**Team Management:**
• `/add_team [team_name] [description]` - Add a new team
• `/remove_team [team_id]` - Remove a team
• `/list_teams [filter]` - List all teams
• `/update_team_info [team_id] [field] [value]` - Update team information

**Match Management:**
• `/create_match [date] [time] [location] [opponent]` - Create a new match
• `/attend_match [match_id] [availability]` - Mark attendance for a match
• `/unattend_match [match_id]` - Remove attendance for a match
• `/list_matches [filter]` - List all matches
• `/record_result [match_id] [our_score] [their_score] [notes]` - Record match result

**Payment Management:**
• `/create_payment [amount] [description] [player_id]` - Create a new payment
• `/payment_status [payment_id] [player_id]` - Check payment status
• `/pending_payments [filter]` - List pending payments
• `/payment_history [player_id] [period]` - Get payment history
• `/financial_dashboard [period]` - Show financial dashboard

**Admin Commands:**
• `/broadcast [message] [target]` - Broadcast a message to users
• `/promote_user [user_id] [role]` - Promote a user to a higher role
• `/demote_user [user_id] [reason]` - Demote a user to a lower role
• `/system_status [detailed]` - Show system status

**General:**
• `/start` - Start the bot
• `/help [command]` - Show help

Use `/help [command]` for detailed help on specific commands."""


# Global parser instance
_improved_parser = None

def get_improved_parser() -> ImprovedCommandParser:
    """Get the global improved command parser instance."""
    global _improved_parser
    if _improved_parser is None:
        _improved_parser = ImprovedCommandParser()
    return _improved_parser


def parse_command_improved(text: str) -> ParsedCommand:
    """Parse a command using the improved parser with Typer and Pydantic."""
    return get_improved_parser().parse(text)


def parse_command(text: str) -> ParsedCommand:
    """Parse a command using the improved parser with Typer and Pydantic."""
    return get_improved_parser().parse(text)


def get_help_text_improved(command_type: Optional[CommandType] = None) -> str:
    """Get help text using the improved parser."""
    return get_improved_parser().get_help_text(command_type) 