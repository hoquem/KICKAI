"""
Factory pattern for creating feature services with proper dependency injection.

This module provides factories for creating all feature services, ensuring
proper dependency management and avoiding circular imports.
"""

from typing import Dict, Any, Type, Optional, TYPE_CHECKING
from database.interfaces import DataStoreInterface
from utils.id_generator import PlayerIDGenerator

if TYPE_CHECKING:
    from core.dependency_container import DependencyContainer


class ServiceFactory:
    """Factory for creating feature services with proper dependency injection."""
    
    def __init__(self, container, database):
        self.container = container
        self.database = database
        self._cache: Dict[str, Any] = {}
    
    def get_database(self) -> DataStoreInterface:
        """Get the database interface."""
        return self.database
    
    def create_base_services(self):
        """Create base services that don't depend on other services."""
        # Create repositories first
        print("🔍 Creating base services...")
        from features.team_administration.infrastructure.firebase_team_repository import FirebaseTeamRepository
        print("🔍 Imported FirebaseTeamRepository")
        from features.player_registration.infrastructure.firebase_player_repository import FirebasePlayerRepository
        print("🔍 Imported FirebasePlayerRepository")
        from features.payment_management.infrastructure.firebase_expense_repository import FirebaseExpenseRepository
        print("🔍 Imported FirebaseExpenseRepository")
        
        print("🔍 Creating team repository...")
        team_repo = FirebaseTeamRepository(self.database)
        print("🔍 Creating player repository...")
        player_repo = FirebasePlayerRepository(self.database)
        print("🔍 Creating expense repository...")
        expense_repo = FirebaseExpenseRepository(self.database)
        
        # Register repositories
        from features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
        from features.player_registration.domain.repositories.player_repository_interface import PlayerRepositoryInterface
        from features.payment_management.domain.repositories.expense_repository_interface import ExpenseRepositoryInterface
        
        self.container.register_service(TeamRepositoryInterface, team_repo)
        self.container.register_service(PlayerRepositoryInterface, player_repo)
        self.container.register_service(ExpenseRepositoryInterface, expense_repo)
        
        return {
            'team_repository': team_repo,
            'player_repository': player_repo,
            'expense_repository': expense_repo
        }
    
    def create_payment_services(self):
        """Create payment services that depend on repositories."""
        print("🔍 Creating payment services...")
        from features.payment_management.domain.services.expense_service import ExpenseService
        print("🔍 Imported ExpenseService")
        from features.payment_management.domain.repositories.expense_repository_interface import ExpenseRepositoryInterface
        print("🔍 Imported ExpenseRepositoryInterface")
        
        expense_repo = self.container.get_service(ExpenseRepositoryInterface)
        print("🔍 Got expense repository from container")
        expense_service = ExpenseService(expense_repo)
        print("🔍 Created ExpenseService")
        
        self.container.register_service(ExpenseService, expense_service)
        
        return {
            'expense_service': expense_service
        }
    
    def create_team_services(self):
        """Create team services that depend on repositories and payment services."""
        print("🔍 Creating team services...")
        from features.team_administration.domain.services.team_service import TeamService
        print("🔍 Imported TeamService")
        from features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
        print("🔍 Imported TeamRepositoryInterface")
        from features.team_administration.domain.interfaces.team_service_interface import ITeamService
        print("🔍 Imported ITeamService")
        from features.payment_management.domain.services.expense_service import ExpenseService
        print("🔍 Imported ExpenseService")
        
        team_repo = self.container.get_service(TeamRepositoryInterface)
        print("🔍 Got team repository from container")
        expense_service = self.container.get_service(ExpenseService)
        print("🔍 Got expense service from container")
        
        team_service = TeamService(team_repo, expense_service)
        print("🔍 Created TeamService")
        
        # Register both the concrete class and the interface
        self.container.register_service(TeamService, team_service)
        self.container.register_service(ITeamService, team_service)
        
        return {
            'team_service': team_service
        }
    
    def create_player_registration_services(self):
        """Create player registration services that depend on team services."""
        print("🔍 Creating player registration services...")
        from features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
        print("🔍 Imported PlayerRegistrationService")
        from features.player_registration.domain.services.player_id_service import PlayerIDService
        print("🔍 Imported PlayerIDService")
        from features.player_registration.domain.services.player_service import PlayerService
        print("🔍 Imported PlayerService")
        # TeamMemberService removed - using mock service instead
        from features.player_registration.domain.interfaces.player_service_interface import IPlayerService
        print("🔍 Imported IPlayerService")
        from features.player_registration.domain.repositories.player_repository_interface import PlayerRepositoryInterface
        print("🔍 Imported PlayerRepositoryInterface")
        from features.team_administration.domain.services.team_service import TeamService
        print("🔍 Imported TeamService")
        
        player_repo = self.container.get_service(PlayerRepositoryInterface)
        print("🔍 Got player repository from container")
        team_service = self.container.get_service(TeamService)
        print("🔍 Got team service from container")
        
        player_id_generator = PlayerIDGenerator()
        print("🔍 Created PlayerIDGenerator")
        player_id_service = PlayerIDService(player_id_generator)
        print("🔍 Created PlayerIDService")
        registration_service = PlayerRegistrationService(player_repo)
        print("🔍 Created PlayerRegistrationService")
        player_service = PlayerService(player_repo, team_service)
        print("🔍 Created PlayerService")
        
        # Create a mock team member repository for now since we don't have a real one
        class MockTeamMemberRepository:
            async def create(self, team_member):
                return team_member
            async def get_by_team(self, team_id):
                return []
            async def get_by_player(self, player_id, team_id):
                return None
            async def update(self, team_member):
                return team_member
            async def delete_by_player(self, player_id, team_id):
                return True
        
        team_member_repo = MockTeamMemberRepository()
        # TeamMemberService removed - using mock service instead
        
        self.container.register_service(PlayerRegistrationService, registration_service)
        self.container.register_service(PlayerIDService, player_id_service)
        self.container.register_service(PlayerService, player_service)
        self.container.register_service(IPlayerService, player_service)
        # TeamMemberService removed - using mock service instead
        
        return {
            'registration_service': registration_service,
            'player_id_service': player_id_service,
            'player_service': player_service,
            # 'team_member_service': team_member_service  # Removed - using mock service instead
        }
    
    def create_team_administration_services(self):
        """Create team administration services."""
        print("🔍 Creating team administration services...")
        from features.team_administration.domain.services.team_administration_service import TeamAdministrationService
        print("🔍 Imported TeamAdministrationService")
        from features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
        print("🔍 Imported TeamRepositoryInterface")
        team_repo = self.container.get_service(TeamRepositoryInterface)
        print("🔍 Got team repository from container")
        admin_service = TeamAdministrationService(team_repo)
        print("🔍 Created TeamAdministrationService")
        self.container.register_service(TeamAdministrationService, admin_service)
        return {
            'admin_service': admin_service
        }
    
    def create_match_management_services(self):
        """Create match management services."""
        from features.match_management.domain.repositories.match_repository_interface import MatchRepositoryInterface
        from features.match_management.infrastructure.firebase_match_repository import FirebaseMatchRepository
        from features.match_management.domain.services.match_management_service import MatchManagementService
        
        # Create repositories
        match_repo = FirebaseMatchRepository(self.database)
        
        # Create services
        match_service = MatchManagementService(match_repo)
        
        # Register with container
        self.container.register_service(MatchRepositoryInterface, match_repo)
        self.container.register_service(MatchManagementService, match_service)
        
        return {
            'match_repository': match_repo,
            'match_service': match_service
        }
    
    def create_attendance_management_services(self):
        """Create attendance management services."""
        from features.attendance_management.domain.repositories.attendance_repository_interface import AttendanceRepositoryInterface
        from features.attendance_management.infrastructure.firestore_attendance_repository import FirestoreAttendanceRepository
        from features.attendance_management.domain.services.attendance_service import AttendanceService
        
        # Create repositories
        attendance_repo = FirestoreAttendanceRepository(self.database)
        
        # Create services
        attendance_service = AttendanceService(attendance_repo)
        
        # Register with container
        self.container.register_service(AttendanceRepositoryInterface, attendance_repo)
        self.container.register_service(AttendanceService, attendance_service)
        
        return {
            'attendance_repository': attendance_repo,
            'attendance_service': attendance_service
        }
    
    def create_payment_management_services(self):
        """Create payment management services."""
        from features.payment_management.domain.repositories.payment_repository_interface import PaymentRepositoryInterface
        from features.payment_management.domain.repositories.budget_repository_interface import BudgetRepositoryInterface
        from features.payment_management.infrastructure.firebase_payment_repository import FirebasePaymentRepository
        from features.payment_management.infrastructure.firebase_budget_repository import FirebaseBudgetRepository
        from features.payment_management.domain.services.payment_service import PaymentService
        from features.payment_management.domain.services.budget_service import BudgetService
        
        # Create repositories
        payment_repo = FirebasePaymentRepository(self.database)
        budget_repo = FirebaseBudgetRepository(self.database)
        
        # Create services
        payment_service = PaymentService(payment_repo)
        budget_service = BudgetService(budget_repo)
        
        # Register with container
        self.container.register_service(PaymentRepositoryInterface, payment_repo)
        self.container.register_service(BudgetRepositoryInterface, budget_repo)
        self.container.register_service(PaymentService, payment_service)
        self.container.register_service(BudgetService, budget_service)
        
        return {
            'payment_repository': payment_repo,
            'budget_repository': budget_repo,
            'payment_service': payment_service,
            'budget_service': budget_service
        }
    
    def create_communication_services(self):
        """Create communication services."""
        from features.communication.domain.services.message_service import MessageService
        from features.communication.domain.services.notification_service import NotificationService
        from features.communication.infrastructure.firebase_message_repository import FirebaseMessageRepository
        from features.communication.infrastructure.firebase_notification_repository import FirebaseNotificationRepository
        
        # Create services
        message_repository = FirebaseMessageRepository(self.database)
        message_service = MessageService(message_repository)
        notification_repository = FirebaseNotificationRepository(self.database)
        notification_service = NotificationService(notification_repository)
        
        # Register with container
        self.container.register_service(MessageService, message_service)
        self.container.register_service(NotificationService, notification_service)
        
        return {
            'message_service': message_service,
            'notification_service': notification_service
        }
    
    def create_health_monitoring_services(self):
        """Create health monitoring services."""
        from features.health_monitoring.domain.repositories.health_check_repository_interface import HealthCheckRepositoryInterface
        from features.health_monitoring.infrastructure.firebase_health_check_repository import FirebaseHealthCheckRepository
        from features.health_monitoring.domain.services.health_monitoring_service import HealthMonitoringService
        
        # Create repositories
        health_repo = FirebaseHealthCheckRepository(self.database)
        
        # Create services
        health_service = HealthMonitoringService(health_repo)
        
        # Register with container
        self.container.register_service(HealthCheckRepositoryInterface, health_repo)
        self.container.register_service(HealthMonitoringService, health_service)
        
        return {
            'health_repository': health_repo,
            'health_service': health_service
        }
    
    def create_system_infrastructure_services(self):
        """Create system infrastructure services."""
        from features.system_infrastructure.domain.services.configuration_service import ConfigurationService
        from features.system_infrastructure.domain.services.logging_service import LoggingService
        from features.system_infrastructure.domain.services.permission_service import PermissionService
        from database.firebase_client import FirebaseClient
        
        # Create services
        config_service = ConfigurationService()
        logging_service = LoggingService()
        
        # Create permission service with database
        firebase_client = FirebaseClient() if hasattr(self.database, '_firebase_client') else self.database
        permission_service = PermissionService(firebase_client)
        
        # Register with container
        self.container.register_service(ConfigurationService, config_service)
        self.container.register_service(LoggingService, logging_service)
        self.container.register_service(PermissionService, permission_service)
        
        return {
            'config_service': config_service,
            'logging_service': logging_service,
            'permission_service': permission_service
        }
    
    def create_all_services(self) -> Dict[str, Any]:
        """Create all feature services in the correct dependency order."""
        services = {}
        
        # Create services in dependency order
        services.update(self.create_base_services())
        services.update(self.create_payment_services())
        services.update(self.create_team_services())
        services.update(self.create_player_registration_services())
        services.update(self.create_team_administration_services())
        services.update(self.create_match_management_services())
        services.update(self.create_attendance_management_services())
        services.update(self.create_payment_management_services())
        services.update(self.create_communication_services())
        services.update(self.create_health_monitoring_services())
        services.update(self.create_system_infrastructure_services())
        
        return services


def create_service_factory(container, database):
    """Factory function to create a ServiceFactory instance."""
    return ServiceFactory(container, database) 