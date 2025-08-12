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

# Serve the Liverpool FC themed frontend by default
@app.get("/")
async def serve_lfc_frontend():
    """Serve the Liverpool FC themed mock Telegram tester frontend"""
    # First try the root mock_tester.html (consolidated version)
    root_frontend_path = project_root / "mock_tester.html"
    if root_frontend_path.exists():
        return FileResponse(str(root_frontend_path))
    
    # Fallback to the root mock_tester.html
    return {"error": "Liverpool FC themed frontend not found. Please ensure mock_tester.html exists in the project root."}

# Static files are no longer needed since we serve the consolidated mock_tester.html from root


def main():
    """Main startup function"""
    print("🚀 Starting Liverpool FC Mock Telegram Tester...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not (project_root / "kickai").exists():
        print("❌ Error: Must run from project root directory")
        sys.exit(1)
    
    # Set up environment
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Validate configuration
    try:
        config = get_config()
        validate_config(config)
        print("✅ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Start the server
    host = config.host
    port = config.port
    
    print(f"🌐 Starting server on http://{host}:{port}")
    print(f"📱 Mock Telegram API: http://{host}:{port}/api")
    print(f"🔗 WebSocket: ws://{host}:{port}/ws")
    print(f"💚 Health Check: http://{host}:{port}/health")
    print("=" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(f"http://{host}:{port}")
            print("🌐 Browser opened automatically")
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print(f"📱 Please open: http://{host}:{port}")
    
    # Start browser in a separate thread
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 