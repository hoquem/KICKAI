#!/usr/bin/env python3
"""
Combined Mock System Startup Script

This script starts both the Mock Telegram Tester and the main KICKAI bot system
for complete end-to-end testing without real Telegram accounts.
"""

import asyncio
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def setup_environment():
    """Set up the environment for the mock system."""
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Set environment variables for mock testing
    os.environ['PYTHONPATH'] = f"{project_root}/src:{project_root}"
    os.environ['TEST_MODE'] = 'true'
    
    print("🔧 Environment configured for mock testing")

def start_mock_telegram_tester():
    """Start the Mock Telegram Tester service."""
    print("🚀 Starting Mock Telegram Tester...")
    
    # Start the mock tester in a subprocess
    mock_process = subprocess.Popen([
        sys.executable, 
        "tests/mock_telegram/start_mock_tester.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for it to start
    time.sleep(5)
    
    # Check if it's running
    try:
        import httpx
        response = httpx.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Mock Telegram Tester is running on http://localhost:8001")
            return mock_process
        else:
            print("❌ Mock Telegram Tester failed to start")
            return None
    except Exception as e:
        print(f"❌ Mock Telegram Tester failed to start: {e}")
        return None

def start_main_bot_system():
    """Start the main KICKAI bot system."""
    print("🤖 Starting Main KICKAI Bot System...")
    
    # Start the main bot in a subprocess
    bot_process = subprocess.Popen([
        sys.executable, 
        "run_bot_local.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for it to start
    time.sleep(10)
    
    print("✅ Main Bot System started")
    return bot_process

def cleanup_processes(processes):
    """Clean up running processes."""
    print("\n🛑 Shutting down services...")
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def main():
    """Main function to start the complete mock system."""
    print("🎯 Starting Complete Mock KICKAI System")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Start services
    processes = []
    
    try:
        # Start Mock Telegram Tester
        mock_process = start_mock_telegram_tester()
        if mock_process:
            processes.append(mock_process)
        else:
            print("❌ Failed to start Mock Telegram Tester")
            return 1
        
        # Start Main Bot System
        bot_process = start_main_bot_system()
        if bot_process:
            processes.append(bot_process)
        else:
            print("❌ Failed to start Main Bot System")
            return 1
        
        print("\n🎉 Complete Mock System is Running!")
        print("=" * 50)
        print("📱 Mock Telegram Tester: http://localhost:8001")
        print("🤖 Main Bot System: Running on local environment")
        print("🔗 WebSocket: Connected for real-time updates")
        print("\n💡 Usage:")
        print("   1. Open http://localhost:8001 in your browser")
        print("   2. Select a user and chat")
        print("   3. Send messages like /help, /myinfo, etc.")
        print("   4. Watch real-time bot responses")
        print("\n⏹️  Press Ctrl+C to stop all services")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                for process in processes:
                    if process.poll() is not None:
                        print(f"❌ Process {process.pid} has stopped unexpectedly")
                        return 1
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
            
    except Exception as e:
        print(f"❌ Error starting mock system: {e}")
        return 1
    finally:
        cleanup_processes(processes)
        print("✅ All services stopped")

if __name__ == "__main__":
    sys.exit(main()) 