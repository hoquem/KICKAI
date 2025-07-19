"""
Modular Command Parser

This package provides a modular command parsing system that replaces the monolithic
ImprovedCommandParser with smaller, focused components following the single responsibility principle.
"""

from .parser import ImprovedCommandParser, parse_command_improved, get_improved_parser
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
from .validators import CommandValidator, FieldValidator
# Help generation moved to permission service

__all__ = [
    'ImprovedCommandParser',
    'parse_command_improved',
    'get_improved_parser',
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
    # Help generation moved to permission service
] 