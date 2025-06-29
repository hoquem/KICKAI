#!/usr/bin/env python3
"""
Telegram Bot Runner for KICKAI
Handles incoming Telegram messages and processes commands using LLM-based parsing
"""

# --- MONKEY-PATCH MUST BE FIRST - before any other imports ---
import httpx

# --- Monkey-patch to remove 'proxy' and 'proxies' kwargs from httpx.Client/AsyncClient ---
_original_client_init = httpx.Client.__init__
def _patched_client_init(self, *args, **kwargs):
    kwargs.pop("proxy", None)
    kwargs.pop("proxies", None)
    _original_client_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_client_init

_original_async_client_init = httpx.AsyncClient.__init__
def _patched_async_client_init(self, *args, **kwargs):
    kwargs.pop("proxy", None)
    kwargs.pop("proxies", None)
    _original_async_client_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_async_client_init

# --- Now safe to import other modules ---
import os
import logging
import sys
from dotenv import load_dotenv
from telegram.ext import Application

# Add src directory to Python path for Railway deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if os.path.exists(src_dir):
    sys.path.insert(0, src_dir)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_bot_token_from_db():
    """Get bot token from Supabase database."""
    try:
        logger.info("🔍 Starting bot token retrieval from database...")
        
        # Import the Supabase client
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
            
        # Create Supabase client
        logger.info("🔧 Creating Supabase client...")
        try:
            supabase = get_supabase_client()
            logger.info("✅ Supabase client created successfully")
        except Exception as client_error:
            logger.error(f"❌ Failed to create Supabase client: {client_error}")
            raise
        
        # Execute database query
        logger.info("🔍 Executing database query...")
        try:
            response = supabase.table('team_bots').select('bot_token').eq('team_id', '0854829d-445c-4138-9fd3-4db562ea46ee').eq('is_active', True).execute()
            logger.info("✅ Database query executed successfully")
            logger.info(f"📊 Response data: {response.data if hasattr(response, 'data') else 'No data attribute'}")
        except Exception as query_error:
            logger.error(f"❌ Database query failed: {query_error}")
            raise
        
        # Process response
        if response and hasattr(response, 'data') and response.data:
            bot_token = response.data[0]['bot_token']
            logger.info(f"✅ Bot token retrieved successfully: {bot_token[:10]}...")
            return bot_token
        else:
            logger.error("❌ No active bot found in database")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error getting bot token from database: {e}")
        return None

def test_bot_connection(bot_token):
    """Test bot connection and get bot info."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
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
    """Main function to run the bot with LLM-based command parsing."""
    print("🏆 KICKAI Telegram Bot Runner (LLM Parsing)")
    print("=" * 50)
    
    # Start health server for Railway monitoring
    try:
        from health_check import start_health_server
        health_thread = start_health_server()
        logger.info("✅ Health server started for Railway monitoring")
    except Exception as e:
        logger.warning(f"⚠️ Could not start health server: {e}")
    
    try:
        # Get bot token from database
        bot_token = get_bot_token_from_db()
        if not bot_token:
            print("❌ Bot token not found. Exiting.")
            return
        
        # Test connection
        print("\n🔍 Testing bot connection...")
        if not test_bot_connection(bot_token):
            print("❌ Bot connection failed. Check your bot token.")
            return
        
        # Set up python-telegram-bot Application
        print("\n🚀 Setting up LLM-based bot...")
        app = Application.builder().token(bot_token).build()
        
        # Register agent-based commands
        try:
            from src.telegram_command_handler import register_agent_based_commands
            register_agent_based_commands(app)
            logger.info("✅ Agent-based command processing registered")
        except Exception as e:
            logger.error(f"❌ Failed to register agent-based commands: {e}")
            return
        
        print("✅ Bot is running with 8-agent CrewAI system! Send messages to your Telegram groups to test.")
        print("🤖 Agent-based natural language processing enabled:")
        print("   • Message Processing Specialist - Primary interface")
        print("   • Team Manager - Strategic coordination")
        print("   • Player Coordinator - Operational management")
        print("   • Match Analyst - Tactical analysis")
        print("   • Communication Specialist - Broadcast management")
        print("   • Finance Manager - Financial management")
        print("   • Squad Selection Specialist - Squad selection")
        print("   • Analytics Specialist - Performance analytics")
        print("💡 Try: \"Create a match against Arsenal on July 1st at 2pm\"")
        print("💡 Try: \"Plan our next match including squad selection\"")
        print("💡 Try: \"Analyze our team performance and suggest improvements\"")
        print("💡 Press Ctrl+C to stop the bot.")
        
        # Run the bot with polling
        app.run_polling()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure bot token is available in the database")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Bot error: {e}", exc_info=True)

if __name__ == "__main__":
    main() 