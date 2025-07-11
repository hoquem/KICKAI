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
    ADD_PLAYER = "addplayer"
    REGISTER = "register"
    REMOVE_PLAYER = "removeplayer"
    APPROVE = "approve"
    REJECT = "reject"
    INVITE_LINK = "invitelink"
    STATUS = "status"
    LIST = "list"
    HELP = "help"
    
    # Team Management Commands
    ADD_TEAM = "addteam"
    REMOVE_TEAM = "removeteam"
    LIST_TEAMS = "listteams"
    UPDATE_TEAM_INFO = "updateteaminfo"
    
    # Match Commands
    CREATE_MATCH = "creatematch"
    ATTEND_MATCH = "attendmatch"
    UNATTEND_MATCH = "unattendmatch"
    LIST_MATCHES = "listmatches"
    RECORD_RESULT = "recordresult"
    
    # Payment Commands
    CREATE_PAYMENT = "createpayment"
    PAYMENT_STATUS = "paymentstatus"
    PENDING_PAYMENTS = "pendingpayments"
    PAYMENT_HISTORY = "paymenthistory"
    FINANCIAL_DASHBOARD = "financialdashboard"
    
    # Admin Commands
    BROADCAST = "broadcast"
    PROMOTE_USER = "promoteuser"
    DEMOTE_USER = "demoteuser"
    SYSTEM_STATUS = "systemstatus"


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
        
        @self.app.command("invitelink")
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
        
        # ============================================================================
        # TEAM MANAGEMENT COMMANDS
        # ============================================================================
        
        @self.app.command("addteam")
        def add_team(
            team_name: str = typer.Argument(..., help="Team name"),
            description: str = typer.Option(None, help="Team description")
        ):
            """Add a new team."""
            pass
        
        @self.app.command("removeteam")
        def remove_team(
            team_id: str = typer.Argument(..., help="Team ID or name")
        ):
            """Remove a team."""
            pass
        
        @self.app.command("listteams")
        def list_teams(
            filter: str = typer.Option(None, help="Filter type (active, inactive, etc.)")
        ):
            """List all teams."""
            pass
        
        @self.app.command("updateteaminfo")
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
        
        @self.app.command("creatematch")
        def create_match(
            date: str = typer.Argument(..., help="Match date (YYYY-MM-DD)"),
            time: str = typer.Argument(..., help="Match time (HH:MM)"),
            location: str = typer.Argument(..., help="Match location"),
            opponent: str = typer.Option(None, help="Opponent team name")
        ):
            """Create a new match."""
            pass
        
        @self.app.command("attendmatch")
        def attend_match(
            match_id: str = typer.Argument(..., help="Match ID"),
            availability: str = typer.Option("yes", help="Availability (yes/no/maybe)")
        ):
            """Mark attendance for a match."""
            pass
        
        @self.app.command("unattendmatch")
        def unattend_match(
            match_id: str = typer.Argument(..., help="Match ID")
        ):
            """Cancel attendance for a match."""
            pass
        
        @self.app.command("listmatches")
        def list_matches(
            filter: str = typer.Option(None, help="Filter type (upcoming, past, etc.)")
        ):
            """List matches."""
            pass
        
        @self.app.command("recordresult")
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
        
        @self.app.command("createpayment")
        def create_payment(
            amount: float = typer.Argument(..., help="Payment amount"),
            description: str = typer.Argument(..., help="Payment description"),
            player_id: str = typer.Option(None, help="Player ID for player-specific payment")
        ):
            """Create a payment."""
            pass
        
        @self.app.command("paymentstatus")
        def payment_status(
            payment_id: str = typer.Option(None, help="Payment ID to check"),
            player_id: str = typer.Option(None, help="Player ID to check payments for")
        ):
            """Check payment status."""
            pass
        
        @self.app.command("pendingpayments")
        def pending_payments(
            filter: str = typer.Option(None, help="Filter type (overdue, upcoming, etc.)")
        ):
            """List pending payments."""
            pass
        
        @self.app.command("paymenthistory")
        def payment_history(
            player_id: str = typer.Option(None, help="Player ID to get history for"),
            period: str = typer.Option(None, help="Time period (week, month, year)")
        ):
            """Get payment history."""
            pass
        
        @self.app.command("financialdashboard")
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
            """Broadcast a message."""
            pass
        
        @self.app.command("promoteuser")
        def promote_user(
            user_id: str = typer.Argument(..., help="User ID to promote"),
            role: str = typer.Argument(..., help="New role (admin, moderator, etc.)")
        ):
            """Promote a user."""
            pass
        
        @self.app.command("demoteuser")
        def demote_user(
            user_id: str = typer.Argument(..., help="User ID to demote"),
            reason: str = typer.Option(None, help="Reason for demotion")
        ):
            """Demote a user."""
            pass
        
        @self.app.command("systemstatus")
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
        
        # Command to type mapping
        self.command_mapping = {
            "/add": CommandType.ADD_PLAYER,
            "/register": CommandType.REGISTER,
            "/remove": CommandType.REMOVE_PLAYER,
            "/approve": CommandType.APPROVE,
            "/reject": CommandType.REJECT,
            "/invitelink": CommandType.INVITE_LINK,
            "/status": CommandType.STATUS,
            "/list": CommandType.LIST,
            "/help": CommandType.HELP,
            
            # Team Management Commands
            "/addteam": CommandType.ADD_TEAM,
            "/removeteam": CommandType.REMOVE_TEAM,
            "/listteams": CommandType.LIST_TEAMS,
            "/updateteaminfo": CommandType.UPDATE_TEAM_INFO,
            
            # Match Commands
            "/creatematch": CommandType.CREATE_MATCH,
            "/attendmatch": CommandType.ATTEND_MATCH,
            "/unattendmatch": CommandType.UNATTEND_MATCH,
            "/listmatches": CommandType.LIST_MATCHES,
            "/recordresult": CommandType.RECORD_RESULT,
            
            # Payment Commands
            "/createpayment": CommandType.CREATE_PAYMENT,
            "/paymentstatus": CommandType.PAYMENT_STATUS,
            "/pendingpayments": CommandType.PENDING_PAYMENTS,
            "/paymenthistory": CommandType.PAYMENT_HISTORY,
            "/financialdashboard": CommandType.FINANCIAL_DASHBOARD,
            
            # Admin Commands
            "/broadcast": CommandType.BROADCAST,
            "/promoteuser": CommandType.PROMOTE_USER,
            "/demoteuser": CommandType.DEMOTE_USER,
            "/systemstatus": CommandType.SYSTEM_STATUS,
        }
        
        if command_name not in self.command_mapping:
            return ParsedCommand(
                command_type=CommandType.START,
                raw_text=text,
                is_valid=False,
                error_message=f"Unknown command: {command_name}"
            )
        
        command_type = self.command_mapping[command_name]
        
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
            # Parse /register player_id
            if len(args) < 1:
                raise ValueError("Register command requires: player_id")
            
            player_id = args[0]
            
            model = RegisterCommand(
                player_id=player_id
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
        
        elif command_type == CommandType.INVITE_LINK:
            # Parse /invitelink identifier
            if len(args) < 1:
                raise ValueError("Invite link command requires: identifier")
            
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
            help_text = """
🤖 KICKAI Bot Commands

📋 PLAYER MANAGEMENT:
• `/add [name] [phone] [position]` - Add player
• `/register [player_id]` - Register yourself
• `/remove [identifier]` - Remove player
• `/approve [player_id]` - Approve player
• `/reject [player_id] [reason]` - Reject player
• `/invitelink [identifier]` - Generate invitation
• `/status [identifier]` - Check player status
• `/list [filter]` - List players
• `/pending` - Show pending approvals

🏆 TEAM MANAGEMENT:
• `/addteam [name] [description]` - Add team
• `/removeteam [team_id]` - Remove team
• `/listteams [filter]` - List teams
• `/updateteaminfo [team_id] [field] [value]` - Update team

⚽ MATCH MANAGEMENT:
• `/creatematch [date] [time] [location] [opponent]` - Create match
• `/attendmatch [match_id] [availability]` - Mark attendance
• `/unattendmatch [match_id]` - Cancel attendance
• `/listmatches [filter]` - List matches
• `/recordresult [match_id] [our_score] [their_score]` - Record result

💰 PAYMENT MANAGEMENT:
• `/createpayment [amount] [description] [player_id]` - Create payment
• `/paymentstatus [payment_id/player_id]` - Check status
• `/pendingpayments [filter]` - List pending
• `/paymenthistory [player_id] [period]` - Get history
• `/financialdashboard [period]` - Show dashboard

👑 ADMIN COMMANDS:
• `/broadcast [message] [target]` - Broadcast message
• `/promoteuser [user_id] [role]` - Promote user
• `/demoteuser [user_id] [reason]` - Demote user
• `/systemstatus [detailed]` - Show system status

💡 For detailed help on any command, type: `/help [command]`
"""
            return help_text 


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