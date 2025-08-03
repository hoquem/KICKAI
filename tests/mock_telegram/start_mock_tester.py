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
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Configure logging
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.mock_telegram.backend.mock_telegram_service import app as mock_app
from tests.mock_telegram.backend.config import get_config, validate_config

# Create a combined FastAPI app
app = FastAPI(title="Mock Telegram Tester")

# Mount the mock Telegram API
app.mount("/api", mock_app)

# Add WebSocket endpoint at root level
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    # Get the mock service from the imported module
    from tests.mock_telegram.backend.mock_telegram_service import mock_service
    await mock_service.connect_websocket(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        await mock_service.disconnect_websocket(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await mock_service.disconnect_websocket(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mock_telegram_tester"}

# Serve the enhanced frontend by default
@app.get("/")
async def serve_enhanced_frontend():
    """Serve the enhanced mock Telegram tester frontend"""
    frontend_path = Path(__file__).parent / "frontend" / "enhanced_index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    else:
        # Fallback to regular index.html if enhanced version doesn't exist
        fallback_path = Path(__file__).parent / "frontend" / "index.html"
        if fallback_path.exists():
            return FileResponse(str(fallback_path))
        else:
            return {"error": "Frontend files not found"}

@app.get("/legacy")
async def serve_legacy_frontend():
    """Serve the legacy mock Telegram tester frontend"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    else:
        return {"error": "Legacy frontend not found"}

# Serve static files (frontend) - but exclude WebSocket paths and root
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path), html=True, check_dir=False), name="static")


def main():
    """Main startup function"""
    print("🚀 Starting Enhanced Mock Telegram Tester...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not (project_root / "kickai").exists():
        print("❌ Error: Must run from project root directory")
        sys.exit(1)
    
    # Set up environment
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Load test environment variables
    test_env_file = project_root / ".env.test"
    if test_env_file.exists():
        print(f"📄 Loading test environment from: {test_env_file}")
        from dotenv import load_dotenv
        load_dotenv(test_env_file)
        print("✅ Test environment loaded")
    else:
        print(f"⚠️  Test environment file not found: {test_env_file}")
        print("Using default environment variables")
    
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
    print(f"🌐 Enhanced frontend will be available at: http://{config.host}:{config.port}")
    print(f"📄 Legacy frontend available at: http://{config.host}:{config.port}/legacy")
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