"""
Main Command Parser

This module provides the main command parser that orchestrates all components
following the single responsibility principle.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

try:
    import typer
    from typer import Typer
except ImportError as e:
    raise ImportError(f"Required libraries missing: {e}\nInstall with: pip install typer")

from .models import (
    PlayerPosition, UKPhoneNumber,
    AddPlayerCommand, RegisterCommand, RemovePlayerCommand,
    ApprovePlayerCommand, RejectPlayerCommand, InvitePlayerCommand,
    StatusCommand, ListCommand, HelpCommand,
    AddTeamCommand, RemoveTeamCommand, ListTeamsCommand, UpdateTeamInfoCommand,
    CreateMatchCommand, AttendMatchCommand, UnattendMatchCommand,
    ListMatchesCommand, RecordResultCommand,
    CreatePaymentCommand, PaymentStatusCommand, PendingPaymentsCommand,
    PaymentHistoryCommand, FinancialDashboardCommand,
    BroadcastCommand, PromoteUserCommand, DemoteUserCommand, SystemStatusCommand
)
from .validators import CommandValidator
# Help generation moved to permission service

logger = logging.getLogger(__name__)


@dataclass
class ParsedCommand:
    """Result of command parsing."""
    command_type: str
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
    """
    Improved command parser using modular components.
    
    This class orchestrates the parsing process using separate components
    for validation, help generation, and command handling.
    """
    
    def __init__(self):
        self.app = Typer()
        self.validator = CommandValidator()
        # Help generation moved to permission service
        self._setup_commands()
        logger.info("ImprovedCommandParser initialized with modular components")
    
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
            """Register yourself or another player."""
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
            """Approve a player for team participation."""
            pass
        
        @self.app.command("reject")
        def reject_player(
            player_id: str = typer.Argument(..., help="Player ID or name"),
            reason: str = typer.Option("No reason provided", help="Reason for rejection")
        ):
            """Reject a player from team participation."""
            pass
        
        @self.app.command("invitelink")
        def invite_player(
            identifier: str = typer.Argument(..., help="Phone number or player name")
        ):
            """Generate invitation link for a player."""
            pass
        
        @self.app.command("status")
        def status(
            identifier: str = typer.Argument(..., help="Phone number or player name")
        ):
            """Check player registration status."""
            pass
        
        @self.app.command("list")
        def list_players(
            filter: str = typer.Option(None, help="Filter type (pending, active, etc.)")
        ):
            """List all players."""
            pass
        
        @self.app.command("help")
        def help_command(
            command: str = typer.Option(None, help="Specific command to get help for")
        ):
            """Show help information."""
            pass
        
        # Team commands
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
        
        # Match commands
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
            """Remove attendance for a match."""
            pass
        
        @self.app.command("listmatches")
        def list_matches(
            filter: str = typer.Option(None, help="Filter type (upcoming, past, etc.)")
        ):
            """List all matches."""
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
        
        # Payment commands
        @self.app.command("createpayment")
        def create_payment(
            amount: float = typer.Argument(..., help="Payment amount"),
            description: str = typer.Argument(..., help="Payment description"),
            player_id: str = typer.Option(None, help="Player ID for player-specific payment")
        ):
            """Create a new payment."""
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
        
        # Admin commands
        @self.app.command("broadcast")
        def broadcast(
            message: str = typer.Argument(..., help="Message to broadcast"),
            target: str = typer.Option("all", help="Target audience (all, players, admins)")
        ):
            """Send a broadcast message."""
            pass
        
        @self.app.command("promoteuser")
        def promote_user(
            user_id: str = typer.Argument(..., help="User ID to promote"),
            role: str = typer.Argument(..., help="New role (admin, moderator, etc.)")
        ):
            """Promote a user to admin."""
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
        """
        Parse a command from text using modular components.
        
        Args:
            text: The text to parse
            
        Returns:
            ParsedCommand object with parsing results
        """
        if not text or not text.strip():
            return ParsedCommand(
                command_type="",
                raw_text=text,
                is_valid=False,
                error_message="Empty command"
            )
        
        text = text.strip()
        
        try:
            # Use the validator to parse and validate the command
            validation_result = self.validator.validate_command(text)
            
            if not validation_result.is_valid:
                return ParsedCommand(
                    command_type="",
                    raw_text=text,
                    is_valid=False,
                    error_message=validation_result.error_message,
                    validation_errors=validation_result.validation_errors
                )
            
            return ParsedCommand(
                command_type=validation_result.command_type.value if validation_result.command_type else "",
                parameters=validation_result.parameters or {},
                raw_text=text,
                is_valid=True
            )
            
        except Exception as e:
            logger.error(f"Error parsing command '{text}': {e}")
            return ParsedCommand(
                command_type="",
                raw_text=text,
                is_valid=False,
                error_message=f"Parsing error: {str(e)}"
            )
    
    def get_help_text(self, command_name: Optional[str] = None) -> str:
        """
        Get help text for commands using the help generator.
        
        Args:
            command_name: Optional specific command to get help for
            
        Returns:
            Help text string
        """
        return self.help_generator.get_help_text(command_name)
    
    def get_feature_help(self, feature: str) -> str:
        """
        Get help text for a specific feature.
        
        Args:
            feature: Feature name (player, match, payment, admin, team)
            
        Returns:
            Feature help text
        """
        return self.help_generator.get_feature_help(feature)


# Global parser instance
_parser_instance: Optional[ImprovedCommandParser] = None


def get_improved_parser() -> ImprovedCommandParser:
    """Get the global parser instance."""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = ImprovedCommandParser()
    return _parser_instance


def parse_command_improved(text: str) -> ParsedCommand:
    """Parse a command using the improved parser."""
    parser = get_improved_parser()
    return parser.parse(text)


def parse_command(text: str) -> ParsedCommand:
    """Alias for parse_command_improved for backward compatibility."""
    return parse_command_improved(text)


def get_help_text_improved(command_name: Optional[str] = None) -> str:
    """Get help text using the improved parser."""
    parser = get_improved_parser()
    return parser.get_help_text(command_name) 