"""
Factory pattern for creating feature services with proper dependency injection.

This module provides factories for creating all feature services, ensuring
proper dependency management and avoiding circular imports.
"""

from typing import TYPE_CHECKING, Any

from loguru import logger

from kickai.database.interfaces import DataStoreInterface

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
        from kickai.features.team_administration.infrastructure.firebase_team_repository import (
            FirebaseTeamRepository,
        )

        logger.debug("🔍 Imported FirebaseTeamRepository")
        from kickai.features.player_registration.infrastructure.firebase_player_repository import (
            FirebasePlayerRepository,
        )

        logger.debug("🔍 Imported FirebasePlayerRepository")
        from kickai.features.payment_management.infrastructure.firebase_expense_repository import (
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
        from kickai.features.payment_management.domain.repositories.expense_repository_interface import (
            ExpenseRepositoryInterface,
        )
        from kickai.features.player_registration.domain.repositories.player_repository_interface import (
            PlayerRepositoryInterface,
        )
        from kickai.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )

        self.container.register_service(TeamRepositoryInterface, team_repo)
        self.container.register_service(PlayerRepositoryInterface, player_repo)
        self.container.register_service(ExpenseRepositoryInterface, expense_repo)

        return {
            "team_repository": team_repo,
            "player_repository": player_repo,
            "expense_repository": expense_repo,
        }

    def create_payment_services(self):
        """Create payment services that depend on repositories."""
        logger.info("🔍 Creating payment services...")
        from kickai.features.payment_management.domain.services.expense_service import (
            ExpenseService,
        )

        logger.debug("🔍 Imported ExpenseService")
        from kickai.features.payment_management.domain.repositories.expense_repository_interface import (
            ExpenseRepositoryInterface,
        )

        logger.debug("🔍 Imported ExpenseRepositoryInterface")

        expense_repo = self.container.get_service(ExpenseRepositoryInterface)
        logger.debug("🔍 Got expense repository from container")
        expense_service = ExpenseService(expense_repo)
        logger.debug("🔍 Created ExpenseService")

        self.container.register_service(ExpenseService, expense_service)

        return {"expense_service": expense_service}

    def create_team_services(self):
        """Create team services that depend on repositories and payment services."""
        logger.info("🔍 Creating team services...")
        from kickai.features.team_administration.domain.services.team_service import TeamService

        logger.debug("🔍 Imported TeamService")
        from kickai.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )

        logger.debug("🔍 Imported TeamRepositoryInterface")
        from kickai.features.team_administration.domain.interfaces.team_service_interface import (
            ITeamService,
        )

        logger.debug("🔍 Imported ITeamService")
        from kickai.features.payment_management.domain.services.expense_service import (
            ExpenseService,
        )

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
        
        # Debug: Verify registration
        logger.debug(f"✅ Registered TeamService: {type(team_service)}")
        logger.debug(f"✅ Registered ITeamService: {type(team_service)}")
        
        # Debug: Check if services are available immediately after registration
        try:
            team_service_check = self.container.get_service(TeamService)
            logger.debug(f"✅ TeamService immediately available: {type(team_service_check)}")
        except Exception as e:
            logger.error(f"❌ TeamService not immediately available: {e}")
            
        try:
            team_service_interface_check = self.container.get_service(ITeamService)
            logger.debug(f"✅ ITeamService immediately available: {type(team_service_interface_check)}")
        except Exception as e:
            logger.error(f"❌ ITeamService not immediately available: {e}")

        return {"team_service": team_service}

    def create_player_registration_services(self):
        """Create player registration services that depend on team services."""
        logger.info("🔍 Creating player registration services...")
        from kickai.features.player_registration.domain.services.player_registration_service import (
            PlayerRegistrationService,
        )

        logger.debug("🔍 Imported PlayerRegistrationService")
        from kickai.features.player_registration.domain.services.player_service import PlayerService

        logger.debug("🔍 Imported PlayerService")
        # TeamMemberService removed - using mock service instead
        from kickai.features.player_registration.domain.interfaces.player_service_interface import (
            IPlayerService,
        )

        logger.debug("🔍 Imported IPlayerService")
        from kickai.features.player_registration.domain.repositories.player_repository_interface import (
            PlayerRepositoryInterface,
        )

        logger.debug("🔍 Imported PlayerRepositoryInterface")
        from kickai.features.team_administration.domain.services.team_service import TeamService

        logger.debug("🔍 Imported TeamService")

        player_repo = self.container.get_service(PlayerRepositoryInterface)
        logger.debug("🔍 Got player repository from container")
        
        # Try to get TeamService by interface first, then by concrete class
        try:
            from kickai.features.team_administration.domain.interfaces.team_service_interface import ITeamService
            team_service = self.container.get_service(ITeamService)
            logger.debug("🔍 Got team service from container by interface")
        except Exception as e:
            logger.warning(f"⚠️ Could not get TeamService by interface: {e}")
            team_service = self.container.get_service(TeamService)
            logger.debug("🔍 Got team service from container by concrete class")

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
        from kickai.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )
        from kickai.features.team_administration.domain.services.team_member_service import (
            TeamMemberService,
        )

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
        logger.debug(
            f"🔍 Container services after player registration: {[cls.__name__ for cls in self.container._services.keys()]}"
        )
        logger.debug(f"🔍 Container service count: {len(self.container._services)}")
        
        # Debug: Check if TeamService is available
        try:
            team_service_check = self.container.get_service(TeamService)
            logger.debug(f"✅ TeamService is available in container: {type(team_service_check)}")
        except Exception as e:
            logger.error(f"❌ TeamService not available in container: {e}")
            
        try:
            from kickai.features.team_administration.domain.interfaces.team_service_interface import ITeamService
            team_service_interface_check = self.container.get_service(ITeamService)
            logger.debug(f"✅ ITeamService is available in container: {type(team_service_interface_check)}")
        except Exception as e:
            logger.error(f"❌ ITeamService not available in container: {e}")

        return {
            "player_service": player_service,
            "team_member_service": team_member_service,
            "registration_service": registration_service,
        }

    def create_team_administration_services(self):
        """Create team administration services."""
        logger.info("🔍 Creating team administration services...")
        from kickai.features.team_administration.domain.services.team_administration_service import (
            TeamAdministrationService,
        )

        logger.debug("🔍 Imported TeamAdministrationService")
        from kickai.features.team_administration.domain.services.multi_bot_manager import (
            MultiBotManager,
        )

        logger.debug("🔍 Imported MultiBotManager")
        from kickai.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )

        logger.debug("🔍 Imported TeamRepositoryInterface")
        from kickai.features.team_administration.domain.interfaces.team_service_interface import (
            ITeamService,
        )

        logger.debug("🔍 Imported ITeamService")

        team_repo = self.container.get_service(TeamRepositoryInterface)
        logger.debug("🔍 Got team repository from container")

        admin_service = TeamAdministrationService(team_repo)
        logger.debug("🔍 Created TeamAdministrationService")

        # Create MultiBotManager with database and team service
        team_service = self.container.get_service(ITeamService)
        multi_bot_manager = MultiBotManager(self.database, team_service)
        logger.debug("🔍 Created MultiBotManager")

        # Register services
        self.container.register_service(TeamAdministrationService, admin_service)
        self.container.register_service(MultiBotManager, multi_bot_manager)

        return {"admin_service": admin_service, "multi_bot_manager": multi_bot_manager}

    def create_match_management_services(self):
        """Create match management services."""
        from kickai.features.match_management.domain.repositories.match_repository_interface import (
            MatchRepositoryInterface,
        )
        from kickai.features.match_management.domain.services.match_management_service import (
            MatchManagementService,
        )
        from kickai.features.match_management.infrastructure.firebase_match_repository import (
            FirebaseMatchRepository,
        )

        # Create repositories
        match_repo = FirebaseMatchRepository(self.database)

        # Create services
        match_service = MatchManagementService(match_repo)

        # Register with container
        self.container.register_service(MatchRepositoryInterface, match_repo)
        self.container.register_service(MatchManagementService, match_service)

        return {"match_repository": match_repo, "match_service": match_service}

    def create_attendance_management_services(self):
        """Create attendance management services."""
        from kickai.features.attendance_management.domain.repositories.attendance_repository_interface import (
            AttendanceRepositoryInterface,
        )
        from kickai.features.attendance_management.domain.services.attendance_service import (
            AttendanceService,
        )
        from kickai.features.attendance_management.infrastructure.firestore_attendance_repository import (
            FirestoreAttendanceRepository,
        )

        # Create repositories
        attendance_repo = FirestoreAttendanceRepository(self.database)

        # Create services
        attendance_service = AttendanceService(attendance_repo)

        # Register with container
        self.container.register_service(AttendanceRepositoryInterface, attendance_repo)
        self.container.register_service(AttendanceService, attendance_service)

        return {"attendance_repository": attendance_repo, "attendance_service": attendance_service}

    def create_payment_management_services(self):
        """Create payment management services."""
        from kickai.features.payment_management.domain.repositories.budget_repository_interface import (
            BudgetRepositoryInterface,
        )
        from kickai.features.payment_management.domain.repositories.payment_repository_interface import (
            PaymentRepositoryInterface,
        )
        from kickai.features.payment_management.domain.services.budget_service import BudgetService
        from kickai.features.payment_management.domain.services.payment_service import (
            PaymentService,
        )
        from kickai.features.payment_management.infrastructure.firebase_budget_repository import (
            FirebaseBudgetRepository,
        )
        from kickai.features.payment_management.infrastructure.firebase_payment_repository import (
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
            "payment_repository": payment_repo,
            "budget_repository": budget_repo,
            "payment_service": payment_service,
            "budget_service": budget_service,
        }

    def create_communication_services(self):
        """Create communication services."""
        from kickai.features.communication.domain.services.communication_service import (
            CommunicationService,
        )
        from kickai.features.communication.domain.services.invite_link_service import (
            InviteLinkService,
        )
        from kickai.features.communication.domain.services.message_service import MessageService
        from kickai.features.communication.domain.services.notification_service import (
            NotificationService,
        )
        from kickai.features.communication.infrastructure.firebase_message_repository import (
            FirebaseMessageRepository,
        )
        from kickai.features.communication.infrastructure.firebase_notification_repository import (
            FirebaseNotificationRepository,
        )

        # Create services
        message_repository = FirebaseMessageRepository(self.database)
        message_service = MessageService(message_repository)
        notification_repository = FirebaseNotificationRepository(self.database)
        notification_service = NotificationService(notification_repository)

        # Create invite link service (bot token will be set later from Firestore)
        invite_link_service = InviteLinkService(bot_token=None, database=self.database)

        # Create communication service (TelegramBotService will be injected later)
        communication_service = CommunicationService(
            None
        )  # Will be updated when TelegramBotService is available

        # Register with container
        self.container.register_service(MessageService, message_service)
        self.container.register_service(NotificationService, notification_service)
        self.container.register_service(InviteLinkService, invite_link_service)
        self.container.register_service(CommunicationService, communication_service)

        return {
            "message_service": message_service,
            "notification_service": notification_service,
            "invite_link_service": invite_link_service,
            "communication_service": communication_service,
        }

    def create_health_monitoring_services(self):
        """Create health monitoring services."""
        from kickai.features.health_monitoring.domain.repositories.health_check_repository_interface import (
            HealthCheckRepositoryInterface,
        )
        from kickai.features.health_monitoring.domain.services.health_monitoring_service import (
            HealthMonitoringService,
        )
        from kickai.features.health_monitoring.infrastructure.firebase_health_check_repository import (
            FirebaseHealthCheckRepository,
        )

        # Create repositories
        health_repo = FirebaseHealthCheckRepository(self.database)

        # Create services
        health_service = HealthMonitoringService(health_repo)

        # Register with container
        self.container.register_service(HealthCheckRepositoryInterface, health_repo)
        self.container.register_service(HealthMonitoringService, health_service)

        return {"health_repository": health_repo, "health_service": health_service}

    def create_system_infrastructure_services(self):
        """Create system infrastructure services."""
        from kickai.features.system_infrastructure.domain.services.bot_status_service import (
            BotStatusService,
        )
        from kickai.features.system_infrastructure.domain.services.permission_service import (
            PermissionService,
        )

        # Create services
        bot_status_service = BotStatusService()
        permission_service = PermissionService(self.database)

        # Register with container
        self.container.register_service(BotStatusService, bot_status_service)
        self.container.register_service(PermissionService, permission_service)

        return {
            "bot_status_service": bot_status_service,
            "permission_service": permission_service,
        }

    def create_helper_system_services(self):
        """Create helper system services."""
        from kickai.features.helper_system.domain.interfaces.command_help_service_interface import (
            ICommandHelpService,
        )
        from kickai.features.helper_system.domain.interfaces.event_bus_interface import (
            IEventBus,
        )
        from kickai.features.helper_system.domain.interfaces.feature_suggestion_service_interface import (
            IFeatureSuggestionService,
        )
        from kickai.features.helper_system.domain.interfaces.guidance_service_interface import (
            IGuidanceService,
        )
        from kickai.features.helper_system.domain.interfaces.learning_analytics_service_interface import (
            ILearningAnalyticsService,
        )
        from kickai.features.helper_system.domain.interfaces.reminder_service_interface import (
            IReminderService,
        )
        from kickai.features.helper_system.domain.interfaces.user_analytics_service_interface import (
            IUserAnalyticsService,
        )
        from kickai.features.helper_system.domain.repositories.help_request_repository_interface import (
            HelpRequestRepositoryInterface,
        )
        from kickai.features.helper_system.domain.repositories.learning_profile_repository_interface import (
            LearningProfileRepositoryInterface,
        )
        from kickai.features.helper_system.domain.services.command_help_service import (
            CommandHelpService,
        )
        from kickai.features.helper_system.domain.services.feature_suggestion_service import (
            FeatureSuggestionService,
        )
        from kickai.features.helper_system.domain.services.guidance_service import (
            GuidanceService,
        )
        from kickai.features.helper_system.domain.services.learning_analytics_service import (
            LearningAnalyticsService,
        )
        from kickai.features.helper_system.domain.services.reminder_service import (
            ReminderService,
        )
        from kickai.features.helper_system.domain.services.user_analytics_service import (
            UserAnalyticsService,
        )
        from kickai.features.helper_system.infrastructure.event_bus import (
            EventBus,
        )
        from kickai.features.helper_system.infrastructure.firebase_help_request_repository import (
            FirebaseHelpRequestRepository,
        )
        from kickai.features.helper_system.infrastructure.firebase_learning_profile_repository import (
            FirebaseLearningProfileRepository,
        )

        # Create repositories
        learning_profile_repo = FirebaseLearningProfileRepository(self.database)
        help_request_repo = FirebaseHelpRequestRepository(self.database)

        # Create event bus
        event_bus = EventBus()

        # Create services
        guidance_service = GuidanceService(learning_profile_repo, help_request_repo)
        learning_analytics_service = LearningAnalyticsService(learning_profile_repo)
        reminder_service = ReminderService(learning_profile_repo)

        # Create split services
        command_help_service = CommandHelpService()
        feature_suggestion_service = FeatureSuggestionService(learning_profile_repo)
        user_analytics_service = UserAnalyticsService(learning_profile_repo)

        # Register with container using interfaces
        self.container.register_service(LearningProfileRepositoryInterface, learning_profile_repo)
        self.container.register_service(HelpRequestRepositoryInterface, help_request_repo)
        self.container.register_service(IEventBus, event_bus)
        self.container.register_service(ILearningAnalyticsService, learning_analytics_service)
        self.container.register_service(IGuidanceService, guidance_service)
        self.container.register_service(IReminderService, reminder_service)
        self.container.register_service(ICommandHelpService, command_help_service)
        self.container.register_service(IFeatureSuggestionService, feature_suggestion_service)
        self.container.register_service(IUserAnalyticsService, user_analytics_service)

        return {
            "learning_profile_repository": learning_profile_repo,
            "help_request_repository": help_request_repo,
            "event_bus": event_bus,
            "learning_analytics_service": learning_analytics_service,
            "guidance_service": guidance_service,
            "reminder_service": reminder_service,
            "command_help_service": command_help_service,
            "feature_suggestion_service": feature_suggestion_service,
            "user_analytics_service": user_analytics_service,
        }

    def create_all_services(self) -> dict[str, Any]:
        """Create all feature services in the correct dependency order."""
        services = {}
        
        logger.info("🚀 Starting service creation in dependency order...")

        # Create services in dependency order
        logger.info("📦 Creating base services...")
        services.update(self.create_base_services())
        
        logger.info("💰 Creating payment services...")
        services.update(self.create_payment_services())
        
        logger.info("🏆 Creating team services...")
        services.update(self.create_team_services())
        
        logger.info("👤 Creating player registration services...")
        services.update(self.create_player_registration_services())
        
        logger.info("⚙️ Creating team administration services...")
        services.update(self.create_team_administration_services())
        
        logger.info("⚽ Creating match management services...")
        services.update(self.create_match_management_services())
        
        logger.info("📊 Creating attendance management services...")
        services.update(self.create_attendance_management_services())
        
        logger.info("💳 Creating payment management services...")
        services.update(self.create_payment_management_services())
        
        logger.info("💬 Creating communication services...")
        services.update(self.create_communication_services())
        
        logger.info("🏥 Creating health monitoring services...")
        services.update(self.create_health_monitoring_services())
        
        logger.info("🔧 Creating system infrastructure services...")
        services.update(self.create_system_infrastructure_services())
        
        logger.info("🤝 Creating helper system services...")
        services.update(self.create_helper_system_services())
        
        logger.info(f"✅ All services created successfully. Total services: {len(services)}")
        
        # Debug: List all services in container
        logger.debug(f"🔍 Final container services: {[cls.__name__ for cls in self.container._services.keys()]}")

        return services


def create_service_factory(container, database):
    """Factory function to create a ServiceFactory instance."""
    return ServiceFactory(container, database)
