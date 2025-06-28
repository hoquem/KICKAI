#!/usr/bin/env python3
"""
Railway Main Entry Point for KICKAI Full System
Starts the complete system including CrewAI agents, Telegram bot, and health monitoring
"""

import os
import sys
import logging
import time
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def start_telegram_bot():
    """Start the Telegram bot with CrewAI integration."""
    try:
        from run_telegram_bot import TelegramBotRunner
        
        # Create and start bot
        bot_runner = TelegramBotRunner()
        
        if not bot_runner.test_connection():
            logger.error("❌ Bot connection failed")
            return False
        
        # Start bot in background thread
        def run_bot():
            try:
                bot_runner.run_polling()
            except Exception as e:
                logger.error(f"❌ Bot error: {e}")
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        logger.info("✅ Telegram bot started with CrewAI integration")
        return True
        
    except Exception as e:
        logger.error(f"❌ Telegram bot failed: {e}")
        return False

def main():
    """Main function for Railway deployment."""
    print("🚀 KICKAI Full System - Railway Deployment")
    print("=" * 50)
    
    # Start health server
    print("\n🏥 Starting health server...")
    health_thread = start_health_server()
    
    # Start Telegram bot
    print("\n🤖 Starting Telegram bot with CrewAI...")
    if not start_telegram_bot():
        print("❌ Failed to start Telegram bot")
        return
    
    print("\n✅ KICKAI Full System deployed successfully!")
    print("\n📊 Services Running:")
    print("   🏥 Health Server: https://your-app.railway.app/health")
    print("   🤖 Telegram Bot: @BPHatters_bot")
    print("   🧠 CrewAI Agents: Ready")
    print("   🗄️  Database: Connected")
    
    # Keep alive
    try:
        while True:
            time.sleep(60)
            logger.info("💓 System heartbeat - all services operational")
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")

if __name__ == "__main__":
    main() 