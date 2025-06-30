#!/usr/bin/env python3
"""
Full System Deployment Script for KICKAI
Deploys the complete system including CrewAI agents, Telegram bot, and monitoring.
"""

import os
import sys
import logging
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required environment variables
REQUIRED_ENV_VARS = [
    'TELEGRAM_BOT_TOKEN',
    'FIREBASE_PROJECT_ID',
    'FIREBASE_PRIVATE_KEY_ID',
    'FIREBASE_PRIVATE_KEY',
    'FIREBASE_CLIENT_EMAIL',
    'FIREBASE_CLIENT_ID',
    'FIREBASE_AUTH_URI',
    'FIREBASE_TOKEN_URI',
    'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
    'FIREBASE_CLIENT_X509_CERT_URL',
    'GOOGLE_API_KEY',
    'OPENAI_API_KEY',  # Required by CrewAI even if using Gemini
]

def check_environment():
    """Check if all required environment variables are set."""
    missing_vars = []
    
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def check_firebase_connection():
    """Test Firebase connection."""
    try:
        from src.tools.firebase_tools import get_firebase_client
        client = get_firebase_client()
        # Test a simple query
        client.collection('teams').limit(1).get()
        logger.info("✅ Firebase connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Firebase connection failed: {e}")
        return False

def check_ai_provider():
    """Check AI provider configuration."""
    try:
        from config import config
        ai_provider = config.ai_provider
        logger.info(f"✅ AI Provider configured: {ai_provider}")
        return True
    except Exception as e:
        logger.error(f"❌ AI Provider configuration failed: {e}")
        return False

def run_health_check():
    """Run health check to verify system components."""
    try:
        result = subprocess.run([sys.executable, 'health_check.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✅ Health check passed")
            return True
        else:
            logger.error(f"❌ Health check failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False

def start_monitoring():
    """Start monitoring dashboard."""
    try:
        logger.info("Starting monitoring dashboard...")
        # Start monitoring in background
        subprocess.Popen([sys.executable, 'scripts/monitoring_dashboard.py'])
        logger.info("✅ Monitoring dashboard started")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start monitoring: {e}")
        return False

def deploy_to_railway():
    """Deploy the system to Railway."""
    try:
        logger.info("Deploying to Railway...")
        
        # Check if Railway CLI is installed
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error("❌ Railway CLI not found. Please install it first.")
            return False
        
        # Deploy to Railway
        result = subprocess.run(['railway', 'deploy'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Deployment to Railway successful")
            return True
        else:
            logger.error(f"❌ Railway deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Railway deployment failed: {e}")
        return False

def main():
    """Main deployment function."""
    logger.info("🚀 Starting KICKAI Full System Deployment")
    logger.info(f"📅 Deployment timestamp: {datetime.now()}")
    
    # Step 1: Check environment
    logger.info("\n📋 Step 1: Checking environment variables...")
    if not check_environment():
        logger.error("❌ Environment check failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Check Firebase connection
    logger.info("\n🔥 Step 2: Testing Firebase connection...")
    if not check_firebase_connection():
        logger.error("❌ Firebase connection failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Check AI provider
    logger.info("\n🤖 Step 3: Checking AI provider configuration...")
    if not check_ai_provider():
        logger.error("❌ AI provider configuration failed. Exiting.")
        sys.exit(1)
    
    # Step 4: Run health check
    logger.info("\n🏥 Step 4: Running health check...")
    if not run_health_check():
        logger.error("❌ Health check failed. Exiting.")
        sys.exit(1)
    
    # Step 5: Start monitoring
    logger.info("\n📊 Step 5: Starting monitoring...")
    if not start_monitoring():
        logger.warning("⚠️ Monitoring failed to start, but continuing...")
    
    # Step 6: Deploy to Railway (optional)
    deploy_choice = input("\n🚂 Do you want to deploy to Railway? (y/n): ").lower().strip()
    if deploy_choice == 'y':
        logger.info("\n🚂 Step 6: Deploying to Railway...")
        if not deploy_to_railway():
            logger.error("❌ Railway deployment failed.")
            sys.exit(1)
    
    # Step 7: Start the system locally
    logger.info("\n🎯 Step 7: Starting the system locally...")
    try:
        logger.info("Starting KICKAI system...")
        subprocess.run([sys.executable, 'railway_main.py'])
    except KeyboardInterrupt:
        logger.info("\n👋 System stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 