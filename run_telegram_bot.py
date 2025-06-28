#!/usr/bin/env python3
"""
Telegram Bot Runner for KICKAI
Handles incoming Telegram messages and processes commands
"""

import os
import time
import logging
import requests
import random
import sys
from dotenv import load_dotenv

# Add src directory to Python path for Railway deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)

try:
    from telegram_command_handler import TelegramCommandHandler
except ImportError:
    # Fallback for local development
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
        self.consecutive_errors = 0
        self.max_retries = 5
        self.base_delay = 1
        
    def _get_bot_token_from_db(self):
        """Get bot token from Supabase database."""
        try:
            logger.info("🔍 Starting bot token retrieval from database...")
            
            # Step 1: Import the Supabase client
            logger.info("📦 Importing Supabase client...")
            try:
                from tools.supabase_tools import get_supabase_client
                logger.info("✅ Imported from tools.supabase_tools")
            except ImportError as import_error:
                logger.warning(f"⚠️ Import failed from tools.supabase_tools: {import_error}")
                # Fallback for local development
                try:
                    from src.tools.supabase_tools import get_supabase_client
                    logger.info("✅ Imported from src.tools.supabase_tools")
                except ImportError as fallback_error:
                    logger.error(f"❌ Both import paths failed: {fallback_error}")
                    raise
                
            # Step 2: Create Supabase client
            logger.info("🔧 Creating Supabase client...")
            try:
                supabase = get_supabase_client()
                logger.info("✅ Supabase client created successfully")
            except Exception as client_error:
                logger.error(f"❌ Failed to create Supabase client: {client_error}")
                logger.error(f"❌ Error type: {type(client_error)}")
                logger.error(f"❌ Error args: {client_error.args}")
                raise
            
            # Step 3: Execute database query
            logger.info("🔍 Executing database query...")
            try:
                response = supabase.table('team_bots').select('bot_token').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').eq('is_active', True).execute()
                logger.info("✅ Database query executed successfully")
                logger.info(f"📊 Response data: {response.data if hasattr(response, 'data') else 'No data attribute'}")
            except Exception as query_error:
                logger.error(f"❌ Database query failed: {query_error}")
                logger.error(f"❌ Query error type: {type(query_error)}")
                raise
            
            # Step 4: Process response
            if response and hasattr(response, 'data') and response.data:
                bot_token = response.data[0]['bot_token']
                logger.info(f"✅ Bot token retrieved successfully: {bot_token[:10]}...")
                return bot_token
            else:
                logger.error("❌ No active bot found in database")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting bot token from database: {e}")
            logger.error(f"❌ Full error details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    def _calculate_delay(self):
        """Calculate delay with exponential backoff and jitter."""
        if self.consecutive_errors == 0:
            return self.base_delay
        
        delay = min(self.base_delay * (2 ** self.consecutive_errors), 60)  # Max 60 seconds
        jitter = random.uniform(0.5, 1.5)
        return delay * jitter
    
    def _reset_error_count(self):
        """Reset consecutive error count on successful operation."""
        if self.consecutive_errors > 0:
            logger.info(f"✅ Connection restored after {self.consecutive_errors} errors")
            self.consecutive_errors = 0
    
    def get_updates(self, offset=None, limit=100, timeout=30):
        """Get updates from Telegram API with improved error handling."""
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {
            'timeout': timeout,
            'limit': limit
        }
        if offset:
            params['offset'] = offset
            
        try:
            # Use a shorter timeout for the request itself
            response = requests.get(url, params=params, timeout=timeout + 10)
            response.raise_for_status()
            
            # Reset error count on success
            self._reset_error_count()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self.consecutive_errors += 1
            if e.response.status_code == 409:
                logger.warning(f"409 Conflict: Another bot instance may be running. Error #{self.consecutive_errors}")
                # For 409 errors, try to delete webhook first
                self._delete_webhook()
                return None
            elif e.response.status_code == 429:
                logger.warning(f"429 Rate limited. Error #{self.consecutive_errors}")
                return None
            else:
                logger.error(f"HTTP Error getting updates: {e}")
                return None
                
        except requests.exceptions.Timeout:
            self.consecutive_errors += 1
            logger.warning(f"Timeout getting updates. Error #{self.consecutive_errors}")
            return None
            
        except requests.exceptions.ConnectionError:
            self.consecutive_errors += 1
            logger.warning(f"Connection error getting updates. Error #{self.consecutive_errors}")
            return None
            
        except Exception as e:
            self.consecutive_errors += 1
            logger.error(f"Unexpected error getting updates: {e}")
            return None
    
    def _delete_webhook(self):
        """Delete webhook to resolve 409 conflicts."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook"
            response = requests.post(url, timeout=10)
            if response is not None and response.status_code == 200:
                logger.info("✅ Webhook deleted successfully")
            else:
                status_code = response.status_code if response is not None else 'No response'
                logger.warning(f"Failed to delete webhook: {status_code}")
        except Exception as e:
            logger.warning(f"Error deleting webhook: {e}")
    
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
        """Run the bot using polling method with improved error handling."""
        logger.info("🤖 Starting Telegram bot (polling mode)...")
        logger.info(f"📱 Bot token: {self.bot_token[:10]}...")
        
        # Delete any existing webhook first
        self._delete_webhook()
        
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
                
                # Calculate delay based on error count
                delay = self._calculate_delay()
                if self.consecutive_errors > 0:
                    logger.info(f"⏳ Waiting {delay:.1f}s before next request (error #{self.consecutive_errors})")
                
                time.sleep(delay)
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            raise
    
    def test_connection(self):
        """Test bot connection and get bot info."""
        url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
        try:
            response = requests.get(url, timeout=10)
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
            print("❌ Bot connection failed. Check your bot token.")
            return
        
        # Run the bot
        print("\n🚀 Starting bot...")
        bot_runner.run_polling()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure bot token is available in the database")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Bot error: {e}", exc_info=True)

if __name__ == "__main__":
    main() 