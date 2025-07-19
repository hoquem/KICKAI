#!/bin/bash

# KICKAI Safe Bot Startup Script
# This script ensures only one bot instance is running at a time

echo "🤖 KICKAI Safe Bot Startup Script"
echo "=================================="

# Function to kill existing bot processes
kill_existing_bots() {
    echo "🔍 Checking for existing bot processes..."
    
    # Find all python processes running run_bot_local.py
    PIDS=$(ps aux | grep python | grep run_bot_local | grep -v grep | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "⚠️  Found existing bot processes: $PIDS"
        echo "🛑 Killing existing bot processes..."
        
        for PID in $PIDS; do
            echo "   Killing process $PID..."
            kill $PID 2>/dev/null
            sleep 1
            
            # Force kill if still running
            if kill -0 $PID 2>/dev/null; then
                echo "   Force killing process $PID..."
                kill -9 $PID 2>/dev/null
            fi
        done
        
        echo "✅ Existing bot processes killed"
        sleep 2
    else
        echo "✅ No existing bot processes found"
    fi
}

# Function to start the bot
start_bot() {
    echo "🚀 Starting KICKAI bot..."
    echo "📝 Logs will be saved to: kickai_nlp_test.log"
    echo "=================================="
    
    # Activate virtual environment and start bot
    source venv/bin/activate && python run_bot_local.py 2>&1 | tee kickai_nlp_test.log
}

# Main execution
main() {
    # Kill any existing bot processes
    kill_existing_bots
    
    # Start the bot
    start_bot
}

# Run main function
main 