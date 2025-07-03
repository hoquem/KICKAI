#!/usr/bin/env python3
"""
Bot Status Service

This service handles sending startup and shutdown messages to Telegram chats.
"""

import asyncio
import requests
from datetime import datetime
from typing import Optional

from src.core.logging import get_logger
from src.core.bot_config_manager import get_bot_config_manager

logger = get_logger("bot_status_service")

class BotStatusService:
    """Service for sending bot status messages to Telegram chats."""
    
    def __init__(self, bot_token: str, team_id: str):
        self.bot_token = bot_token
        self.team_id = team_id
        self.manager = get_bot_config_manager()
        self.bot_config = self.manager.get_bot_config(team_id)
        self.team_config = self.manager.get_team_config(team_id)
        
    def _send_telegram_message(self, chat_id: str, message: str) -> bool:
        """Send a message to a Telegram chat."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=data, timeout=10)
            success = response.status_code == 200
            
            if success:
                logger.info(f"✅ Status message sent to chat {chat_id}")
            else:
                logger.error(f"❌ Failed to send status message to chat {chat_id}: {response.status_code}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error sending status message to chat {chat_id}: {e}")
            return False
    
    def get_version_info(self) -> str:
        """Get the current version information."""
        return "v1.5.0"
    
    def get_main_chat_features(self) -> str:
        """Get features available in main chat (market-facing, no admin or tech info)."""
        return """<b>Welcome to your team's official chat, powered by KICKAI!</b>

Here you can:
• View your team roster and stats
• Get updates and important announcements
• Connect with your teammates
• Check your player information

📋 <b>Player Commands:</b>
• <code>/list</code> – View all players
• <code>/status &lt;phone&gt;</code> – Check your status
• <code>/stats</code> – Team statistics
• <code>/myinfo</code> – Your player info
• <code>/help</code> – Show help

💬 <b>Natural Language:</b>
• Ask questions about the team
• Request player information
• Get match details
• Plan team activities

Let's play, grow, and win together! ⚽️"""
    
    def get_leadership_chat_features(self) -> str:
        """Get features available in leadership chat."""
        return """📋 <b>Available Commands:</b>

👥 <b>Player Management:</b>
• <code>/add &lt;name&gt; &lt;phone&gt; &lt;position&gt;</code> - Add a new player
• <code>/remove &lt;phone&gt;</code> - Remove a player
• <code>/list</code> - List all players
• <code>/status &lt;phone&gt;</code> - Get player status
• <code>/stats</code> - Get team statistics
• <code>/invite &lt;phone_or_player_id&gt;</code> - Generate invitation message

👨‍💼 <b>Admin Commands:</b>
• <code>/approve &lt;player_id&gt;</code> - Approve a player
• <code>/reject &lt;player_id&gt; [reason]</code> - Reject a player
• <code>/pending</code> - List players pending approval
• <code>/checkfa</code> - Check FA registration status
• <code>/dailystatus</code> - Generate daily team status report

👤 <b>Player Commands:</b>
• <code>/myinfo</code> - Get your player information

❓ <b>Help:</b>
• <code>/help</code> - Show this help message

💬 <b>Natural Language:</b>
• Team management and strategy
• Player analysis and selection
• Match planning and coordination
• Financial management
• Performance analytics"""
    
    def send_startup_message(self) -> bool:
        """Send startup message to both chats."""
        if not self.bot_config:
            logger.error("❌ Bot configuration not found")
            return False
        
        version = self.get_version_info()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot_name = self.bot_config.username or "KICKAI Bot"
        team_name = self.team_config.name if self.team_config else "Team"
        
        # Main chat startup message (market-facing)
        main_message = f'''🟢 <b>Welcome to {team_name} Team Chat!</b>

{self.get_main_chat_features()}'''
        
        # Leadership chat startup message
        leadership_message = f'''🟢 <b>Welcome to {team_name} Leadership Chat!</b>

📅 <b>Started:</b> {timestamp}
🏆 <b>Version:</b> {version}
🔥 <b>Database:</b> Firebase Firestore Connected
🤖 <b>AI:</b> 8-Agent CrewAI System Active
🔧 <b>Background Tasks:</b> FA Registration Checker & Daily Status Active

{self.get_leadership_chat_features()}

💡 <b>Try:</b> "Generate daily status report" or "Check FA registrations"'''
        
        # Send messages
        main_success = self._send_telegram_message(self.bot_config.main_chat_id, main_message)
        leadership_success = self._send_telegram_message(self.bot_config.leadership_chat_id, leadership_message)
        
        if main_success and leadership_success:
            logger.info("✅ Startup messages sent to both chats successfully")
            return True
        else:
            logger.warning("⚠️ Some startup messages failed to send")
            return False
    
    def send_shutdown_message(self) -> bool:
        """Send shutdown message to both chats."""
        if not self.bot_config:
            logger.error("❌ Bot configuration not found")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot_name = self.bot_config.username or "KICKAI Bot"
        team_name = self.team_config.name if self.team_config else "Team"
        
        # Shutdown message for both chats
        shutdown_message = f'''🔴 <b>{team_name} Bot is Shutting Down</b>

📅 <b>Shutdown Time:</b> {timestamp}
🔧 <b>Reason:</b> Maintenance/Update
⏱️ <b>Expected Duration:</b> 2-5 minutes

🔄 <b>Services Affected:</b>
• Player management commands
• FA registration checking
• Daily status reports
• Natural language processing

✅ <b>Services Will Resume:</b>
• Automatic FA registration monitoring
• Daily status reports at 9:00 AM
• All player management features
• AI-powered team assistance

💡 <b>Note:</b> This is a scheduled maintenance. The bot will be back online shortly.'''
        
        # Send messages
        main_success = self._send_telegram_message(self.bot_config.main_chat_id, shutdown_message)
        leadership_success = self._send_telegram_message(self.bot_config.leadership_chat_id, shutdown_message)
        
        if main_success and leadership_success:
            logger.info("✅ Shutdown messages sent to both chats successfully")
            return True
        else:
            logger.warning("⚠️ Some shutdown messages failed to send")
            return False


def send_startup_messages(bot_token: str, team_id: str) -> bool:
    """Send startup messages to both chats."""
    try:
        service = BotStatusService(bot_token, team_id)
        return service.send_startup_message()
    except Exception as e:
        logger.error(f"❌ Error sending startup messages: {e}")
        return False


def send_shutdown_messages(bot_token: str, team_id: str) -> bool:
    """Send shutdown messages to both chats."""
    try:
        service = BotStatusService(bot_token, team_id)
        return service.send_shutdown_message()
    except Exception as e:
        logger.error(f"❌ Error sending shutdown messages: {e}")
        return False 