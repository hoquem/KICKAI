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
    
    print("📁 Project root:", project_root)
    print("🔧 Mock service will run on: http://localhost:8001")
    print("🌐 Frontend will be available at: http://localhost:8001")
    print("=" * 50)
    
    # Start the server
    try:
        print("🔄 Starting server...")
        uvicorn.run(
            "start_mock_tester:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 