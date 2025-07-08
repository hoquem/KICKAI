"""
Domain adapters package.

This package contains adapters that implement domain interfaces
by wrapping application layer services.
"""

from src.domain.adapters.player_operations_adapter import PlayerOperationsAdapter
from src.domain.adapters.team_operations_adapter import TeamOperationsAdapter
from src.domain.adapters.match_operations_adapter import MatchOperationsAdapter
from src.domain.adapters.payment_operations_adapter import PaymentOperationsAdapter
from src.domain.adapters.utility_operations_adapter import UtilityOperationsAdapter
from src.domain.adapters.user_management_adapter import UserManagementAdapter

__all__ = [
    'PlayerOperationsAdapter',
    'TeamOperationsAdapter',
    'MatchOperationsAdapter',
    'PaymentOperationsAdapter',
    'UtilityOperationsAdapter',
    'UserManagementAdapter',
] 