"""
Factory pattern for creating feature services with proper dependency injection.

This module provides factories for creating all feature services, ensuring
proper dependency management and avoiding circular imports.
"""

from typing import TYPE_CHECKING, Any

from loguru import logger

from src.database.interfaces import DataStoreInterface

if TYPE_CHECKING:
    pass


class ServiceFactory:
    """Factory for creating feature services with proper dependency injection."""

    def __init__(self, container, database):
        self.container = container
        self.database = database
        self._cache: dict[str, Any] = {}

    def get_database(self) -> DataStoreInterface:
        """Get the database interface."""
        return self.database

    def create_base_services(self):
        """Create base services that don't depend on other services."""
        # Create repositories first
        logger.info("🔍 Creating base services...")
        from src.features.team_administration.infrastructure.firebase_team_repository import (
            FirebaseTeamRepository,
        )
        logger.debug("🔍 Imported FirebaseTeamRepository")
        from src.features.player_registration.infrastructure.firebase_player_repository import (
            FirebasePlayerRepository,
        )
        logger.debug("🔍 Imported FirebasePlayerRepository")
        from src.features.payment_management.infrastructure.firebase_expense_repository import (
            FirebaseExpenseRepository,
        )
        logger.debug("🔍 Imported FirebaseExpenseRepository")

        logger.debug("🔍 Creating team repository...")
        team_repo = FirebaseTeamRepository(self.database)
        logger.debug("🔍 Creating player repository...")
        player_repo = FirebasePlayerRepository(self.database)
        logger.debug("🔍 Creating expense repository...")
        expense_repo = FirebaseExpenseRepository(self.database)

        # Register repositories
        from src.features.payment_management.domain.repositories.expense_repository_interface import (
            ExpenseRepositoryInterface,
        )
        from src.features.player_registration.domain.repositories.player_repository_interface import (
            PlayerRepositoryInterface,
        )
        from src.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )

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
        logger.info("🔍 Creating payment services...")
        from src.features.payment_management.domain.services.expense_service import ExpenseService
        logger.debug("🔍 Imported ExpenseService")
        from src.features.payment_management.domain.repositories.expense_repository_interface import (
            ExpenseRepositoryInterface,
        )
        logger.debug("🔍 Imported ExpenseRepositoryInterface")

        expense_repo = self.container.get_service(ExpenseRepositoryInterface)
        logger.debug("🔍 Got expense repository from container")
        expense_service = ExpenseService(expense_repo)
        logger.debug("🔍 Created ExpenseService")

        self.container.register_service(ExpenseService, expense_service)

        return {
            'expense_service': expense_service
        }

    def create_team_services(self):
        """Create team services that depend on repositories and payment services."""
        logger.info("🔍 Creating team services...")
        from src.features.team_administration.domain.services.team_service import TeamService
        logger.debug("🔍 Imported TeamService")
        from src.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )
        logger.debug("🔍 Imported TeamRepositoryInterface")
        from src.features.team_administration.domain.interfaces.team_service_interface import (
            ITeamService,
        )
        logger.debug("🔍 Imported ITeamService")
        from src.features.payment_management.domain.services.expense_service import ExpenseService
        logger.debug("🔍 Imported ExpenseService")

        team_repo = self.container.get_service(TeamRepositoryInterface)
        logger.debug("🔍 Got team repository from container")
        expense_service = self.container.get_service(ExpenseService)
        logger.debug("🔍 Got expense service from container")

        team_service = TeamService(team_repo, expense_service)
        logger.debug("🔍 Created TeamService")

        # Register both the concrete class and the interface
        self.container.register_service(TeamService, team_service)
        self.container.register_service(ITeamService, team_service)

        return {
            'team_service': team_service
        }

    def create_player_registration_services(self):
        """Create player registration services that depend on team services."""
        logger.info("🔍 Creating player registration services...")
        from src.features.player_registration.domain.services.player_registration_service import (
            PlayerRegistrationService,
        )
        logger.debug("🔍 Imported PlayerRegistrationService")
        from src.features.player_registration.domain.services.player_service import PlayerService
        logger.debug("🔍 Imported PlayerService")
        # TeamMemberService removed - using mock service instead
        from src.features.player_registration.domain.interfaces.player_service_interface import (
            IPlayerService,
        )
        logger.debug("🔍 Imported IPlayerService")
        from src.features.player_registration.domain.repositories.player_repository_interface import (
            PlayerRepositoryInterface,
        )
        logger.debug("🔍 Imported PlayerRepositoryInterface")
        from src.features.team_administration.domain.services.team_service import TeamService
        logger.debug("🔍 Imported TeamService")

        player_repo = self.container.get_service(PlayerRepositoryInterface)
        logger.debug("🔍 Got player repository from container")
        team_service = self.container.get_service(TeamService)
        logger.debug("🔍 Got team service from container")

        registration_service = PlayerRegistrationService(player_repo)
        logger.debug("🔍 Created PlayerRegistrationService")
        player_service = PlayerService(player_repo, team_service)
        logger.debug("🔍 Created PlayerService")

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

        # Create TeamMemberService
        from src.features.team_administration.domain.services.team_member_service import TeamMemberService
        from src.features.team_administration.domain.repositories.team_repository_interface import TeamRepositoryInterface
        logger.debug("🔍 Imported TeamMemberService")
        
        # Get team repository from container
        team_repo = self.container.get_service(TeamRepositoryInterface)
        logger.debug("🔍 Got team repository from container for TeamMemberService")
        
        team_member_service = TeamMemberService(team_repo)
        logger.debug("🔍 Created TeamMemberService")

        logger.debug("🔍 Registering PlayerRegistrationService...")
        self.container.register_service(PlayerRegistrationService, registration_service)
        logger.debug("🔍 Registering PlayerService...")
        self.container.register_service(PlayerService, player_service)
        logger.debug("🔍 Registering IPlayerService...")
        self.container.register_service(IPlayerService, player_service)
        logger.debug("🔍 Registering TeamMemberService...")
        self.container.register_service(TeamMemberService, team_member_service)
        
        # Debug: Log what services are now in the container
        logger.debug(f"🔍 Container services after player registration: {[cls.__name__ for cls in self.container._services.keys()]}")
        logger.debug(f"🔍 Container service count: {len(self.container._services)}")

        return {
            'player_service': player_service,
            'team_member_service': team_member_service,
            'registration_service': registration_service
        }

    def create_team_administration_services(self):
        """Create team administration services."""
        logger.info("🔍 Creating team administration services...")
        from src.features.team_administration.domain.services.team_administration_service import (
            TeamAdministrationService,
        )
        logger.debug("🔍 Imported TeamAdministrationService")
        from src.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )
        logger.debug("🔍 Imported TeamRepositoryInterface")
        team_repo = self.container.get_service(TeamRepositoryInterface)
        logger.debug("🔍 Got team repository from container")
        admin_service = TeamAdministrationService(team_repo)
        logger.debug("🔍 Created TeamAdministrationService")
        self.container.register_service(TeamAdministrationService, admin_service)
        return {
            'admin_service': admin_service
        }

    def create_match_management_services(self):
        """Create match management services."""
        from src.features.match_management.domain.repositories.match_repository_interface import (
            MatchRepositoryInterface,
        )
        from src.features.match_management.domain.services.match_management_service import (
            MatchManagementService,
        )
        from src.features.match_management.infrastructure.firebase_match_repository import (
            FirebaseMatchRepository,
        )

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
        from src.features.attendance_management.domain.repositories.attendance_repository_interface import (
            AttendanceRepositoryInterface,
        )
        from src.features.attendance_management.domain.services.attendance_service import (
            AttendanceService,
        )
        from src.features.attendance_management.infrastructure.firestore_attendance_repository import (
            FirestoreAttendanceRepository,
        )

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
        from src.features.payment_management.domain.repositories.budget_repository_interface import (
            BudgetRepositoryInterface,
        )
        from src.features.payment_management.domain.repositories.payment_repository_interface import (
            PaymentRepositoryInterface,
        )
        from src.features.payment_management.domain.services.budget_service import BudgetService
        from src.features.payment_management.domain.services.payment_service import PaymentService
        from src.features.payment_management.infrastructure.firebase_budget_repository import (
            FirebaseBudgetRepository,
        )
        from src.features.payment_management.infrastructure.firebase_payment_repository import (
            FirebasePaymentRepository,
        )

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
        from src.features.communication.domain.services.invite_link_service import InviteLinkService
        from src.features.communication.domain.services.message_service import MessageService
        from src.features.communication.domain.services.notification_service import NotificationService
        from src.features.communication.infrastructure.firebase_message_repository import (
            FirebaseMessageRepository,
        )
        from src.features.communication.infrastructure.firebase_notification_repository import (
            FirebaseNotificationRepository,
        )

        # Create services
        message_repository = FirebaseMessageRepository(self.database)
        message_service = MessageService(message_repository)
        notification_repository = FirebaseNotificationRepository(self.database)
        notification_service = NotificationService(notification_repository)

        # Create invite link service (bot token will be set later from Firestore)
        invite_link_service = InviteLinkService(self.database)

        # Register with container
        self.container.register_service(MessageService, message_service)
        self.container.register_service(NotificationService, notification_service)
        self.container.register_service(InviteLinkService, invite_link_service)

        return {
            'message_service': message_service,
            'notification_service': notification_service,
            'invite_link_service': invite_link_service
        }

    def create_health_monitoring_services(self):
        """Create health monitoring services."""
        from src.features.health_monitoring.domain.repositories.health_check_repository_interface import (
            HealthCheckRepositoryInterface,
        )
        from src.features.health_monitoring.domain.services.health_monitoring_service import (
            HealthMonitoringService,
        )
        from src.features.health_monitoring.infrastructure.firebase_health_check_repository import (
            FirebaseHealthCheckRepository,
        )

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
        from src.database.firebase_client import FirebaseClient
        from src.features.system_infrastructure.domain.services.configuration_service import (
            ConfigurationService,
        )
        from src.features.system_infrastructure.domain.services.logging_service import LoggingService
        from src.features.system_infrastructure.domain.services.permission_service import (
            PermissionService,
        )

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

    def create_all_services(self) -> dict[str, Any]:
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
