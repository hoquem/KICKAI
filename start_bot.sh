#!/bin/bash
# KICKAI Bot Startup Script
#
# This script follows the ground rules for starting the bot locally:
# - Always uses run_bot_local.py
# - Sets PYTHONPATH to src
# - Activates virtual environment
# - Provides clear feedback

set -e  # Exit on any error

echo "🚀 Starting KICKAI Bot (Local Mode)"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create .env file with your configuration."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Package structure - no PYTHONPATH needed
echo "🔧 Using package structure - imports work directly"

# Check if run_bot_local.py exists
if [ ! -f "run_bot_local.py" ]; then
    echo "❌ run_bot_local.py not found in current directory."
    exit 1
fi

echo "🤖 Starting bot with process management..."
echo "💡 Press Ctrl+C to stop the bot"
echo "📝 Logs will be written to both console and logs/kickai.log"
echo ""

# Start the bot
python run_bot_local.py 