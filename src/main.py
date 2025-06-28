#!/usr/bin/env python3
"""
KICKAI Main Application
Flask web server with Telegram bot integration and monitoring
"""

import os
import sys
import time
import logging
import threading
from flask import Flask, jsonify, request
from datetime import datetime

# Add current directory to Python path for Railway deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Import monitoring and bot components
try:
    from monitoring import SystemMonitor, AppMetrics
    from tools.supabase_tools import test_supabase_connection
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback imports for Railway deployment
    try:
        sys.path.insert(0, os.path.join(project_root, 'src'))
        from monitoring import SystemMonitor, AppMetrics
        from tools.supabase_tools import test_supabase_connection
    except ImportError as e2:
        print(f"Fallback import error: {e2}")
        # Create minimal fallback classes
        class SystemMonitor:
            def get_metrics(self):
                return {"status": "monitoring_unavailable"}
        class AppMetrics:
            def __init__(self):
                self.metrics = {"status": "metrics_unavailable"}
        def test_supabase_connection():
            return {"status": "error", "message": "Supabase tools unavailable"}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variables
bot_runner = None
system_monitor = SystemMonitor()
app_metrics = AppMetrics()

@app.route('/')
def home():
    """Home endpoint with basic info."""
    return jsonify({
        'app': 'KICKAI',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Test Supabase connection
        supabase_status = test_supabase_connection()
        
        # Get system metrics
        system_metrics = system_monitor.get_metrics()
        
        # Get app metrics
        app_metrics_data = app_metrics.metrics
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'supabase': supabase_status,
            'system': system_metrics,
            'app': app_metrics_data
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/metrics')
def metrics():
    """Metrics endpoint."""
    try:
        return jsonify({
            'system': system_monitor.get_metrics(),
            'app': app_metrics.metrics,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500

def start_bot():
    """Start the Telegram bot in a separate thread."""
    global bot_runner, app_metrics
    
    try:
        # Test Supabase connection first
        supabase_status = test_supabase_connection()
        if supabase_status['status'] != 'success':
            logger.error(f"Supabase connection failed: {supabase_status['message']}")
            app_metrics.metrics['bot_status'] = 'supabase_error'
            return
        
        # Import bot components
        try:
            from telegram_command_handler import TelegramCommandHandler
            from run_telegram_bot import TelegramBotRunner
        except ImportError as e:
            logger.error(f"Bot import error: {e}")
            app_metrics.metrics['bot_status'] = 'import_error'
            return
        
        logger.info("Starting Telegram bot...")
        bot_runner = TelegramBotRunner()
        app_metrics.metrics['bot_status'] = 'starting'
        
        # Test connection first
        if bot_runner.test_connection():
            app_metrics.metrics['bot_status'] = 'connected'
            logger.info("✅ Bot connected successfully!")
            
            # Start bot in background thread
            bot_thread = threading.Thread(target=bot_runner.run_polling, daemon=True)
            bot_thread.start()
            app_metrics.metrics['bot_status'] = 'running'
            logger.info("✅ Bot started successfully!")
        else:
            app_metrics.metrics['bot_status'] = 'connection_failed'
            logger.error("❌ Bot connection failed")
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        app_metrics.metrics['bot_status'] = 'error'
        app_metrics.metrics['bot_error'] = str(e)

def main():
    """Main application entry point."""
    logger.info("🚀 Starting KICKAI application...")
    
    # Start bot in background
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Starting Flask app on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    main()
