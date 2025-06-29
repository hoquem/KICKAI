#!/usr/bin/env python3
"""
Railway Main Entry Point for KICKAI
Deployment timestamp: 2024-12-19 16:20 UTC - Match Management Active
Version: 1.3.0-match-management
FORCE DEPLOYMENT: 2024-12-19 16:50 UTC - Updated Firebase Credentials
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

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('railway.log')
    ]
)
logger = logging.getLogger(__name__)

def start_simple_health_server():
    """Start a simple health check server for Railway monitoring."""
    logger.info("🏥 Starting health server initialization...")
    
    try:
        logger.info("📦 Importing Flask...")
        from flask import Flask, jsonify
        import threading
        logger.info("✅ Flask imported successfully")
        
        app = Flask(__name__)
        logger.info("✅ Flask app created")
        
        @app.route('/health')
        def health_check():
            """Health check endpoint for Railway."""
            logger.info("🏥 Health check request received")
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
            logger.info("🏠 Root request received")
            return jsonify({
                'message': 'KICKAI Telegram Bot is running',
                'status': 'operational',
                'timestamp': time.time()
            })
        
        def run_server():
            try:
                port = int(os.getenv('PORT', 8080))
                logger.info(f"🏥 Starting Flask server on port {port}")
                logger.info(f"🏥 Server will bind to 0.0.0.0:{port}")
                
                # Test if port is available
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    logger.warning(f"⚠️ Port {port} might be in use")
                else:
                    logger.info(f"✅ Port {port} is available")
                
                app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
                logger.info("✅ Flask server started successfully")
                
            except Exception as e:
                logger.error(f"❌ Flask server failed to start: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        logger.info("🧵 Creating health server thread...")
        health_thread = threading.Thread(target=run_server, daemon=True)
        logger.info("🧵 Starting health server thread...")
        health_thread.start()
        
        # Wait a moment to see if thread starts successfully
        time.sleep(1)
        if health_thread.is_alive():
            logger.info("✅ Health server thread is alive")
        else:
            logger.error("❌ Health server thread died immediately")
            return None
        
        logger.info("✅ Health server started for Railway")
        return health_thread
        
    except Exception as e:
        logger.error(f"❌ Health server failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

def start_telegram_bot():
    """Start Telegram bot in a separate thread."""
    try:
        logger.info("🤖 Importing Telegram bot...")
        from run_telegram_bot import main as run_bot
        logger.info("✅ Telegram bot imported successfully")
        logger.info("🤖 Starting Telegram bot with match management...")
        run_bot()
    except Exception as e:
        logger.error(f"❌ Telegram bot failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

def main():
    """Main entry point for Railway deployment."""
    try:
        logger.info("🚀 Starting KICKAI on Railway...")
        logger.info("📅 Deployment timestamp: 2024-12-19 16:50 UTC")
        logger.info("🏆 Version: 1.3.0-match-management")
        logger.info("🏆 Match Management System: ACTIVE")
        logger.info("🏥 Enhanced Logging: ACTIVE")
        
        # Log environment info
        logger.info(f"🌍 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
        logger.info(f"🔢 Port: {os.getenv('PORT', '8080')}")
        logger.info(f"🐍 Python version: {sys.version}")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        
        # Start health server first (for Railway health checks)
        logger.info("🏥 Starting health server...")
        health_thread = start_simple_health_server()
        if not health_thread:
            logger.error("❌ Health server failed to start")
            sys.exit(1)
        
        # Wait a moment for health server to start
        logger.info("⏳ Waiting for health server to start...")
        time.sleep(5)
        
        # Check if health server is still alive
        if health_thread.is_alive():
            logger.info("✅ Health server thread is still alive")
        else:
            logger.error("❌ Health server thread died")
            sys.exit(1)
        
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
                
                # Check if threads are still alive
                if health_thread.is_alive():
                    logger.info("✅ Health server thread is alive")
                else:
                    logger.error("❌ Health server thread died")
                
                if bot_thread.is_alive():
                    logger.info("✅ Bot thread is alive")
                else:
                    logger.warning("⚠️ Bot thread died")
                    
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down KICKAI...")
        
    except Exception as e:
        logger.error(f"❌ Failed to start KICKAI: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    # FORCE DEPLOYMENT: 2024-12-19 16:40 UTC - Firebase Fix + Dependencies
