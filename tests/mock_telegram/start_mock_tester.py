#!/usr/bin/env python3
"""
Mock Telegram Tester Startup Script

This script starts both the mock Telegram service and serves the frontend
for a complete testing environment.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.mock_telegram.backend.mock_telegram_service import app as mock_app
from tests.mock_telegram.backend.config import get_config, validate_config

# Create a combined FastAPI app
app = FastAPI(title="Mock Telegram Tester")

# Mount the mock Telegram API
app.mount("/api", mock_app)

# Serve static files (frontend)
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mock_telegram_tester"}


def main():
    """Main startup function"""
    print("🚀 Starting Mock Telegram Tester...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not (project_root / "kickai").exists():
        print("❌ Error: Must run from project root directory")
        sys.exit(1)
    
    # Set up environment
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Load and validate configuration
    try:
        config = get_config()
        validate_config(config)
        print("✅ Configuration loaded and validated")
    except Exception as e:
        print(f"⚠️  Configuration error: {e}")
        print("Using default configuration")
        config = get_config()
    
    print("📁 Project root:", project_root)
    print(f"🔧 Mock service will run on: http://{config.host}:{config.port}")
    print(f"🌐 Frontend will be available at: http://{config.host}:{config.port}")
    print(f"📊 Max messages: {config.max_messages}, Max users: {config.max_users}")
    print(f"🤖 Bot integration: {'Enabled' if config.enable_bot_integration else 'Disabled'}")
    print("=" * 50)
    
    # Start the server
    try:
        print("🔄 Starting server...")
        uvicorn.run(
            "start_mock_tester:app",
            host=config.host,
            port=config.port,
            reload=config.debug,
            log_level=config.log_level.lower()
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 