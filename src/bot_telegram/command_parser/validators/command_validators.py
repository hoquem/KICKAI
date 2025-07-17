"""
Command Validators

This module contains command-level validation logic.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


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
class ValidationResult:
    """Result of command validation."""
    is_valid: bool
    command_type: Optional[CommandType] = None
    parameters: Dict[str, Any] = None
    error_message: str = ""
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.validation_errors is None:
            self.validation_errors = []


class CommandValidator:
    """Handles command-level validation and parsing."""
    
    def __init__(self):
        self.command_mappings = self._build_command_mappings()
    
    def _build_command_mappings(self) -> Dict[str, CommandType]:
        """Build mappings from command names to command types."""
        return {
            # Player commands
            "/add": CommandType.ADD_PLAYER,
            "/register": CommandType.REGISTER,
            "/remove": CommandType.REMOVE_PLAYER,
            "/approve": CommandType.APPROVE,
            "/reject": CommandType.REJECT,
            "/invitelink": CommandType.INVITE_LINK,
            "/status": CommandType.STATUS,
            "/list": CommandType.LIST,
            "/help": CommandType.HELP,
            
            # Team commands
            "/addteam": CommandType.ADD_TEAM,
            "/removeteam": CommandType.REMOVE_TEAM,
            "/listteams": CommandType.LIST_TEAMS,
            "/updateteaminfo": CommandType.UPDATE_TEAM_INFO,
            
            # Match commands
            "/creatematch": CommandType.CREATE_MATCH,
            "/attendmatch": CommandType.ATTEND_MATCH,
            "/unattendmatch": CommandType.UNATTEND_MATCH,
            "/listmatches": CommandType.LIST_MATCHES,
            "/recordresult": CommandType.RECORD_RESULT,
            
            # Payment commands
            "/createpayment": CommandType.CREATE_PAYMENT,
            "/paymentstatus": CommandType.PAYMENT_STATUS,
            "/pendingpayments": CommandType.PENDING_PAYMENTS,
            "/paymenthistory": CommandType.PAYMENT_HISTORY,
            "/financialdashboard": CommandType.FINANCIAL_DASHBOARD,
            
            # Admin commands
            "/broadcast": CommandType.BROADCAST,
            "/promoteuser": CommandType.PROMOTE_USER,
            "/demoteuser": CommandType.DEMOTE_USER,
            "/systemstatus": CommandType.SYSTEM_STATUS,
        }
    
    def validate_command(self, text: str) -> ValidationResult:
        """Validate and parse a command from text."""
        if not text or not text.strip():
            return ValidationResult(False, error_message="Empty command")
        
        text = text.strip()
        
        # Check if it's a slash command
        if text.startswith('/'):
            return self._validate_slash_command(text)
        
        # Check if it's a natural language command
        return self._validate_natural_language_command(text)
    
    def _validate_slash_command(self, text: str) -> ValidationResult:
        """Validate a slash command."""
        parts = text.split()
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Check if command exists
        if command_name not in self.command_mappings:
            return ValidationResult(False, error_message=f"Unknown command: {command_name}")
        
        command_type = self.command_mappings[command_name]
        
        # Validate parameters based on command type
        try:
            parameters = self._validate_parameters(command_type, args, text)
            return ValidationResult(
                is_valid=True,
                command_type=command_type,
                parameters=parameters
            )
        except ValueError as e:
            return ValidationResult(
                is_valid=False,
                command_type=command_type,
                error_message=str(e),
                validation_errors=[str(e)]
            )
    
    def _validate_natural_language_command(self, text: str) -> ValidationResult:
        """Validate a natural language command."""
        # For now, treat as a generic query
        return ValidationResult(
            is_valid=True,
            command_type=CommandType.HELP,
            parameters={"query": text}
        )
    
    def _validate_parameters(self, command_type: CommandType, args: List[str], raw_text: str) -> Dict[str, Any]:
        """Validate parameters for a specific command type."""
        # This is a simplified validation - in practice, you'd use Pydantic models
        parameters = {}
        
        if command_type == CommandType.ADD_PLAYER:
            if len(args) < 2:
                raise ValueError("Usage: /add <name> <phone> [position]")
            parameters["name"] = args[0]
            parameters["phone"] = args[1]
            if len(args) > 2:
                parameters["position"] = args[2]
        
        elif command_type == CommandType.REGISTER:
            if len(args) < 1:
                raise ValueError("Usage: /register <player_id> or /register <name> <phone> [position]")
            if len(args) == 1:
                parameters["player_id"] = args[0]
            else:
                parameters["name"] = args[0]
                parameters["phone"] = args[1]
                if len(args) > 2:
                    parameters["position"] = args[2]
        
        elif command_type == CommandType.STATUS:
            if len(args) < 1:
                raise ValueError("Usage: /status <phone_or_name>")
            parameters["identifier"] = args[0]
        
        elif command_type == CommandType.APPROVE:
            if len(args) < 1:
                raise ValueError("Usage: /approve <player_id>")
            parameters["player_id"] = args[0]
        
        elif command_type == CommandType.REJECT:
            if len(args) < 1:
                raise ValueError("Usage: /reject <player_id> [reason]")
            parameters["player_id"] = args[0]
            if len(args) > 1:
                parameters["reason"] = " ".join(args[1:])
        
        # Add more command validations as needed
        
        return parameters 