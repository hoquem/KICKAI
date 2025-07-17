"""
Multi-Bot Manager for KICKAI

This module manages multiple Telegram bots, loading their configurations
from the teams collection in Firestore.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from telegram.ext import Application

from database.models_improved import BotMapping, Team
from database.interfaces import DataStoreInterface
from services.interfaces.team_service_interface import ITeamService
from bot_telegram.simplified_message_handler import register_simplified_handler
from bot_telegram.chat_member_handler import register_chat_member_handler

logger = logging.getLogger(__name__)


class MultiBotManager:
    """Manages multiple Telegram bots with configurations loaded from Firestore."""
    
    def __init__(self, data_store: DataStoreInterface, team_service: ITeamService):
        self._data_store = data_store
        self._team_service = team_service
        self._applications: Dict[str, Application] = {}
        self._bot_mappings: Dict[str, dict] = {} # Changed to dict to store raw config
        self._running = False
        self.polling_tasks = []  # List of asyncio.Task
    
    async def load_bot_configurations(self) -> List[dict]:
        """Load all bot configurations from the settings field of each team in Firestore."""
        try:
            # Get all teams
            teams = await self._team_service.get_all_teams()
            bot_configs = []
            for team in teams:
                settings = team.settings or {}
                try:
                    bot_token = settings['bot_token']
                    main_chat_id = settings['main_chat_id']
                    leadership_chat_id = settings.get('leadership_chat_id')
                    bot_username = settings['bot_username']
                    config = {
                        'team_id': team.id,
                        'team_name': team.name,
                        'bot_token': bot_token,
                        'main_chat_id': main_chat_id,
                        'leadership_chat_id': leadership_chat_id,
                        'bot_username': bot_username,
                        'settings': settings
                    }
                    bot_configs.append(config)
                    self._bot_mappings[team.id] = config
                    logger.info(f"✅ Loaded bot configuration for team: {team.name} (ID: {team.id})")
                except KeyError as e:
                    logger.warning(f"⚠️ Missing bot config field {e} for team: {team.name} (ID: {team.id})")
            logger.info(f"📊 Loaded {len(bot_configs)} bot configurations from teams collection")
            return bot_configs
        except Exception as e:
            logger.error(f"❌ Failed to load bot configurations from teams collection: {e}")
            raise
    
    async def create_bot_application(self, bot_config: dict) -> Application:
        """Create a Telegram application for a bot configuration."""
        try:
            logger.info(f"🤖 Creating bot application for team: {bot_config['team_name']}")
            
            # Create application
            application = Application.builder().token(bot_config['bot_token']).build()
            
            # Register handlers
            register_simplified_handler(application)
            register_chat_member_handler(application)
            
            logger.info(f"✅ Bot application created for team: {bot_config['team_name']}")
            return application
            
        except Exception as e:
            logger.error(f"❌ Failed to create bot application for team {bot_config['team_name']}: {e}")
            raise
    
    @property
    def bot_apps(self):
        """Public property to access bot applications (team_id -> Application)."""
        return self._applications

    async def start_all_bots(self) -> None:
        """Start all loaded bots."""
        if self._running:
            logger.warning("⚠️ Bots are already running")
            return
        
        try:
            logger.info("🚀 Starting all bots...")
            
            # Create and start applications for all bot configurations
            for team_id, bot_config in self._bot_mappings.items():
                try:
                    application = await self.create_bot_application(bot_config)
                    
                    # Initialize and start the application
                    await application.initialize()
                    await application.start()
                    await application.updater.start_polling()
                    
                    # Store the application
                    self._applications[team_id] = application
                    
                    # Note: In python-telegram-bot 20.7+, polling runs in background
                    # No need for wait_until_closed as it's handled internally
                    
                    logger.info(f"✅ Bot started for team: {bot_config['team_name']} (ID: {team_id})")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to start bot for team {bot_config['team_name']} (ID: {team_id}): {e}")
                    # Continue with other bots even if one fails
            
            self._running = True
            logger.info(f"🎉 Started {len(self._applications)} bots successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start bots: {e}")
            raise
    
    async def wait_for_all_bots(self):
        """Wait for all polling tasks to complete (keeps process alive)."""
        # In python-telegram-bot 20.7+, polling runs in background
        # We just need to keep the event loop alive
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def stop_all_bots(self) -> None:
        """Stop all running bots."""
        if not self._running:
            logger.warning("⚠️ No bots are running")
            return
        
        try:
            logger.info("🛑 Stopping all bots...")
            
            # Stop polling and shutdown all bots
            for app in self._applications.values():
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            
            # Clear applications
            self._applications.clear()
            self._running = False
            
            logger.info("🎉 All bots stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop bots: {e}")
            raise
    
    async def send_startup_messages(self) -> None:
        """Send startup messages to all configured chats."""
        try:
            logger.info("📢 Sending startup messages...")
            
            for team_id, application in self._applications.items():
                bot_config = self._bot_mappings.get(team_id)
                if not bot_config:
                    continue
                
                try:
                    # Get bot info
                    bot_info = await application.bot.get_me()
                    bot_name = bot_info.first_name
                    
                    startup_message = (
                        f"🚀 **{bot_name} is now online!**\n\n"
                        f"✅ Bot started successfully for team: {bot_config['team_name']} (ID: {team_id})\n"
                        f"📡 Ready to receive messages\n"
                        f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"💡 Type `/help` to see available commands"
                    )
                    
                    # Send to main chat
                    await application.bot.send_message(
                        chat_id=bot_config['main_chat_id'],
                        text=startup_message,
                        parse_mode='Markdown'
                    )
                    
                    # Send to leadership chat
                    await application.bot.send_message(
                        chat_id=bot_config['leadership_chat_id'],
                        text=startup_message,
                        parse_mode='Markdown'
                    )
                    
                    logger.info(f"✅ Startup message sent for team: {bot_config['team_name']} (ID: {team_id})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send startup message for team {bot_config['team_name']} (ID: {team_id}): {e}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to send startup messages: {e}")
    
    async def send_shutdown_messages(self) -> None:
        """Send shutdown messages to all configured chats."""
        try:
            logger.info("📢 Sending shutdown messages...")
            
            for team_id, application in self._applications.items():
                bot_config = self._bot_mappings.get(team_id)
                if not bot_config:
                    continue
                
                try:
                    # Get bot info
                    bot_info = await application.bot.get_me()
                    bot_name = bot_info.first_name
                    
                    shutdown_message = (
                        f"🛑 **{bot_name} is shutting down**\n\n"
                        f"👋 Bot will be offline until restarted"
                    )
                    
                    # Send to main chat
                    await application.bot.send_message(
                        chat_id=bot_config['main_chat_id'],
                        text=shutdown_message,
                        parse_mode='Markdown'
                    )
                    
                    # Send to leadership chat
                    await application.bot.send_message(
                        chat_id=bot_config['leadership_chat_id'],
                        text=shutdown_message,
                        parse_mode='Markdown'
                    )
                    
                    logger.info(f"✅ Shutdown message sent for team: {bot_config['team_name']} (ID: {team_id})")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to send shutdown message for team {bot_config['team_name']} (ID: {team_id}): {e}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to send shutdown messages: {e}")
    
    def get_running_bots(self) -> List[str]:
        """Get list of team IDs with running bots."""
        return list(self._applications.keys())
    
    def get_running_bot_names(self) -> List[str]:
        """Get list of team names with running bots."""
        return [self._bot_mappings[team_id]['team_name'] for team_id in self._applications.keys()]
    
    def is_running(self) -> bool:
        """Check if bots are running."""
        return self._running
    
    def get_bot_mapping(self, team_id: str) -> Optional[dict]:
        """Get bot configuration for a specific team ID."""
        return self._bot_mappings.get(team_id)
    
    def get_all_bot_mappings(self) -> Dict[str, dict]:
        """Get all bot configurations."""
        return self._bot_mappings.copy() 