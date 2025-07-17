"""
Dependency injection container for managing service dependencies.
Provides a centralized way to manage and inject service dependencies.
"""

from typing import Dict, Any, Optional, Type
from services.interfaces.player_service_interface import IPlayerService
from services.interfaces.team_service_interface import ITeamService
from services.interfaces.payment_service_interface import IPaymentService
from services.interfaces.fa_registration_checker_interface import IFARegistrationChecker
from services.interfaces.daily_status_service_interface import IDailyStatusService
from services.interfaces.expense_service_interface import IExpenseService
from services.interfaces.health_check_service_interface import IHealthCheckService
from services.interfaces.match_service_interface import IMatchService
from services.interfaces.payment_gateway_interface import IPaymentGateway
from services.interfaces.reminder_service_interface import IReminderService
from services.interfaces.team_member_service_interface import ITeamMemberService
from services.interfaces.external_player_service_interface import IExternalPlayerService
from services.interfaces.budget_service_interface import IBudgetService
from services.interfaces.bot_status_service_interface import IBotStatusService
from services.interfaces.monitoring_service_interface import IMonitoringService
from services.interfaces.background_tasks_service_interface import IBackgroundTasksService
from services.interfaces.error_handling_service_interface import IErrorHandlingService
from services.interfaces.financial_report_service_interface import IFinancialReportService
from services.interfaces.user_management_interface import IUserManagement
from services.interfaces.access_control_service_interface import IAccessControlService
from database.interfaces import DataStoreInterface
from database.mock_data_store import MockDataStore
from database.firebase_client import get_firebase_client
from core.cache.cache_manager import CacheManager


class DependencyContainer:
    """Centralized dependency injection container."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._implementations: Dict[Type, Type] = {}
        self._singletons: Dict[str, Any] = {}
        
    def register_service(self, interface: Type, implementation: Type) -> None:
        """Register a service implementation for an interface."""
        self._implementations[interface] = implementation
        
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance."""
        self._singletons[name] = instance
        
    def get_service(self, interface: Type, **kwargs) -> Any:
        """Get a service instance, creating it if necessary."""
        if interface in self._implementations:
            implementation = self._implementations[interface]
            # Check if implementation is a factory function (callable but not a class)
            if callable(implementation) and not isinstance(implementation, type):
                return implementation()
            else:
                return implementation(**kwargs)
        raise ValueError(f"No implementation registered for {interface}")
    
    def get_singleton(self, name: str) -> Any:
        """Get a singleton instance."""
        if name in self._singletons:
            return self._singletons[name]
        raise ValueError(f"No singleton registered with name '{name}'")
    
    def reset(self) -> None:
        """Reset all services and singletons."""
        self._services.clear()
        self._singletons.clear()


# Global dependency container instance
_container = DependencyContainer()


def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    return _container


def get_service(interface: Type, **kwargs) -> Any:
    """Get a service instance from the global container."""
    return _container.get_service(interface, **kwargs)


def get_singleton(name: str) -> Any:
    """Get a singleton instance from the global container."""
    return _container.get_singleton(name)


