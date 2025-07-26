#!/usr/bin/env python3
"""
KICKAI Bot Startup Script - Railway Deployment

A clean, robust bot startup script for Railway deployment with health check server.
"""

import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Optional

# Enable nested event loops for environments that already have an event loop running
import nest_asyncio
nest_asyncio.apply()

from kickai.core.settings import initialize_settings, get_settings
from kickai.database.firebase_client import initialize_firebase_client
from kickai.features.team_administration.domain.services.multi_bot_manager import MultiBotManager
from kickai.core.dependency_container import get_service, get_singleton, ensure_container_initialized
from kickai.features.team_administration.domain.interfaces.team_service_interface import ITeamService
from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
from kickai.core.startup_validator import StartupValidator
from kickai.core.logging_config import logger

# Global state
multi_bot_manager: Optional[MultiBotManager] = None
shutdown_event = asyncio.Event()


def setup_logging():
    """Configure logging for Railway deployment - console only."""
    # Loguru is already configured in core.logging_config to log to console
    # Railway will capture console output for log aggregation
    logger.info("📝 Logging configured for Railway deployment")
    logger.info("📄 Console output: INFO level and above")
    logger.info("🔄 Railway will capture console logs for monitoring")


def setup_environment():
    """Set up the environment and load configuration."""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize settings
        initialize_settings()
        config = get_settings()
        
        # Validate required fields (only Firebase and AI config, not bot tokens)
        errors = config.validate_required_fields()
        if errors:
            logger.error("❌ Configuration errors:")
            for error in errors:
                logger.error(f"   - {error}")
            raise ValueError("Configuration validation failed")
        
        # Configure logging
        setup_logging()
        logger.info("✅ Configuration loaded successfully and logging configured")
        
        # Set up CrewAI logging to redirect to loguru
        from kickai.utils.crewai_logging import setup_crewai_logging
        setup_crewai_logging("INFO")  # Use INFO level for Railway
        
        # Initialize Firebase
        initialize_firebase_client(config)
        logger.info("✅ Firebase client initialized")
        
        # Ensure dependency container is initialized with Firebase client
        ensure_container_initialized()
        logger.info("✅ Dependency container initialized with Firebase client")
        
        return config
        
    except Exception as e:
        logger.critical(f"❌ Failed to setup environment: {e}", exc_info=True)
        raise


async def run_system_validation():
    """Run comprehensive system validation before starting bots."""
    try:
        logger.info("🔍 Running system validation...")
        
        # Create validator and run checks
        validator = StartupValidator()
        context = {"team_id": "KTI"}  # Use the team ID from your configuration
        
        report = await validator.validate(context)
        
        # Print validation report
        validator.print_report(report)
        
        # Check if system is healthy
        if not report.is_healthy():
            logger.error("❌ System validation failed! Critical issues found:")
            for failure in report.critical_failures:
                logger.error(f"   • {failure}")
            
            logger.error("🚫 Cannot start bots due to critical validation failures")
            return False
        
        if report.warnings:
            logger.warning("⚠️ System validation completed with warnings:")
            for warning in report.warnings:
                logger.warning(f"   • {warning}")
            logger.info("💡 Consider addressing warnings for optimal performance")
        
        logger.info("✅ System validation passed! All critical components are healthy")
        return True
        
    except Exception as e:
        logger.error(f"❌ System validation failed with error: {e}")
        return False


async def create_multi_bot_manager():
    """Create and configure the multi-bot manager."""
    global multi_bot_manager
    
    try:
        # Get services from dependency container
        team_service = get_service(ITeamService)
        data_store = get_singleton("data_store")
        
        # Create multi-bot manager
        multi_bot_manager = MultiBotManager(data_store, team_service)
        
        # Load bot configurations from Firestore
        bot_configs = await multi_bot_manager.load_bot_configurations()
        
        if not bot_configs:
            logger.warning("⚠️ No bot configurations found in teams collection")
            logger.info("💡 You need to create bot configurations in the teams collection")
            return None
        
        logger.info(f"✅ Multi-bot manager created with {len(bot_configs)} bot configurations")
        return multi_bot_manager
        
    except Exception as e:
        logger.error(f"❌ Failed to create multi-bot manager: {e}")
        raise


def start_health_check_server():
    """Start Flask health check server for Railway deployment."""
    try:
        from flask import Flask, jsonify
        from datetime import datetime
        
        app = Flask(__name__)
        
        @app.route('/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'environment': os.getenv('ENVIRONMENT', 'unknown'),
                'version': '1.0.0',
                'bot_running': multi_bot_manager is not None and multi_bot_manager.is_running()
            })
        
        @app.route('/health/detailed')
        def detailed_health_check():
            checks = {
                'bot_running': multi_bot_manager is not None and multi_bot_manager.is_running(),
                'environment': os.getenv('ENVIRONMENT', 'unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            overall_status = 'healthy' if checks['bot_running'] else 'unhealthy'
            
            return jsonify({
                'status': overall_status,
                'checks': checks
            })
        
        # Start Flask app in a separate thread
        port = int(os.getenv('PORT', 8080))
        Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False)).start()
        logger.info(f"✅ Health check server started on port {port}")
        
    except ImportError:
        logger.warning("⚠️ Flask not available, health check server not started")


def flush_and_close_loggers():
    """Flush and close all loggers."""
    # Loguru handles cleanup automatically
    logger.info("📝 Logging cleanup completed")

async def main():
    """Main async entry point with clean shutdown."""
    global multi_bot_manager
    shutdown_event = asyncio.Event()

    def _signal_handler():
        logger.info("🛑 Received shutdown signal, initiating graceful shutdown...")
        shutdown_event.set()

    try:
        logger.info("🎯 KICKAI Multi-Bot Manager Starting (Railway Mode)...")
        
        # Setup environment
        config = setup_environment()
        
        # Start health check server (Railway only)
        start_health_check_server()
        
        # Run system validation
        validation_passed = await run_system_validation()
        if not validation_passed:
            logger.error("❌ System validation failed. Exiting.")
            return
        
        # Create multi-bot manager
        manager = await create_multi_bot_manager()
        if not manager:
            logger.error("❌ No bot configurations available in teams collection. Exiting.")
            return
        
        # Start all bots
        await manager.start_all_bots()
        
        # Send startup messages
        await manager.send_startup_messages()
        
        # Set up signal handling for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _signal_handler)
            except NotImplementedError:
                signal.signal(sig, lambda s, f: asyncio.create_task(shutdown_event.set()))
        
        logger.info("🤖 Multi-bot manager is running. Press Ctrl+C to exit.")
        logger.info(f"📊 Running bots: {list(manager.bots.keys())}")
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        logger.info("🛑 Shutdown signal received, stopping bots...")
        
        # Send shutdown messages
        await manager.send_shutdown_messages()
        
        # Stop all bots
        await manager.stop_all_bots()
        
        logger.info("✅ Multi-bot manager shutdown complete")
        flush_and_close_loggers()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}", exc_info=True)
        raise


def main_sync():
    """Synchronous entry point."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main_sync() 