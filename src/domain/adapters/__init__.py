"""
Domain adapters package.

This package contains adapters that implement domain interfaces
by wrapping application layer services.
"""

from domain.adapters.player_operations_adapter import PlayerOperationsAdapter
from domain.adapters.team_operations_adapter import TeamOperationsAdapter
from domain.adapters.match_operations_adapter import MatchOperationsAdapter
from domain.adapters.payment_operations_adapter import PaymentOperationsAdapter
from domain.adapters.utility_operations_adapter import UtilityOperationsAdapter
from domain.adapters.user_management_adapter import UserManagementAdapter

__all__ = [
    'PlayerOperationsAdapter',
    'TeamOperationsAdapter',
    'MatchOperationsAdapter',
    'PaymentOperationsAdapter',
    'UtilityOperationsAdapter',
    'UserManagementAdapter',
] 