def register_default_services() -> None:
    """Register default service implementations."""
    container = get_container()
    
    # Import implementations locally to avoid circular imports
    from services.player_service import PlayerService
    from services.team_service import TeamService
    from services.payment_service import PaymentService
    from services.fa_registration_checker import FARegistrationChecker
    from services.daily_status_service import DailyStatusService
    from services.expense_service import ExpenseService
    from services.health_check_service import HealthCheckService
    from services.match_service import MatchService
    from services.mocks.mock_payment_gateway import MockPaymentGateway
    from services.reminder_service import ReminderService
    from services.team_member_service import TeamMemberService
    from services.mocks.mock_external_player_service import MockExternalPlayerService
    from services.budget_service import BudgetService
    from services.bot_status_service import BotStatusService
    from services.monitoring import MonitoringService
    from services.background_tasks import BackgroundTaskManager
    from services.error_handling_service import ErrorHandlingService
    from services.financial_report_service import FinancialReportService
    from services.user_management_factory import create_user_management
    from services.player_lookup_service import PlayerLookupService
    from services.multi_team_manager import MultiTeamManager
    from services.team_mapping_service import TeamMappingService
    from services.message_routing_service import MessageRoutingService
    from services.access_control_service import AccessControlService
    
    # Create factory functions for services that need dependencies injected
    def create_team_service():
        data_store = container.get_singleton("data_store")
        budget_service = container.get_service(IBudgetService)
        return TeamService(data_store=data_store, budget_service=budget_service)
    
    def create_player_service():
        data_store = container.get_singleton("data_store")
        return PlayerService(data_store=data_store)
    
    def create_payment_service():
        data_store = container.get_singleton("data_store")
        return PaymentService(data_store=data_store)
    
    def create_expense_service():
        data_store = container.get_singleton("data_store")
        budget_service = container.get_service(IBudgetService)
        return ExpenseService(data_store=data_store, budget_service=budget_service)

    def create_budget_service():
        data_store = container.get_singleton("data_store")
        return BudgetService(data_store=data_store)
    
    def create_health_check_service():
        data_store = container.get_singleton("data_store")
        player_operations = container.get_service(IPlayerOperations)
        team_operations = container.get_service(ITeamOperations)
        payment_operations = container.get_service(IPaymentOperations)
        reminder_service = container.get_service(IReminderService)
        daily_status_service = container.get_service(IDailyStatusService)
        fa_registration_checker = container.get_service(IFARegistrationChecker)
        return HealthCheckService(
            team_id="default", 
            data_store=data_store,
            player_operations=player_operations,
            team_operations=team_operations,
            payment_operations=payment_operations,
            reminder_service=reminder_service,
            daily_status_service=daily_status_service,
            fa_registration_checker=fa_registration_checker
        )
    
    def create_match_service():
        data_store = container.get_singleton("data_store")
        return MatchService(data_store=data_store)
    
    def create_team_member_service():
        data_store = container.get_singleton("data_store")
        player_operations = container.get_service(IPlayerOperations)
        team_operations = container.get_service(ITeamOperations)
        return TeamMemberService(data_store=data_store, player_operations=player_operations, team_operations=team_operations)
    
    def create_reminder_service():
        data_store = container.get_singleton("data_store")
        player_operations = container.get_service(IPlayerOperations)
        payment_operations = container.get_service(IPaymentOperations)
        return ReminderService(team_id="default", player_operations=player_operations, payment_operations=payment_operations)
    
    def create_daily_status_service():
        data_store = container.get_singleton("data_store")
        return DailyStatusService(data_store=data_store)
    
    def create_fa_registration_checker():
        data_store = container.get_singleton("data_store")
        player_service = container.get_service(IPlayerService)
        team_service = container.get_service(ITeamService)
        return FARegistrationChecker(
            player_service=player_service,
            team_service=team_service,
            data_store=data_store,
            team_id="default"
        )
    
    def create_bot_status_service():
        return BotStatusService()
    
    def create_monitoring_service():
        data_store = container.get_singleton("data_store")
        bot_status_service = container.get_service(IBotStatusService)
        return MonitoringService(data_store=data_store, bot_status_service=bot_status_service)
    
    def create_background_tasks_service():
        data_store = container.get_singleton("data_store")
        player_service = container.get_service(IPlayerService)
        team_service = container.get_service(ITeamService)
        team_member_service = container.get_service(ITeamMemberService)
        reminder_service = container.get_service(IReminderService)
        daily_status_service = container.get_service(IDailyStatusService)
        fa_registration_checker = container.get_service(IFARegistrationChecker)
        return BackgroundTaskManager(
            data_store=data_store,
            player_service=player_service,
            team_service=team_service,
            team_member_service=team_member_service,
            reminder_service=reminder_service,
            daily_status_service=daily_status_service,
            fa_registration_checker=fa_registration_checker
        )
    
    def create_error_handling_service():
        # For now, pass None for telegram_service - can be extended later
        return ErrorHandlingService(team_id="default", telegram_service=None)
    
    def create_financial_report_service():
        payment_service = container.get_service(IPaymentService)
        expense_service = container.get_service(IExpenseService)
        team_service = container.get_service(ITeamService)
        return FinancialReportService(
            team_id="default",
            bot_token="default",
            payment_service=payment_service,
            expense_service=expense_service,
            team_service=team_service
        )
    
    def create_user_management():
        team_member_service = container.get_service(ITeamMemberService)
        access_control_service = container.get_service(IAccessControlService)
        return create_user_management(team_member_service, access_control_service)
    
    def create_player_lookup_service():
        data_store = container.get_singleton("data_store")
        return PlayerLookupService(data_store=data_store)
    
    def create_multi_team_manager():
        data_store = container.get_singleton("data_store")
        return MultiTeamManager(data_store=data_store)
    
    def create_team_mapping_service():
        data_store = container.get_singleton("data_store")
        cache_manager = container.get_singleton("cache_manager")
        return TeamMappingService(data_store=data_store, cache_manager=cache_manager)
    
    def create_message_routing_service():
        return MessageRoutingService()
    
    def create_access_control_service():
        return AccessControlService()

    # Register service implementations
    container.register_service(IPlayerService, create_player_service)
    container.register_service(ITeamService, create_team_service)
    container.register_service(IPaymentService, create_payment_service)
    container.register_service(IFARegistrationChecker, create_fa_registration_checker)
    container.register_service(IDailyStatusService, create_daily_status_service)
    container.register_service(IExpenseService, create_expense_service)
    container.register_service(IHealthCheckService, create_health_check_service)
    container.register_service(IMatchService, create_match_service)
    container.register_service(IPaymentGateway, MockPaymentGateway)
    container.register_service(IReminderService, create_reminder_service)
    container.register_service(ITeamMemberService, create_team_member_service)
    container.register_service(IExternalPlayerService, MockExternalPlayerService)
    container.register_service(IBudgetService, create_budget_service)
    container.register_service(IBotStatusService, create_bot_status_service)
    container.register_service(IMonitoringService, create_monitoring_service)
    container.register_service(IBackgroundTasksService, create_background_tasks_service)
    container.register_service(IErrorHandlingService, create_error_handling_service)
    container.register_service(IFinancialReportService, create_financial_report_service)
    container.register_service(IUserManagement, create_user_management)
    container.register_service(IAccessControlService, create_access_control_service)


