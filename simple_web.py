#!/usr/bin/env python3
"""
Simple Web Server for KICKAI Railway Deployment
Handles health checks and basic web requests
"""

import os
import logging
import sys
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if sys.path and src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="KICKAI Bot", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "ok",
        "service": "KICKAI Telegram Bot",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "KICKAI Telegram Bot",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
    }

@app.get("/status")
async def status():
    """Status endpoint."""
    return {
        "status": "running",
        "service": "KICKAI Telegram Bot",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "unknown")
    }

def main():
    """Main entry point."""
    try:
        # Get port from Railway
        port = int(os.getenv("PORT", 8080))
        
        logger.info(f"🚀 Starting Simple KICKAI Web Server on port {port}")
        logger.info(f"🌐 Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'unknown')}")
        logger.info(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 