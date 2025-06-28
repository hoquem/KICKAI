#!/usr/bin/env python3
"""
KICKAI Main Application Entry Point
Handles web server, bot runner, and monitoring for Railway deployment
"""

import os
import threading
import time
import logging
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for monitoring
bot_runner = None
system_metrics = {}
app_metrics = {
    'start_time': time.time(),
    'requests_processed': 0,
    'requests_failed': 0,
    'bot_status': 'stopped'
}

def get_system_metrics():
    """Get basic system metrics."""
    try:
        import psutil
        return {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'process_count': len(psutil.pids())
        }
    except ImportError:
        return {
            'timestamp': time.time(),
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'process_count': 0,
            'note': 'psutil not available'
        }

def start_bot():
    """Start the Telegram bot in a separate thread."""
    global bot_runner, app_metrics
    
    try:
        # Fix imports for Railway deployment
        import sys
        import os
        
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        sys.path.insert(0, project_root)
        
        from telegram_command_handler import TelegramCommandHandler
        from run_telegram_bot import TelegramBotRunner
        
        logger.info("Starting Telegram bot...")
        bot_runner = TelegramBotRunner()
        app_metrics['bot_status'] = 'starting'
        
        # Test connection first
        if bot_runner.test_connection():
            app_metrics['bot_status'] = 'running'
            logger.info("Bot started successfully")
            bot_runner.run_polling()
        else:
            app_metrics['bot_status'] = 'failed'
            logger.error("Bot failed to start")
            
    except Exception as e:
        app_metrics['bot_status'] = 'error'
        logger.error(f"Bot error: {e}")

def start_monitoring():
    """Start monitoring in a separate thread."""
    global system_metrics
    
    while True:
        try:
            system_metrics = get_system_metrics()
            logger.debug(f"System metrics: {system_metrics}")
            time.sleep(60)  # Collect metrics every minute
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            time.sleep(60)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway."""
    global system_metrics, app_metrics, bot_runner
    
    try:
        # Update request metrics
        app_metrics['requests_processed'] += 1
        
        # Check if bot is running
        bot_status = app_metrics['bot_status']
        if bot_runner:
            try:
                # Try to get bot info to verify it's still running
                bot_runner.test_connection()
                bot_status = 'running'
            except:
                bot_status = 'error'
        
        response = {
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime': time.time() - app_metrics['start_time'],
            'bot_status': bot_status,
            'system_metrics': system_metrics,
            'app_metrics': app_metrics,
            'environment': os.getenv('ENVIRONMENT', 'unknown')
        }
        
        return jsonify(response)
        
    except Exception as e:
        app_metrics['requests_failed'] += 1
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/metrics')
def metrics():
    """Detailed metrics endpoint."""
    global system_metrics, app_metrics
    
    return jsonify({
        'system': system_metrics,
        'application': app_metrics,
        'environment': os.getenv('ENVIRONMENT', 'unknown')
    })

@app.route('/')
def home():
    """Home endpoint."""
    return jsonify({
        'service': 'KICKAI Telegram Bot',
        'version': '1.0.0',
        'status': 'running',
        'environment': os.getenv('ENVIRONMENT', 'unknown'),
        'endpoints': {
            'health': '/health',
            'metrics': '/metrics'
        }
    })

@app.route('/bot/status')
def bot_status():
    """Bot status endpoint."""
    global bot_runner, app_metrics
    
    try:
        if bot_runner:
            is_connected = bot_runner.test_connection()
            return jsonify({
                'status': 'connected' if is_connected else 'disconnected',
                'bot_status': app_metrics['bot_status'],
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'status': 'not_initialized',
                'bot_status': app_metrics['bot_status'],
                'timestamp': time.time()
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/bot/restart', methods=['POST'])
def restart_bot():
    """Restart the bot."""
    global bot_runner, app_metrics
    
    try:
        logger.info("Restarting bot...")
        app_metrics['bot_status'] = 'restarting'
        
        # Stop current bot if running
        if bot_runner:
            try:
                # This would need to be implemented in TelegramBotRunner
                pass
            except:
                pass
        
        # Start new bot thread
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        
        return jsonify({
            'status': 'restarting',
            'message': 'Bot restart initiated',
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Bot restart failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }), 500

def main():
    """Main function to start all services."""
    logger.info("Starting KICKAI application...")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting web server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    main()
