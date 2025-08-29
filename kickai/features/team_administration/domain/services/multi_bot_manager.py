import logging
from typing import Any, Optional

from loguru import logger

from kickai.agents.crew_lifecycle_manager import (
    get_crew_lifecycle_manager,
    initialize_crew_lifecycle_manager,
    shutdown_crew_lifecycle_manager,
)
from kickai.features.communication.infrastructure import TelegramBotService


class MultiBotManager:
    """
    Manages multiple bot instances for different teams.
    Loads bot configurations, starts/stops bots, and monitors their status.
    """

    def __init__(self, data_store: Any, team_service: Any):
        logger.debug("DEBUG: MultiBotManager._init_ called")
        self.data_store = data_store
        self.team_service = team_service
        self.bots: dict[str, Any] = {}
        self.bot_configs: list[dict[str, Any]] = []
        self.crewai_systems: dict[str, Any] = {}  # Store CrewAI systems for each team
        self.crew_lifecycle_manager = get_crew_lifecycle_manager()
        self._running = False
        self.logger = logging.getLogger(__name__)
        logger.debug("DEBUG: MultiBotManager._init_ completed")

    async def initialize(self) -> None:
        """Initialize the multi-bot manager."""
        try:
            logger.info("🤖 Initializing MultiBotManager...")

            # Initialize the crew lifecycle manager
            await initialize_crew_lifecycle_manager()

            # Load bot configurations
            await self.load_bot_configurations()

            logger.info("✅ MultiBotManager initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize MultiBotManager: {e}")
            raise

    async def load_bot_configurations(self) -> list[Any]:
        """Load bot configurations from the data store (e.g., Firestore)."""
        try:
            self.logger.info("🔍 Loading bot configurations from data store...")
            teams = await self.team_service.get_all_teams()
            self.logger.info(f"📊 Found {len(teams)} teams in database")

            # Debug: Print each team's bot configuration
            for i, team in enumerate(teams):
                self.logger.info(f"Team {i + 1}: {team.name} (ID: {getattr(team, 'id', 'None')})")
                self.logger.info(f"  - bot_token: {getattr(team, 'bot_token', 'None')}")
                self.logger.info(f"  - main_chat_id: {getattr(team, 'main_chat_id', 'None')}")
                self.logger.info(
                    f"  - leadership_chat_id: {getattr(team, 'leadership_chat_id', 'None')}"
                )

            # Use explicit fields for bot config (single source of truth)
            self.bot_configs = [team for team in teams if getattr(team, "bot_token", None)]
            self.logger.info(
                f"📊 Loaded {len(self.bot_configs)} bot configurations from teams collection"
            )
            return self.bot_configs
        except Exception as e:
            self.logger.error(f"❌ Failed to load bot configurations: {e}")
            return []

    async def initialize_crewai_agents(self, team_id: str, team_config: Any) -> Any:
        """Initialize CrewAI agents for a specific team using the lifecycle manager."""
        try:
            logger.info(f"🤖 Initializing CrewAI agents for team: {team_id}")

            # Use the crew lifecycle manager to get or create the crew
            from kickai.agents.crew_lifecycle_manager import get_crew_lifecycle_manager

            lifecycle_manager = get_crew_lifecycle_manager()
            crew = await lifecycle_manager.get_or_create_crew(team_id)

            if crew is None:
                logger.error(f"❌ Failed to create crew for team {team_id}")
                return None

            logger.info(f"✅ CrewAI agents initialized successfully for team: {team_id}")
            return crew

        except Exception as e:
            logger.error(f"❌ Failed to initialize CrewAI agents for team {team_id}: {e}")
            import traceback

            logger.error(f"❌ CrewAI initialization traceback: {traceback.format_exc()}")
            return None

    async def start_all_bots(self) -> None:
        """Start all bots based on loaded configurations."""
        logger.info("🔍 start_all_bots called")

        # Initialize the crew lifecycle manager
        await initialize_crew_lifecycle_manager()

        if not self.bot_configs:
            logger.info("🔍 Loading bot configurations...")
            await self.load_bot_configurations()
        logger.info("🚀 Starting all bots...")

        for team in self.bot_configs:
            team_id = getattr(team, "team_id", None) or getattr(team, "id", None)
            settings = getattr(team, "settings", {})

            # Read bot configuration ONLY from team explicit fields (single source of truth)
            bot_token = getattr(team, "bot_token", None)
            main_chat_id = getattr(team, "main_chat_id", None)
            leadership_chat_id = getattr(team, "leadership_chat_id", None)

            # Log the configuration being used
            logger.info(f"🔧 Bot configuration for team: {team_id}")
            logger.info(f"  - bot_token: {bot_token[:10]}..." if bot_token else "None")
            logger.info(f"  - main_chat_id: {main_chat_id}")
            logger.info(f"  - leadership_chat_id: {leadership_chat_id}")
            logger.info("  - source: team_explicit_fields_from_firestore")

            name = getattr(team, "name", team_id)

            # Check if team has complete bot configuration
            if not bot_token or not main_chat_id or not leadership_chat_id:
                logger.warning(f"⚠️ Skipping team {name} ({team_id}) - incomplete bot configuration")
                logger.warning(f"  - bot_token: {'✓' if bot_token else '✗'}")
                logger.warning(f"  - main_chat_id: {'✓' if main_chat_id else '✗'}")
                logger.warning(f"  - leadership_chat_id: {'✓' if leadership_chat_id else '✗'}")
                continue

            # Team has complete bot configuration, proceed with bot creation
            try:
                # Initialize CrewAI agents first
                logger.info(f"🤖 Starting CrewAI agents for team: {name}")
                crewai_system = await self.initialize_crewai_agents(team_id, team)
                self.crewai_systems[team_id] = crewai_system

                # Then initialize Telegram bot service
                bot_service = TelegramBotService(
                    token=bot_token,
                    main_chat_id=main_chat_id,
                    leadership_chat_id=leadership_chat_id,
                    team_id=team_id,
                    crewai_system=crewai_system,  # Pass the CrewAI system
                )
                self.bots[team_id] = bot_service

                # Update InviteLinkService with bot token
                try:
                    from kickai.core.dependency_container import get_service
                    from kickai.features.communication.domain.services.invite_link_service import (
                        InviteLinkService,
                    )

                    invite_service = get_service(InviteLinkService)
                    if invite_service:
                        invite_service.set_bot_token(bot_token)
                        logger.info(
                            f"✅ Updated InviteLinkService with bot token for team: {team_id}"
                        )
                except Exception as e:
                    logger.warning(
                        f"⚠️ Failed to update InviteLinkService with bot token for team {team_id}: {e}"
                    )

                # Update CommunicationService with TelegramBotService
                try:
                    from kickai.features.communication.domain.services.communication_service import (
                        CommunicationService,
                    )

                    communication_service = get_service(CommunicationService)
                    if communication_service:
                        communication_service.set_telegram_bot_service(bot_service)
                        logger.info(
                            f"✅ Updated CommunicationService with TelegramBotService for team: {team_id}"
                        )
                except Exception as e:
                    logger.warning(
                        f"⚠️ Failed to update CommunicationService with TelegramBotService for team {team_id}: {e}"
                    )

                # Start the bot polling
                logger.info(f"🚀 Starting Telegram bot polling for team: {name}")
                await bot_service.start_polling()

                logger.info(f"✅ Created TelegramBotService for team: {name}")
                logger.info(f"✅ CrewAI system ready for team: {name}")
                logger.info(f"✅ Telegram bot polling started for team: {name}")

            except Exception as e:
                logger.error(f"❌ Failed to start bot for team {name}: {e}")
                continue

        self._running = True
        logger.info(f"🎉 Started {len(self.bots)} bots successfully")
        logger.info(f"🤖 CrewAI agents initialized for {len(self.crewai_systems)} teams")

    async def stop_all_bots(self) -> None:
        """Stop all running bots."""
        self.logger.info("🛑 Stopping all bots...")

        # Stop CrewAI systems
        for team_id, crewai_system in self.crewai_systems.items():
            try:
                # Add cleanup logic for CrewAI systems if needed
                self.logger.info(f"✅ CrewAI system stopped for team: {team_id}")
            except Exception as e:
                self.logger.error(f"❌ Error stopping CrewAI system for team {team_id}: {e}")

        # Stop Telegram bots
        for team_id, bot in self.bots.items():
            try:
                # Stop the Telegram bot service
                await bot.stop()
                self.logger.info(f"✅ Bot stopped for team: {team_id}")
            except Exception as e:
                self.logger.error(f"❌ Error stopping bot for team {team_id}: {e}")

        self.bots.clear()
        self.crewai_systems.clear()
        self._running = False

        # Shutdown the crew lifecycle manager
        await shutdown_crew_lifecycle_manager()

        self.logger.info("🎉 All bots and CrewAI systems stopped successfully")

    async def send_startup_messages(self):
        """Send a startup message to each team's main chat."""
        from kickai.core.constants import BOT_VERSION

        for team in self.bot_configs:
            team_id = getattr(team, "team_id", None) or getattr(team, "id", None)
            team_name = getattr(team, "name", "your team")
            settings = getattr(team, "settings", {})

            # Read bot configuration ONLY from team explicit fields (single source of truth)
            main_chat_id = getattr(team, "main_chat_id", None)
            leadership_chat_id = getattr(team, "leadership_chat_id", None)

            # Compose the welcome message
            message = (
                f"👋 Welcome to *KICKAI* for *{team_name}*!\n"
                f"\n"
                f"🤖 *KICKAI v{BOT_VERSION}* is your AI-powered football team assistant.\n"
                f"- Organize matches, manage attendance, and more.\n"
                f"- Use /help to see what you can do!\n"
                f"\n"
                f"Let's kick off a smarter season! ⚽️"
            )

            # Send to main chat if available
            if main_chat_id and team_id in self.bots:
                try:
                    bot_service = self.bots[team_id]
                    await bot_service.send_message(chat_id=main_chat_id, text=message)
                    logger.info(
                        f"✅ Startup message sent to main chat {main_chat_id} for team {team_name}"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Failed to send startup message to main chat for team {team_name}: {e}"
                    )
            else:
                logger.warning(f"⚠️ No main chat ID or bot available for team {team_name}")

            # Send to leadership chat if available
            if leadership_chat_id and team_id in self.bots:
                try:
                    leadership_message = (
                        f"👔 KICKAI Leadership for {team_name} is now online!\n"
                        f"\n"
                        f"🤖 KICKAI v{BOT_VERSION} is ready to assist with team management.\n"
                        f"- Access admin commands and team oversight.\n"
                        f"- Use /help for leadership commands.\n"
                        f"\n"
                        f"Leadership dashboard is active! 🏆"
                    )
                    bot_service = self.bots[team_id]
                    await bot_service.send_message(
                        chat_id=leadership_chat_id, text=leadership_message
                    )
                    logger.info(
                        f"✅ Leadership startup message sent to chat {leadership_chat_id} for team {team_name}"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Failed to send leadership startup message for team {team_name}: {e}"
                    )

    async def send_shutdown_messages(self):
        """Send a shutdown message to each team's main chat."""
        for team in self.bot_configs:
            team_id = getattr(team, "team_id", None) or getattr(team, "id", None)
            team_name = getattr(team, "name", "your team")
            settings = getattr(team, "settings", {})

            # Read bot configuration ONLY from team explicit fields (single source of truth)
            main_chat_id = getattr(team, "main_chat_id", None)
            leadership_chat_id = getattr(team, "leadership_chat_id", None)

            # Compose the shutdown message
            message = f"🛑 KICKAI for {team_name} is shutting down.\nSee you next time! 👋"

            # Send to main chat if available
            if main_chat_id and team_id in self.bots:
                try:
                    bot_service = self.bots[team_id]
                    await bot_service.send_message(chat_id=main_chat_id, text=message)
                    logger.info(
                        f"✅ Shutdown message sent to main chat {main_chat_id} for team {team_name}"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Failed to send shutdown message to main chat for team {team_name}: {e}"
                    )

            # Send to leadership chat if available
            if leadership_chat_id and team_id in self.bots:
                try:
                    leadership_message = (
                        f"🛑 KICKAI Leadership for {team_name} is shutting down.\n"
                        f"Leadership dashboard offline. 👋"
                    )
                    bot_service = self.bots[team_id]
                    await bot_service.send_message(
                        chat_id=leadership_chat_id, text=leadership_message
                    )
                    logger.info(
                        f"✅ Leadership shutdown message sent to chat {leadership_chat_id} for team {team_name}"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Failed to send leadership shutdown message for team {team_name}: {e}"
                    )

    def is_running(self) -> bool:
        """Return True if bots are running."""
        return self._running

    def get_bot(self, team_id: str) -> Optional[Any]:
        """Get the bot instance for a given team ID."""
        return self.bots.get(team_id)

    def get_crewai_system(self, team_id: str) -> Optional[Any]:
        """Get the CrewAI system for a given team ID."""
        return self.crewai_systems.get(team_id)

    async def get_crew_metrics(self, team_id: str = None) -> dict[str, Any]:
        """Get crew metrics for a specific team or all teams."""
        if team_id:
            return await self.crew_lifecycle_manager.get_crew_metrics(team_id)
        else:
            return await self.crew_lifecycle_manager.get_all_crew_metrics()

    async def get_crew_health_status(self) -> dict[str, Any]:
        """Get health status of all crews."""
        return await self.crew_lifecycle_manager.health_check()

    async def shutdown(self) -> None:
        """Shutdown the multi-bot manager and all bots."""
        try:
            logger.info("🛑 Shutting down MultiBotManager...")
            await self.stop_all_bots()
            logger.info("✅ MultiBotManager shutdown completed")
        except Exception as e:
            logger.error(f"❌ Error during MultiBotManager shutdown: {e}")
            raise
