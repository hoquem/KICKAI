#!/usr/bin/env python3
"""
Railway Main Entry Point for KICKAI
Deployment timestamp: 2024-12-19 16:20 UTC - Match Management Active
Version: 1.3.0-match-management
FORCE DEPLOYMENT: 2024-12-19 16:30 UTC - Simplified Health Server
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

def start_simple_health_server():
    """Start a simple health check server for Railway monitoring."""
    try:
        from flask import Flask, jsonify
        import threading
        
        app = Flask(__name__)
        
        @app.route('/health')
        def health_check():
            """Health check endpoint for Railway."""
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'service': 'KICKAI Telegram Bot',
                'environment': os.getenv('RAILWAY_ENVIRONMENT', 'development'),
                'version': '1.3.0-match-management'
            })
        
        @app.route('/')
        def root():
            """Root endpoint."""
            return jsonify({
                'message': 'KICKAI Telegram Bot is running',
                'status': 'operational',
                'timestamp': time.time()
            })
        
        def run_server():
            port = int(os.getenv('PORT', 8080))
            logger.info(f"🏥 Starting health server on port {port}")
            app.run(host='0.0.0.0', port=port, debug=False)
        
        health_thread = threading.Thread(target=run_server, daemon=True)
        health_thread.start()
        logger.info("✅ Health server started for Railway")
        return health_thread
        
    except Exception as e:
        logger.error(f"❌ Health server failed: {e}")
        return None

def start_telegram_bot():
    """Start Telegram bot in a separate thread."""
    try:
        from run_telegram_bot import main as run_bot
        logger.info("🤖 Starting Telegram bot with match management...")
        run_bot()
    except Exception as e:
        logger.error(f"❌ Telegram bot failed: {e}")

def main():
    """Main entry point for Railway deployment."""
    try:
        logger.info("🚀 Starting KICKAI on Railway...")
        logger.info("📅 Deployment timestamp: 2024-12-19 16:30 UTC")
        logger.info("🏆 Version: 1.3.0-match-management")
        logger.info("🏆 Match Management System: ACTIVE")
        logger.info("🏥 Simplified Health Server: ACTIVE")
        
        # Start health server first (for Railway health checks)
        logger.info("🏥 Starting health server...")
        health_thread = start_simple_health_server()
        if not health_thread:
            logger.error("❌ Health server failed to start")
            sys.exit(1)
        
        # Wait a moment for health server to start
        time.sleep(3)
        
        # Start Telegram bot in a separate thread
        logger.info("🤖 Starting Telegram bot...")
        bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        bot_thread.start()
        
        logger.info("✅ KICKAI system started successfully!")
        logger.info("🏥 Health endpoint: /health")
        logger.info("🤖 Telegram bot: Running in background")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(60)  # Check every minute
                logger.info("💓 KICKAI system heartbeat - all services running")
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down KICKAI...")
        
    except Exception as e:
        logger.error(f"❌ Failed to start KICKAI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    # FORCE DEPLOYMENT: 2024-12-19 16:30 UTC - Simplified Health Server
