"""
Mock Services Package

This package contains mock implementations of service interfaces for testing.
These mocks provide predictable behavior and can be easily controlled in tests.
"""

from .mock_player_service import MockPlayerService
from .mock_team_service import MockTeamService
from .mock_fa_registration_checker import MockFARegistrationChecker
from .mock_daily_status_service import MockDailyStatusService
from .mock_access_control_service import MockAccessControlService
from .mock_team_member_service import MockTeamMemberService
from .mock_bot_status_service import MockBotStatusService
from .mock_monitoring_service import MockMonitoringService
from .mock_multi_team_manager import MockMultiTeamManager

__all__ = [
    'MockPlayerService',
    'MockTeamService',
    'MockFARegistrationChecker',
    'MockDailyStatusService',
    'MockAccessControlService',
    'MockTeamMemberService',
    'MockBotStatusService',
    'MockMonitoringService',
    'MockMultiTeamManager'
] 