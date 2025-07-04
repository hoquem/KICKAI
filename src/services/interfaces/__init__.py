"""
Service Interfaces Package

This package contains abstract base classes (interfaces) for all major services
in the KICKAI system. These interfaces define contracts that concrete service
implementations must follow, enabling easier testing, mocking, and dependency injection.
"""

from .player_service_interface import IPlayerService
from .team_service_interface import ITeamService
from .fa_registration_checker_interface import IFARegistrationChecker
from .daily_status_service_interface import IDailyStatusService
from .access_control_service_interface import IAccessControlService
from .team_member_service_interface import ITeamMemberService
from .bot_status_service_interface import IBotStatusService
from .monitoring_service_interface import IMonitoringService
from .multi_team_manager_interface import IMultiTeamManager

__all__ = [
    'IPlayerService',
    'ITeamService', 
    'IFARegistrationChecker',
    'IDailyStatusService',
    'IAccessControlService',
    'ITeamMemberService',
    'IBotStatusService',
    'IMonitoringService',
    'IMultiTeamManager'
] 