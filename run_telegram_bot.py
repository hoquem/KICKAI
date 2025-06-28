#!/usr/bin/env python3
"""
Telegram Bot Runner for KICKAI
Handles incoming Telegram messages and processes commands
"""

import os
import time
import logging
import requests
from dotenv import load_dotenv
from src.telegram_command_handler import TelegramCommandHandler

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramBotRunner:
    """Runs the Telegram bot and handles incoming messages."""
    
    def __init__(self):
        # Get bot token from Supabase database
        self.bot_token = self._get_bot_token_from_db()
        if not self.bot_token:
            raise ValueError("Bot token not found in database")
        
        self.command_handler = TelegramCommandHandler()
        self.last_update_id = 0
        
    def _get_bot_token_from_db(self):
        """Get bot token from Supabase database."""
        try:
            from src.tools.supabase_tools import get_supabase_client
            supabase = get_supabase_client()
            
            response = supabase.table('team_bots').select('bot_token').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').eq('is_active', True).execute()
            
            if response.data:
                return response.data[0]['bot_token']
            else:
                logger.error("No active bot found in database")
                return None
                
        except Exception as e:
            logger.error(f"Error getting bot token from database: {e}")
            return None
    
    def get_updates(self, offset=None, limit=100, timeout=30):
        """Get updates from Telegram API."""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            'timeout': timeout,
            'limit': limit
        }
        if offset:
            params['offset'] = offset
            
        try:
            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                logger.warning("409 Conflict: Another bot instance may be running. Retrying in 5 seconds...")
                time.sleep(5)
                return None
            else:
                logger.error(f"HTTP Error getting updates: {e}")
                return None
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return None
    
    def process_updates(self, updates):
        """Process incoming updates."""
        if not updates or not updates.get('ok') or not updates.get('result'):
            return
        
        for update in updates['result']:
            update_id = update.get('update_id', 0)
            
            # Skip already processed updates
            if update_id <= self.last_update_id:
                continue
            
            # Process the update
            try:
                self.command_handler.process_message(update)
                self.last_update_id = update_id
            except Exception as e:
                logger.error(f"Error processing update {update_id}: {e}")
    
    def run_polling(self):
        """Run the bot using polling method."""
        logger.info("🤖 Starting Telegram bot (polling mode)...")
        logger.info(f"📱 Bot token: {self.bot_token[:10]}...")
        
        # Get initial updates to set last_update_id
        initial_updates = self.get_updates()
        if initial_updates is not None and 'result' in initial_updates and initial_updates['result']:
            self.last_update_id = max(update.get('update_id', 0) for update in initial_updates['result'])
            logger.info(f"📋 Starting from update ID: {self.last_update_id}")
        else:
            logger.info("📋 No initial updates found, starting from update ID: 0")
        
        print("✅ Bot is running! Send messages to your Telegram groups to test.")
        print("💡 Press Ctrl+C to stop the bot.")
        
        try:
            while True:
                # Get updates with long polling
                updates = self.get_updates(offset=self.last_update_id + 1)
                if updates and updates.get('result'):
                    self.process_updates(updates)
                
                # Small delay to prevent excessive API calls
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            raise
    
    def test_connection(self):
        """Test bot connection and get bot info."""
        url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
        try:
            response = requests.get(url)
            response.raise_for_status()
            bot_info = response.json()
            
            if bot_info.get('ok'):
                bot = bot_info['result']
                logger.info(f"✅ Bot connected successfully!")
                logger.info(f"   Name: {bot.get('first_name')}")
                logger.info(f"   Username: @{bot.get('username')}")
                logger.info(f"   ID: {bot.get('id')}")
                return True
            else:
                logger.error(f"❌ Bot connection failed: {bot_info}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing bot connection: {e}")
            return False

def main():
    """Main function to run the bot."""
    print("🏆 KICKAI Telegram Bot Runner")
    print("=" * 40)
    
    try:
        # Create bot runner
        bot_runner = TelegramBotRunner()
        
        # Test connection
        print("\n🔍 Testing bot connection...")
        if not bot_runner.test_connection():
            print("❌ Bot connection failed. Check your TELEGRAM_BOT_TOKEN.")
            return
        
        # Run the bot
        print("\n🚀 Starting bot...")
        bot_runner.run_polling()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure TELEGRAM_BOT_TOKEN is set in your .env file")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Bot error: {e}", exc_info=True)

if __name__ == "__main__":
    main() 