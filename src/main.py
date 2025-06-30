#!/usr/bin/env python3
"""
Main entry point for KICKAI application
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import monitoring
from src.monitoring import AppMonitor

# Import configuration
from config import config

# Version and deployment info
VERSION = "1.4.5-signal-fix"
DEPLOYMENT_TIME = "2024-12-19 19:15 UTC"

def test_firebase_connection():
    """Test Firebase connection."""
    try:
        from src.tools.firebase_tools import get_firebase_client
        client = get_firebase_client()
        # Test a simple query
        client.collection('teams').limit(1).get()
        return {"status": "success", "message": "Firebase connection successful"}
    except Exception as e:
        return {"status": "error", "message": f"Firebase connection failed: {str(e)}"}

def get_system_info():
    """Get comprehensive system information."""
    try:
        # Get environment info
        environment = os.getenv('RAILWAY_ENVIRONMENT', 'development')
        python_version = os.sys.version
        working_dir = os.getcwd()
        port = int(os.getenv('PORT', 8080))
        
        # Test Firebase connection
        firebase_status = test_firebase_connection()
        
        # Get configuration info
        ai_provider = config.ai_provider
        database_type = config.database_config['type']
        
        return {
            'version': VERSION,
            'deployment_time': DEPLOYMENT_TIME,
            'environment': environment,
            'python_version': python_version,
            'working_directory': working_dir,
            'port': port,
            'ai_provider': ai_provider,
            'database_type': database_type,
            'firebase': firebase_status,
        }
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            'version': VERSION,
            'deployment_time': DEPLOYMENT_TIME,
            'error': str(e)
        }

def main():
    """Main application entry point."""
    logger.info("🚀 Starting KICKAI on Railway...")
    logger.info(f"📅 Deployment timestamp: {DEPLOYMENT_TIME}")
    logger.info(f"🏆 Version: {VERSION}")
    logger.info("🏆 Match Management System: ACTIVE")
    logger.info("🏥 Enhanced Logging: ACTIVE")
    
    # Get system info
    system_info = get_system_info()
    logger.info(f"🌍 Environment: {system_info['environment']}")
    logger.info(f"🔢 Port: {system_info['port']}")
    logger.info(f"🐍 Python version: {system_info['python_version']}")
    logger.info(f"📁 Working directory: {system_info['working_directory']}")
    
    # Test Firebase connection first
    firebase_status = test_firebase_connection()
    if firebase_status['status'] != 'success':
        logger.error(f"Firebase connection failed: {firebase_status['message']}")
        app_metrics.metrics['bot_status'] = 'firebase_error'
    else:
        logger.info("✅ Firebase connection successful")
    
    # Start health server
    logger.info("🏥 Starting health server...")
    try:
        from health_check import start_health_server
        health_thread = start_health_server()
        logger.info("✅ Health server started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start health server: {e}")
    
    # Start the main application
    try:
        from run_telegram_bot import main as start_bot
        start_bot()
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
