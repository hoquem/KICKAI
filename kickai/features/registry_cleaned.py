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

    def _should_use_mock_telegram_service(self) -> bool:
        """Determine if MockTelegramBotService should be used based on environment and context."""
        import os
        import sys

        # Check for explicit environment override first
        explicit_setting = os.getenv("USE_MOCK_TELEGRAM")
        if explicit_setting is not None:
            return explicit_setting.lower() == "true"

        # Auto-detect based on environment context
        environment = os.getenv("ENVIRONMENT", "development").lower()
        ai_provider = os.getenv("AI_PROVIDER", "groq").lower()

        # Use mock service in development environments
        if environment in ["development", "local", "testing"]:
            logger.debug(
                f"🔍 Auto-detection: environment={environment}, using MockTelegramBotService"
            )
            return True

        # Use mock service when using local AI providers (indicates local development)
        if ai_provider in ["groq", "ollama", "local"]:
            logger.debug(
                f"🔍 Auto-detection: ai_provider={ai_provider}, using MockTelegramBotService"
            )
            return True

        # Use mock service if local bot mode is explicitly enabled
        if os.getenv("KICKAI_LOCAL_MODE", "false").lower() == "true":
            logger.debug("🔍 Auto-detection: KICKAI_LOCAL_MODE=true, using MockTelegramBotService")
            return True

        # Use mock service if running tests
        if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in sys.modules:
            logger.debug("🔍 Auto-detection: pytest environment, using MockTelegramBotService")
            return True

        logger.debug(
            "🔍 Auto-detection: production environment detected, using real TelegramBotService"
        )
        return False

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
        from kickai.features.team_administration.infrastructure.firebase_team_member_repository import (
            FirebaseTeamMemberRepository,
        )

        logger.debug("🔍 Imported FirebaseTeamMemberRepository")

        logger.debug("🔍 Creating team repository...")
        team_repo = FirebaseTeamRepository(self.database)
        logger.debug("🔍 Creating player repository...")
        player_repo = FirebasePlayerRepository(self.database)
        logger.debug("🔍 Creating team member repository...")
        team_member_repo = FirebaseTeamMemberRepository(self.database)

        # Register repositories
        from kickai.features.player_registration.domain.repositories.player_repository_interface import (
            PlayerRepositoryInterface,
        )
        from kickai.features.shared.domain.interfaces.help_service_interface import IHelpService

        # Register shared services
        from kickai.features.shared.domain.services.help_service import HelpService
        from kickai.features.team_administration.domain.repositories.team_member_repository_interface import (
            TeamMemberRepositoryInterface,
        )
        from kickai.features.team_administration.domain.repositories.team_repository_interface import (
            TeamRepositoryInterface,
        )

        help_service = HelpService()
        self.container.register_service(HelpService, help_service)
        self.container.register_service(IHelpService, help_service)

        self.container.register_service(TeamRepositoryInterface, team_repo)
        self.container.register_service(PlayerRepositoryInterface, player_repo)
        self.container.register_service(TeamMemberRepositoryInterface, team_member_repo)

        return {
            "team_repository": team_repo,
            "player_repository": player_repo,
            "team_member_repository": team_member_repo,
        }

    def create_team_services(self):
        """Create team services that depend on repositories."""
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

        team_repo = self.container.get_service(TeamRepositoryInterface)
        logger.debug("🔍 Got team repository from container")

        team_service = TeamService(team_repo)
        logger.debug("🔍 Created TeamService")

        # Create team member services
        from kickai.features.team_administration.domain.repositories.team_member_repository_interface import (
            TeamMemberRepositoryInterface,
        )
        from kickai.features.team_administration.domain.services.team_member_service import (
            TeamMemberService,
        )

        team_member_repo = self.container.get_service(TeamMemberRepositoryInterface)
        logger.debug("🔍 Got team member repository from container")

        # Create team member services with proper dependency injection
        team_member_service = TeamMemberService(team_member_repo)
        logger.debug("🔍 Created TeamMemberService")

        # Register all services
        self.container.register_service(TeamService, team_service)
        self.container.register_service(ITeamService, team_service)
        self.container.register_service(TeamMemberService, team_member_service)

        return {
            "team_service": team_service,
            "team_member_service": team_member_service,
        }

    def create_player_registration_services(self):
        """Create player registration services that depend on team services."""
        logger.info("🔍 Creating player registration services...")
        from kickai.features.player_registration.domain.services.player_registration_service import (
            PlayerRegistrationService,
        )

        logger.debug("🔍 Imported PlayerRegistrationService")
        from kickai.features.player_registration.domain.services.player_service import PlayerService

        logger.debug("🔍 Imported PlayerService")
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
            from kickai.features.team_administration.domain.interfaces.team_service_interface import (
                ITeamService,
            )

            team_service = self.container.get_service(ITeamService)
            logger.debug("🔍 Got team service from container by interface")
        except (RuntimeError, KeyError, AttributeError) as e:
            logger.warning(f"⚠️ Could not get TeamService by interface: {e}")
            team_service = self.container.get_service(TeamService)
            logger.debug("🔍 Got team service from container by concrete class")

        registration_service = PlayerRegistrationService(player_repo)
        logger.debug("🔍 Created PlayerRegistrationService")
        player_service = PlayerService(player_repo, team_service)
        logger.debug("🔍 Created PlayerService")

        # Get TeamMemberService from container
        from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
            ITeamMemberService,
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
        self.container.register_service(ITeamMemberService, team_member_service)

        return {
            "player_service": player_service,
            "team_member_service": team_member_service,
            "registration_service": registration_service,
        }

    def create_team_administration_services(self):
        """Create team administration services."""
        logger.info("🔍 Creating team administration services...")
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

        # Create MultiBotManager with database and team service
        team_service = self.container.get_service(ITeamService)
        multi_bot_manager = MultiBotManager(self.database, team_service)
        logger.debug("🔍 Created MultiBotManager")

        # Register services
        self.container.register_service(MultiBotManager, multi_bot_manager)

        return {"multi_bot_manager": multi_bot_manager}

    def create_match_management_services(self):
        """Create match management services."""
        from kickai.features.match_management.domain.interfaces.attendance_service_interface import (
            IAttendanceService,
        )
        from kickai.features.match_management.domain.interfaces.availability_service_interface import (
            IAvailabilityService,
        )
        from kickai.features.match_management.domain.interfaces.match_service_interface import (
            IMatchService,
        )
        from kickai.features.match_management.domain.repositories.attendance_repository_interface import (
            AttendanceRepositoryInterface,
        )
        from kickai.features.match_management.domain.repositories.availability_repository_interface import (
            AvailabilityRepositoryInterface,
        )
        from kickai.features.match_management.domain.repositories.match_repository_interface import (
            MatchRepositoryInterface,
        )
        from kickai.features.match_management.domain.services.attendance_service import (
            AttendanceService,
        )
        from kickai.features.match_management.domain.services.availability_service import (
            AvailabilityService,
        )
        from kickai.features.match_management.domain.services.match_service import (
            MatchService,
        )
        from kickai.features.match_management.infrastructure.firebase_attendance_repository import (
            FirebaseAttendanceRepository,
        )
        from kickai.features.match_management.infrastructure.firebase_availability_repository import (
            FirebaseAvailabilityRepository,
        )
        from kickai.features.match_management.infrastructure.firebase_match_repository import (
            FirebaseMatchRepository,
        )

        # Create repositories
        match_repo = FirebaseMatchRepository(self.database)
        availability_repo = FirebaseAvailabilityRepository(self.database)
        attendance_repo = FirebaseAttendanceRepository(self.database)

        # Create services
        match_service = MatchService(match_repo)
        availability_service = AvailabilityService(availability_repo)
        attendance_service = AttendanceService(attendance_repo)

        # Register with container
        self.container.register_service(MatchRepositoryInterface, match_repo)
        self.container.register_service(AvailabilityRepositoryInterface, availability_repo)
        self.container.register_service(AttendanceRepositoryInterface, attendance_repo)
        self.container.register_service(MatchService, match_service)
        self.container.register_service(IMatchService, match_service)
        self.container.register_service(AvailabilityService, availability_service)
        self.container.register_service(IAvailabilityService, availability_service)
        self.container.register_service(AttendanceService, attendance_service)
        self.container.register_service(IAttendanceService, attendance_service)

        return {
            "match_repository": match_repo,
            "availability_repository": availability_repo,
            "attendance_repository": attendance_repo,
            "match_service": match_service,
            "availability_service": availability_service,
            "attendance_service": attendance_service,
        }

    def create_communication_services(self):
        """Create communication services with environment-based TelegramBotService selection."""
        from kickai.features.communication.domain.interfaces.communication_service_interface import (
            ICommunicationService,
        )
        from kickai.features.communication.domain.interfaces.telegram_bot_service_interface import (
            TelegramBotServiceInterface,
        )
        from kickai.features.communication.domain.services.communication_service import (
            CommunicationService,
        )

        # Enhanced environment-based TelegramBotService selection with auto-detection
        use_mock_telegram = self._should_use_mock_telegram_service()
        telegram_bot_service = None

        if use_mock_telegram:
            logger.info("🤖 Using MockTelegramBotService (auto-detected or explicitly enabled)")
            from kickai.features.communication.infrastructure.mock_telegram_bot_service import (
                MockTelegramBotService,
            )

            # Create mock service with auto-detection and enhanced UI integration
            telegram_bot_service = MockTelegramBotService(
                token="mock-token-for-development",
                team_id="KTI",  # Default team for testing
                main_chat_id="2001",  # Mock UI main chat
                leadership_chat_id="2002",  # Mock UI leadership chat
            )
            logger.info("🔗 MockTelegramBotService will auto-detect Mock UI availability")
        else:
            logger.info(
                "📱 Real TelegramBotService will be created when bot configuration is available"
            )
            # Real TelegramBotService will be created later when bot token is available from Firestore
            telegram_bot_service = None

        # Create communication service with TelegramBotService (if available)
        communication_service = CommunicationService(telegram_bot_service)

        # Register services and interfaces with container
        self.container.register_service(CommunicationService, communication_service)
        self.container.register_service(ICommunicationService, communication_service)

        # Register TelegramBotService interface if mock is available
        if telegram_bot_service:
            self.container.register_service(TelegramBotServiceInterface, telegram_bot_service)
            logger.info("✅ MockTelegramBotService registered in container")

        return {
            "communication_service": communication_service,
            "telegram_bot_service": telegram_bot_service,
        }

    def create_system_infrastructure_services(self):
        """Create system infrastructure services."""
        from kickai.features.system_infrastructure.domain.interfaces.permission_service_interface import (
            IPermissionService,
        )
        from kickai.features.system_infrastructure.domain.services.permission_service import (
            PermissionService,
        )

        # Create services
        permission_service = PermissionService(self.database)

        # Register services and interfaces with container
        self.container.register_service(PermissionService, permission_service)
        self.container.register_service(IPermissionService, permission_service)

        return {
            "permission_service": permission_service,
        }

    def create_all_services(self) -> dict[str, Any]:
        """Create all feature services in the correct dependency order."""
        services = {}

        logger.info("🚀 Starting service creation in dependency order...")

        # Create services in dependency order
        logger.info("📦 Creating base services...")
        services.update(self.create_base_services())

        logger.info("🏆 Creating team services...")
        services.update(self.create_team_services())

        logger.info("👤 Creating player registration services...")
        services.update(self.create_player_registration_services())

        logger.info("⚙️ Creating team administration services...")
        services.update(self.create_team_administration_services())

        logger.info("⚽ Creating match management services...")
        services.update(self.create_match_management_services())

        logger.info("💬 Creating communication services...")
        services.update(self.create_communication_services())

        logger.info("🔧 Creating system infrastructure services...")
        services.update(self.create_system_infrastructure_services())

        logger.info(f"✅ All services created successfully. Total services: {len(services)}")

        # Debug: List all services in container
        logger.debug(
            f"🔍 Final container services: {[cls.__name__ for cls in self.container._services.keys()]}"
        )

        return services


def create_service_factory(container, database):
    """Factory function to create a ServiceFactory instance."""
    return ServiceFactory(container, database)
