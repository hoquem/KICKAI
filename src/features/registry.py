"""
Factory pattern for creating feature services with proper dependency injection.

This module provides factories for creating all feature services, ensuring
proper dependency management and avoiding circular imports.
"""

from typing import Dict, Any, Type, Optional
from src.core.dependency_container import DependencyContainer
from src.database.interfaces import DataStoreInterface


class ServiceFactory:
    """Factory for creating feature services with proper dependency injection."""
    
    def __init__(self, container: DependencyContainer):
        self.container = container
        self._cache: Dict[str, Any] = {}
    
    def get_database(self) -> DataStoreInterface:
        """Get the database interface."""
        return self.container.get_database()
    
    def create_player_registration_services(self):
        """Create player registration services."""
        from src.features.player_registration.domain.repositories.player_repository_interface import PlayerRepositoryInterface
        from src.features.player_registration.infrastructure.firebase_player_repository import FirebasePlayerRepository
        from src.features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
        from src.features.player_registration.domain.services.player_id_service import PlayerIdService
        
        # Create repositories
        player_repo = FirebasePlayerRepository(self.get_database())
        
        # Create services
        player_id_service = PlayerIdService()
        registration_service = PlayerRegistrationService(player_repo, player_id_service)
        
        # Register with container
        self.container.register_service(PlayerRepositoryInterface, player_repo)
        self.container.register_service(PlayerRegistrationService, registration_service)
        self.container.register_service(PlayerIdService, player_id_service)
        
        return {
            'player_repository': player_repo,
            'registration_service': registration_service,
            'player_id_service': player_id_service
        }
    
    def create_team_administration_services(self):
        """Create team administration services."""
        from src.features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
        from src.features.team_administration.infrastructure.firebase_team_repository import FirebaseTeamRepository
        from src.features.team_administration.domain.services.team_administration_service import TeamAdministrationService
        
        # Create repositories
        team_repo = FirebaseTeamRepository(self.get_database())
        
        # Create services
        admin_service = TeamAdministrationService(team_repo)
        
        # Register with container
        self.container.register_service(TeamRepositoryInterface, team_repo)
        self.container.register_service(TeamAdministrationService, admin_service)
        
        return {
            'team_repository': team_repo,
            'admin_service': admin_service
        }
    
    def create_match_management_services(self):
        """Create match management services."""
        from src.features.match_management.domain.repositories.match_repository_interface import MatchRepositoryInterface
        from src.features.match_management.infrastructure.firebase_match_repository import FirebaseMatchRepository
        from src.features.match_management.domain.services.match_management_service import MatchManagementService
        
        # Create repositories
        match_repo = FirebaseMatchRepository(self.get_database())
        
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
        from src.features.attendance_management.domain.repositories.attendance_repository_interface import AttendanceRepositoryInterface
        from src.features.attendance_management.infrastructure.firestore_attendance_repository import FirestoreAttendanceRepository
        from src.features.attendance_management.domain.services.attendance_service import AttendanceService
        
        # Create repositories
        attendance_repo = FirestoreAttendanceRepository(self.get_database())
        
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
        from src.features.payment_management.domain.repositories.payment_repository_interface import PaymentRepositoryInterface
        from src.features.payment_management.domain.repositories.budget_repository_interface import BudgetRepositoryInterface
        from src.features.payment_management.infrastructure.firebase_payment_repository import FirebasePaymentRepository
        from src.features.payment_management.infrastructure.firebase_budget_repository import FirebaseBudgetRepository
        from src.features.payment_management.domain.services.payment_service import PaymentService
        from src.features.payment_management.domain.services.budget_service import BudgetService
        
        # Create repositories
        payment_repo = FirebasePaymentRepository(self.get_database())
        budget_repo = FirebaseBudgetRepository(self.get_database())
        
        # Create services
        payment_service = PaymentService(payment_repo, budget_repo)
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
        from src.features.communication.domain.services.message_service import MessageService
        from src.features.communication.domain.services.notification_service import NotificationService
        
        # Create services
        message_service = MessageService()
        notification_service = NotificationService()
        
        # Register with container
        self.container.register_service(MessageService, message_service)
        self.container.register_service(NotificationService, notification_service)
        
        return {
            'message_service': message_service,
            'notification_service': notification_service
        }
    
    def create_health_monitoring_services(self):
        """Create health monitoring services."""
        from src.features.health_monitoring.domain.repositories.health_check_repository_interface import HealthCheckRepositoryInterface
        from src.features.health_monitoring.infrastructure.firebase_health_check_repository import FirebaseHealthCheckRepository
        from src.features.health_monitoring.domain.services.health_monitoring_service import HealthMonitoringService
        
        # Create repositories
        health_repo = FirebaseHealthCheckRepository(self.get_database())
        
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
        from src.features.system_infrastructure.domain.services.configuration_service import ConfigurationService
        from src.features.system_infrastructure.domain.services.logging_service import LoggingService
        
        # Create services
        config_service = ConfigurationService()
        logging_service = LoggingService()
        
        # Register with container
        self.container.register_service(ConfigurationService, config_service)
        self.container.register_service(LoggingService, logging_service)
        
        return {
            'config_service': config_service,
            'logging_service': logging_service
        }
    
    def create_all_services(self) -> Dict[str, Any]:
        """Create all feature services and return them as a dictionary."""
        services = {}
        
        # Create services for each feature
        services.update(self.create_player_registration_services())
        services.update(self.create_team_administration_services())
        services.update(self.create_match_management_services())
        services.update(self.create_attendance_management_services())
        services.update(self.create_payment_management_services())
        services.update(self.create_communication_services())
        services.update(self.create_health_monitoring_services())
        services.update(self.create_system_infrastructure_services())
        
        return services


def create_service_factory(container: DependencyContainer) -> ServiceFactory:
    """Factory function to create a ServiceFactory instance."""
    return ServiceFactory(container) 