def initialize_container(data_store: Optional[DataStoreInterface] = None) -> None:
    """Initialize the dependency container with default services."""
    container = get_container()
    
    # Register default services
    register_default_services()
    
    # Register data store singleton
    if data_store is None:
        try:
            data_store = get_firebase_client()
        except Exception as e:
            logging.warning(f"Failed to initialize Firebase client, using mock data store: {e}")
            # Fallback to mock data store for testing
            data_store = MockDataStore()
    
    container.register_singleton("data_store", data_store)
    
    # Register cache manager singleton
    cache_manager = CacheManager()
    container.register_singleton("cache_manager", cache_manager)


def ensure_container_initialized() -> None:
    """Ensure the container is initialized with Firebase client."""
    container = get_container()
    
    # Check if data_store is already registered
    try:
        container.get_singleton("data_store")
        return  # Already initialized
    except KeyError:
        pass
    
    # Initialize with Firebase client
    try:
        data_store = get_firebase_client()
        container.register_singleton("data_store", data_store)
        logging.info("✅ Firebase data store registered in dependency container")
    except Exception as e:
        logging.warning(f"Failed to initialize Firebase client, using mock data store: {e}")
        data_store = MockDataStore()
        container.register_singleton("data_store", data_store)
        logging.info("✅ Mock data store registered in dependency container")


# Initialize container on module import (will use mock data store initially)
initialize_container() 