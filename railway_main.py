#!/usr/bin/env python3
"""
Railway Main Entry Point for KICKAI
Deployment timestamp: 2024-12-19 16:00 UTC - Fixture Management Active
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
import sys
import logging
import time
import threading
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_health_server():
    """Start health check server for Railway monitoring."""
    try:
        from health_check import start_health_server
        health_thread = start_health_server()
        logger.info("✅ Health server started for Railway")
        return health_thread
    except Exception as e:
        logger.error(f"❌ Health server failed: {e}")
        return None

def main():
    """Main entry point for Railway deployment."""
    try:
        logger.info("🚀 Starting KICKAI on Railway...")
        logger.info("📅 Deployment timestamp: 2024-12-19 16:00 UTC")
        logger.info("🏆 Fixture Management System: ACTIVE")
        
        # Start health server
        health_thread = start_health_server()
        
        # Start Telegram bot directly
        from run_telegram_bot import TelegramBotRunner
        
        logger.info("🤖 Starting Telegram bot with fixture management...")
        bot_runner = TelegramBotRunner()
        
        if not bot_runner.test_connection():
            logger.error("❌ Bot connection failed")
            return False
        
        logger.info("✅ Bot connected successfully!")
        logger.info("📅 Fixture management commands available:")
        logger.info("   /newfixture - Create new fixtures")
        logger.info("   /listfixtures - List fixtures with filtering")
        
        # Start bot in polling mode
        bot_runner.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start KICKAI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
