#!/usr/bin/env python3
"""
Improved Command Parser - Modular Architecture

This module has been refactored to use a modular architecture with separate
components for models, validation, and help generation.

The monolithic parser has been split into focused components:
- models/: Pydantic models for command validation
- validators/: Field and command validation logic
- help/: Help text generation and documentation
- parser.py: Main orchestrator class

This refactoring follows the single responsibility principle and improves
maintainability and testability.
"""

# Import from the new modular structure
from .command_parser import (
    ImprovedCommandParser,
    parse_command_improved,
    get_improved_parser,
    parse_command,
    get_help_text_improved,
    ParsedCommand
)

from .command_parser.models import (
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

from .command_parser.validators import CommandValidator, FieldValidator
from .command_parser.help import HelpGenerator, CommandDocumentation

# Re-export for backward compatibility
__all__ = [
    'ImprovedCommandParser',
    'parse_command_improved',
    'get_improved_parser',
    'parse_command',
    'get_help_text_improved',
    'ParsedCommand',
    'PlayerPosition',
    'UKPhoneNumber',
    'AddPlayerCommand',
    'RegisterCommand',
    'RemovePlayerCommand',
    'ApprovePlayerCommand',
    'RejectPlayerCommand',
    'InvitePlayerCommand',
    'StatusCommand',
    'ListCommand',
    'HelpCommand',
    'AddTeamCommand',
    'RemoveTeamCommand',
    'ListTeamsCommand',
    'UpdateTeamInfoCommand',
    'CreateMatchCommand',
    'AttendMatchCommand',
    'UnattendMatchCommand',
    'ListMatchesCommand',
    'RecordResultCommand',
    'CreatePaymentCommand',
    'PaymentStatusCommand',
    'PendingPaymentsCommand',
    'PaymentHistoryCommand',
    'FinancialDashboardCommand',
    'BroadcastCommand',
    'PromoteUserCommand',
    'DemoteUserCommand',
    'SystemStatusCommand',
    'CommandValidator',
    'FieldValidator',
    'HelpGenerator',
    'CommandDocumentation'
] 