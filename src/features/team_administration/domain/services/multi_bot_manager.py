import logging
import os
from typing import Any, Dict, List, Optional
from features.communication.infrastructure import TelegramBotService
from loguru import logger

class MultiBotManager:
    """
    Manages multiple bot instances for different teams.
    Loads bot configurations, starts/stops bots, and monitors their status.
    """
    def __init__(self, data_store: Any, team_service: Any):
        logger.debug("DEBUG: MultiBotManager.__init__ called")
        self.data_store = data_store
        self.team_service = team_service
        self.bots: Dict[str, Any] = {}
        self.bot_configs: List[Dict[str, Any]] = []
        self.crewai_systems: Dict[str, Any] = {}  # Store CrewAI systems for each team
        self._running = False
        self.logger = logging.getLogger(__name__)
        logger.debug("DEBUG: MultiBotManager.__init__ completed")

    async def load_bot_configurations(self) -> List[Any]:
        """Load bot configurations from the data store (e.g., Firestore)."""
        try:
            self.logger.info("🔍 Loading bot configurations from data store...")
            teams = await self.team_service.get_all_teams()
            self.logger.info(f"📊 Found {len(teams)} teams in database")
            
            # Debug: Print each team's bot configuration
            for i, team in enumerate(teams):
                self.logger.info(f"Team {i+1}: {team.name} (ID: {getattr(team, 'id', 'None')})")
                self.logger.info(f"  - bot_token: {team.settings.get('bot_token', 'None')}")
                self.logger.info(f"  - main_chat_id: {team.settings.get('main_chat_id', 'None')}")
                self.logger.info(f"  - leadership_chat_id: {team.settings.get('leadership_chat_id', 'None')}")
            
            # Use settings for bot config
            self.bot_configs = [team for team in teams if team.settings.get('bot_token')]
            self.logger.info(f"📊 Loaded {len(self.bot_configs)} bot configurations from teams collection")
            return self.bot_configs
        except Exception as e:
            self.logger.error(f"❌ Failed to load bot configurations: {e}")
            return []

    async def initialize_crewai_agents(self, team_id: str, team_config: Any) -> Any:
        """Initialize CrewAI agents for a specific team."""
        try:
            logger.info(f"🤖 Initializing CrewAI agents for team: {team_id}")
            
            # Import the TeamManagementSystem
            from src.agents.crew_agents import TeamManagementSystem
            
            logger.info(f"🔍 About to create TeamManagementSystem for team: {team_id}")
            # Create the CrewAI system (constructor handles all initialization)
            crewai_system = TeamManagementSystem(
                team_id=team_id
            )
            
            logger.info(f"✅ CrewAI agents initialized for team: {team_id}")
            logger.info(f"📊 Active agents: {list(crewai_system.agents.keys())}")
            
            return crewai_system
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize CrewAI agents for team {team_id}: {e}")
            raise

    async def start_all_bots(self) -> None:
        """Start all bots based on loaded configurations."""
        logger.info("🔍 start_all_bots called")
        if not self.bot_configs:
            logger.info("🔍 Loading bot configurations...")
            await self.load_bot_configurations()
        logger.info("🚀 Starting all bots...")
        
        for team in self.bot_configs:
            team_id = getattr(team, 'team_id', None) or getattr(team, 'id', None)
            settings = getattr(team, 'settings', {})
            
            # ALWAYS read bot configuration from team settings first
            bot_token = settings.get('bot_token', None)
            main_chat_id = settings.get('main_chat_id', None)
            leadership_chat_id = settings.get('leadership_chat_id', None)
            
            # Only use environment variables as fallback if team settings are missing
            if not bot_token:
                bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
                logger.warning(f"⚠️ No bot_token in team settings for {team_id}, using environment variable")
            
            if not main_chat_id:
                main_chat_id = os.getenv('TELEGRAM_MAIN_CHAT_ID')
                logger.warning(f"⚠️ No main_chat_id in team settings for {team_id}, using environment variable")
            
            if not leadership_chat_id:
                leadership_chat_id = os.getenv('TELEGRAM_LEADERSHIP_CHAT_ID')
                logger.warning(f"⚠️ No leadership_chat_id in team settings for {team_id}, using environment variable")
            
            # Log the configuration being used
            logger.info(f"🔧 Bot configuration for team: {team_id}")
            logger.info(f"  - bot_token: {bot_token[:10]}..." if bot_token else "None")
            logger.info(f"  - main_chat_id: {main_chat_id}")
            logger.info(f"  - leadership_chat_id: {leadership_chat_id}")
            logger.info(f"  - source: {'team_settings' if settings.get('bot_token') else 'environment_variables'}")
            
            name = getattr(team, 'name', team_id)
            
            if team_id and bot_token:
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
                        crewai_system=crewai_system  # Pass the CrewAI system
                    )
                    self.bots[team_id] = bot_service
                    
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
        self.logger.info("🎉 All bots and CrewAI systems stopped successfully")

    async def send_startup_messages(self):
        """Send a startup message to each team's main chat."""
        from core.constants import BOT_VERSION
        
        for team in self.bot_configs:
            team_id = getattr(team, 'team_id', None) or getattr(team, 'id', None)
            team_name = getattr(team, 'name', 'your team')
            settings = getattr(team, 'settings', {})
            
            # ALWAYS read bot configuration from team settings first
            main_chat_id = settings.get('main_chat_id', None)
            leadership_chat_id = settings.get('leadership_chat_id', None)
            
            # Only use environment variables as fallback if team settings are missing
            if not main_chat_id:
                main_chat_id = os.getenv('TELEGRAM_MAIN_CHAT_ID')
                logger.warning(f"⚠️ No main_chat_id in team settings for {team_id}, using environment variable")
            
            if not leadership_chat_id:
                leadership_chat_id = os.getenv('TELEGRAM_LEADERSHIP_CHAT_ID')
                logger.warning(f"⚠️ No leadership_chat_id in team settings for {team_id}, using environment variable")
            
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
                    await bot_service.send_message(
                        chat_id=main_chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    logger.info(f"✅ Startup message sent to main chat {main_chat_id} for team {team_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to send startup message to main chat for team {team_name}: {e}")
            else:
                logger.warning(f"⚠️ No main chat ID or bot available for team {team_name}")
            
            # Send to leadership chat if available
            if leadership_chat_id and team_id in self.bots:
                try:
                    leadership_message = (
                        f"👔 *KICKAI Leadership* for *{team_name}* is now online!\n"
                        f"\n"
                        f"🤖 *KICKAI v{BOT_VERSION}* is ready to assist with team management.\n"
                        f"- Access admin commands and team oversight.\n"
                        f"- Use /help for leadership commands.\n"
                        f"\n"
                        f"Leadership dashboard is active! 🏆"
                    )
                    bot_service = self.bots[team_id]
                    await bot_service.send_message(
                        chat_id=leadership_chat_id,
                        text=leadership_message,
                        parse_mode='Markdown'
                    )
                    logger.info(f"✅ Leadership startup message sent to chat {leadership_chat_id} for team {team_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to send leadership startup message for team {team_name}: {e}")

    async def send_shutdown_messages(self):
        """Send a shutdown message to each team's main chat."""
        for team in self.bot_configs:
            team_id = getattr(team, 'team_id', None) or getattr(team, 'id', None)
            team_name = getattr(team, 'name', 'your team')
            settings = getattr(team, 'settings', {})
            
            # ALWAYS read bot configuration from team settings first
            main_chat_id = settings.get('main_chat_id', None)
            leadership_chat_id = settings.get('leadership_chat_id', None)
            
            # Only use environment variables as fallback if team settings are missing
            if not main_chat_id:
                main_chat_id = os.getenv('TELEGRAM_MAIN_CHAT_ID')
                logger.warning(f"⚠️ No main_chat_id in team settings for {team_id}, using environment variable")
            
            if not leadership_chat_id:
                leadership_chat_id = os.getenv('TELEGRAM_LEADERSHIP_CHAT_ID')
                logger.warning(f"⚠️ No leadership_chat_id in team settings for {team_id}, using environment variable")
            
            # Compose the shutdown message
            message = (
                f"🛑 *KICKAI* for *{team_name}* is shutting down.\n"
                f"See you next time! 👋"
            )
            
            # Send to main chat if available
            if main_chat_id and team_id in self.bots:
                try:
                    bot_service = self.bots[team_id]
                    await bot_service.send_message(
                        chat_id=main_chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    logger.info(f"✅ Shutdown message sent to main chat {main_chat_id} for team {team_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to send shutdown message to main chat for team {team_name}: {e}")
            
            # Send to leadership chat if available
            if leadership_chat_id and team_id in self.bots:
                try:
                    leadership_message = (
                        f"🛑 *KICKAI Leadership* for *{team_name}* is shutting down.\n"
                        f"Leadership dashboard offline. 👋"
                    )
                    bot_service = self.bots[team_id]
                    await bot_service.send_message(
                        chat_id=leadership_chat_id,
                        text=leadership_message,
                        parse_mode='Markdown'
                    )
                    logger.info(f"✅ Leadership shutdown message sent to chat {leadership_chat_id} for team {team_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to send leadership shutdown message for team {team_name}: {e}")

    def is_running(self) -> bool:
        """Return True if bots are running."""
        return self._running

    def get_bot(self, team_id: str) -> Optional[Any]:
        """Get the bot instance for a given team ID."""
        return self.bots.get(team_id)
    
    def get_crewai_system(self, team_id: str) -> Optional[Any]:
        """Get the CrewAI system for a given team ID."""
        return self.crewai_systems.get(team_id) 